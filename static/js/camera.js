// Camera JavaScript for Criminal Detection System

// Global variables
let imageData = '';
let cameraStream = null;
let currentFacingMode = 'user'; // 'user' for front camera, 'environment' for back camera

// DOM Elements
const cameraVideo = document.getElementById('cameraVideo');
const cameraCanvas = document.getElementById('cameraCanvas');
const cameraContainer = document.getElementById('cameraContainer');
const previewContainer = document.getElementById('previewContainer');
const previewImg = document.getElementById('previewImg');
const captureBtn = document.getElementById('captureBtn');
const switchCameraBtn = document.getElementById('switchCameraBtn');
const closeBtn = document.getElementById('closeBtn');
const retakeBtn = document.getElementById('retakeBtn');
const usePhotoBtn = document.getElementById('usePhotoBtn');

console.log('Camera JavaScript loaded');

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');
    initEventListeners();
    openCamera();
});

// Initialize event listeners
function initEventListeners() {
    console.log('Initializing event listeners');
    
    if (captureBtn) {
        captureBtn.addEventListener('click', function(e) {
            console.log('Capture button clicked');
            e.preventDefault();
            e.stopPropagation();
            capturePhoto();
        });
    }
    
    if (switchCameraBtn) {
        switchCameraBtn.addEventListener('click', function(e) {
            console.log('Switch camera button clicked');
            e.preventDefault();
            e.stopPropagation();
            switchCamera();
        });
    }
    
    if (closeBtn) {
        closeBtn.addEventListener('click', function(e) {
            console.log('Close button clicked');
            e.preventDefault();
            e.stopPropagation();
            closeCameraAndExit();
        });
    }
    
    if (retakeBtn) {
        retakeBtn.addEventListener('click', function(e) {
            console.log('Retake button clicked');
            e.preventDefault();
            e.stopPropagation();
            retakePhoto();
        });
    }
    
    if (usePhotoBtn) {
        usePhotoBtn.addEventListener('click', function(e) {
            console.log('Use photo button clicked');
            e.preventDefault();
            e.stopPropagation();
            usePhoto();
        });
    }
}

// Open camera with comprehensive error handling
async function openCamera() {
    console.log('Opening camera function called');
    
    // Close any existing camera first
    closeCamera();
    
    if (!cameraVideo) {
        console.error('Camera video element not found');
        alert('Camera element not found. Please refresh the page and try again.');
        return;
    }
    
    try {
        console.log('Requesting camera permissions');
        
        // Camera constraints
        const constraints = {
            video: {
                facingMode: currentFacingMode,
                width: { ideal: 1280 },
                height: { ideal: 720 }
            },
            audio: false
        };
        
        console.log('Constraints:', constraints);
        
        // Get camera stream
        console.log('Requesting user media');
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        
        console.log('Camera stream received:', stream);
        
        // Set up the video element
        cameraVideo.srcObject = stream;
        cameraStream = stream;
        
        // Play the video
        await cameraVideo.play();
        console.log('Video playing successfully');
        
        console.log('Camera opened successfully');
        
    } catch (error) {
        console.error('Camera error:', error);
        handleCameraError(error);
    }
}

// Enhanced camera error handling
function handleCameraError(error) {
    closeCamera();
    
    let errorMessage = 'Failed to access camera. ';
    
    if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
        errorMessage += 'Please allow camera access and try again.';
    } else if (error.name === 'NotFoundError' || error.name === 'OverconstrainedError') {
        errorMessage += 'No camera found. Please check if a camera is connected.';
    } else if (error.name === 'NotReadableError') {
        errorMessage += 'Camera is being used by another application.';
    } else if (error.name === 'AbortError') {
        errorMessage += 'Camera access was aborted. Please try again.';
    } else {
        errorMessage += 'Please check your camera settings and try again.';
    }
    
    showCameraError(errorMessage);
}

// Show camera error message
function showCameraError(message) {
    const errorElement = document.getElementById('cameraErrorMessage');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.remove('d-none');
        
        // Auto-hide error after 5 seconds
        setTimeout(() => {
            errorElement.classList.add('d-none');
        }, 5000);
    }
    
    console.error('Camera Error:', message);
}

// Capture photo with comprehensive debugging
function capturePhoto() {
    console.log('Capture photo function called');
    
    if (!cameraVideo || !cameraCanvas) {
        console.log('Required elements not found');
        showCameraError('Camera not ready. Please try again.');
        return;
    }
    
    if (!cameraVideo.srcObject) {
        console.log('No camera stream available');
        showCameraError('Camera stream not available. Please check camera permissions.');
        return;
    }
    
    // Check if video is actually playing
    if (cameraVideo.paused || cameraVideo.ended) {
        console.log('Video is not playing');
        showCameraError('Camera not ready. Please wait a moment and try again.');
        return;
    }
    
    try {
        console.log('Video dimensions:', cameraVideo.videoWidth, 'x', cameraVideo.videoHeight);
        
        // Ensure we have valid dimensions
        if (cameraVideo.videoWidth === 0 || cameraVideo.videoHeight === 0) {
            console.log('Video dimensions not ready');
            showCameraError('Camera not ready. Please wait a moment and try again.');
            return;
        }
        
        // Set canvas dimensions to match video
        cameraCanvas.width = cameraVideo.videoWidth;
        cameraCanvas.height = cameraVideo.videoHeight;
        
        // Get canvas context
        const context = cameraCanvas.getContext('2d');
        if (!context) {
            console.log('Could not get canvas context');
            showCameraError('Failed to capture photo. Please try again.');
            return;
        }
        
        // Draw video frame to canvas
        context.drawImage(cameraVideo, 0, 0, cameraCanvas.width, cameraCanvas.height);
        
        // Convert to data URL
        imageData = cameraCanvas.toDataURL('image/jpeg', 0.8);
        console.log('Image captured successfully, data length:', imageData.length);
        
        // Display in preview
        if (previewImg) {
            previewImg.src = imageData;
        }
        
        // Show preview container and hide camera container
        if (cameraContainer) {
            cameraContainer.style.display = 'none';
        }
        
        if (previewContainer) {
            previewContainer.style.display = 'block';
        }
        
        console.log('Capture process completed successfully');
        
    } catch (error) {
        console.error('Capture error:', error);
        showCameraError('Failed to capture photo. Please try again.');
    }
}

// Switch camera with improved handling
async function switchCamera() {
    console.log('Switching camera...');
    
    // Stop current stream
    closeCamera();
    
    // Toggle facing mode
    currentFacingMode = currentFacingMode === 'user' ? 'environment' : 'user';
    
    // Reopen camera with new facing mode
    await openCamera();
}

// Retake photo
function retakePhoto() {
    // Hide preview container and show camera container
    if (previewContainer) {
        previewContainer.style.display = 'none';
    }
    
    if (cameraContainer) {
        cameraContainer.style.display = 'block';
    }
    
    // Clear preview image
    if (previewImg) {
        previewImg.src = '';
    }
    
    imageData = '';
}

// Use photo - send to detection page
function usePhoto() {
    if (!imageData) {
        alert('No image captured. Please capture a photo first.');
        return;
    }
    
    // Store image data in sessionStorage
    sessionStorage.setItem('capturedImageData', imageData);
    
    // Store location data if available
    const locationInput = document.getElementById('cameraLocation');
    if (locationInput && locationInput.value.trim() !== '') {
        sessionStorage.setItem('capturedLocation', locationInput.value.trim());
    }
    
    // Redirect to citizen dashboard
    window.location.href = '/';
}

// Close camera and exit
function closeCameraAndExit() {
    closeCamera();
    // Redirect to citizen dashboard
    window.location.href = '/';
}

// Enhanced close camera function
function closeCamera() {
    console.log('Closing camera function called');
    
    // Stop all tracks in the stream
    if (cameraStream) {
        console.log('Stopping camera tracks');
        const tracks = cameraStream.getTracks();
        tracks.forEach(track => {
            console.log('Stopping track:', track.kind);
            track.stop();
        });
        cameraStream = null;
    }
    
    // Clear video source
    if (cameraVideo) {
        console.log('Clearing video source');
        cameraVideo.srcObject = null;
        cameraVideo.pause();
    }
    
    console.log('Camera closed successfully');
}

// Close camera when window is closed
window.addEventListener('beforeunload', function() {
    closeCamera();
});