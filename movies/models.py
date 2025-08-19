from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "Movie"
        ordering = ['-release_date']