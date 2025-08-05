from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from movies.serializers import MovieSerializer
from movies.models import Movie

class MovieSerializerTestCase(TestCase):
    def setUp(self):
        self.valid_data = {
            "title": "Inception",
            "original_title": "Inception",
            "synopsis": "A thief who steals corporate secrets...",
            "tagline": "Your mind is the scene of the crime",
            "language": "English",
            "country": "US",
            "release_date": "2010-07-16",
            "runtime": 148,
            "director": "Christopher Nolan",
            "cast": ["Leonardo DiCaprio", "Joseph Gordon-Levitt"],
            "genres": ["Action", "Sci-Fi"],
            "keywords": ["dream", "subconscious"],
            "composer": ["Hans Zimmer"],
            "poster_url": "https://example.com/poster.jpg",
            "backdrop_url": "https://example.com/backdrop.jpg",
            "avg_rating": 8.8,
            "tmdb_id": 12345
        }

    def test_valid_serialization(self):
        serializer = MovieSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_required_fields(self):
        required_fields = ['title', 'release_date', 'runtime', 'director', 'poster_url', 'tmdb_id']
        for field in required_fields:
            invalid_data = self.valid_data.copy()
            del invalid_data[field]
            serializer = MovieSerializer(data=invalid_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn(field, serializer.errors)

    def test_tmdb_id_uniqueness(self):
        Movie.objects.create(**self.valid_data)
        serializer = MovieSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('tmdb_id', serializer.errors)