from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import datetime

class Criminal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='criminal_photos/')
    is_wanted = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class DetectionReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    citizen = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    photo = models.ImageField(upload_to='detection_reports/')
    detection_time = models.DateTimeField(default=datetime.now)
    location = models.CharField(max_length=200, blank=True)
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Report {self.id} - {self.detection_time}"

class DetectionResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(DetectionReport, on_delete=models.CASCADE, related_name='results')
    criminal = models.ForeignKey(Criminal, on_delete=models.CASCADE)
    confidence = models.FloatField()
    face_coordinates = models.TextField()  # Store face bounding box coordinates as JSON string
    detected_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Detection of {self.criminal.name} in report {self.report}"