from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Movie
from .serializers import MovieSerializer
from django.shortcuts import get_object_or_404
from .services.movie_search import MovieSearchService  # Fixed import
class MovieListCreateView(APIView):
    def get(self, request):
        movies = Movie.objects.all()
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MovieSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MovieDetailView(APIView):
    def get(self, request, id):
        movie = get_object_or_404(Movie, id=id)
        serializer = MovieSerializer(movie)
        return Response(serializer.data)


class MovieSearch(APIView):
    def get(self, request):
        query = request.GET.get('q', '').strip()
        if not query:
            return Response([])

        # Suche in Elasticsearch
        search = MovieSearchService.search(query)
        response = search.execute()

        # IDs der Treffer extrahieren (nutzt meta.id)
        movie_ids = [hit.meta.id for hit in response]

        # Hole entsprechende Movies aus der DB
        movies = Movie.objects.filter(id__in=movie_ids)

        # Optional: Reihenfolge der ES-Treffer beibehalten
        movie_dict = {str(movie.id): movie for movie in movies}
        sorted_movies = [
            movie_dict.get(str(hit.meta.id))
            for hit in response
            if str(hit.meta.id) in movie_dict
        ]

        # Serialisieren
        serializer = MovieSerializer(sorted_movies, many=True)
        return Response(serializer.data)
