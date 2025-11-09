import os
from django.core.management.base import BaseCommand
from django.conf import settings
from detection.models import Criminal, DetectionReport, DetectionResult

class Command(BaseCommand):
    help = 'Clear all data from the database and media files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion without prompting',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This will delete ALL data from the database and ALL media files. '
                    'This action cannot be undone.'
                )
            )
            confirm = input('Are you sure you want to proceed? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('Operation cancelled.'))
                return

        try:
            # Delete all detection results
            DetectionResult.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'Deleted all detection results')
            )

            # Delete all detection reports
            DetectionReport.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'Deleted all detection reports')
            )

            # Delete all criminals
            Criminal.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'Deleted all criminals')
            )

            # Delete media files
            media_dirs = [
                os.path.join(settings.MEDIA_ROOT, 'criminal_photos'),
                os.path.join(settings.MEDIA_ROOT, 'detection_reports')
            ]

            for media_dir in media_dirs:
                if os.path.exists(media_dir):
                    for filename in os.listdir(media_dir):
                        file_path = os.path.join(media_dir, filename)
                        try:
                            if os.path.isfile(file_path):
                                os.unlink(file_path)
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f'Failed to delete {file_path}: {e}')
                            )
                    self.stdout.write(
                        self.style.SUCCESS(f'Cleared media directory: {media_dir}')
                    )

            self.stdout.write(
                self.style.SUCCESS('Successfully cleared all database data and media files')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error clearing database: {e}')
            )