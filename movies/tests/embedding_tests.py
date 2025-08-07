import os
from unittest import skipIf

from django.test import TestCase
from unittest.mock import patch
from datetime import datetime
from movies.models import Movie
from movies.services.embed_service import embed_data, embed_model




@skipIf(os.getenv("SKIP_HEAVY_TESTS") == "1", "Skip heavy tests in CI")
class EmbeddingTests(TestCase):

    @patch("movies.services.embed_service.model.encode")
    def test_embed_data_with_mixed_input(self, mock_encode):
        mock_encode.return_value = [0.1, 0.2, 0.3]

        result = embed_data([
            "Hello world",
            ["tag1", "tag2"],
            datetime(2020, 1, 1)
        ])

        expected_input = "Hello world tag1 tag2 2020-01-01 00:00:00"
        mock_encode.assert_called_once_with(expected_input)
        self.assertEqual(result, [0.1, 0.2, 0.3])

    @patch("movies.services.embed_service.embed_data")
    def test_embed_model(self, mock_embed_data):
        mock_embed_data.side_effect = [
            [0.1, 0.1, 0.1],  # vibe embedding
            [0.2, 0.2, 0.2],  # narrative embedding
            [0.3, 0.3, 0.3],  # style embedding
        ]

        movie = Movie(
            title="Test Movie",
            original_title="Test Movie Original",
            synopsis="A thrilling movie.",
            plot="An orphan becomes a wizard.",
            tagline="Magic begins here.",
            language="en",
            country="US",
            release_date=datetime(2001, 11, 16),
            runtime=152,
            director="John Doe",
            cast=["Actor A", "Actor B"],
            genres=["Fantasy", "Adventure"],
            keywords=["magic", "school"],
            composer=["Composer A"],
            poster_url="http://example.com/poster.jpg",
            backdrop_url="http://example.com/backdrop.jpg",
            trailer_url="http://example.com/trailer.mp4",
            avg_rating=8.5,
            tmdb_id=123456,
        )

        result = embed_model(movie)

        self.assertEqual(result["vibe"], [0.1, 0.1, 0.1])
        self.assertEqual(result["narrative"], [0.2, 0.2, 0.2])
        self.assertEqual(result["style"], [0.3, 0.3, 0.3])
