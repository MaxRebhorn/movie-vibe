import os
import unittest
from datetime import datetime
from unittest import skipIf
from django.conf import settings
from qdrant_client.http.models import Filter, FieldCondition, MatchValue, VectorParams, Distance


@skipIf(os.getenv("SKIP_HEAVY_TESTS") == "1", "Skip heavy tests in CI")
class VectorServiceIntegrationTest(unittest.TestCase):
    COLLECTION_NAME = settings.QDRANT_COLLECTIONS["movies_vibe"]

    @classmethod
    def setUpClass(cls):
        # Import Qdrant client only after skip check
        from movies.services.vector_service import client

        # Create collection if it doesn't exist
        existing_collections = [c.name for c in client.get_collections().collections]
        if cls.COLLECTION_NAME not in existing_collections:
            client.recreate_collection(
                collection_name=cls.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=384,  # for all-MiniLM-L6-v2
                    distance=Distance.COSINE
                )
            )

    def setUp(self):
        from movies.services.vector_service import client
        # Delete all points before each test
        client.delete(
            collection_name=self.COLLECTION_NAME,
            points_selector=Filter(must=[])
        )

    def create_movie(self, title, keywords):
        from movies.models import Movie
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

    def embed_to_db(self, movie):
        from movies.services.embed_service import embed_model
        from movies.services.vector_service import save_embedding

        embeddings = embed_model(movie)
        payload = {
            "movie_tmdb_id": movie.tmdb_id,
            "title": movie.title,
            "type": "vibe"
        }
        save_embedding(embeddings["vibe"], movie.tmdb_id, payload, "movies_vibe")

    def test_embed_and_similarity_search(self):
        # Import heavy dependencies only when needed
        from movies.services.embed_service import embed_model
        from movies.services.vector_service import client

        # Prepare movies
        movie1 = self.create_movie("Magic School", ["magic", "school", "wizard"])
        movie2 = self.create_movie("Wizard Academy", ["wizard", "academy", "magic"])
        movie3 = self.create_movie("Space Battle", ["space", "battle", "aliens"])

        # Insert all into DB
        self.embed_to_db(movie1)
        self.embed_to_db(movie2)
        self.embed_to_db(movie3)

        # Search for similar vibes to movie1
        embeddings = embed_model(movie1)
        query_vector = embeddings["vibe"]

        filter_condition = Filter(
            must=[
                FieldCondition(
                    key="type",
                    match=MatchValue(value="vibe")
                )
            ]
        )

        search_results = client.search(
            collection_name=self.COLLECTION_NAME,
            query_vector=query_vector,
            limit=5,
            query_filter=filter_condition
        )

        # Analyze results
        found_tmdb_ids = [hit.payload.get("movie_tmdb_id") for hit in search_results]

        # movie1 should be the top result
        self.assertEqual(found_tmdb_ids[0], movie1.tmdb_id)

        # movie2 should be closer to movie1 than movie3
        try:
            pos2 = found_tmdb_ids.index(movie2.tmdb_id)
        except ValueError:
            pos2 = -1
        try:
            pos3 = found_tmdb_ids.index(movie3.tmdb_id)
        except ValueError:
            pos3 = -1

        self.assertTrue(
            (0 <= pos2 < pos3) or (pos3 == -1),
            f"Expected movie2 (tmdb_id={movie2.tmdb_id}) to be closer than movie3 (tmdb_id={movie3.tmdb_id})"
        )


if __name__ == "__main__":
    unittest.main()