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
    answers = models.JSONField(default=dict)  # alle Quiz-Antworten
    vibe_embedding = models.JSONField(null=True, blank=True)
    narrative_embedding = models.JSONField(null=True, blank=True)
    style_embedding = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'movie')  # damit ein User nur eine Review pro Movie hat