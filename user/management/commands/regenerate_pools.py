from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from user.models import UserProfile, UserPool
from user.services.pool_service import get_user_pools, recompute_user_pools

class Command(BaseCommand):
    help = "Regenerate all UserPools for all users and populate with favorite movies"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Deleting all existing pools..."))
        UserPool.objects.all().delete()

        for user in User.objects.all():
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                self.stdout.write(self.style.NOTICE(f"Created missing profile for user: {user.username}"))

            # Recreate pools
            get_user_pools(profile)

            # Recompute all pools at once (faster, compatible with new API)
            recompute_user_pools(profile)

            self.stdout.write(self.style.SUCCESS(f"Regenerated pools for user: {user.username}"))

        self.stdout.write(self.style.SUCCESS("✅ All user pools have been regenerated."))
