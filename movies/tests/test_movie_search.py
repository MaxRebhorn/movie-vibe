from unittest.mock import MagicMock, patch
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from movies.models import Movie


class MovieSearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.movie_1 = Movie.objects.create(
            title="Star Chronicles",
            original_title="Star Chronicles",
            synopsis="A space opera",
            tagline="In space no one can hear you scream",
            language="English",
            country="US",
            release_date="2021-01-01",
            runtime=120,
            director="John Director",
            cast=["Actor 1", "Actor 2"],
            genres=["Sci-Fi"],
            keywords=["space", "future"],
            composer=["Composer 1"],
            poster_url="https://example.com/poster1.jpg",
            backdrop_url="https://example.com/backdrop1.jpg",
            avg_rating=8.0,
            tmdb_id=12346
        )

        cls.movie_2 = Movie.objects.create(
            title="Love in the Sand",
            original_title="Love in the Sand",
            synopsis="Romantic desert adventure",
            tagline="Love finds a way",
            language="English",
            country="US",
            release_date="2022-01-01",
            runtime=110,
            director="Jane Director",
            cast=["Actor 3", "Actor 4"],
            genres=["Romance"],
            keywords=["desert", "love"],
            composer=["Composer 2"],
            poster_url="https://example.com/poster2.jpg",
            backdrop_url="https://example.com/backdrop2.jpg",
            avg_rating=7.5,
            tmdb_id=12347
        )

    def setUp(self):
        # Patch the MovieSearchService.search method
        self.search_patcher = patch('movies.services.movie_search.MovieSearchService.search')
        self.mock_search_method = self.search_patcher.start()

        # Create mock hits that simulate search results
        mock_hit_1 = MagicMock()
        mock_hit_1.meta.id = str(self.movie_1.id)

        mock_hit_2 = MagicMock()
        mock_hit_2.meta.id = str(self.movie_2.id)

        # Simulate .execute() returning mock hits
        mock_search_response = MagicMock()
        mock_search_response.execute.return_value = [mock_hit_1, mock_hit_2]
        self.mock_search_method.return_value = mock_search_response

    def tearDown(self):
        self.search_patcher.stop()

    def test_search_returns_mocked_results(self):
        url = reverse('movie_search')
        response = self.client.get(url, {'q': 'space'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.mock_search_method.called)

        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['title'], self.movie_1.title)
        self.assertEqual(data[1]['title'], self.movie_2.title)

    def test_empty_query_returns_empty_list(self):
        url = reverse('movie_search')
        response = self.client.get(url, {'q': ''})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])

    def test_search_with_no_results(self):
        # Return empty list for execute
        self.mock_search_method.return_value.execute.return_value = []

        url = reverse('movie_search')
        response = self.client.get(url, {'q': 'nonexistent'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)
