from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, ScoredPoint
from django.conf import settings
from typing import List, Dict, Tuple
import heapq

client = QdrantClient(url=settings.QDRANT_URL)

COLLECTIONS = ["movies_narrative", "movies_style", "movies_vibe"]


def get_vector(collection: str, point_id: int) -> List[float]:
    """
    Holt den Vektor zu einer gegebenen Punkt-ID aus Qdrant.
    """
    result = client.retrieve(
        collection_name=collection,
        ids=[point_id],
        with_vectors=True,
    )
    if not result:
        raise ValueError(f"No point with ID {point_id} in {collection}")
    return result[0].vector


def search_similar(collection: str, vector: List[float], limit: int, exclude_id: int) -> List[int]:
    """
    Führt eine Nearest Neighbor Search durch und gibt die ähnlichsten IDs zurück.
    Der Punkt mit exclude_id wird aus den Ergebnissen entfernt.
    """
    response: List[ScoredPoint] = client.search(
        collection_name=collection,
        query_vector=vector,
        limit=limit + 1,  # einen mehr holen, damit wir exclude_id rauswerfen können
    )
    ids = [pt.id for pt in response if pt.id != exclude_id][:limit]
    return ids


def get_similar_movies(movie_id: int, limit: int, collection: str) -> List[int]:
    """
    Kombiniert get_vector() und search_similar(), um ähnliche Filme zu finden.
    """
    vector = get_vector(collection, movie_id)
    return search_similar(collection, vector, limit, exclude_id=movie_id)


def search_across_collections(
    query_vector: List[float],
    limit: int,
    exclude_id: int = None,
    weight_map: Dict[str, float] = None
) -> List[Tuple[int, float]]:
    """
    Search across all collections and merge results into a single ranked list.
    :param query_vector: vector to search with
    :param limit: number of results to return
    :param exclude_id: optional ID to exclude
    :param weight_map: optional dict to weight collections, e.g. {"movies_style": 2.0}
    :return: List of (id, score) sorted by best match
    """
    if weight_map is None:
        weight_map = {c: 1.0 for c in COLLECTIONS}

    combined_scores: Dict[int, float] = {}

    for collection in COLLECTIONS:
        results: List[ScoredPoint] = client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=limit * 2,  # etwas mehr holen, da wir mergen
        )

        for r in results:
            if exclude_id is not None and r.id == exclude_id:
                continue
            weighted_score = r.score * weight_map.get(collection, 1.0)
            combined_scores[r.id] = combined_scores.get(r.id, 0.0) + weighted_score

    # sortieren nach Score
    top_results = heapq.nlargest(limit, combined_scores.items(), key=lambda x: x[1])
    return top_results


def get_similar_movies_across(movie_id: int, limit: int) -> List[int]:
    """
    Gets vector from the narrative collection and searches across all collections.
    Returns top similar movie IDs.
    """
    base_vector = client.retrieve(
        collection_name="movies_narrative",
        ids=[movie_id],
        with_vectors=True,
    )
    if not base_vector:
        raise ValueError(f"Movie ID {movie_id} not found in movies_narrative")

    vector = base_vector[0].vector
    merged = search_across_collections(vector, limit, exclude_id=movie_id)

    return [mid for mid, score in merged]
