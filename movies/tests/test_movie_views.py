from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
import json
from movies.models import Movie


class MovieViewTestCase(APITestCase):
    def setUp(self):
        self.list_url = reverse('movie_list_create')
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
            poster_url="https://example.com/inception.jpg",
            backdrop_url="https://example.com/inception-bg.jpg",
            avg_rating=8.8,
            tmdb_id=12345
        )
        self.detail_url = reverse('movie_detail', kwargs={'id': self.movie.id})
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

    def test_get_all_movies(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Inception")

    def test_create_movie_success(self):
        response = self.client.post(
            self.list_url,
            data=json.dumps(self.valid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Movie.objects.count(), 2)

    def test_get_movie_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Inception")

    def test_get_nonexistent_movie(self):
        invalid_url = reverse('movie_detail', kwargs={'id': 9999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_movie_invalid_data(self):
        invalid_data = self.valid_data.copy()
        invalid_data['title'] = ""

        response = self.client.post(
            self.list_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
