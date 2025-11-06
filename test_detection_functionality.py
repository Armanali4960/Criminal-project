import os
import django
from django.conf import settings

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'criminal_detection_system.settings')
django.setup()

from detection.models import Criminal, DetectionReport, DetectionResult
from detection.views import process_image_for_detection
from django.core.files.uploadedfile import SimpleUploadedFile
import uuid
from datetime import datetime

def test_detection_functionality():
    """Test the detection functionality"""
    print("Testing detection functionality...")
    
    # Check if we have criminals with photos
    criminals_with_photos = Criminal.objects.exclude(photo='').count()
    print(f"Number of criminals with photos: {criminals_with_photos}")
    
    if criminals_with_photos == 0:
        print("No criminals with photos found. Please run populate_criminals command first.")
        return False
    
    # List some criminals
    criminals = Criminal.objects.exclude(photo='')[:3]
    print("Sample criminals:")
    for criminal in criminals:
        print(f"  - {criminal.name} ({criminal.photo})")
    
    print("\nDetection functionality test completed.")
    return True

if __name__ == "__main__":
    test_detection_functionality()