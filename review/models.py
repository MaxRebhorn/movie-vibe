
from django.db import models
from django.conf import settings
from movies.models import Movie

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.IntegerField()
    text = models.TextField()
    tags = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class MovieQuizReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_reviews')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='quiz_reviews')
    answers = models.JSONField(default=dict)  # all quiz answers
    vibe_embedding = models.JSONField(null=True, blank=True)
    narrative_embedding = models.JSONField(null=True, blank=True)
    style_embedding = models.JSONField(null=True, blank=True)
    user_level_at_review = models.IntegerField(default=0)  # Store user level at time of review
    vector_effect = models.JSONField(default=dict)  # Store the effect this review had on the vectors
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'movie')  # so a user can only have one review per movie

class VectorHistory(models.Model):
    """Track historical changes to all movie vectors at once"""
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='vector_history')

    # Store all three vectors together
    vibe_vector = models.JSONField(null=True, blank=True)
    narrative_vector = models.JSONField(null=True, blank=True)
    style_vector = models.JSONField(null=True, blank=True)

    # Meta info
    change_source = models.CharField(max_length=50, choices=[
        ('review', 'Review'),
        ('manual', 'Manual Adjustment'),
        ('system', 'System Update'),
    ])
    source_id = models.IntegerField(null=True, blank=True)  # ID of review/system/etc.
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['movie']),
            models.Index(fields=['created_at']),
        ]

# [file content end]