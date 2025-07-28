# movies/management/commands/vector_generate.py

from django.core.management.base import BaseCommand
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from movies.models import Movie
from movies.services.embed_service import embed_model
from movies.services.vector_service import save_embedding
from django.conf import settings

VECTOR_SIZE = 384  # Adjust to your model's output size


class Command(BaseCommand):
    help = "Erzeugt Vektoren für alle Filme und speichert sie in Qdrant"

    def handle(self, *args, **options):
        client = QdrantClient(url="http://vektor:6333")

        # Get collection names from settings
        collections = settings.QDRANT_COLLECTIONS

        # Get existing collections from Qdrant
        existing_collections = [c.name for c in client.get_collections().collections]

        # Recreate collections if missing
        for collection_name in collections.values():
            if collection_name in existing_collections:
                self.stdout.write(self.style.WARNING(f"Collection '{collection_name}' bereits vorhanden."))
            else:
                client.recreate_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
                )
                self.stdout.write(self.style.SUCCESS(f"Collection '{collection_name}' erstellt."))

        # Loop through all movies
        for movie in Movie.objects.all():
            embeddings = embed_model(movie)  # embeddings dict with keys like 'vibe', 'narrative', etc.

            for key, embedding in embeddings.items():
                collection_key = collections.get(f"movies_{key}", collections.get(key))  # Try with prefix first

                if not collection_key:
                    self.stdout.write(self.style.ERROR(f"No collection configured for vector type '{key}'. Skipping..."))
                    continue

                payload = {
                    "title": movie.title,
                    "type": key,
                    "movie_id": movie.id,
                    "movie_tmdb_id": movie.tmdb_id,
                }
                save_embedding(embedding, movie.id, payload, collection_key)

        self.stdout.write(self.style.SUCCESS("Alle Filme erfolgreich eingebettet."))
