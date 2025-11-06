from django.contrib import admin
from .models import Criminal, DetectionReport, DetectionResult

@admin.register(Criminal)
class CriminalAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_wanted', 'created_at')
    list_filter = ('is_wanted', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('is_wanted',)

@admin.register(DetectionReport)
class DetectionReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'citizen', 'detection_time', 'location', 'is_processed')
    list_filter = ('is_processed', 'detection_time')
    search_fields = ('location',)
    date_hierarchy = 'detection_time'

@admin.register(DetectionResult)
class DetectionResultAdmin(admin.ModelAdmin):
    list_display = ('report', 'criminal', 'confidence', 'detected_at')
    list_filter = ('confidence', 'detected_at')
    search_fields = ('criminal__name',)