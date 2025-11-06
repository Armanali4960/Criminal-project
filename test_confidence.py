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

# Test confidence scores between criminal photos
def test_confidence_scores():
    # Get all criminals with photos
    criminals = Criminal.objects.exclude(photo='')
    print(f"Found {criminals.count()} criminals with photos")
    
    if criminals.count() < 2:
        print("Not enough criminals for comparison")
        return
    
    # Get the first two criminals
    criminal_list = list(criminals)
    criminal1 = criminal_list[0]
    criminal2 = criminal_list[1]
    
    # Load their photos
    photo1_path = os.path.join(settings.MEDIA_ROOT, str(criminal1.photo))
    photo2_path = os.path.join(settings.MEDIA_ROOT, str(criminal2.photo))
    
    print(f"Comparing {criminal1.name} with {criminal2.name}")
    print(f"Photo 1: {photo1_path}")
    print(f"Photo 2: {photo2_path}")
    
    if not os.path.exists(photo1_path) or not os.path.exists(photo2_path):
        print("One or both photos don't exist")
        return
    
    img1 = cv2.imread(photo1_path)
    img2 = cv2.imread(photo2_path)
    
    if img1 is None or img2 is None:
        print("Could not load one or both images")
        return
    
    # Convert to grayscale
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # Resize for consistency
    gray1 = cv2.resize(gray1, (100, 100))
    gray2 = cv2.resize(gray2, (100, 100))
    
    # Test matching
    result = cv2.matchTemplate(gray1, gray2, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    
    confidence = max_val * 100
    print(f"Match confidence: {confidence:.2f}%")
    
    # Also test each image against itself
    result_self = cv2.matchTemplate(gray1, gray1, cv2.TM_CCOEFF_NORMED)
    _, max_val_self, _, _ = cv2.minMaxLoc(result_self)
    confidence_self = max_val_self * 100
    print(f"Self-match confidence: {confidence_self:.2f}%")

if __name__ == "__main__":
    print("Testing confidence scores...")
    test_confidence_scores()