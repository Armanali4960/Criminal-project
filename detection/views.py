import os
import cv2
import numpy as np
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Criminal, DetectionReport, DetectionResult

def index(request):
    """Citizen dashboard - upload image for criminal detection"""
    # If user is authenticated and is staff, redirect to police dashboard
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('police_dashboard')
    return render(request, 'detection/citizen_dashboard.html')

def camera_page(request):
    """Camera page - capture image directly from camera"""
    # If user is authenticated and is staff, redirect to police dashboard
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('police_dashboard')
    return render(request, 'detection/camera.html')

def police_dashboard(request):
    """Police dashboard - view detection reports"""
    # If user is not authenticated, redirect to police login
    if not request.user.is_authenticated:
        return redirect('police_login')
    
    # If user is not staff, redirect to police login
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Police access only.')
        return redirect('police_login')
    
    # Check if this is an AJAX request for data
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Get all detection reports
        reports = DetectionReport.objects.all().order_by('-created_at')[:10]  # Limit to 10 most recent
        
        # Serialize the data
        reports_data = []
        for report in reports:
            # Get detection results for this report
            results = DetectionResult.objects.filter(report=report)
            detections = []
            for result in results:
                detections.append({
                    'criminal_name': result.criminal.name,
                    'confidence': float(result.confidence),
                })
            
            reports_data.append({
                'id': str(report.id),
                'detection_time': report.detection_time.strftime('%b %d, %Y %H:%M'),
                'location': report.location if report.location else '',
                'status': 'Criminal Detected' if detections else 'No Match',
                'has_detections': len(detections) > 0,
            })
        
        # Get statistics
        total_reports = DetectionReport.objects.count()
        criminals_detected = DetectionResult.objects.count()
        pending_review = DetectionReport.objects.filter(is_processed=False).count()
        
        # Calculate accuracy rate (simplified)
        accuracy_rate = 92  # This would be calculated based on actual data in a real system
        
        return JsonResponse({
            'reports': reports_data,
            'stats': {
                'total_reports': total_reports,
                'criminals_detected': criminals_detected,
                'pending_review': pending_review,
                'accuracy_rate': accuracy_rate
            }
        })
    
    # Get all detection reports for initial page load
    reports = DetectionReport.objects.all().order_by('-created_at')
    return render(request, 'detection/police_dashboard.html', {'reports': reports})

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
                # Only save results that have a criminal match
                if result.get('is_criminal', False) and 'criminal_id' in result:
                    detection_result = DetectionResult(
                        report=report,
                        criminal_id=result['criminal_id'],
                        confidence=result['confidence'],
                        face_coordinates=result['face_coordinates']
                    )
                    detection_result.save()
            
            # Update report as processed
            report.is_processed = True
            report.save(update_fields=['is_processed'])
            
            # Count total faces and criminals detected
            total_faces = len(detection_results)
            criminals_found = [result for result in detection_results if result.get('is_criminal', False)]
            
            return JsonResponse({
                'success': True,
                'report_id': str(report.id),
                'message': 'Image processed successfully',
                'detections': detection_results,
                'total_faces_detected': total_faces,
                'total_criminals_found': len(criminals_found),
                'criminals_list': [{'name': c['criminal_name'], 'confidence': c['confidence']} for c in criminals_found]
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

def process_image_for_detection(report):
    """Process image and detect faces with improved matching"""
    try:
        # Get the image path
        image_path = report.photo.path
        
        # Load the image
        img = cv2.imread(image_path)
        if img is None:
            return []
        
        # Convert to grayscale
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply histogram equalization to improve contrast
        gray_img = cv2.equalizeHist(gray_img)
        
        # Apply Gaussian blur to reduce noise
        gray_img = cv2.GaussianBlur(gray_img, (3, 3), 0)
        
        # Load face cascade classifier
        # Use the standard path for Haar cascades
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        except AttributeError:
            # Fallback path if cv2.data is not available
            cascade_path = 'cv2/data/haarcascade_frontalface_default.xml'
        
        face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Detect faces with improved parameters
        faces = face_cascade.detectMultiScale(
            gray_img, 
            scaleFactor=1.05,  # Reduced for better accuracy
            minNeighbors=5, 
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        results = []
        
        # If no faces detected, return empty results
        if len(faces) == 0:
            return results
        
        # Get all criminals with photos
        criminals = Criminal.objects.exclude(photo='')
        
        # For each detected face, compare with criminal database
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
            
            # Compare with each criminal
            for criminal in criminals:
                try:
                    # Load criminal's photo
                    criminal_image_path = os.path.join(settings.MEDIA_ROOT, str(criminal.photo))
                    if os.path.exists(criminal_image_path):
                        criminal_img = cv2.imread(criminal_image_path)
                        if criminal_img is not None:
                            # Convert to grayscale
                            criminal_gray = cv2.cvtColor(criminal_img, cv2.COLOR_BGR2GRAY)
                            
                            # Apply the same preprocessing
                            criminal_gray = cv2.equalizeHist(criminal_gray)
                            criminal_gray = cv2.GaussianBlur(criminal_gray, (3, 3), 0)
                            
                            # Detect face in criminal's photo
                            criminal_faces = face_cascade.detectMultiScale(
                                criminal_gray,
                                scaleFactor=1.05,  # Reduced for better accuracy
                                minNeighbors=5,
                                minSize=(30, 30),
                                flags=cv2.CASCADE_SCALE_IMAGE
                            )
                            
                            if len(criminal_faces) > 0:
                                # Extract first face
                                (cx, cy, cw, ch) = criminal_faces[0]
                                criminal_face = criminal_gray[cy:cy+ch, cx:cx+cw]
                                
                                # Apply sharpening
                                criminal_face = cv2.filter2D(criminal_face, -1, kernel)
                                
                                # Resize for consistency
                                criminal_face = cv2.resize(criminal_face, (100, 100))
                                
                                # Calculate similarity using normalized cross correlation
                                # This method is more robust than template matching
                                result = cv2.matchTemplate(face_img, criminal_face, cv2.TM_CCOEFF_NORMED)
                                _, max_val, _, _ = cv2.minMaxLoc(result)
                                
                                # Convert to percentage (0-100)
                                confidence = max_val * 100
                                
                                # If this is a better match and above threshold
                                if confidence > best_confidence and confidence > 25:  # Adjusted threshold for better accuracy
                                    best_confidence = confidence
                                    best_match = criminal
                except Exception as e:
                    # Skip this criminal if there's an error loading their photo
                    continue
            
            # Create result for this face
            face_result = {
                'face_coordinates': {
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h)
                }
            }
            
            # If we found a match
            if best_match and best_confidence > 25:  # Adjusted threshold for better accuracy
                face_result.update({
                    'criminal_id': str(best_match.id),
                    'criminal_name': best_match.name,
                    'confidence': round(best_confidence, 2),  # Already in percentage
                    'is_criminal': True
                })
            else:
                # No match found, but still detected a face
                face_result.update({
                    'criminal_name': 'Unknown Person',
                    'confidence': round(best_confidence, 2) if best_confidence > 0 else 0,
                    'is_criminal': False
                })
            
            results.append(face_result)
        
        return results
    
    except Exception as e:
        # Return empty results if there's an error
        return []

def get_report_details(request, report_id):
    """Get detailed information about a detection report"""
    try:
        report = DetectionReport.objects.get(id=report_id)
        results = DetectionResult.objects.filter(report=report)
        
        detections = []
        for result in results:
            detections.append({
                'criminal_name': result.criminal.name,
                'confidence': float(result.confidence),
                'face_coordinates': result.face_coordinates
            })
        
        return JsonResponse({
            'success': True,
            'report_id': str(report.id),
            'detection_time': report.detection_time.strftime('%b %d, %Y %H:%M'),
            'location': report.location if report.location else '',
            'detections': detections
        })
    except DetectionReport.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Report not found'
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
                messages.error(request, 'Access denied. Please use police login.')
                logout(request)
                return redirect('citizen_login')
            else:
                return redirect('citizen_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'detection/login.html')

def citizen_logout(request):
    """Handle citizen logout"""
    logout(request)
    return redirect('citizen_dashboard')

def police_logout(request):
    """Handle police logout"""
    logout(request)
    return redirect('police_login')

def police_login(request):
    """Handle police login"""
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
                messages.error(request, 'Access denied. Police access only.')
                logout(request)
                return redirect('police_login')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'detection/police_login.html')

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
