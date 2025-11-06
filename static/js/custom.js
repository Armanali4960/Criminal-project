// Custom JavaScript for Criminal Detection System

// Global variables
let imageData = '';
let currentReportId = null;
let cameraStream = null;
let currentFacingMode = 'user'; // 'user' for front camera, 'environment' for back camera
let autoRefreshInterval = null;
let isAutoRefreshActive = false;
let isCameraActive = false;
let cameraRetryCount = 0;
const MAX_CAMERA_RETRIES = 3;

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const photoInput = document.getElementById('photoInput');
const previewImg = document.getElementById('previewImg');
const imagePreview = document.getElementById('imagePreview');
const detectionForm = document.getElementById('detectionForm');
const processingIndicator = document.getElementById('processingIndicator');
const resultsSection = document.getElementById('resultsSection');
const resultsContent = document.getElementById('resultsContent');
const submitBtn = document.getElementById('submitBtn');
const retakeButton = document.getElementById('retakeButton');
const refreshBtn = document.getElementById('refreshBtn');
const autoRefreshBtn = document.getElementById('autoRefreshBtn');
const cameraVideo = document.getElementById('cameraVideo');
const cameraCanvas = document.getElementById('cameraCanvas');
const cameraModal = document.getElementById('cameraModal');
const cameraButton = document.getElementById('cameraButton');
const captureBtn = document.getElementById('captureBtn');
const switchCameraBtn = document.getElementById('switchCameraBtn');

console.log('JavaScript loaded');
console.log('Camera button:', cameraButton);

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed');
    console.log('Camera button in DOMContentLoaded:', cameraButton);
    initEventListeners();
    initRealTimeFeatures();
    initTooltips();
    
    // Check if there's captured image data in sessionStorage
    checkForCapturedImage();
    
    // Add animation to cards
    animateCards();
});

// Add animation to cards
function animateCards() {
    const cards = document.querySelectorAll('.dashboard-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 * index);
    });
}

// Check for captured image data in sessionStorage
function checkForCapturedImage() {
    const capturedImageData = sessionStorage.getItem('capturedImageData');
    if (capturedImageData) {
        // Clear the sessionStorage
        sessionStorage.removeItem('capturedImageData');
        
        // Set the image data
        imageData = capturedImageData;
        
        // Show image preview
        showImagePreview(imageData);
        
        // Enable submit button
        if (submitBtn) {
            submitBtn.disabled = false;
        }
        
        // Show success message
        showNotification('Photo captured successfully!', 'success');
    }
}

// Show notification
function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
    notification.style.zIndex = '9999';
    notification.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'} me-2"></i>
            ${message}
        </div>
    `;
    
    // Add to body
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Initialize event listeners
function initEventListeners() {
    console.log('Initializing event listeners');
    
    // File upload functionality
    if (uploadArea) {
        console.log('Upload area found');
        uploadArea.addEventListener('click', function() {
            console.log('Upload area clicked');
            if (photoInput) {
                photoInput.click();
            }
        });
        
        // Add drag and drop functionality
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('active');
        });
        
        uploadArea.addEventListener('dragleave', function() {
            uploadArea.classList.remove('active');
        });
        
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('active');
            
            if (e.dataTransfer.files.length) {
                photoInput.files = e.dataTransfer.files;
                const event = new Event('change', { bubbles: true });
                photoInput.dispatchEvent(event);
            }
        });
    }
    
    if (photoInput) {
        photoInput.addEventListener('change', handleImageUpload);
    }
    
    // Retake button
    if (retakeButton) {
        retakeButton.addEventListener('click', retakePhoto);
    }
    
    // Form submission
    if (detectionForm) {
        detectionForm.addEventListener('submit', submitDetection);
    }
    
    // Police dashboard refresh buttons
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshReports);
    }
    
    if (autoRefreshBtn) {
        autoRefreshBtn.addEventListener('click', toggleAutoRefresh);
    }
    
    // Camera functionality
    if (cameraButton) {
        console.log('Camera button found, adding event listener');
        cameraButton.addEventListener('click', function(e) {
            console.log('Camera button clicked, event:', e);
            e.preventDefault();
            e.stopPropagation();
            openCamera();
        });
    } else {
        console.log('Camera button not found');
    }
    
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
    
    // Close camera modal event
    if (cameraModal) {
        cameraModal.addEventListener('hidden.bs.modal', function() {
            console.log('Camera modal hidden');
            closeCamera();
        });
    }
    
    // View details button functionality for police dashboard
    const viewButtons = document.querySelectorAll('.view-details');
    viewButtons.forEach(button => {
        button.addEventListener('click', function() {
            const reportId = this.getAttribute('data-report');
            viewReportDetails(reportId);
        });
    });
}

// Initialize real-time features for police dashboard
function initRealTimeFeatures() {
    // Check if we're on the police dashboard
    if (document.querySelector('.police-dashboard')) {
        // Start periodic refresh (every 30 seconds)
        // setInterval(refreshReportsData, 30000);
    }
}

// Initialize tooltips
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Handle image upload
function handleImageUpload(event) {
    const file = event.target.files[0];
    if (file) {
        // Validate file type
        if (!file.type.match('image.*')) {
            showNotification('Please select an image file (JPEG, PNG, etc.)', 'danger');
            return;
        }
        
        // Validate file size (16MB max)
        if (file.size > 16 * 1024 * 1024) {
            showNotification('File size exceeds 16MB limit. Please choose a smaller file.', 'danger');
            return;
        }
        
        const reader = new FileReader();
        reader.onload = function(e) {
            imageData = e.target.result;
            // Don't show image preview to hide the person's image
            hideImagePreview();
            
            // Enable submit button
            if (submitBtn) {
                submitBtn.disabled = false;
            }
            
            // Show success message
            showNotification('Photo uploaded successfully!', 'success');
        };
        reader.readAsDataURL(file);
    }
}

// Hide image preview to prevent displaying the person's image
function hideImagePreview() {
    if (imagePreview) {
        imagePreview.style.display = 'none';
    }
    
    if (previewImg) {
        previewImg.src = '';
    }
    
    if (uploadArea) {
        uploadArea.style.display = 'block';
    }
}

// Show image preview (only used for camera capture)
function showImagePreview(dataUrl) {
    if (previewImg) {
        previewImg.src = dataUrl;
        previewImg.style.display = 'block';
    }
    
    if (imagePreview) {
        imagePreview.style.display = 'block';
    }
    
    if (uploadArea) {
        uploadArea.style.display = 'none';
    }
    
    // Show retake button
    if (retakeButton) {
        retakeButton.classList.remove('d-none');
    }
}

// Retake photo
function retakePhoto() {
    resetUploadArea();
    showNotification('Photo discarded. You can upload or capture a new photo.', 'info');
}

// Reset upload area to initial state
function resetUploadArea() {
    if (imagePreview) {
        imagePreview.style.display = 'none';
    }
    
    if (uploadArea) {
        uploadArea.style.display = 'block';
    }
    
    if (photoInput) {
        photoInput.value = '';
    }
    
    if (previewImg) {
        previewImg.src = '';
    }
    
    if (submitBtn) {
        submitBtn.disabled = true;
    }
    
    // Hide retake button
    if (retakeButton) {
        retakeButton.classList.add('d-none');
    }
    
    imageData = '';
}

// Submit detection
function submitDetection(event) {
    event.preventDefault();
    
    if (!imageData) {
        showNotification('Please select an image first', 'danger');
        return;
    }
    
    // Show processing indicator
    if (processingIndicator) {
        processingIndicator.classList.remove('d-none');
    }
    
    // Hide results section
    if (resultsSection) {
        resultsSection.classList.add('d-none');
    }
    
    // Disable submit button
    if (submitBtn) {
        submitBtn.disabled = true;
    }
    
    // Create form data
    const formData = new FormData();
    formData.append('image_data', imageData);
    
    // Add location if provided
    const locationInput = document.getElementById('location');
    if (locationInput && locationInput.value.trim() !== '') {
        formData.append('location', locationInput.value.trim());
    }
    
    // Send request
    fetch('/upload/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        // Hide processing indicator
        if (processingIndicator) {
            processingIndicator.classList.add('d-none');
        }
        
        // Display results
        displayResults(data);
        
        // Reset upload area after successful submission
        resetUploadArea();
        
        // Show success message
        showNotification('Detection completed successfully!', 'success');
    })
    .catch(error => {
        console.error('Error:', error);
        // Hide processing indicator
        if (processingIndicator) {
            processingIndicator.classList.add('d-none');
        }
        
        // Show error message
        if (resultsContent) {
            resultsContent.innerHTML = `
                <div class="alert alert-danger">
                    <h5><i class="fas fa-exclamation-triangle"></i> Error</h5>
                    <p>Failed to process the image. Please try again.</p>
                </div>
            `;
        }
        
        if (resultsSection) {
            resultsSection.classList.remove('d-none');
        }
        
        // Re-enable submit button
        if (submitBtn) {
            submitBtn.disabled = false;
        }
        
        showNotification('Failed to process the image. Please try again.', 'danger');
    });
}

// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Display detection results
function displayResults(data) {
    if (resultsSection) {
        resultsSection.classList.remove('d-none');
    }
    
    if (!resultsContent) return;
    
    // Only show detailed results if criminals are found
    if (data.total_criminals_found > 0 && data.detections && data.detections.length > 0) {
        // Criminals detected
        let html = `
            <div class="alert alert-success alert-criminal">
                <div class="d-flex">
                    <div class="flex-shrink-0">
                        <i class="fas fa-check-circle fa-2x"></i>
                    </div>
                    <div class="flex-grow-1 ms-3">
                        <h5>Criminal Detected!</h5>
                        <p>A match has been found in our criminal database.</p>
                    </div>
                </div>
        `;
        
        // Add detection details only for criminal matches
        data.detections.forEach(detection => {
            // Only show details for actual criminal matches
            if (detection.is_criminal) {
                html += `
                    <div class="detection-result positive mt-3">
                        <div class="row">
                            <div class="col-md-3 text-center">
                                <div class="bg-light rounded p-3 mb-3">
                                    <i class="fas fa-user-shield fa-3x text-danger"></i>
                                </div>
                            </div>
                            <div class="col-md-9">
                                <h5>${detection.criminal_name}</h5>
                                <p class="mb-2"><strong>Confidence Level:</strong> ${detection.confidence}%</p>
                                <div class="progress mb-3">
                                    <div class="progress-bar bg-danger" role="progressbar" style="width: ${detection.confidence}%"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }
        });
        
        html += `
                <div class="mt-3">
                    <p><strong>Report ID:</strong> ${data.report_id}</p>
                </div>
            </div>
        `;
        
        resultsContent.innerHTML = html;
    } else {
        // No criminals detected - show minimal message or hide completely
        resultsContent.innerHTML = `
            <div class="alert alert-info">
                <div class="d-flex">
                    <div class="flex-shrink-0">
                        <i class="fas fa-info-circle fa-2x"></i>
                    </div>
                    <div class="flex-grow-1 ms-3">
                        <h5>No Match Found</h5>
                        <p>No matches found in our criminal database.</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Open camera with comprehensive error handling
async function openCamera() {
    console.log('Opening camera function called');
    
    // Close any existing camera first
    closeCamera();
    
    if (!cameraVideo) {
        console.error('Camera video element not found');
        showNotification('Camera element not found. Please refresh the page and try again.', 'danger');
        return;
    }
    
    try {
        console.log('Requesting camera permissions');
        
        // Camera constraints with simpler settings to prevent blurring
        const constraints = {
            video: {
                facingMode: currentFacingMode,
                width: { ideal: 1280 },
                height: { ideal: 720 }
            },
            audio: false
        };
        
        console.log('Constraints:', constraints);
        
        // Show the camera modal first
        console.log('Showing camera modal');
        const modal = new bootstrap.Modal(cameraModal);
        modal.show();
        
        // Small delay to ensure modal is fully displayed
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // Get camera stream
        console.log('Requesting user media');
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        
        console.log('Camera stream received:', stream);
        
        // Set up the video element
        cameraVideo.srcObject = stream;
        cameraStream = stream;
        isCameraActive = true;
        cameraRetryCount = 0;
        
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
    showNotification(errorMessage, 'danger');
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
        showNotification('Camera not ready. Please try again.', 'danger');
        return;
    }
    
    if (!cameraVideo.srcObject) {
        console.log('No camera stream available');
        showCameraError('Camera stream not available. Please check camera permissions.');
        showNotification('Camera stream not available. Please check camera permissions.', 'danger');
        return;
    }
    
    // Check if video is actually playing
    if (cameraVideo.paused || cameraVideo.ended) {
        console.log('Video is not playing');
        showCameraError('Camera not ready. Please wait a moment and try again.');
        showNotification('Camera not ready. Please wait a moment and try again.', 'danger');
        return;
    }
    
    try {
        console.log('Video dimensions:', cameraVideo.videoWidth, 'x', cameraVideo.videoHeight);
        
        // Ensure we have valid dimensions
        if (cameraVideo.videoWidth === 0 || cameraVideo.videoHeight === 0) {
            console.log('Video dimensions not ready');
            showCameraError('Camera not ready. Please wait a moment and try again.');
            showNotification('Camera not ready. Please wait a moment and try again.', 'danger');
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
            showNotification('Failed to capture photo. Please try again.', 'danger');
            return;
        }
        
        // Draw video frame to canvas
        context.drawImage(cameraVideo, 0, 0, cameraCanvas.width, cameraCanvas.height);
        
        // Convert to data URL
        imageData = cameraCanvas.toDataURL('image/jpeg', 0.8);
        console.log('Image captured successfully, data length:', imageData.length);
        
        // Display in preview (only for camera capture)
        showImagePreview(imageData);
        
        // Enable submit button
        if (submitBtn) {
            submitBtn.disabled = false;
        }
        
        // Hide the camera modal
        if (cameraModal) {
            const modalInstance = bootstrap.Modal.getInstance(cameraModal);
            if (modalInstance) {
                console.log('Hiding camera modal');
                modalInstance.hide();
            } else {
                console.log('Creating new modal instance to hide');
                const modal = new bootstrap.Modal(cameraModal);
                modal.hide();
            }
        }
        
        console.log('Capture process completed successfully');
        showNotification('Photo captured successfully!', 'success');
        
    } catch (error) {
        console.error('Capture error:', error);
        showCameraError('Failed to capture photo. Please try again.');
        showNotification('Failed to capture photo. Please try again.', 'danger');
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
    
    // Reset state
    isCameraActive = false;
    console.log('Camera closed successfully');
}

// Refresh reports for police dashboard
function refreshReports() {
    if (refreshBtn) {
        const originalHtml = refreshBtn.innerHTML;
        refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
        refreshBtn.disabled = true;
        
        fetch('/police/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            updateReportsTable(data.reports);
            refreshBtn.innerHTML = originalHtml;
            refreshBtn.disabled = false;
            showNotification('Reports refreshed successfully!', 'success');
        })
        .catch(error => {
            console.error('Error refreshing reports:', error);
            refreshBtn.innerHTML = originalHtml;
            refreshBtn.disabled = false;
            showNotification('Failed to refresh reports. Please try again.', 'danger');
        });
    }
}

// Toggle auto refresh for police dashboard
function toggleAutoRefresh() {
    if (isAutoRefreshActive) {
        clearInterval(autoRefreshInterval);
        isAutoRefreshActive = false;
        if (autoRefreshBtn) {
            autoRefreshBtn.innerHTML = '<i class="fas fa-play"></i> Auto Refresh';
            autoRefreshBtn.className = 'btn btn-sm btn-success ms-2';
            autoRefreshBtn.setAttribute('data-active', 'false');
        }
        showNotification('Auto refresh disabled', 'info');
    } else {
        autoRefreshInterval = setInterval(refreshReports, 10000);
        isAutoRefreshActive = true;
        if (autoRefreshBtn) {
            autoRefreshBtn.innerHTML = '<i class="fas fa-stop"></i> Stop Auto Refresh';
            autoRefreshBtn.className = 'btn btn-sm btn-danger ms-2';
            autoRefreshBtn.setAttribute('data-active', 'true');
        }
        showNotification('Auto refresh enabled (10s interval)', 'success');
    }
}

// Update reports table for police dashboard
function updateReportsTable(reports) {
    const tbody = document.querySelector('.table tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    reports.forEach(report => {
        const row = document.createElement('tr');
        row.className = report.has_detections ? 'alert-criminal' : '';
        row.innerHTML = `
            <td>${report.id.substring(0, 12)}...</td>
            <td>${report.detection_time}</td>
            <td>${report.location || ''}</td>
            <td>
                <span class="badge bg-${report.has_detections ? 'danger' : 'success'}">
                    ${report.status}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-primary view-details" data-report="${report.id}" data-bs-toggle="tooltip" title="View Details">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
    
    // Re-initialize tooltips
    initTooltips();
    
    // Re-bind event listeners to new buttons
    const viewButtons = document.querySelectorAll('.view-details');
    viewButtons.forEach(button => {
        button.addEventListener('click', function() {
            const reportId = this.getAttribute('data-report');
            viewReportDetails(reportId);
        });
    });
}

// View report details for police dashboard
function viewReportDetails(reportId) {
    fetch(`/report/${reportId}/`)
        .then(response => response.json())
        .then(data => {
            // Update modal content with report data
            document.getElementById('modalReportId').textContent = data.report_id;
            document.getElementById('modalDateTime').textContent = data.detection_time;
            document.getElementById('modalLocation').textContent = data.location || 'Not specified';
            
            // Update status badge
            const statusBadge = document.querySelector('#reportDetailsModal .badge');
            if (statusBadge) {
                statusBadge.className = `badge bg-${data.detections.length > 0 ? 'danger' : 'success'}`;
                statusBadge.textContent = data.detections.length > 0 ? 'Criminal Detected' : 'No Match';
            }
            
            // Update detection results
            const resultsContainer = document.querySelector('#reportDetailsModal .detection-result');
            if (resultsContainer && data.detections.length > 0) {
                const detection = data.detections[0]; // For simplicity, show first detection
                resultsContainer.querySelector('h5').textContent = detection.criminal_name;
                resultsContainer.querySelector('.confidence-meter .progress-bar').style.width = `${detection.confidence * 100}%`;
                resultsContainer.querySelector('p.mb-2').innerHTML = `<strong>Confidence Level:</strong> ${(detection.confidence * 100).toFixed(1)}%`;
            }
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('reportDetailsModal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error fetching report details:', error);
            showNotification('Failed to load report details. Please try again.', 'danger');
        });
}