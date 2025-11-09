import os
import sys
from django.core.management.base import BaseCommand
from detection.models import DetectionResult

class Command(BaseCommand):
    help = 'Fix confidence values that are outside the 0-100 range'

    def handle(self, *args, **options):
        """Fix confidence values that are outside the 0-100 range"""
        results = DetectionResult.objects.all()
        fixed_count = 0
        
        for result in results:
            old_confidence = float(result.confidence)
            # Clamp confidence between 0 and 100
            clamped_confidence = max(0.0, min(100.0, old_confidence))
            
            # If the confidence was outside the valid range, update it
            if old_confidence != clamped_confidence:
                result.confidence = clamped_confidence
                result.save()
                fixed_count += 1
                self.stdout.write(f"Fixed record {result.id}: {old_confidence} -> {clamped_confidence}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully fixed {fixed_count} records with incorrect confidence values"
            )
        )