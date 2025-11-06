import cv2
import os
import numpy as np
from django.conf import settings

# Test face matching
def test_face_matching():
    # Create two similar face images
    face1 = np.zeros((100, 100, 3), dtype=np.uint8)
    face1[:, :] = [100, 150, 200]  # Blue tint
    cv2.circle(face1, (50, 50), 30, (255, 255, 255), -1)  # Face
    cv2.circle(face1, (35, 40), 8, (0, 0, 0), -1)  # Left eye
    cv2.circle(face1, (65, 40), 8, (0, 0, 0), -1)  # Right eye
    cv2.ellipse(face1, (50, 65), (15, 8), 0, 0, 180, (0, 0, 0), -1)  # Mouth
    
    # Create a slightly different face
    face2 = np.zeros((100, 100, 3), dtype=np.uint8)
    face2[:, :] = [100, 150, 200]  # Same blue tint
    cv2.circle(face2, (50, 50), 30, (255, 255, 255), -1)  # Face
    cv2.circle(face2, (35, 40), 8, (0, 0, 0), -1)  # Left eye
    cv2.circle(face2, (65, 40), 8, (0, 0, 0), -1)  # Right eye
    cv2.ellipse(face2, (50, 65), (15, 8), 0, 0, 180, (0, 0, 0), -1)  # Mouth
    
    # Convert to grayscale
    gray1 = cv2.cvtColor(face1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(face2, cv2.COLOR_BGR2GRAY)
    
    # Test matching
    result = cv2.matchTemplate(gray1, gray2, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    
    confidence = max_val * 100
    print(f"Match confidence: {confidence:.2f}%")
    
    # Save test images
    cv2.imwrite('test_face1.png', face1)
    cv2.imwrite('test_face2.png', face2)
    
    return confidence

if __name__ == "__main__":
    print("Testing face matching...")
    confidence = test_face_matching()
    print(f"Face matching test: {'PASSED' if confidence > 50 else 'FAILED'}")