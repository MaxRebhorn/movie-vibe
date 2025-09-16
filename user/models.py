import numpy as np
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.contrib.auth.models import User
from movies.models import Movie

# ============================
# Configurable Hyperparameters
# ============================
# All values here can be easily tweaked without digging into logic.
POOL_MIN_RADIUS = 0.5          # fallback minimum radius
POOL_GROW_FACTOR = 1.2         # factor to grow radius each iteration
POOL_MAX_GROW_STEPS = 5        # safety limit to avoid infinite loops
POOL_MIN_CANDIDATES = 10       # target minimum candidates inside the sphere
POOL_SIGMA_DIVISOR = 3.0       # controls Gaussian score sharpness
POOL_SURFACE_TENSION = 0.02  # controls how resistant pools are to splitting

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
        return self.xp // 100


class UserPool(models.Model):
    DIMENSION_CHOICES = [
        ("vibe", "Vibe"),
        ("style", "Style"),
        ("plot", "Plot"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pools")
    dimension = models.CharField(max_length=20, choices=DIMENSION_CHOICES)

    # Hypersphere
    center = ArrayField(models.FloatField(), size=300)
    radius = models.FloatField(default=POOL_MIN_RADIUS)

    # Surface Tension Parameter
    surface_tension = models.FloatField(default=POOL_SURFACE_TENSION)

    # Aggregates for incremental updates
    pos_weight_sum = models.FloatField(default=0.0)
    pos_weighted_sum = ArrayField(models.FloatField(), size=300, default=list)

    neg_weight_sum = models.FloatField(default=0.0)
    neg_weighted_sum = ArrayField(models.FloatField(), size=300, default=list)

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
        """Recalculate pool center from positive weighted vectors."""
        if self.pos_weight_sum > 0:
            vec = np.array(self.pos_weighted_sum)
            self.center = (vec / self.pos_weight_sum).tolist()
            self.save()

    def contains(self, vector):
        """Check if vector lies inside hypersphere."""
        dist = np.linalg.norm(np.array(vector) - np.array(self.center))
        return dist <= self.radius

    def distance(self, vector):
        return float(np.linalg.norm(np.array(vector) - np.array(self.center)))

    def score(self, vector):
        """Gaussian scoring relative to pool center and radius."""
        dist = self.distance(vector)
        sigma = max(self.radius / POOL_SIGMA_DIVISOR, 0.1)
        return float(np.exp(- (dist ** 2) / (2 * sigma ** 2)))

    def grow_radius_until_candidates(self, candidate_vectors):
        """
        Dynamically grow radius until at least N candidates are inside.
        """
        step = 0
        while step < POOL_MAX_GROW_STEPS:
            inside = [vec for vec in candidate_vectors if self.contains(vec)]
            if len(inside) >= POOL_MIN_CANDIDATES:
                break
            self.radius *= POOL_GROW_FACTOR
            step += 1
        self.save()
        return self.radius

    def check_surface_tension_and_split(self, candidate_vectors):
        """
        Placeholder: detect clusters outside the pool and decide if a split is needed.
        """
        pass
