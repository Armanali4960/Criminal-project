import os
import sys
import django
import cv2
import numpy as np

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'criminal_detection_system.settings')
django.setup()

from django.conf import settings
from detection.models import Criminal

def debug_matching():
    print("Debugging face matching...")
    
    # Get all criminals with photos
    criminals = Criminal.objects.exclude(photo='')
    print(f"Found {criminals.count()} criminals with photos")
    
    # Load face cascade classifier
    cascade_path = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')
    face_cascade = cv2.CascadeClassifier(cascade_path)
    
    # Test with the first criminal
    if criminals.count() > 0:
        criminal = criminals.first()
        photo_path = os.path.join(settings.MEDIA_ROOT, str(criminal.photo))
        print(f"Testing with criminal: {criminal.name}")
        print(f"Photo path: {photo_path}")
        
        if os.path.exists(photo_path):
            img = cv2.imread(photo_path)
            if img is not None:
                print(f"Image loaded successfully. Shape: {img.shape}")
                
                # Convert to grayscale
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                print(f"Converted to grayscale. Shape: {gray.shape}")
                
                # Detect faces
                faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
                print(f"Detected {len(faces)} faces in criminal photo")
                
                if len(faces) > 0:
                    # Extract first face
                    (x, y, w, h) = faces[0]
                    face = gray[y:y+h, x:x+w]
                    print(f"Extracted face. Shape: {face.shape}")
                    
                    # Resize for consistency
                    face_resized = cv2.resize(face, (100, 100))
                    print(f"Resized face. Shape: {face_resized.shape}")
                    
                    # Test self-matching
                    result = cv2.matchTemplate(face_resized, face_resized, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, _ = cv2.minMaxLoc(result)
                    confidence = max_val * 100
                    print(f"Self-match confidence: {confidence:.2f}%")
                else:
                    print("No faces detected in criminal photo")
            else:
                print("Could not load image")
        else:
            print("Photo file does not exist")

if __name__ == "__main__":
    debug_matching()