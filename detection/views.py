from django.http.response import HttpResponse, HttpResponsePermanentRedirect, HttpResponseRedirect


import os
import cv2
import numpy as np
import json
import csv
import io
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone
from .models import Criminal, DetectionReport, DetectionResult
from datetime import datetime
from PIL import Image


def index(request):
    """Citizen dashboard - upload image for criminal detection"""
    # If user is authenticated and is staff, redirect to police dashboard
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('police_dashboard')
    # If user is authenticated but not staff, show citizen dashboard
    elif request.user.is_authenticated:
        return render(request, 'detection/citizen_dashboard.html')
    # If not authenticated, redirect to login
    else:
        return redirect('citizen_login')

def camera_page(request) -> HttpResponsePermanentRedirect | HttpResponseRedirect | HttpResponse:
    """Camera page - capture image directly from camera"""
    # If user is not authenticated, redirect to login
    if not request.user.is_authenticated:
        return redirect('citizen_login')
    # If user is authenticated and is staff, redirect to police dashboard
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('police_dashboard')
    return render(request, 'detection/camera.html')

def police_dashboard(request):
    """Police dashboard - view detection reports"""
    # If user is not authenticated, redirect to unified login
    if not request.user.is_authenticated:
        return redirect('citizen_login')
    
    # If user is not staff, redirect to citizen dashboard
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Police access only.')
        return redirect('citizen_dashboard')
    
    # Check if this is an AJAX request for data
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Get all detection reports
            reports = DetectionReport.objects.all().order_by('-created_at')[:10]  # Limit to 10 most recent
            
            # Serialize the data
            reports_data = []
            for report in reports:
                # Get detection results for this report
                results = DetectionResult.objects.filter(report=report)
                detections = []
                for result in results:
                    # Ensure confidence is properly clamped
                    confidence = float(result.confidence)
                    if confidence > 100.0:
                        confidence = 100.0
                    elif confidence < 0.0:
                        confidence = 0.0
                        
                    detections.append({
                        'criminal_name': result.criminal.name,
                        'confidence': confidence,
                    })
                
                reports_data.append({
                    'id': str(report.id),
                    'detection_time': report.detection_time.strftime('%b %d, %Y %H:%M'),
                    'location': report.location if report.location else '',
                    'status': 'Criminal Detected' if detections else 'No Match',
                    'has_detections': len(detections) > 0,
                    'first_detection_id': str(results.first().id) if results.exists() and results.first() else None,
                })
            
            # Get statistics
            total_reports = DetectionReport.objects.count()
            criminals_detected = DetectionResult.objects.count()
            pending_review = DetectionReport.objects.filter(is_processed=False).count()
            
            # Calculate accuracy rate based on verified detections
            accuracy_rate = calculate_detection_accuracy()
            
            return JsonResponse({
                'reports': reports_data,
                'stats': {
                    'total_reports': total_reports,
                    'criminals_detected': criminals_detected,
                    'pending_review': pending_review,
                    'accuracy_rate': accuracy_rate
                }
            })
        except Exception as e:
            print(f"Error in AJAX request: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    # Get statistics
    try:
        total_reports = DetectionReport.objects.count()
        criminals_detected = DetectionResult.objects.count()
        pending_review = DetectionReport.objects.filter(is_processed=False).count()
        
        # Calculate accuracy rate based on verified detections
        accuracy_rate = calculate_detection_accuracy()
        
        stats = {
            'total_reports': total_reports,
            'criminals_detected': criminals_detected,
            'pending_review': pending_review,
            'accuracy_rate': accuracy_rate
        }
        
        # Get all detection reports for initial page load
        reports = DetectionReport.objects.all().order_by('-created_at')
        return render(request, 'detection/police_dashboard.html', {'reports': reports, 'stats': stats})
    except Exception as e:
        print(f"Error in police dashboard: {e}")
        messages.error(request, f'Error loading dashboard: {e}')
        return redirect('citizen_login')

@csrf_exempt
def upload_image(request):
    """Handle image upload from citizen"""
    if request.method == 'POST':
        try:
            # Check if we have a file upload
            if request.FILES.get('image'):
                # Handle file upload
                image_file = request.FILES['image']
            elif request.POST.get('image_data'):
                # Handle base64 data upload
                image_data = request.POST['image_data']
                # Remove data URL prefix if present
                if image_data.startswith('data:image'):
                    image_data = image_data.split(',')[1]
                
                # Decode base64 data
                import base64
                from django.core.files.base import ContentFile
                from django.utils.crypto import get_random_string
                
                image_data = base64.b64decode(image_data)
                image_file = ContentFile(image_data, name=f"upload_{get_random_string(10)}.jpg")
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'No image data provided'
                })
            
            # Create a detection report
            report = DetectionReport(
                citizen=request.user if request.user.is_authenticated else None,
                location=request.POST.get('location', '')
            )
            report.save()
            
            # Save the image file
            report.photo.save(f'report_{report.id}.jpg', image_file, save=True)
            
            # Process the image for face detection
            detection_results = process_image_for_detection(report)
            
            # Save detection results
            for result in detection_results:
                # Save all results that have a criminal ID (potential matches)
                if result.get('criminal_id'):
                    # Ensure confidence is properly clamped before saving to database
                    confidence = float(result['confidence'])
                    clamped_confidence = max(0.0, min(100.0, confidence))
                    
                    detection_result = DetectionResult(
                        report=report,
                        criminal_id=result['criminal_id'],
                        confidence=clamped_confidence,  # Use clamped confidence
                        face_coordinates=json.dumps(result['face_coordinates'])
                    )
                    detection_result.save()
                # Also save results that detected a face but no match was found (for review)
                elif not result.get('is_criminal', False) and result.get('confidence', 0) >= 0:
                    # Create a placeholder criminal for "Unknown Person" if one doesn't exist
                    unknown_criminal, created = Criminal.objects.get_or_create(
                        name="Unknown Person",
                        defaults={
                            'description': 'Face detected but no match found in database',
                        }
                    )
                    
                    # Ensure confidence is properly clamped before saving to database
                    confidence = float(result['confidence'])
                    clamped_confidence = max(0.0, min(100.0, confidence))
                    
                    detection_result = DetectionResult(
                        report=report,
                        criminal=unknown_criminal,
                        confidence=clamped_confidence,  # Use clamped confidence
                        face_coordinates=json.dumps(result['face_coordinates'])
                    )
                    detection_result.save()
            
            # Update report as processed
            report.is_processed = True
            report.save(update_fields=['is_processed'])
            
            # Count total faces and criminals detected
            total_faces = len(detection_results)
            # Consider any result with a criminal_id as a potential criminal detection
            criminals_found = [result for result in detection_results if result.get('criminal_id') and result.get('confidence', 0) > 5]
            
            # Only return detailed results if criminals are found
            if len(criminals_found) > 0:
                # Enhance the criminals list with more detailed information
                enhanced_criminals = []
                for criminal_data in criminals_found:
                    try:
                        criminal = Criminal.objects.get(id=criminal_data['criminal_id'])
                        enhanced_criminals.append({
                            'id': str(criminal.id),
                            'name': criminal.name,
                            'description': criminal.description,
                            'photo_url': criminal.photo.url if criminal.photo else '',
                            'confidence': criminal_data['confidence'],
                            'face_coordinates': criminal_data['face_coordinates']
                        })
                    except Criminal.DoesNotExist:
                        # Fallback if criminal not found
                        enhanced_criminals.append({
                            'id': criminal_data['criminal_id'],
                            'name': criminal_data['criminal_name'],
                            'description': '',
                            'photo_url': '',
                            'confidence': criminal_data['confidence'],
                            'face_coordinates': criminal_data['face_coordinates']
                        })
                
                return JsonResponse({
                    'success': True,
                    'report_id': str(report.id),
                    'message': 'Potential criminal detected!',
                    'detections': detection_results,
                    'total_faces_detected': total_faces,
                    'total_criminals_found': len(criminals_found),
                    'criminals_list': enhanced_criminals,
                    'location': report.location,
                    'detection_time': report.detection_time.strftime('%b %d, %Y %H:%M')
                })
            else:
                # Show all detections even if no high-confidence matches
                enhanced_detections = []
                for result in detection_results:
                    if result.get('criminal_id'):
                        try:
                            criminal = Criminal.objects.get(id=result['criminal_id'])
                            enhanced_detections.append({
                                'id': str(criminal.id),
                                'name': criminal.name,
                                'description': criminal.description,
                                'photo_url': criminal.photo.url if criminal.photo else '',
                                'confidence': result['confidence'],
                                'face_coordinates': result['face_coordinates']
                            })
                        except Criminal.DoesNotExist:
                            enhanced_detections.append({
                                'id': result['criminal_id'],
                                'name': result.get('criminal_name', 'Unknown'),
                                'description': '',
                                'photo_url': '',
                                'confidence': result['confidence'],
                                'face_coordinates': result['face_coordinates']
                            })
                    else:
                        enhanced_detections.append({
                            'id': 'unknown',
                            'name': result.get('criminal_name', 'Unknown Person'),
                            'description': 'Face detected but no match found',
                            'photo_url': '',
                            'confidence': result['confidence'],
                            'face_coordinates': result['face_coordinates']
                        })
                
                return JsonResponse({
                    'success': True,
                    'report_id': str(report.id),
                    'message': 'Detection completed with all results',
                    'detections': detection_results,
                    'total_faces_detected': total_faces,
                    'total_criminals_found': len([r for r in detection_results if r.get('criminal_id')]),
                    'criminals_list': enhanced_detections,
                    'location': report.location,
                    'detection_time': report.detection_time.strftime('%b %d, %Y %H:%M')
                })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request'
    })


def convert_image_to_pixels(image_path):
    """Convert image to pixel array for storage and comparison"""
    try:
        # Open image using PIL for better pixel handling
        img = Image.open(image_path)
        
        # Convert to RGB if not already
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize to standard size for consistency
        img = img.resize((100, 100), Image.Resampling.LANCZOS)
        
        # Convert to numpy array
        pixel_array = np.array(img)
        
        # Normalize pixel values to 0-1 range
        normalized_pixels = pixel_array.astype(np.float32) / 255.0
        
        # Return flattened array for storage
        return normalized_pixels.flatten()
    except Exception as e:
        print(f"Error converting image to pixels: {e}")
        return None

def compare_images_pixel_by_pixel(pixels1, pixels2):
    """Compare two images pixel by pixel using multiple methods"""
    try:
        # Ensure both arrays are numpy arrays
        arr1 = np.array(pixels1)
        arr2 = np.array(pixels2)
        
        # Method 1: Mean Squared Error (MSE)
        mse = np.mean((arr1 - arr2) ** 2)
        
        # Method 2: Structural Similarity Index (SSIM) approximation
        # Calculate mean and standard deviation
        mean1, std1 = np.mean(arr1), np.std(arr1)
        mean2, std2 = np.mean(arr2), np.std(arr2)
        
        # Covariance calculation
        covariance = np.mean((arr1 - mean1) * (arr2 - mean2))
        
        # SSIM constants
        C1 = (0.01 * 255) ** 2
        C2 = (0.03 * 255) ** 2
        
        # SSIM calculation
        ssim = ((2 * mean1 * mean2 + C1) * (2 * covariance + C2)) / \
               ((mean1 ** 2 + mean2 ** 2 + C1) * (std1 ** 2 + std2 ** 2 + C2))
        
        # Method 3: Normalized Cross-Correlation
        # Normalize arrays
        norm1 = (arr1 - np.mean(arr1)) / (np.std(arr1) * len(arr1))
        norm2 = (arr2 - np.mean(arr2)) / np.std(arr2)
        ncc = np.correlate(norm1, norm2)[0]
        
        # Convert to similarity score (0-100)
        # Lower MSE means higher similarity
        mse_similarity = max(0, (1 - mse) * 100)
        
        # SSIM is already in range -1 to 1, convert to 0-100
        ssim_similarity = max(0, (ssim + 1) * 50)
        
        # NCC is in range -1 to 1, convert to 0-100
        ncc_similarity = max(0, (ncc + 1) * 50)
        
        # Weighted average of all methods
        final_similarity = (mse_similarity * 0.4 + ssim_similarity * 0.4 + ncc_similarity * 0.2)
        
        return min(100.0, max(0.0, final_similarity))
    except Exception as e:
        print(f"Error comparing images: {e}")
        return 0.0

def process_image_for_detection(report):
    """Process image and detect faces with pixel-based matching"""
    try:
        # Get the image path
        image_path = report.photo.path
        
        # Load the image
        img = cv2.imread(image_path)
        if img is None:
            return []
        
        # Convert to grayscale for face detection
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply histogram equalization to improve contrast
        gray_img = cv2.equalizeHist(gray_img)
        
        # Apply Gaussian blur to reduce noise
        gray_img = cv2.GaussianBlur(gray_img, (3, 3), 0)
        
        # Load multiple face cascade classifiers for better detection
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            alt_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'
        except AttributeError:
            # Fallback path if cv2.data is not available
            cascade_path = 'cv2/data/haarcascade_frontalface_default.xml'
            alt_cascade_path = 'cv2/data/haarcascade_frontalface_alt2.xml'
        
        face_cascade = cv2.CascadeClassifier(cascade_path)
        alt_face_cascade = cv2.CascadeClassifier(alt_cascade_path)
        
        # Detect faces with multiple classifiers and combine results
        faces1 = face_cascade.detectMultiScale(
            gray_img, 
            scaleFactor=1.05,
            minNeighbors=3,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        faces2 = alt_face_cascade.detectMultiScale(
            gray_img, 
            scaleFactor=1.08,
            minNeighbors=2,
            minSize=(25, 25),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        # Combine results from both classifiers
        all_faces = list(faces1) + list(faces2)
        
        # Remove duplicate detections by merging overlapping rectangles
        if len(all_faces) > 0:
            filtered_faces = []
            for (x, y, w, h) in all_faces:
                # Check if this face overlaps significantly with any already added face
                overlap = False
                for fx, fy, fw, fh in filtered_faces:
                    # Calculate overlap area
                    x1 = max(x, fx)
                    y1 = max(y, fy)
                    x2 = min(x + w, fx + fw)
                    y2 = min(y + h, fy + fh)
                    
                    if x1 < x2 and y1 < y2:
                        # Calculate overlap ratio
                        overlap_area = (x2 - x1) * (y2 - y1)
                        area1 = w * h
                        area2 = fw * fh
                        min_area = min(area1, area2)
                        
                        # If overlap is more than 50% of the smaller face, consider it duplicate
                        if overlap_area > 0.5 * min_area:
                            overlap = True
                            break
                
                if not overlap:
                    filtered_faces.append((x, y, w, h))
            
            faces = filtered_faces
        else:
            faces = []
        
        results = []
        
        # If no faces detected, return empty results
        if len(faces) == 0:
            return results
        
        # Convert input image to pixels for comparison
        input_pixels = convert_image_to_pixels(image_path)
        if input_pixels is None:
            return results
        
        # Get all criminals with photos
        criminals = Criminal.objects.exclude(photo='')
        
        # For each detected face, compare with criminal database
        face_results = []
        for (x, y, w, h) in faces:
            # Extract face region
            face_img = gray_img[y:y+h, x:x+w]
            
            # Apply additional preprocessing for better matching
            # Sharpen the face image
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            face_img = cv2.filter2D(face_img, -1, kernel)
            
            # Resize face for consistency
            face_img = cv2.resize(face_img, (100, 100))
            
            best_match = None
            best_confidence = 0.0
            
            # Compare with each criminal using pixel-based comparison
            for criminal in criminals:
                try:
                    # Load criminal's photo
                    criminal_image_path = os.path.join(settings.MEDIA_ROOT, str(criminal.photo))
                    if os.path.exists(criminal_image_path):
                        # Convert criminal image to pixels
                        criminal_pixels = convert_image_to_pixels(criminal_image_path)
                        if criminal_pixels is not None:
                            # Compare pixels
                            confidence = compare_images_pixel_by_pixel(input_pixels, criminal_pixels)
                            
                            # If this is a better match and above threshold
                            if confidence > best_confidence and confidence > 5:  # Low threshold for sensitivity
                                best_confidence = confidence
                                best_match = criminal
                except Exception as e:
                    # Skip this criminal if there's an error loading their photo
                    continue
            
            # Store result for this face
            face_result = {
                'face_coordinates': {
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h)
                },
                'confidence': best_confidence,
                'best_match': best_match
            }
            
            face_results.append(face_result)
        
        # Now select only the most confident result to avoid multiple detections
        if face_results:
            # Sort by confidence (highest first)
            face_results.sort(key=lambda x: x['confidence'], reverse=True)
            
            # Take only the best result if it meets our criteria
            best_face_result = face_results[0]
            
            # Create the final result
            final_result = {
                'face_coordinates': best_face_result['face_coordinates']
            }
            
            # If we found a good match
            if best_face_result['best_match'] and best_face_result['confidence'] > 5:
                # Ensure confidence is properly clamped before saving
                clamped_confidence = max(0.0, min(100.0, best_face_result['confidence']))
                final_result.update({
                    'criminal_id': str(best_face_result['best_match'].id),
                    'criminal_name': best_face_result['best_match'].name,
                    'confidence': round(clamped_confidence, 2),  # Already in percentage
                    'is_criminal': True
                })
            else:
                # No match found, but still detected a face
                clamped_confidence = max(0.0, min(100.0, best_face_result['confidence']))
                final_result.update({
                    'criminal_name': 'Unknown Person',
                    'confidence': round(clamped_confidence, 2) if clamped_confidence > 0 else 0,
                    'is_criminal': False
                })
            
            results.append(final_result)
        
        return results
    
    except Exception as e:
        # Return empty results if there's an error
        print(f"Error in process_image_for_detection: {e}")
        return []

def get_report_details(request, report_id):
    """Get detailed information about a detection report"""
    try:
        report = DetectionReport.objects.get(id=report_id)
        results = DetectionResult.objects.filter(report=report)
        
        detections = []
        for result in results:
            # Ensure confidence is properly clamped when retrieving from database
            confidence = float(result.confidence)
            # Clamp confidence between 0 and 100 with additional validation
            if confidence > 100.0:
                confidence = 100.0
            elif confidence < 0.0:
                confidence = 0.0
            
            detections.append({
                'id': str(result.id),  # Add the detection ID for verification
                'criminal_id': str(result.criminal.id),
                'criminal_name': result.criminal.name,
                'confidence': round(confidence, 2),  # Ensure proper formatting
                'face_coordinates': json.loads(result.face_coordinates) if result.face_coordinates else {}
            })
        
        return JsonResponse({
            'success': True,
            'report_id': str(report.id),
            'detection_time': report.detection_time.strftime('%b %d, %Y %H:%M'),
            'location': report.location,
            'detections': detections,
            'status': 'Criminal Detected' if detections else 'No Match'
        })
    except DetectionReport.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Report not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def citizen_login(request):
    """Handle citizen login"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Check if user is staff (police/admin)
            if user.is_staff:
                return redirect('police_dashboard')
            else:
                return redirect('citizen_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'detection/login.html')

@require_POST
def citizen_logout(request):
    """Handle citizen logout"""
    logout(request)
    return redirect('citizen_dashboard')

@require_POST
def police_logout(request):
    """Handle police logout"""
    logout(request)
    return redirect('police_login')

def police_login(request):
    """Handle police login - redirect to unified login"""
    return redirect('citizen_login')

def register_citizen(request):
    """Handle citizen registration"""
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'detection/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'detection/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'detection/register.html')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, 'Registration successful. Please log in.')
        return redirect('citizen_login')
    
    return render(request, 'detection/register.html')

def calculate_detection_accuracy():
    """
    Calculate the accuracy rate of the detection system based on all detections.
    
    For dynamic accuracy tracking:
    - True Positives: Detections that were later verified as correct
    - False Positives: Detections that were later verified as incorrect
    - Unverified Detections: Use confidence scores as probabilistic accuracy
    """
    try:
        # Get all detections
        all_detections = DetectionResult.objects.all()
        total_detections = all_detections.count()
        
        # If no detections, return 0% accuracy
        if total_detections == 0:
            return 0
        
        # Get verified detections
        verified_detections = all_detections.filter(is_verified=True)
        total_verified = verified_detections.count()
        
        # If no verified detections, calculate based on confidence distribution
        if total_verified == 0:
            # Calculate weighted accuracy based on confidence scores
            if total_detections > 0:
                total_weighted_confidence = 0
                total_weight = 0
                
                for detection in all_detections:
                    confidence = float(detection.confidence)
                    # Use confidence as a weight for accuracy calculation
                    # But normalize it to be more conservative
                    normalized_confidence = confidence * 0.7  # Reduce confidence to be more realistic
                    total_weighted_confidence += normalized_confidence
                    total_weight += 1
                
                if total_weight > 0:
                    avg_accuracy = total_weighted_confidence / total_weight
                    # Ensure accuracy is reasonable (not too high for unverified detections)
                    dynamic_accuracy = min(avg_accuracy, 85)  # Cap at 85% for unverified detections
                    return round(dynamic_accuracy)
            return 0
        
        # If we have verified detections, calculate based on verification results
        correct_detections = verified_detections.filter(is_correct=True).count()
        incorrect_detections = verified_detections.filter(is_correct=False).count()
        
        # Calculate accuracy as percentage
        # Accuracy = True Positives / (True Positives + False Positives)
        if (correct_detections + incorrect_detections) > 0:
            accuracy = (correct_detections / (correct_detections + incorrect_detections)) * 100
            
            # Apply dynamic adjustment based on verification volume
            # More verifications = more trust in the accuracy
            verification_ratio = total_verified / total_detections
            if verification_ratio < 0.1:  # Less than 10% verified
                # Reduce accuracy to reflect uncertainty
                accuracy *= 0.8
            elif verification_ratio < 0.3:  # 10-30% verified
                # Moderate reduction
                accuracy *= 0.9
            
            # Ensure accuracy is reasonable
            dynamic_accuracy = min(accuracy, 95)  # Cap at 95%
        else:
            dynamic_accuracy = 0
        
        # Round to nearest integer
        return round(dynamic_accuracy)
        
    except Exception as e:
        # If there's an error in calculation, return 0
        print(f"Error calculating accuracy: {e}")
        return 0

def verify_detection(request, detection_id):
    """Police can verify if a detection was correct or not"""
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    if request.method == 'POST':
        try:
            detection = DetectionResult.objects.get(id=detection_id)
            is_correct = request.POST.get('is_correct') == 'true'
            notes = request.POST.get('notes', '')
            
            # Update verification fields
            detection.is_verified = True
            detection.is_correct = is_correct
            detection.verified_by = request.user
            detection.verification_notes = notes
            detection.verified_at = timezone.now()  # Use timezone.now() instead of datetime.now()
            detection.save()
            
            # Also update the associated report to mark it as processed
            detection.report.is_processed = True
            detection.report.save(update_fields=['is_processed'])
            
            return JsonResponse({'success': True, 'message': 'Detection verified successfully'})
        except DetectionResult.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Detection not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def confirm_criminal_status(request, detection_id):
    """Police can confirm whether a detected person is actually a criminal or not"""
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Access denied'})
    
    if request.method == 'POST':
        try:
            detection = DetectionResult.objects.get(id=detection_id)
            is_criminal = request.POST.get('is_criminal') == 'true'
            notes = request.POST.get('notes', '')
            
            # Update criminal confirmation fields
            detection.is_verified = True
            detection.is_correct = is_criminal  # True if confirmed as criminal, False if not
            detection.verified_by = request.user
            detection.verification_notes = f"Criminal Status Confirmation: {notes}"
            detection.verified_at = timezone.now()
            detection.save()
            
            # Update the associated report
            detection.report.is_processed = True
            detection.report.save(update_fields=['is_processed'])
            
            # Update the criminal record if needed
            if not is_criminal:
                # If police confirm the person is NOT a criminal, we might want to flag this
                # This could be used to improve the detection algorithm
                pass
            
            status = "confirmed as criminal" if is_criminal else "confirmed as NOT a criminal"
            return JsonResponse({'success': True, 'message': f'Person {status} successfully'})
        except DetectionResult.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Detection not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def test_view(request):
    """Simple test view to check if basic functionality is working"""
    return JsonResponse({'status': 'ok', 'message': 'Test view is working'})

def bulk_upload_criminals(request):
    """Handle bulk upload of criminals via CSV file"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'User not authenticated'})
    
    if not getattr(request.user, 'is_staff', False):
        return JsonResponse({'success': False, 'error': 'User is not staff'})
    
    if request.method == 'POST' and request.FILES.get('csv_file'):
        try:
            csv_file = request.FILES['csv_file']
            
            # Check if file is CSV
            if not csv_file.name.endswith('.csv'):
                return JsonResponse({'success': False, 'error': 'Please upload a CSV file'})
            
            # Read CSV file
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            created_count = 0
            errors = []
            
            # Process each row in CSV
            for row_num, row in enumerate(reader, start=2):  # Start at 2 since header is row 1
                try:
                    # Extract required fields
                    name = row.get('name', '').strip()
                    description = row.get('description', '').strip()
                    
                    # Validate required fields
                    if not name:
                        errors.append(f"Row {row_num}: Missing name")
                        continue
                    
                    # Create criminal record
                    criminal = Criminal(
                        name=name,
                        description=description
                    )
                    criminal.save()
                    created_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            if errors:
                return JsonResponse({
                    'success': True, 
                    'message': f'Bulk upload completed with {created_count} records created. Some errors occurred.',
                    'created_count': created_count,
                    'errors': errors
                })
            else:
                return JsonResponse({
                    'success': True, 
                    'message': f'Successfully uploaded {created_count} criminals',
                    'created_count': created_count
                })
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error processing file: {str(e)}'})
    
    # For GET requests or when no file is provided, return an error indicating this endpoint is for POST only
    return JsonResponse({'success': False, 'error': 'Invalid request - use POST method with CSV file'})


# Add the necessary imports at the top of the file
