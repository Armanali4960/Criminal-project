#!/usr/bin/env python
"""
Test script to verify that all dependencies can be imported correctly
"""
import sys

def test_imports():
    """Test that all required packages can be imported"""
    packages = [
        'django',
        'cv2',
        'numpy',
        'PIL',
        'gunicorn',
        'whitenoise',
        'dj_database_url',
        'psycopg2'
    ]
    
    failed_imports = []
    
    for package in packages:
        try:
            if package == 'cv2':
                import cv2
                print(f"✓ Successfully imported {package} (version: {cv2.__version__})")
            elif package == 'numpy':
                import numpy
                print(f"✓ Successfully imported {package} (version: {numpy.__version__})")
            elif package == 'PIL':
                from PIL import Image
                print(f"✓ Successfully imported {package}")
            else:
                __import__(package)
                print(f"✓ Successfully imported {package}")
        except ImportError as e:
            print(f"✗ Failed to import {package}: {e}")
            failed_imports.append(package)
    
    return len(failed_imports) == 0

if __name__ == "__main__":
    print("Testing Render setup dependencies...")
    print("=" * 40)
    
    success = test_imports()
    
    print("=" * 40)
    if success:
        print("All dependencies imported successfully!")
        sys.exit(0)
    else:
        print("Some dependencies failed to import.")
        sys.exit(1)