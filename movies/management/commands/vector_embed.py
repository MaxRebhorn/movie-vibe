from django.core.management.base import BaseCommand
from movies.models import Movie
from movies.services.vector_service import client, COLLECTION_NAME, embed_to_db
from qdrant_client.http import models as rest  # Import ergänzen

class Command(BaseCommand):
    help = "Embeddet alle Filme, die noch nicht in Qdrant vorhanden sind"

    def ensure_collection_exists(self):
        collections = client.get_collections().collections
        existing = {c.name for c in collections}
        if COLLECTION_NAME not in existing:
            self.stdout.write(f"📁 Collection '{COLLECTION_NAME}' nicht gefunden. Erstelle sie...")
            client.recreate_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=rest.VectorParams(
                    size=384,  # ← Je nach Dimension deines Embeddings
                    distance=rest.Distance.COSINE,
                )
            )
            self.stdout.write("✅ Collection erstellt.")

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("== Starte Embedding-Abgleich =="))
        self.ensure_collection_exists()
        total_movies = Movie.objects.count()
        self.stdout.write(f"🎞️  Filme in der relationalen Datenbank: {total_movies}")

        existing_ids = self.get_existing_movie_ids()
        self.stdout.write(f"📦 Filme bereits in Qdrant: {len(existing_ids)}")

        new_movies = Movie.objects.exclude(tmdb_id__in=existing_ids)

        self.stdout.write(f"🧠 Filme, die noch eingebettet werden müssen: {new_movies.count()}")
        self.stdout.write("")  # Leerzeile zur Lesbarkeit

        for i, movie in enumerate(new_movies, start=1):
            self.stdout.write(f"➡️  [{i}/{new_movies.count()}] Embedding: {movie.title} (TMDB ID: {movie.tmdb_id})")
            try:
                embed_to_db(movie)
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Fehler bei {movie.title}: {e}"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("✅ Embedding abgeschlossen."))

    def get_existing_movie_ids(self) -> set:
        self.stdout.write("🔍 Lade vorhandene Einträge aus Qdrant...")

        try:
            scroll = client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter={"must": [{"key": "type", "match": {"value": "vibe"}}]},
                limit=10000
            )
            result = {
                point.payload["movie_tmdb_id"]
                for point in scroll[0]
                if "movie_tmdb_id" in point.payload
            }
            self.stdout.write(f"📄 {len(result)} Punkte mit Typ 'vibe' gefunden.")
            return result
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Fehler beim Abfragen der Vector-Datenbank: {e}"))
            return set()
