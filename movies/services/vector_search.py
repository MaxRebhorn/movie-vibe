# movies/services/vector_search.py

from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from django.conf import settings
import numpy as np

# Initialize Qdrant client using the URL from settings
client = QdrantClient(url=settings.QDRANT_URL)

# Collection mapping, e.g., {"vibe": "movie_vibe", ...}
COLLECTIONS = settings.QDRANT_COLLECTIONS

def _get_vector_for_movie(movie, vector_type: str) -> list[float] | None:
    """
    Fetch the vector for a specific movie and vector type from Qdrant.
    Uses `scroll()` because we are not doing similarity search here.
    """
    collection = COLLECTIONS.get(vector_type)
    if not collection:
        raise ValueError(f"No collection for vector type '{vector_type}'")

    result, _ = client.scroll(
        collection_name=collection,
        scroll_filter=Filter(
            must=[
                FieldCondition(key="movie_id", match=MatchValue(value=movie.id)),
                FieldCondition(key="type", match=MatchValue(value=vector_type)),
            ]
        ),
        limit=1
    )

    if not result:
        raise ValueError(f"No vector found for movie ID {movie.id} with type '{vector_type}'")

    return result[0].vector

def _get_combined_vector(movie, types=("vibe", "narrative", "style")):
    """
    Compute the mean of multiple vector types for a movie.
    Returns None if no vectors are found.
    """
    vectors = []
    for t in types:
        try:
            v = _get_vector_for_movie(movie, t)
            if v:
                vectors.append(np.array(v))
        except ValueError:
            continue  # Skip missing vectors
    if not vectors:
        return None
    return np.mean(vectors, axis=0).tolist()

def get_similar_movies(movie, vector_type="vibe", k=5) -> list[int]:
    """
    Search Qdrant for similar movies based on a vector.
    Returns a list of up to `k` movie IDs, excluding the query movie.
    """
    try:
        if vector_type == "all":
            query_vector = _get_combined_vector(movie)
            collection = COLLECTIONS.get("combined")
            type_filter = "combined"
        else:
            query_vector = _get_vector_for_movie(movie, vector_type)
            collection = COLLECTIONS.get(vector_type)
            type_filter = vector_type

        if not collection:
            raise ValueError(f"No collection defined for vector type '{vector_type}'")

    except ValueError as e:
        print(f"[ERROR] {e}")
        return []

    if not query_vector:
        return []

    results = client.search(
        collection_name=collection,
        query_vector=query_vector,
        query_filter=Filter(
            must=[FieldCondition(key="type", match=MatchValue(value=type_filter))]
        ),
        limit=k + 5  # Slight overfetch to exclude original movie
    )

    return [
        res.payload.get("movie_id")
        for res in results
        if res.payload.get("movie_id") != movie.id
    ][:k]
