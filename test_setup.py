"""
Test script for the Criminal Detection System
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'criminal_detection_system.settings')
django.setup()

def test_django_setup():
    """Test that Django is properly configured"""
    print("Testing Django setup...")
    
    # Test that settings are loaded
    print(f"✓ Django version: {django.VERSION}")
    print(f"✓ Settings module: {settings.SETTINGS_MODULE}")
    print(f"✓ Database engine: {settings.DATABASES['default']['ENGINE']}")
    print(f"✓ Installed apps: {', '.join(settings.INSTALLED_APPS)}")
    
    # Test that models can be imported
    try:
        from detection.models import Criminal, DetectionReport, DetectionResult
        print("✓ Models imported successfully")
    except Exception as e:
        print(f"✗ Error importing models: {e}")
        return False
    
    # Test that views can be imported
    try:
        from detection.views import index, police_dashboard, upload_image
        print("✓ Views imported successfully")
    except Exception as e:
        print(f"✗ Error importing views: {e}")
        return False
    
    print("\n✓ Django setup test passed!")
    return True

if __name__ == "__main__":
    success = test_django_setup()
    sys.exit(0 if success else 1)