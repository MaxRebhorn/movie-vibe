import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from movies.models import Movie
from movies.services.vector_service import save_embedding


class VectorServiceMockTest(unittest.TestCase):

    def setUp(self):
        # Mock the Qdrant client
        self.mock_client_patcher = patch('movies.services.vector_service.client')
        self.mock_client = self.mock_client_patcher.start()

        # Mock collections config
        self.collections_patcher = patch.dict(
            'movies.services.vector_service.COLLECTIONS',
            {
                'vibe': 'movies_vibe',
                'narrative': 'movies_narrative',
                'style': 'movies_style'
            }
        )
        self.collections_patcher.start()

        # Mock Qdrant client methods
        mock_collection = MagicMock()
        mock_collection.name = "movies_vibe"
        self.mock_client.get_collections.return_value = MagicMock(collections=[mock_collection])
        self.mock_client.recreate_collection.return_value = None
        self.mock_client.delete.return_value = None
        self.mock_client.search.return_value = []
        self.mock_client.upsert.return_value = None

        # Patch embed_model so we don’t load SentenceTransformer
        self.embed_patcher = patch('movies.services.embed_service.embed_model')
        self.mock_embed_model = self.embed_patcher.start()
        self.mock_embed_model.return_value = {
            'vibe': [0.1, 0.2, 0.3],
            'narrative': [0.4, 0.5, 0.6],
            'style': [0.7, 0.8, 0.9]
        }

    def tearDown(self):
        self.mock_client_patcher.stop()
        self.collections_patcher.stop()
        self.embed_patcher.stop()

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
        movie = self.create_movie("Magic School", ["magic", "school", "wizard"])

        # use mocked embed_model (fast, no transformer load)
        embeddings = self.mock_embed_model(movie)

        for vector_type, vector in embeddings.items():
            payload = {
                "movie_tmdb_id": movie.tmdb_id,
                "title": movie.title,
                "type": vector_type
            }
            save_embedding(vector, movie.tmdb_id, payload, vector_type)

        # Verify client.upsert was called
        self.assertTrue(self.mock_client.upsert.called)


if __name__ == "__main__":
    unittest.main()
