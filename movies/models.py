from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class StreamingProvider(models.Model):
    tmdb_id = models.IntegerField(unique=True)  # TMDb's provider_id
    name = models.CharField(max_length=100)
    logo_path = models.CharField(max_length=255, blank=True, null=True)

    def logo_url(self):
        if self.logo_path:
            return f"https://image.tmdb.org/t/p/w92{self.logo_path}"
        return None

    class Meta:
        db_table = "StreamingProvider"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=50)
    original_title = models.CharField(max_length=50)
    synopsis = models.TextField()  # Changed to TextField for longer content
    plot = models.TextField(null=True)
    plot_normalized = models.TextField(null=True)
    tagline = models.CharField(max_length=255)
    language = models.CharField(max_length=50)
    country = models.CharField(max_length=4)
    release_date = models.DateField()
    runtime = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1000)]
    )
    director = models.CharField(max_length=100)
    cast = models.JSONField(default=list)  # Array of strings
    genres = models.JSONField(default=list)  # Array of strings
    keywords = models.JSONField(default=list)  # Array of strings
    composer = models.JSONField(default=list)  # Array of strings
    poster_url = models.URLField(max_length=500)
    backdrop_url = models.URLField(max_length=500)
    trailer_url = models.URLField(max_length=500, blank=True, null=True)
    avg_rating = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        default=0.0
    )
    tmdb_id = models.IntegerField(unique=True)

    # ✅ Make streaming providers optional (nullable ManyToMany)
    streaming_providers = models.ManyToManyField(
        StreamingProvider,
        through="MovieProviderLink",
        related_name="movies",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "Movie"
        ordering = ['-release_date']

    def __str__(self):
        return self.title


class MovieProviderLink(models.Model):
    """Intermediate table to capture the relation + access type."""
    ACCESS_CHOICES = [
        ("flatrate", "Flatrate"),
        ("buy", "Buy"),
        ("rent", "Rent"),
    ]

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    provider = models.ForeignKey(StreamingProvider, on_delete=models.CASCADE)
    access_type = models.CharField(max_length=20, choices=ACCESS_CHOICES)
    link = models.URLField(blank=True, null=True)  # link to TMDb availability page
    country = models.CharField(max_length=5, default="DE")  # ISO 3166-1 code

    class Meta:
        db_table = "MovieProviderLink"
        unique_together = ("movie", "provider", "access_type", "country")

    def __str__(self):
        return f"{self.movie.title} - {self.provider.name} ({self.access_type})"
