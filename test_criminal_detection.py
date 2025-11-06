import os
import django
from django.conf import settings

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'criminal_detection_system.settings')
django.setup()

from detection.models import Criminal, DetectionReport
from detection.views import process_image_for_detection
import uuid
from datetime import datetime
import cv2
import numpy as np

def test_criminal_detection():
    """Test the criminal detection functionality"""
    print("Testing criminal detection functionality...")
    
    # Check if we have criminals with photos
    criminals_with_photos = Criminal.objects.exclude(photo='').count()
    print(f"Number of criminals with photos: {criminals_with_photos}")
    
    if criminals_with_photos == 0:
        print("No criminals with photos found. Please run populate_criminals command first.")
        return False
    
    # List all criminals
    criminals = Criminal.objects.exclude(photo='')
    print("All criminals in database:")
    for criminal in criminals:
        print(f"  - {criminal.name} ({criminal.photo})")
    
    # Test with one of the test images
    test_image_path = 'test_face.png'
    if os.path.exists(test_image_path):
        print(f"\nTesting with image: {test_image_path}")
        
        # Create a detection report
        report = DetectionReport(
            detection_time=datetime.now(),
            location="Test Location"
        )
        report.save()
        
        # Save the test image to the report
        with open(test_image_path, 'rb') as f:
            report.photo.save(f'test_{uuid.uuid4()}.png', f, save=True)
        
        print(f"Created detection report: {report.id}")
        
        # Process the image for detection
        print("Processing image for detection...")
        results = process_image_for_detection(report)
        
        print(f"Detection results: {len(results)} faces detected")
        for i, result in enumerate(results):
            print(f"  Face {i+1}:")
            print(f"    Coordinates: {result.get('face_coordinates', 'N/A')}")
            if result.get('is_criminal', False):
                print(f"    Criminal detected: {result.get('criminal_name', 'Unknown')}")
                print(f"    Confidence: {result.get('confidence', 0)}%")
            else:
                print(f"    No criminal match found")
                print(f"    Confidence: {result.get('confidence', 0)}%")
        
        return len(results) > 0
    else:
        print(f"Test image not found: {test_image_path}")
        return False

if __name__ == "__main__":
    test_criminal_detection()