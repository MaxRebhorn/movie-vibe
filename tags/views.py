from rest_framework import generics, permissions
from .models import Tag, UserMovieTag, MovieTagAggregate
from .serializer import UserMovieTagSerializer, TagSerializer
from django.db.models import F

class AddTagView(generics.CreateAPIView):
    serializer_class = UserMovieTagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)
        agg, created = MovieTagAggregate.objects.get_or_create(
            movie=instance.movie,
            tag=instance.tag,
            defaults={'count': 1}
        )
        if not created:
            agg.count = F('count') + 1
            agg.save()
