from django.core.management.base import BaseCommand
from app.views import update_cache

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        update_cache()
        self.stdout.write("Cache updated")