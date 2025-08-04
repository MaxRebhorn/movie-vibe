from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from tmdb.services.api_service import get_movie_by_name, create_movie_from_tmdb_details, tmdbMovie
from movies.serializers import MovieSerializer
from movies.models import Movie


class CreateMovieView(APIView):
    def get(self, request):
        title = request.query_params.get("title")
        if not title:
            return Response({"error": "Missing title query parameter."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            results = get_movie_by_name(title)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        simplified = []
        for movie in results[:10]:  # Limit to top 10 results
            simplified.append({
                "title": movie.title,
                "release_date": movie.release_date,
                "tmdb_id": movie.id,
                "poster_url": f"https://image.tmdb.org/t/p/w200{movie.poster_path}" if movie.poster_path else None
            })

        return Response(simplified, status=status.HTTP_200_OK)

    def post(self, request):
        tmdb_id = request.data.get("tmdb_id")
        if not tmdb_id:
            return Response({"error": "Missing tmdb_id in request body."}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent duplicates
        if Movie.objects.filter(tmdb_id=tmdb_id).exists():
            movie = Movie.objects.get(tmdb_id=tmdb_id)
            serializer = MovieSerializer(movie)
            return Response(serializer.data, status=status.HTTP_200_OK)

        try:
            tmdb_instance = tmdbMovie()
            details = tmdb_instance.details(tmdb_id)

            # Optional: enrich details with extra data for create function
            details.credits = tmdb_instance.credits(tmdb_id)
            details.keywords = tmdb_instance.keywords(tmdb_id)
            details.videos = tmdb_instance.videos(tmdb_id)

            movie = create_movie_from_tmdb_details(details)
            serializer = MovieSerializer(movie)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
