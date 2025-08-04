from django.db import models
from django.contrib.auth.models import User
from movies.models import Movie

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    favorite_movies = models.ManyToManyField(
        Movie,
        related_name='favorited_by',
        blank=True
    )

    def __str__(self):
        return self.user.username