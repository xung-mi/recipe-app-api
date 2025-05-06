from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """Django command to wait for the database to be available"""

    def handle(self, *args, **options):
        pass  # Chưa làm gì cả, chỉ là stub
