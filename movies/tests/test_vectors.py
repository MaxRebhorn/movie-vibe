import unittest
from datetime import datetime
from movies.models import Movie
from movies.services.vector_service import embed_to_db, client, COLLECTION_NAME
from movies.services.embed_service import embed_model
from qdrant_client.http.models import Filter, FieldCondition, MatchValue


class VectorServiceIntegrationTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Collection neu anlegen, falls nicht vorhanden
        if COLLECTION_NAME not in [c.name for c in client.get_collections().collections]:
            client.recreate_collection(
                collection_name=COLLECTION_NAME,
                vectors_config={"size": 384, "distance": "Cosine"}  # für all-MiniLM-L6-v2
            )

    def setUp(self):
        # Vor jedem Test alle Punkte löschen
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=Filter(must=[])
        )

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

    def test_embed_and_similarity_search(self):
        # Filme vorbereiten
        movie1 = self.create_movie("Magic School", ["magic", "school", "wizard"])
        movie2 = self.create_movie("Wizard Academy", ["wizard", "academy", "magic"])
        movie3 = self.create_movie("Space Battle", ["space", "battle", "aliens"])

        # Alle in DB einfügen
        embed_to_db(movie1)
        embed_to_db(movie2)
        embed_to_db(movie3)

        # Suche nach ähnlichen Vibes zu movie1
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
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=5,
            query_filter=filter_condition
        )

        # Treffer analysieren
        found_tmdb_ids = [hit.payload.get("movie_tmdb_id") for hit in search_results]

        # movie1 sollte der Top-Treffer sein
        self.assertEqual(found_tmdb_ids[0], movie1.tmdb_id)

        # movie2 sollte näher an movie1 liegen als movie3
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
