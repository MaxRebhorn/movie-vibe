import os
from django.core.management.base import BaseCommand
from django.conf import settings
from movies.models import Movie
from qdrant_client import QdrantClient
from qdrant_client.http import models
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import umap.umap_ as umap
import requests
from PIL import Image
import io


class Command(BaseCommand):
    help = "Visualize a movie and its 10 nearest neighbors on a 2D map"

    def add_arguments(self, parser):
        parser.add_argument("movie_id", type=int, help="ID of the movie")

    def handle(self, *args, **options):
        movie_id = options["movie_id"]

        # --- Step 1: Movie laden ---
        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Movie {movie_id} not found"))
            return

        self.stdout.write(self.style.SUCCESS(f"Querying neighbors for: {movie.title}"))

        # --- Step 2: Qdrant Client ---
        client = QdrantClient(url=settings.QDRANT_URL)

        collections_to_try = [
            "movies_combined",
            "movies_vibe",
            "movies_narrative",
            "movies_style",
        ]

        query_vec = None
        found_collection = None

        for collection in collections_to_try:
            for test_id in (str(movie_id), movie_id):
                try:
                    query_point = client.retrieve(
                        collection_name=collection,
                        ids=[test_id],
                        with_vectors=True,
                    )
                    if query_point:
                        query_vec = query_point[0].vector
                        found_collection = collection
                        self.stdout.write(
                            self.style.SUCCESS(f"Found movie in collection: {collection}")
                        )
                        break
                except Exception:
                    continue
            if query_vec:
                break

        if not query_vec:
            self.stdout.write(self.style.ERROR(f"No embedding found in Qdrant for {movie.title}"))
            try:
                collections = client.get_collections()
                self.stdout.write(f"Available collections: {[c.name for c in collections.collections]}")
            except Exception as e:
                self.stdout.write(f"Error getting collections: {e}")
            return

        # --- Step 3: Nearest Neighbors suchen ---
        search_result = client.search(
            collection_name=found_collection,
            query_vector=query_vec,
            limit=11,
            with_payload=True,
            with_vectors=True,
        )

        # --- Step 4: Embeddings + Poster sammeln ---
        ids = [movie.id]
        titles = [movie.title]
        posters = [movie.poster_url]
        vectors = [np.array(query_vec)]

        for hit in search_result:
            if (hasattr(hit, "id") and (hit.id == movie_id or hit.id == str(movie_id))):
                continue

            neighbor_id = None
            if hasattr(hit, "payload") and hit.payload:
                if "movie_id" in hit.payload:
                    neighbor_id = int(hit.payload["movie_id"])
                elif "id" in hit.payload:
                    neighbor_id = int(hit.payload["id"])
            elif hasattr(hit, "id"):
                try:
                    neighbor_id = int(hit.id)
                except (ValueError, TypeError):
                    continue

            if neighbor_id and neighbor_id != movie_id:
                try:
                    neighbor = Movie.objects.get(id=neighbor_id)
                    ids.append(neighbor.id)
                    titles.append(neighbor.title)
                    posters.append(neighbor.poster_url)
                    vectors.append(
                        np.array(hit.vector)
                        if hasattr(hit, "vector") and hit.vector
                        else np.zeros_like(query_vec)
                    )
                except Movie.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Movie with ID {neighbor_id} not found in DB"))
                    continue

        if len(vectors) < 2:
            self.stdout.write(self.style.ERROR("Not enough vectors for UMAP reduction"))
            return

        # --- Step 5: UMAP ---
        reducer = umap.UMAP(n_neighbors=min(5, len(vectors) - 1), min_dist=0.3, random_state=42)
        coords = reducer.fit_transform(vectors)

        # --- Step 6: Plot ---
        fig, ax = plt.subplots(figsize=(14, 12))
        ax.set_title(f"Movie Map for '{movie.title}'", fontsize=18, pad=20)
        ax.set_axis_off()

        for (x, y), title, poster in zip(coords, titles, posters):
            try:
                if poster and poster.startswith("http"):
                    headers = {
                        "User-Agent": "Mozilla/5.0"
                    }
                    response = requests.get(poster, headers=headers, timeout=10)
                    response.raise_for_status()
                    img = Image.open(io.BytesIO(response.content)).convert("RGB")
                    img = np.array(img)  # ✅ convert to numpy array for OffsetImage
                else:
                    raise ValueError("No valid poster URL")

                imagebox = OffsetImage(img, zoom=0.18)
                ab = AnnotationBbox(imagebox, (x, y), frameon=False, pad=0)
                ax.add_artist(ab)

                ax.text(
                    x,
                    y - 0.9,
                    title,
                    fontsize=10,
                    ha="center",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9),
                )
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Could not load poster for {title}: {e}"))
                ax.text(
                    x,
                    y,
                    title,
                    fontsize=9,
                    ha="center",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                )

        # --- Step 7: Save PNG ---
        output_dir = os.path.join(settings.MEDIA_ROOT, "plots")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"movie_{movie.id}.png")
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close()

        self.stdout.write(self.style.SUCCESS(f"Plot saved to {output_file}"))
