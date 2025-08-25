from django.test import TestCase
from unittest.mock import patch, MagicMock
from datetime import datetime
from movies.models import Movie
from movies.services.vector_service import save_embedding

# Patch the Qdrant client and COLLECTIONS for all tests
@patch.dict(
    'movies.services.vector_service.COLLECTIONS',
    {
        'vibe': 'movies_vibe',
        'narrative': 'movies_narrative',
        'style': 'movies_style'
    }
)
@patch('movies.services.vector_service.client')
@patch('movies.services.embed_service.embed_model')
class VectorServiceMockTest(TestCase):

    def create_movie(self, title, keywords):
        """Helper to create a Movie instance for tests"""
        return Movie(
            title=title,
            original_title=title,
            synopsis="",
            plot="",
            tagline="",
            language="en",
            country="US",
            release_date=datetime(2020, 1, 1),
            runtime=120,
            director="Director",
            cast=[],
            genres=[],
            keywords=keywords,
            composer=[],
            poster_url="",
            backdrop_url="",
            trailer_url="",
            avg_rating=5.0,
            tmdb_id=hash(title) % 1000000
        )

    def test_embed_and_save(self, mock_embed_model, mock_qdrant_client):
        """Test embedding and saving vectors with mocks"""

        # Mock embeddings to avoid calling sentence-transformers
        mock_embed_model.return_value = {
            "vibe": [0.1, 0.2, 0.3],
            "narrative": [0.4, 0.5, 0.6],
            "style": [0.7, 0.8, 0.9]
        }

        # Mock Qdrant client methods
        mock_qdrant_client.upsert = MagicMock()
        # Return an object with a 'collections' attribute
        mock_get_collections = MagicMock()
        mock_get_collections.collections = []
        mock_qdrant_client.get_collections = MagicMock(return_value=mock_get_collections)

        mock_qdrant_client.recreate_collection = MagicMock()
        mock_qdrant_client.delete = MagicMock()
        mock_qdrant_client.search = MagicMock(return_value=[])

        # Create a test movie
        movie = self.create_movie("Magic School", ["magic", "school", "wizard"])

        # Get embeddings (mocked)
        embeddings = mock_embed_model(movie)

        # Test saving embeddings
        for vector_type, vector in embeddings.items():
            payload = {
                "movie_tmdb_id": movie.tmdb_id,
                "title": movie.title,
                "type": vector_type
            }
            save_embedding(vector, movie.tmdb_id, payload, vector_type)

            # Verify upsert was called
            mock_qdrant_client.upsert.assert_called()
