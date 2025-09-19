# user/management/commands/delete_all_pools.py
from django.core.management.base import BaseCommand
from user.models import UserPool

class Command(BaseCommand):
    help = "Delete all UserPools for all users"

    def handle(self, *args, **options):
        total = UserPool.objects.count()
        if total == 0:
            self.stdout.write(self.style.WARNING("⚠️ No pools to delete."))
            return

        UserPool.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"✅ Deleted {total} UserPools."))
