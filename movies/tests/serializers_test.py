from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta
from movies.serializers import MovieSerializer
from movies.models import Movie
import json


class MovieSerializerTests(TestCase):
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
            "trailer_url": "https://youtube.com/watch?v=123",
            "avg_rating": 8.8,
            "tmdb_id": 12345
        }

    def test_valid_data(self):
        serializer = MovieSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_json_fields(self):
        invalid_data = self.valid_data.copy()
        invalid_data['cast'] = "not a list"
        serializer = MovieSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('cast', serializer.errors)

    def test_future_release_date(self):
        future_date = (timezone.now() + timedelta(days=365)).date().isoformat()
        invalid_data = self.valid_data.copy()
        invalid_data['release_date'] = future_date
        serializer = MovieSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('release_date', serializer.errors)

    def test_invalid_runtime(self):
        for value in [0, 1001]:
            invalid_data = self.valid_data.copy()
            invalid_data['runtime'] = value
            serializer = MovieSerializer(data=invalid_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn('runtime', serializer.errors)

    def test_invalid_rating(self):
        for value in [-0.1, 10.1]:
            invalid_data = self.valid_data.copy()
            invalid_data['avg_rating'] = value
            serializer = MovieSerializer(data=invalid_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn('avg_rating', serializer.errors)

    def test_invalid_urls(self):
        invalid_urls = [
            ("poster_url", "https://example.com/poster.pdf"),
            ("backdrop_url", "https://example.com/backdrop.pdf"),
            ("trailer_url", "https://example.com/trailer.mp4")
        ]

        for field, url in invalid_urls:
            invalid_data = self.valid_data.copy()
            invalid_data[field] = url
            serializer = MovieSerializer(data=invalid_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn(field, serializer.errors)

    def test_country_code_validation(self):
        for code in ['USA', 'X', '']:
            invalid_data = self.valid_data.copy()
            invalid_data['country'] = code
            serializer = MovieSerializer(data=invalid_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn('country', serializer.errors)

    def test_duplicate_tmdb_id(self):
        Movie.objects.create(**{
            k: v for k, v in self.valid_data.items()
            if k not in ['cast', 'genres', 'keywords', 'composer']
        })
        serializer = MovieSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('tmdb_id', serializer.errors)

    def test_empty_title(self):
        invalid_data = self.valid_data.copy()
        invalid_data['title'] = " "
        serializer = MovieSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)

    def test_uppercase_country_code(self):
        valid_data = self.valid_data.copy()
        valid_data['country'] = "us"
        serializer = MovieSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['country'], "US")