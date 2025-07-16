from django.test import TestCase
from movies.models import Movie
from django.core.exceptions import ValidationError
from datetime import date, timedelta
import json


class MovieTestCase(TestCase):
    def setUp(self):
        # Create a sample movie for testing
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
            cast=json.dumps(["Leonardo DiCaprio", "Joseph Gordon-Levitt"]),
            genres=json.dumps(["Action", "Sci-Fi"]),
            keywords=json.dumps(["dream", "subconscious"]),
            composer=json.dumps(["Hans Zimmer"]),
            poster_url="https://example.com/poster.jpg",
            backdrop_url="https://example.com/backdrop.jpg",
            trailer_url="https://example.com/trailer.mp4",
            avg_rating=8.8,
            tmdb_id=12345
        )

    def test_attributes_exist(self):
        """Test that all required attributes exist on the model"""
        fields = [
            'title', 'original_title', 'synopsis', 'tagline', 'language', 'country',
            'release_date', 'runtime', 'director', 'cast', 'genres', 'keywords',
            'composer', 'poster_url', 'backdrop_url', 'trailer_url', 'avg_rating',
            'tmdb_id', 'created_at', 'updated_at'
        ]
        for field in fields:
            self.assertTrue(hasattr(self.movie, field), f"Field {field} is missing")

    def test_attributes_reject_invalid_data(self):
        """Test that invalid data is properly rejected"""
        # Test required fields
        with self.assertRaises(ValidationError):
            movie = Movie(title="")  # Missing required fields
            movie.full_clean()

        # Test max length constraints
        with self.assertRaises(ValidationError):
            movie = Movie(
                title="A" * 51,  # Exceeds max_length=50
                original_title="A" * 51,
                tagline="A" * 256,
                language="A" * 51,
                country="USA",  # Exceeds max_length=4
                release_date=date.today(),
                runtime=148,
                director="Director",
                cast=json.dumps(["Actor"]),
                genres=json.dumps(["Genre"]),
                poster_url="https://example.com/poster.jpg",
                backdrop_url="https://example.com/backdrop.jpg",
                avg_rating=5.0,
                tmdb_id=12346
            )
            movie.full_clean()

        # Test runtime validation
        with self.assertRaises(ValidationError):
            self.movie.runtime = 0  # Below MinValueValidator(1)
            self.movie.full_clean()

        with self.assertRaises(ValidationError):
            self.movie.runtime = 1001  # Above MaxValueValidator(1000)
            self.movie.full_clean()

        # Test avg_rating validation
        with self.assertRaises(ValidationError):
            self.movie.avg_rating = -0.1  # Below MinValueValidator(0.0)
            self.movie.full_clean()

        with self.assertRaises(ValidationError):
            self.movie.avg_rating = 10.1  # Above MaxValueValidator(10.0)
            self.movie.full_clean()

        # Test JSON fields
        with self.assertRaises(ValidationError):
            self.movie.cast = "not a json string"  # Invalid JSON
            self.movie.full_clean()

        # Test unique constraint
        with self.assertRaises(ValidationError):
            Movie.objects.create(
                title="Another Movie",
                original_title="Another Movie",
                synopsis="Another movie...",
                tagline="Another tagline",
                language="English",
                country="US",
                release_date=date.today(),
                runtime=120,
                director="Director",
                cast=json.dumps(["Actor"]),
                genres=json.dumps(["Genre"]),
                poster_url="https://example.com/poster2.jpg",
                backdrop_url="https://example.com/backdrop2.jpg",
                avg_rating=7.5,
                tmdb_id=12344  # Duplicate of setup movie
            ).full_clean()

    def test_db_accuracy(self):
        """Test that data is accurately stored and retrieved from the database"""
        db_movie = Movie.objects.get(id=self.movie.id)

        # Test standard fields
        self.assertEqual(db_movie.title, "Inception")
        self.assertEqual(db_movie.runtime, 148)
        self.assertEqual(db_movie.avg_rating, 8.8)

        # Test JSON fields
        self.assertEqual(json.loads(db_movie.cast), ["Leonardo DiCaprio", "Joseph Gordon-Levitt"])
        self.assertEqual(json.loads(db_movie.genres), ["Action", "Sci-Fi"])

        # Test date field
        self.assertEqual(db_movie.release_date, date(2010, 7, 16))

        # Test URL fields
        self.assertEqual(db_movie.poster_url, "https://example.com/poster.jpg")

        # Test automatic fields
        self.assertIsNotNone(db_movie.created_at)
        self.assertIsNotNone(db_movie.updated_at)

        # Test optional field
        self.assertEqual(db_movie.trailer_url, "https://example.com/trailer.mp4")

    def test_meta_options(self):
        """Test that Meta options are correctly set"""
        self.assertEqual(Movie._meta.db_table, "Movie")
        self.assertEqual(Movie._meta.ordering, ['-release_date'])