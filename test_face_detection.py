import cv2
import numpy as np
import os

def test_face_detection_with_real_image():
    """Test face detection with a real image"""
    try:
        # Check if we have the test images
        test_images = ['test_face.png', 'test_face1.png', 'test_face2.png']
        
        for test_image in test_images:
            if os.path.exists(test_image):
                print(f"Testing with image: {test_image}")
                
                # Load the image
                img = cv2.imread(test_image)
                if img is None:
                    print(f"Could not load image: {test_image}")
                    continue
                    
                print(f"Image loaded successfully. Size: {img.shape}")
                
                # Try to detect faces
                try:
                    # Load face cascade classifier
                    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                    face_cascade = cv2.CascadeClassifier(cascade_path)
                    
                    # Convert to grayscale
                    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    
                    # Detect faces
                    faces = face_cascade.detectMultiScale(
                        gray_img, 
                        scaleFactor=1.1,
                        minNeighbors=5, 
                        minSize=(30, 30)
                    )
                    
                    print(f"Detected {len(faces)} faces in {test_image}")
                    for (x, y, w, h) in faces:
                        print(f"Face at position: x={x}, y={y}, width={w}, height={h}")
                        # Draw rectangle around face
                        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    
                    # Save result image
                    result_image_path = f'result_{test_image}'
                    cv2.imwrite(result_image_path, img)
                    print(f"Result image saved to: {result_image_path}")
                    
                    if len(faces) > 0:
                        return True
                        
                except Exception as e:
                    print(f"Error in face detection for {test_image}: {e}")
                    continue
            else:
                print(f"Image not found: {test_image}")
        
        return False
    except Exception as e:
        print(f"Error in test_face_detection_with_real_image: {e}")
        return False

def test_face_detection():
    """Test face detection functionality"""
    try:
        # Create a simple test image with a face-like pattern
        img = np.ones((300, 300, 3), dtype=np.uint8) * 255  # White background
        
        # Draw a face-like pattern
        # Face outline
        cv2.circle(img, (150, 150), 100, (0, 0, 0), 2)
        
        # Eyes
        cv2.circle(img, (110, 120), 20, (0, 0, 0), -1)
        cv2.circle(img, (190, 120), 20, (0, 0, 0), -1)
        
        # Nose
        cv2.circle(img, (150, 160), 15, (0, 0, 0), -1)
        
        # Mouth
        cv2.ellipse(img, (150, 200), (40, 20), 0, 0, 180, (0, 0, 0), 2)
        
        # Save test image
        test_image_path = 'test_face_detection.jpg'
        cv2.imwrite(test_image_path, img)
        print(f"Test image saved to: {test_image_path}")
        
        # Try to detect faces
        try:
            # Load face cascade classifier
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(cascade_path)
            
            # Convert to grayscale
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray_img, 
                scaleFactor=1.1,
                minNeighbors=5, 
                minSize=(30, 30)
            )
            
            print(f"Detected {len(faces)} faces in generated image")
            for (x, y, w, h) in faces:
                print(f"Face at position: x={x}, y={y}, width={w}, height={h}")
                
            return len(faces) > 0
        except Exception as e:
            print(f"Error in face detection: {e}")
            return False
            
    except Exception as e:
        print(f"Error in test_face_detection: {e}")
        return False

if __name__ == "__main__":
    print("Testing face detection with real images...")
    result1 = test_face_detection_with_real_image()
    
    print("\nTesting face detection with generated image...")
    result2 = test_face_detection()
    
    if result1 or result2:
        print("\nFace detection is working!")
    else:
        print("\nFace detection is not working properly.")