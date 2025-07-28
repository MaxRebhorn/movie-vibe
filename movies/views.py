import logging

from qdrant_client.http.exceptions import UnexpectedResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Movie
from .serializers import MovieSerializer
from django.shortcuts import get_object_or_404
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
    def get(self, request, *args, **kwargs):
        # Step 1: Extract query params
        movie_id = request.query_params.get("id")
        limit = int(request.query_params.get("limit", 10))

        if not movie_id:
            return Response(
                {"error": "Missing ?id= parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Step 2: Get reference movie or 404
        reference_movie = get_object_or_404(Movie, id=movie_id)

        try:
            # Step 3: Get similar movie IDs from vector DB
            # CHANGED: Using single vector type instead of set
            similar_ids = get_similar_movies(reference_movie, k=limit)

            # Step 4: Fetch those movies from the database
            similar_movies = Movie.objects.filter(id__in=similar_ids)

            # Step 5: Optional – preserve similarity order
            movie_map = {movie.id: movie for movie in similar_movies}
            ordered = [movie_map[mid] for mid in similar_ids if mid in movie_map]

            return Response(MovieSerializer(ordered, many=True).data)

        except UnexpectedResponse as e:
            return Response(
                {"error": "Vector search failed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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


class MovieSimilarView(APIView):
    def get(self, request, id):
        limit = int(request.query_params.get("limit", 10))
        reference_movie = get_object_or_404(Movie, id=id)

        try:
            # CHANGED: Use single vector type parameter
            similar_ids = get_similar_movies(
                movie_id=reference_movie.id,
                limit=limit,
                collection="movies_vibe"
            )

            similar_movies = Movie.objects.filter(id__in=similar_ids)


            serializer = MovieSerializer(similar_movies, many=True)
            return Response(serializer.data)

        except UnexpectedResponse as e:
            logger.exception(f"Vector search failed for movie ID {reference_movie.id}: {e}")
            return Response(
                {"error": "Vector search failed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )