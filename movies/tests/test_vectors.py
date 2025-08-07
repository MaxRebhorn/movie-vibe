import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from movies.models import Movie
from movies.services import vector_service
from movies.services.vector_service import save_embedding, COLLECTIONS
from movies.services.embed_service import embed_model


class VectorServiceMockTest(unittest.TestCase):

    # Update the test_vectors.py setUp method to mock COLLECTIONS
    def setUp(self):
        self.mock_client_patcher = patch('movies.services.vector_service.client')
        self.mock_client = self.mock_client_patcher.start()

        # Mock collections configuration
        self.collections_patcher = patch.dict(
            'movies.services.vector_service.COLLECTIONS',
            {
                'vibe': 'movies_vibe',
                'narrative': 'movies_narrative',
                'style': 'movies_style'
            }
        )
        self.collections_patcher.start()

        # Rest of the setup remains the same...
        self.mock_client.get_collections.return_value = MagicMock(collections=[])
        self.mock_client.recreate_collection.return_value = None
        self.mock_client.delete.return_value = None
        self.mock_client.search.return_value = []

    def tearDown(self):
        self.mock_client_patcher.stop()
        self.collections_patcher.stop()

    def create_movie(self, title, keywords):
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

    def test_embed_and_save(self):
        # Create test movie
        movie = self.create_movie("Magic School", ["magic", "school", "wizard"])

        # Get embeddings
        embeddings = embed_model(movie)

        # Test saving embeddings
        for vector_type, vector in embeddings.items():
            payload = {
                "movie_tmdb_id": movie.tmdb_id,
                "title": movie.title,
                "type": vector_type
            }
            save_embedding(vector, movie.tmdb_id, payload, vector_type)

            # Verify the mock was called
            self.mock_client.upsert.assert_called()


if __name__ == "__main__":
    unittest.main()