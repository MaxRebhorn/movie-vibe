from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Review
from movies.models import Movie
from review.serializer import ReviewSerializer

class MovieReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        movie_id = self.kwargs['movie_id']
        return Review.objects.filter(movie__id=movie_id)

    def perform_create(self, serializer):
        movie = get_object_or_404(Movie, pk=self.kwargs['movie_id'])
        serializer.save(user=self.request.user, movie=movie)
