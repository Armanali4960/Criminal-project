import cv2
import os
import numpy as np

# Test if face detection is working
def test_face_detection():
    # Load the cascade
    cascade_path = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')
    face_cascade = cv2.CascadeClassifier(cascade_path)
    
    # Create a more realistic test image with face-like features
    test_img = np.zeros((300, 300, 3), dtype=np.uint8)
    
    # Draw a face-like pattern
    # Face outline
    cv2.circle(test_img, (150, 150), 80, (255, 255, 255), -1)
    
    # Eyes
    cv2.circle(test_img, (120, 130), 15, (0, 0, 0), -1)
    cv2.circle(test_img, (180, 130), 15, (0, 0, 0), -1)
    
    # Mouth
    cv2.ellipse(test_img, (150, 180), (30, 15), 0, 0, 180, (0, 0, 0), -1)
    
    # Convert to grayscale
    gray = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
    
    print(f"Detected {len(faces)} faces")
    
    # Save test image for debugging
    cv2.imwrite('test_face.png', test_img)
    print("Test image saved as 'test_face.png'")
    
    return len(faces) > 0

# Test with a real image if available
def test_with_real_image():
    # Try to load an existing image
    image_files = [f for f in os.listdir('.') if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if image_files:
        img_path = image_files[0]
        print(f"Testing with real image: {img_path}")
        img = cv2.imread(img_path)
        if img is not None:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            cascade_path = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')
            face_cascade = cv2.CascadeClassifier(cascade_path)
            faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
            print(f"Detected {len(faces)} faces in {img_path}")
            return len(faces) > 0
    return False

if __name__ == "__main__":
    print("Testing face detection...")
    success1 = test_face_detection()
    success2 = test_with_real_image()
    print(f"Face detection test: {'PASSED' if success1 or success2 else 'FAILED'}")