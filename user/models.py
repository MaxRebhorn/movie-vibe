import numpy as np
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.contrib.auth.models import User
from movies.models import Movie

# ============================
# Hyperparameters
# ============================
POOL_MIN_RADIUS = 1.0
POOL_GROW_FACTOR = 1.2
POOL_MAX_GROW_STEPS = 10
POOL_MIN_CANDIDATES = 3
POOL_SIGMA_DIVISOR = 3.0
POOL_SURFACE_TENSION = 0.1
POOL_MAX_MOVIE_DUPLICATES = 2  # Max pools per movie

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
    pos_weight_sum = models.FloatField(default=0.0)
    center = ArrayField(models.FloatField(), size=300)
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
        if self.support_movie_ids:
            vecs = np.array(self.pos_weighted_sum) if hasattr(self, "pos_weighted_sum") else np.zeros(300)
            self.center = (vecs / max(self.pos_weight_sum, 1)).tolist()
            self.save()

    def contains(self, vector):
        return np.linalg.norm(np.array(vector) - np.array(self.center)) <= self.radius

    def distance(self, vector):
        return float(np.linalg.norm(np.array(vector) - np.array(self.center)))

    def score(self, vector):
        dist = self.distance(vector)
        sigma = max(self.radius / POOL_SIGMA_DIVISOR, 0.1)
        return float(np.exp(- (dist ** 2) / (2 * sigma ** 2)))
