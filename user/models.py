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

    def give_xp(self, xp):
        self.xp += xp
        self.save()

    def add_favorite_movie(self, movie_id):
        try:
            movie = Movie.objects.get(id=movie_id)
            self.favorite_movies.add(movie)
            self.save()
        except Movie.DoesNotExist:
            # Optional: handle the case where the movie doesn't exist
            pass

    def remove_favorite_movie(self, movie_id):
        try:
            movie = Movie.objects.get(id=movie_id)
            if movie in self.favorite_movies.all():
                self.favorite_movies.remove(movie)
                self.save()
        except Movie.DoesNotExist:
            pass


    @property
    def level(self):
        # Beispiel: jede 100 XP = 1 Level, hier leicht skalierbar
        return self.xp // 100