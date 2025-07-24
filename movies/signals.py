from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Movie
from django_elasticsearch_dsl.registries import registry

@receiver(post_save, sender=Movie)
def update_movie_index(sender, instance, **kwargs):
    registry.update(instance)

@receiver(post_delete, sender=Movie)
def delete_movie_index(sender, instance, **kwargs):
    registry.delete(instance)