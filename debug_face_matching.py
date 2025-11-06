import os
import django
from django.conf import settings

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'criminal_detection_system.settings')
django.setup()

from detection.models import Criminal
import cv2
import numpy as np

def debug_face_matching():
    """Debug the face matching process"""
    print("Debugging face matching process...")
    
    # Load the test image
    test_image_path = 'test_face.png'
    if not os.path.exists(test_image_path):
        print(f"Test image not found: {test_image_path}")
        return
    
    # Load the image
    img = cv2.imread(test_image_path)
    if img is None:
        print(f"Could not load image: {test_image_path}")
        return
    
    print(f"Test image loaded. Size: {img.shape}")
    
    # Convert to grayscale
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply histogram equalization to improve contrast
    gray_img = cv2.equalizeHist(gray_img)
    
    # Apply Gaussian blur to reduce noise
    gray_img = cv2.GaussianBlur(gray_img, (3, 3), 0)
    
    # Load face cascade classifier
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray_img, 
        scaleFactor=1.05,
        minNeighbors=5, 
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    print(f"Detected {len(faces)} faces in test image")
    
    if len(faces) == 0:
        print("No faces detected in test image")
        return
    
    # Process the first detected face
    (x, y, w, h) = faces[0]
    face_img = gray_img[y:y+h, x:x+w]
    
    # Apply sharpening
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    face_img = cv2.filter2D(face_img, -1, kernel)
    
    # Resize face for consistency
    face_img = cv2.resize(face_img, (100, 100))
    
    print(f"Processed test face. Size: {face_img.shape}")
    
    # Now compare with each criminal
    criminals = Criminal.objects.exclude(photo='')
    print(f"Comparing with {criminals.count()} criminals...")
    
    for i, criminal in enumerate(criminals):
        try:
            # Load criminal's photo
            criminal_image_path = os.path.join(settings.MEDIA_ROOT, str(criminal.photo))
            print(f"Checking criminal {i+1}: {criminal.name} - {criminal_image_path}")
            
            if os.path.exists(criminal_image_path):
                criminal_img = cv2.imread(criminal_image_path)
                if criminal_img is not None:
                    print(f"  Criminal image loaded. Size: {criminal_img.shape}")
                    
                    # Convert to grayscale
                    criminal_gray = cv2.cvtColor(criminal_img, cv2.COLOR_BGR2GRAY)
                    
                    # Apply the same preprocessing
                    criminal_gray = cv2.equalizeHist(criminal_gray)
                    criminal_gray = cv2.GaussianBlur(criminal_gray, (3, 3), 0)
                    
                    # Detect face in criminal's photo
                    criminal_faces = face_cascade.detectMultiScale(
                        criminal_gray,
                        scaleFactor=1.05,
                        minNeighbors=5,
                        minSize=(30, 30),
                        flags=cv2.CASCADE_SCALE_IMAGE
                    )
                    
                    print(f"  Detected {len(criminal_faces)} faces in criminal image")
                    
                    if len(criminal_faces) > 0:
                        # Extract first face
                        (cx, cy, cw, ch) = criminal_faces[0]
                        criminal_face = criminal_gray[cy:cy+ch, cx:cx+cw]
                        
                        print(f"  Criminal face extracted. Size: {criminal_face.shape}")
                        
                        # Apply sharpening
                        criminal_face = cv2.filter2D(criminal_face, -1, kernel)
                        
                        # Resize for consistency
                        criminal_face = cv2.resize(criminal_face, (100, 100))
                        
                        print(f"  Criminal face processed. Size: {criminal_face.shape}")
                        
                        # Calculate similarity using normalized cross correlation
                        result = cv2.matchTemplate(face_img, criminal_face, cv2.TM_CCOEFF_NORMED)
                        _, max_val, _, _ = cv2.minMaxLoc(result)
                        
                        confidence = max_val * 100
                        print(f"  Confidence for {criminal.name}: {confidence:.2f}%")
                    else:
                        print(f"  No faces detected in criminal image")
                else:
                    print(f"  Could not load criminal image")
            else:
                print(f"  Criminal image file not found: {criminal_image_path}")
        except Exception as e:
            print(f"  Error processing {criminal.name}: {e}")
            continue

if __name__ == "__main__":
    debug_face_matching()