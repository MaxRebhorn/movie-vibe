import numpy as np
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.contrib.auth.models import User
from movies.models import Movie
from user.settings.pool_settings import (

    POOL_MIN_RADIUS,
    POOL_SURFACE_TENSION,
    POOL_SIGMA_DIVISOR,
    POOL_VECTOR_SIZE

)  # Embedding vector size


# ============================
# User Profile
# ============================
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    favorite_movies = models.ManyToManyField(Movie, related_name='favorited_by', blank=True)
    xp = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

    @property
    def level(self):
        return self.xp // 100

    def give_xp(self, xp: int):
        self.xp += xp
        self.save()

    def add_favorite_movie(self, movie_id: int):
        try:
            movie = Movie.objects.get(id=movie_id)
            self.favorite_movies.add(movie)
            self.save()
        except Movie.DoesNotExist:
            pass

    def remove_favorite_movie(self, movie_id: int):
        try:
            movie = Movie.objects.get(id=movie_id)
            self.favorite_movies.remove(movie)
            self.save()
        except Movie.DoesNotExist:
            pass


# ============================
# User Pool
# ============================
class UserPool(models.Model):
    DIMENSION_CHOICES = [
        ("vibe", "Vibe"),
        ("style", "Style"),
        ("plot", "Plot"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pools")
    dimension = models.CharField(max_length=20, choices=DIMENSION_CHOICES)
    name = models.CharField(max_length=100, blank=True, default="")
    pos_weight_sum = models.FloatField(default=0.0)  # Sum of weights for favorites
    center = ArrayField(models.FloatField(), size=POOL_VECTOR_SIZE)
    radius = models.FloatField(default=POOL_MIN_RADIUS)
    surface_tension = models.FloatField(default=POOL_SURFACE_TENSION)

    support_movie_ids = ArrayField(models.IntegerField(), blank=True, default=list)
    parent_pool = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="child_pools"
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "dimension", "id")

    def __str__(self):
        return f"{self.user.username} - {self.dimension} Pool"

    # ---------------- Core Methods ----------------
    def update_center(self):
        """Update center based on weighted favorite vectors."""
        if hasattr(self, "pos_weighted_sum") and self.support_movie_ids:
            vecs = np.array(self.pos_weighted_sum)
            self.center = (vecs / max(self.pos_weight_sum, 1)).tolist()
            self.save()

    def contains(self, vector):
        """Check if a vector lies within this pool's radius."""
        return np.linalg.norm(np.array(vector) - np.array(self.center)) <= self.radius

    def distance(self, vector):
        """Euclidean distance from the pool center."""
        return float(np.linalg.norm(np.array(vector) - np.array(self.center)))

    def score(self, vector):
        """Gaussian score for a vector relative to pool center."""
        dist = self.distance(vector)
        sigma = max(self.radius / POOL_SIGMA_DIVISOR, 0.1)
        return float(np.exp(- (dist ** 2) / (2 * sigma ** 2)))

    def update_support_movies(self):
        """Ensure only favorite movies are tracked in the pool."""
        profile = self.user.profile
        favorite_ids = set(profile.favorite_movies.values_list("id", flat=True))
        self.support_movie_ids = [mid for mid in self.support_movie_ids if mid in favorite_ids]
        self.save()
