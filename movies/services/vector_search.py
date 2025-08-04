import requests
from typing import List, Dict
from django.conf import settings
from qdrant_client import QdrantClient, models

COLLECTIONS = {
    "vibe": settings.QDRANT_COLLECTIONS["movies_vibe"],
    "narrative": settings.QDRANT_COLLECTIONS["movies_narrative"],
    "style": settings.QDRANT_COLLECTIONS["movies_style"],
}

QDRANT_URL = settings.QDRANT_URL  # e.g. "http://localhost:6333"
client = QdrantClient(url=settings.QDRANT_URL)
def get_vector_from_qdrant(collection: str, point_id: int) -> List[float]:
    url = f"{QDRANT_URL}/collections/{collection}/points/scroll"
    payload = {
        "filter": {
            "must": [
                {"key": "id", "match": {"value": point_id}}
            ]
        },
        "limit": 1,
        "with_vector": True,
        "with_payload": False
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    data = response.json()

    points = data.get("result", {}).get("points", [])
    if not points:
        raise ValueError(f"No point with ID {point_id} in collection {collection}.")
    vector = points[0].get("vector")
    if not vector:
        raise ValueError(f"No vector for point {point_id} in collection {collection}.")
    return vector

def search_similar(collection: str, vector: List[float], limit: int, exclude_id: int) -> List[int]:
    url = f"{QDRANT_URL}/collections/{collection}/points/search"
    payload = {
        "vector": vector,
        "limit": limit + 1,
        "with_payload": False,
        "with_vector": False,
        "filter": {
            "must_not": [
                {"key": "id", "match": {"value": exclude_id}}
            ]
        }
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    data = response.json()

    points = data.get("result", [])
    filtered_ids = [pt["id"] for pt in points][:limit]
    return filtered_ids

def get_similar_movies(movie_id: int, limit: int,collection:str):
    return unpack_movies(client.query_points(
        collection_name=collection,
        query=movie_id,  # <--- point id
        limit=limit
    )
    )

def unpack_movies(response):
    return [point.payload["movie_id"] for point in response.points]