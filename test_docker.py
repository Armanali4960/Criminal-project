#!/usr/bin/env python
"""
Test script to verify Dockerfile configuration
"""
import os
import sys

def test_dockerfile():
    """Test that Dockerfile exists and has correct configuration"""
    dockerfile_path = 'Dockerfile'
    
    if not os.path.exists(dockerfile_path):
        print(f"✗ Dockerfile not found at {dockerfile_path}")
        return False
        
    try:
        with open(dockerfile_path, 'r') as f:
            content = f.read()
            
        # Check for required elements
        required_elements = [
            'FROM python:3.10.15-slim',
            'WORKDIR /app',
            'COPY requirements.txt /app/requirements.txt',
            'pip install setuptools==69.5.1 wheel==0.43.0',
            'COPY . /app/',
            'EXPOSE $PORT'
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in content:
                missing_elements.append(element)
                
        if missing_elements:
            print("✗ Missing required elements in Dockerfile:")
            for element in missing_elements:
                print(f"  - {element}")
            return False
        else:
            print("✓ Dockerfile has all required elements")
            return True
            
    except Exception as e:
        print(f"✗ Error reading Dockerfile: {e}")
        return False

def test_requirements():
    """Test that requirements.txt has correct dependencies"""
    requirements_path = 'requirements.txt'
    
    if not os.path.exists(requirements_path):
        print(f"✗ requirements.txt not found at {requirements_path}")
        return False
        
    try:
        with open(requirements_path, 'r') as f:
            content = f.read()
            
        # Check for required dependencies
        required_deps = [
            'Django==5.1',
            'opencv-python==4.8.0.74',
            'numpy==1.24.3',
            'setuptools==69.5.1',
            'wheel==0.43.0'
        ]
        
        missing_deps = []
        for dep in required_deps:
            if dep not in content:
                missing_deps.append(dep)
                
        if missing_deps:
            print("✗ Missing required dependencies in requirements.txt:")
            for dep in missing_deps:
                print(f"  - {dep}")
            return False
        else:
            print("✓ requirements.txt has all required dependencies")
            return True
            
    except Exception as e:
        print(f"✗ Error reading requirements.txt: {e}")
        return False

if __name__ == "__main__":
    print("Testing Docker configuration...")
    print("=" * 40)
    
    docker_success = test_dockerfile()
    requirements_success = test_requirements()
    
    print("=" * 40)
    if docker_success and requirements_success:
        print("All Docker configuration tests passed!")
        sys.exit(0)
    else:
        print("Docker configuration tests failed.")
        sys.exit(1)