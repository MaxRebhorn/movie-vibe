from django.contrib.auth.models import User
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from user.services import pool_service
from movies.models import Movie
from user.models import UserProfile, UserPool


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(m2m_changed, sender=UserProfile.favorite_movies.through)
def favorite_movies_updated(sender, instance: UserProfile, action, reverse, pk_set, **kwargs):
    """
    Signal: Wenn ein Film favorisiert oder entfernt wird.
    Aktualisiert die Pools des Users entsprechend.
    """
    if action == "post_add":
        for movie_id in pk_set:
            movie = Movie.objects.get(id=movie_id)
            pool_service.update_pools_with_movie(instance, movie)
    elif action == "post_remove":
        # Optional: Pool neu berechnen oder Film entfernen
        pass

@receiver(post_save, sender=UserProfile)
def create_user_pools(sender, instance, created, **kwargs):
    if created:
        for dim in ["vibe", "style", "plot"]:
            UserPool.objects.create(
                user=instance.user,
                dimension=dim,
                center=[0.0] * 300,  # neutral vector
                radius=0.7
            )