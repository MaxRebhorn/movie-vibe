from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date
import json
from movies.models import Movie

class MovieModelTestCase(TestCase):
    def setUp(self):
        self.movie = Movie.objects.create(
            title="Inception",
            original_title="Inception",
            synopsis="A thief who steals corporate secrets...",
            tagline="Your mind is the scene of the crime",
            language="English",
            country="US",
            release_date=date(2010, 7, 16),
            runtime=148,
            director="Christopher Nolan",
            cast=["Leonardo DiCaprio", "Joseph Gordon-Levitt"],
            genres=["Action", "Sci-Fi"],
            keywords=["dream", "subconscious"],
            composer=["Hans Zimmer"],
            poster_url="https://example.com/poster.jpg",
            backdrop_url="https://example.com/backdrop.jpg",
            trailer_url="https://example.com/trailer.mp4",
            avg_rating=8.8,
            tmdb_id=12345
        )

    def test_attributes_exist(self):
        fields = [
            'title', 'original_title', 'synopsis', 'tagline', 'language', 'country',
            'release_date', 'runtime', 'director', 'cast', 'genres', 'keywords',
            'composer', 'poster_url', 'backdrop_url', 'trailer_url', 'avg_rating',
            'tmdb_id', 'created_at', 'updated_at'
        ]
        for field in fields:
            self.assertTrue(hasattr(self.movie, field), f"Field {field} is missing")

    def test_validation(self):
        with self.assertRaises(ValidationError):
            Movie(title="").full_clean()

    def test_db_accuracy(self):
        db_movie = Movie.objects.get(id=self.movie.id)
        self.assertEqual(db_movie.title, "Inception")
        self.assertEqual(db_movie.cast, ["Leonardo DiCaprio", "Joseph Gordon-Levitt"])

    def test_meta_options(self):
        self.assertEqual(Movie._meta.db_table, "Movie")
        self.assertEqual(Movie._meta.ordering, ['-release_date'])