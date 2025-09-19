from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from user.models import UserProfile, UserPool
from user.services.pool_service import recompute_user_pools
from user.settings.pool_settings import POOL_MIN_RADIUS

class Command(BaseCommand):
    help = "Regenerate all UserPools for all users and populate with favorite movies"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Deleting all existing pools..."))
        UserPool.objects.all().delete()

        for user in User.objects.all():
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                self.stdout.write(self.style.NOTICE(f"Created missing profile for user: {user.username}"))

            # Recompute all pools at once using the new service
            recompute_user_pools(profile)

            self.stdout.write(self.style.SUCCESS(f"✅ Regenerated pools for user: {user.username}"))

        self.stdout.write(self.style.SUCCESS("🎯 All user pools have been regenerated."))
