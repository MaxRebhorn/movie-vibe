import logging
from qdrant_client.http.exceptions import UnexpectedResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Movie
from .serializers import MovieSerializer
from .services.movie_search import MovieSearchService
from .services.vector_search import get_similar_movies

logger = logging.getLogger(__name__)


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

        search = MovieSearchService.search(query)
        response = search.execute()

        movie_ids = [hit.meta.id for hit in response]
        movies = Movie.objects.filter(id__in=movie_ids)

        movie_dict = {str(movie.id): movie for movie in movies}
        sorted_movies = [
            movie_dict.get(str(hit.meta.id))
            for hit in response
            if str(hit.meta.id) in movie_dict
        ]

        serializer = MovieSerializer(sorted_movies, many=True)
        return Response(serializer.data)


class MovieSimilarView(APIView):
    def get(self, request, id):
        limit = int(request.query_params.get("limit", 10))
        reference_movie = get_object_or_404(Movie, id=id)

        try:
            similar_ids = get_similar_movies(
                movie_id=reference_movie.id,
                limit=limit,
                collection="movies_narrative"
            )

            similar_movies = Movie.objects.filter(id__in=similar_ids)
            movie_dict = {movie.id: movie for movie in similar_movies}
            ordered = [movie_dict[mid] for mid in similar_ids if mid in movie_dict]

            serializer = MovieSerializer(ordered, many=True)
            return Response(serializer.data)

        except UnexpectedResponse as e:
            logger.exception(f"Vector search failed for movie ID {reference_movie.id}: {e}")
            return Response(
                {"error": "Vector search failed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
