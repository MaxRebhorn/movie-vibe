from django.contrib.auth.models import User
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from movies.models import Movie
from user.models import UserProfile, UserPool
from user.services import pool_service
from pool_settings import POOL_MIN_RADIUS

# -----------------------------
# User Profile Creation
# -----------------------------
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, "profile"):
        instance.profile.save()

# -----------------------------
# Default User Pools
# -----------------------------
@receiver(post_save, sender=UserProfile)
def create_default_user_pools(sender, instance: UserProfile, created, **kwargs):
    if created:
        for dim in ["vibe", "style", "plot"]:
            UserPool.objects.create(
                user=instance.user,
                dimension=dim,
                center=[0.0] * 300,  # neutral vector
                radius=POOL_MIN_RADIUS
            )
        # Population of pools happens automatically when favorites are added

# -----------------------------
# Favorite Movies Changed
# -----------------------------
@receiver(m2m_changed, sender=UserProfile.favorite_movies.through)
def favorite_movies_updated(sender, instance: UserProfile, action, **kwargs):
    """
    Signal: When a movie is added or removed from favorites,
    recompute all pools for the user using the new pool service.
    """
    if action in ["post_add", "post_remove"]:
        pool_service.recompute_user_pools(instance)
