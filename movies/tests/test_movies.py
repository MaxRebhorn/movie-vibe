from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase
from movies.models import Movie
from django.core.exceptions import ValidationError
from datetime import date, timedelta
import json

from movies.serializers import MovieSerializer
from rest_framework import status
from rest_framework.test import APIClient

from movies.models import Movie
from movies.document import MovieDocument
from datetime import date
from django.db import connection, transaction


# Create your tests here.
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
        self.assertEqual(db_movie.cast, ["Leonardo DiCaprio", "Joseph Gordon-Levitt"])
        self.assertEqual(db_movie.genres, ["Action", "Sci-Fi"])

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


class MovieSerializerTestCase(TestCase):
    def setUp(self):
        # Gültige Testdaten
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
            "trailer_url": "https://youtube.com/trailer",
            "avg_rating": 8.8,
            "tmdb_id": 12345
        }

    def test_valid_data_serialization(self):
        """Testet Serialisierung von gültigen Daten"""
        serializer = MovieSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

        # Teste spezifische Feldtransformationen
        movie = serializer.save()
        self.assertEqual(movie.country, "US")  # Ländercode in Großbuchstaben

    def test_required_fields(self):
        """Testet Pflichtfelder"""
        required_fields = ['title', 'release_date', 'runtime', 'director',
                           'poster_url', 'tmdb_id']

        for field in required_fields:
            # Temporär Feld entfernen
            invalid_data = self.valid_data.copy()
            del invalid_data[field]

            serializer = MovieSerializer(data=invalid_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn(field, serializer.errors)

    def test_invalid_runtime(self):
        """Testet ungültige Laufzeiten"""
        for value in [0, 1001]:
            invalid_data = self.valid_data.copy()
            invalid_data['runtime'] = value

            serializer = MovieSerializer(data=invalid_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn('runtime', serializer.errors)

            # Aktualisierte Assertion:
            self.assertIn('Laufzeit', serializer.errors['runtime'][0])

    def test_invalid_rating(self):
        """Testet ungültige Bewertungen"""
        for value in [-0.1, 10.1]:
            invalid_data = self.valid_data.copy()
            invalid_data['avg_rating'] = value

            serializer = MovieSerializer(data=invalid_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn('avg_rating', serializer.errors)

    def test_future_release_date(self):
        """Testet zukünftiges Release-Datum"""
        future_date = (timezone.now() + timedelta(days=365)).date().isoformat()
        invalid_data = self.valid_data.copy()
        invalid_data['release_date'] = future_date

        serializer = MovieSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('release_date', serializer.errors)
        self.assertIn('Zukunft', serializer.errors['release_date'][0])

    def test_invalid_country_code(self):
        """Testet ungültige Ländercodes"""
        for code in ['USA', 'X', '']:
            invalid_data = self.valid_data.copy()
            invalid_data['country'] = code

            serializer = MovieSerializer(data=invalid_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn('country', serializer.errors)

    def test_json_field_validation(self):
        """Testet Validierung von JSON-Feldern"""
        for field in ['cast', 'genres', 'keywords', 'composer']:
            # Falscher Typ (keine Liste)
            invalid_data = self.valid_data.copy()
            invalid_data[field] = "keine-liste"

            serializer = MovieSerializer(data=invalid_data)
            self.assertFalse(serializer.is_valid())
            self.assertIn(field, serializer.errors)
            self.assertIn('Liste', serializer.errors[field][0])

    def test_url_validation(self):
        """Testet URL-Validierung"""
        # Ungültiges Poster-Format
        invalid_data = self.valid_data.copy()
        invalid_data['poster_url'] = "https://example.com/poster.pdf"
        serializer = MovieSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('poster_url', serializer.errors)

        # Ungültiger Trailer-Host
        invalid_data = self.valid_data.copy()
        invalid_data['trailer_url'] = "https://example.com/trailer.mp4"
        serializer = MovieSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('trailer_url', serializer.errors)

    def test_tmdb_id_uniqueness(self):
        """Testet Eindeutigkeit der TMDB-ID"""
        # Erstes Objekt erstellen
        serializer1 = MovieSerializer(data=self.valid_data)
        serializer1.is_valid()
        serializer1.save()

        # Zweites Objekt mit gleicher TMDB-ID
        duplicate_data = self.valid_data.copy()
        duplicate_data['title'] = "Inception 2"
        serializer2 = MovieSerializer(data=duplicate_data)

        self.assertFalse(serializer2.is_valid())
        self.assertIn('tmdb_id', serializer2.errors)
        self.assertIn('existiert bereits', serializer2.errors['tmdb_id'][0])


class MovieViewTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.list_url = reverse('movie_list_create')
        self.valid_data = {
            "title": "The Shawshank Redemption",
            "original_title": "The Shawshank Redemption",
            "synopsis": "Two imprisoned men bond...",
            "tagline": "Fear can hold you prisoner. Hope can set you free.",
            "language": "English",
            "country": "US",
            "release_date": "1994-09-23",
            "runtime": 142,
            "director": "Frank Darabont",
            "cast": ["Tim Robbins", "Morgan Freeman"],
            "genres": ["Drama"],
            "keywords": ["prison", "hope"],
            "composer": ["Thomas Newman"],
            "poster_url": "https://example.com/shawshank.jpg",
            "backdrop_url": "https://example.com/shawshank-bg.jpg",
            "avg_rating": 9.3,
            "tmdb_id": 278
        }

        # Testfilm erstellen
        self.movie = Movie.objects.create(
            title="Inception",
            original_title="Inception",
            synopsis="A thief who steals corporate secrets...",
            tagline="Your mind is the scene of the crime",
            language="English",
            country="US",
            release_date="2010-07-16",
            runtime=148,
            director="Christopher Nolan",
            cast=["Leonardo DiCaprio", "Joseph Gordon-Levitt"],  # Fixed: Use list instead of JSON string
            genres=["Action", "Sci-Fi"],  # Fixed: Use list instead of JSON string
            keywords=["dream", "subconscious"],  # Fixed: Use list instead of JSON string
            composer=["Hans Zimmer"],  # Fixed: Use list instead of JSON string
            poster_url="https://example.com/inception.jpg",
            backdrop_url="https://example.com/inception-bg.jpg",
            avg_rating=8.8,
            tmdb_id=12345
        )
        self.detail_url = reverse('movie_detail', kwargs={'id': self.movie.id})

    # ===== LIST/CREATE VIEW TESTS =====
    def test_get_all_movies(self):
        """Testet GET /movies/ - Liste aller Filme"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Nur unser Testfilm

        # Prüfe, ob die Daten korrekt serialisiert wurden
        self.assertEqual(response.data[0]['title'], "Inception")
        self.assertEqual(response.data[0]['runtime'], 148)

    def test_create_movie_success(self):
        """Testet erfolgreiche Film-Erstellung via POST"""
        response = self.client.post(
            self.list_url,
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Movie.objects.count(), 2)  # Ursprünglicher + neuer Film

        # Prüfe Datenbankeintrag
        new_movie = Movie.objects.get(title="The Shawshank Redemption")
        self.assertEqual(new_movie.director, "Frank Darabont")
        self.assertEqual(new_movie.cast, ["Tim Robbins", "Morgan Freeman"])

    def test_create_movie_invalid_data(self):
        """Testet fehlgeschlagene Film-Erstellung"""
        invalid_data = self.valid_data.copy()
        invalid_data['title'] = ""  # Titel ist Pflichtfeld

        response = self.client.post(
            self.list_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        self.assertEqual(Movie.objects.count(), 1)  # Nur der ursprüngliche Film

    def test_create_movie_duplicate_tmdb_id(self):
        """Testet doppelte TMDB-ID"""
        duplicate_data = self.valid_data.copy()
        duplicate_data['tmdb_id'] = 12345  # Existiert bereits

        response = self.client.post(
            self.list_url,
            data=json.dumps(duplicate_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('tmdb_id', response.data)

    # ===== DETAIL VIEW TESTS =====
    def test_get_movie_detail(self):
        """Testet GET /movies/<id>/ - Einzelner Film"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Inception")
        self.assertEqual(response.data['runtime'], 148)

    def test_get_nonexistent_movie(self):
        """Testet Abfrage nicht existierender Film"""
        invalid_url = reverse('movie_detail', kwargs={'id': 9999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class MovieSearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test data once for the test class
        cls.movie_1 = Movie.objects.create(
            title="Star Chronicles",
            description="A space opera",
            genres="Sci-Fi",
            release_year=2021,
        )
        cls.movie_2 = Movie.objects.create(
            title="Love in the Sand",
            description="Romantic desert adventure",
            genres="Romance",
            release_year=2022,
        )
        cls.mock_search_results = [cls.movie_1, cls.movie_2]

    def setUp(self):
        # Patch the MovieDocument.search method for every test
        self.patcher = patch.object(MovieDocument, 'search')
        self.mock_search = self.patcher.start()

        # Return mocked results from Elasticsearch
        mock_result = MagicMock()
        mock_result.to_queryset.return_value = self.mock_search_results
        self.mock_search.return_value = mock_result

        # Patch Elasticsearch index methods to avoid network calls
        for method in ('create', 'delete', 'refresh', 'update'):
            patcher = patch.object(MovieDocument._index, method, lambda *args, **kwargs: None)
            patcher.start()
            self.addCleanup(patcher.stop)

        self.addCleanup(self.patcher.stop)

    def test_search_returns_mocked_results(self):
        url = reverse('movie_search')  # Make sure this name matches your urls.py
        response = self.client.get(url, {'q': 'space'})  # or whatever param you use

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.mock_search.called)

        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['title'], self.movie_1.title)
        self.assertEqual(data[1]['title'], self.movie_2.title)

    def test_empty_query_returns_all_mocked(self):
        url = reverse('movie_search')
        response = self.client.get(url, {'q': ''})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 2)
