#!/usr/bin/env python
"""
Test script to verify that the Django application can start correctly
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

def test_django_setup():
    """Test that Django can be configured correctly"""
    try:
        # Configure Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'criminal_detection_system.settings')
        django.setup()
        
        # Test importing models
        from detection.models import Criminal, DetectionReport, DetectionResult
        print("✓ Django models imported successfully")
        
        # Test database connection
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        if result:
            print("✓ Database connection successful")
        else:
            print("✗ Database connection failed")
            
        # Test if tables exist
        try:
            criminal_count = Criminal.objects.count()
            print(f"✓ Criminal table exists with {criminal_count} records")
        except Exception as e:
            print(f"⚠ Criminal table may not exist yet: {e}")
            
        return True
        
    except Exception as e:
        print(f"✗ Django setup failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Django application setup...")
    print("=" * 40)
    
    success = test_django_setup()
    
    print("=" * 40)
    if success:
        print("Django application setup test completed successfully!")
        sys.exit(0)
    else:
        print("Django application setup test failed.")
        sys.exit(1)