from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Movie
from .serializers import MovieSerializer
from django.shortcuts import get_object_or_404
from movies.services.movie_search import search_for_movie
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
    def get(self, request, query):
        movies = search_for_movie(query)
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)