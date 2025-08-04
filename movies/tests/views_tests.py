from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch
from movies.models import Movie
from qdrant_client.http.exceptions import UnexpectedResponse
import json

class MovieListCreateViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('movie_list_create')
        self.movie_data = {
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
            "trailer_url": "https://youtube.com/trailer.mp4",
            "avg_rating": 8.8,
            "tmdb_id": 12345
        }

    def test_get_empty_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_create_movie_success(self):
        response = self.client.post(
            self.url,
            data=json.dumps(self.movie_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Movie.objects.count(), 1)

    def test_create_movie_invalid_data(self):
        invalid_data = self.movie_data.copy()
        invalid_data['title'] = ''
        response = self.client.post(
            self.url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_list_movies(self):
        Movie.objects.create(**{
            k: v for k, v in self.movie_data.items()
            if k not in ['cast', 'genres', 'keywords', 'composer']
        })
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class MovieDetailViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
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
            cast=["Leonardo DiCaprio", "Joseph Gordon-Levitt"],
            genres=["Action", "Sci-Fi"],
            keywords=["dream", "subconscious"],
            composer=["Hans Zimmer"],
            poster_url="https://example.com/poster.jpg",
            backdrop_url="https://example.com/backdrop.jpg",
            trailer_url="https://youtube.com/trailer.mp4",
            avg_rating=8.8,
            tmdb_id=12345
        )
        self.url = reverse('movie_detail', kwargs={'id': self.movie.id})

    @patch('movies.views.get_similar_movies')
    def test_get_similar_movies_success(self, mock_get_similar):
        mock_get_similar.return_value = [self.movie.id]
        response = self.client.get(self.url, {'id': str(self.movie.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    @patch('movies.views.get_similar_movies')
    def test_get_similar_movies_failure(self, mock_get_similar):
        mock_get_similar.side_effect = UnexpectedResponse("Qdrant error")
        response = self.client.get(self.url, {'id': str(self.movie.id)})
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_get_similar_movies_missing_id(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class MovieSearchViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('movie_search')
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
            cast=["Leonardo DiCaprio", "Joseph Gordon-Levitt"],
            genres=["Action", "Sci-Fi"],
            keywords=["dream", "subconscious"],
            composer=["Hans Zimmer"],
            poster_url="https://example.com/poster.jpg",
            backdrop_url="https://example.com/backdrop.jpg",
            trailer_url="https://youtube.com/trailer.mp4",
            avg_rating=8.8,
            tmdb_id=12345
        )

    @patch('movies.views.MovieSearchService.search')
    def test_search_success(self, mock_search):
        mock_search.return_value = []
        response = self.client.get(self.url, {'q': 'inception'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_empty_query(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])