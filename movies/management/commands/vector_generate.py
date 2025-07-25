# movies/management/commands/vector_generate.py

from django.core.management.base import BaseCommand
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from movies.models import Movie
from movies.services.embed_service import embed_model
from movies.services.vector_service import save_embedding
import uuid
import numpy as np

COLLECTION_NAME = "movies"
VECTOR_SIZE = 384  # <- je nach deinem Modell anpassen!


class Command(BaseCommand):
    help = "Erzeugt Vektoren für alle Filme und speichert sie in Qdrant"

    def handle(self, *args, **options):
        client = QdrantClient(url="http://vektor:6333")

        # (Re)create collection
        existing_collections = [c.name for c in client.get_collections().collections]
        if COLLECTION_NAME in existing_collections:
            self.stdout.write(self.style.WARNING(f"Collection '{COLLECTION_NAME}' bereits vorhanden."))
        else:
            client.recreate_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )
            self.stdout.write(self.style.SUCCESS(f"Collection '{COLLECTION_NAME}' erstellt."))

        # Alle Filme durchgehen
        for movie in Movie.objects.all():
            embeddings = embed_model(movie)

            for key, embedding in embeddings.items():
                payload = {
                    "title": movie.title,
                    "type": key,
                    "movie_id": movie.id,
                    "movie_tmdb_id": movie.tmdb_id,
                }
                save_embedding(embedding, movie.id, payload, key)

        self.stdout.write(self.style.SUCCESS("Alle Filme erfolgreich eingebettet."))
