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
    radius = models.FloatField(default=0.7)

    # Surface Tension Parameter
    surface_tension = models.FloatField(default=0.02, help_text="Wie groß/dicht muss ein Außencluster sein, damit ein neuer Pool gebildet werden kann")

    # Aggregats für inkrementelle Updates
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
        """Berechnet das neue Zentrum aus den gewichteten Summen"""
        if self.pos_weight_sum > 0:
            vec = np.array(self.pos_weighted_sum)
            self.center = (vec / self.pos_weight_sum).tolist()
        self.save()

    def contains(self, vector):
        """Prüft, ob ein Vektor innerhalb der Hypersphäre liegt"""
        dist = np.linalg.norm(np.array(vector) - np.array(self.center))
        return dist <= self.radius

    def distance(self, vector):
        return float(np.linalg.norm(np.array(vector) - np.array(self.center)))

    def score(self, vector, sigma_divisor=3.0):
        """Gauß-Score für Empfehlungen"""
        dist = self.distance(vector)
        sigma = self.radius / sigma_divisor
        return float(np.exp(- (dist ** 2) / (2 * sigma ** 2)))

    def check_surface_tension_and_split(self, candidate_vectors):
        """
        Prüft Cluster außerhalb des Pools.
        Wenn SurfaceTension überschritten wird, wird ein neuer Pool gebildet.
        candidate_vectors: Liste von Movie-Embeddings außerhalb des Pools
        """
        # Placeholder: Cluster-Detection & Vergleich mit surface_tension
        # -> Wenn Cluster groß genug -> erstelle neuen UserPool
        pass
