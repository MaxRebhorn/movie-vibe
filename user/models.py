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
    xp = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


    def give_xp(self,xp):
        self.xp += xp
    @property
    def level(self):
        # Beispiel: jede 100 XP = 1 Level, hier leicht skalierbar
        return self.xp // 100