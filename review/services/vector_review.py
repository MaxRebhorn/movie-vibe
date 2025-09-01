# movies/services/vector_service.py

from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue, PointStruct
from django.conf import settings
import uuid
from qdrant_client.http.models import VectorParams, Distance

client = QdrantClient(url=settings.QDRANT_URL)

# Create a mapping from vector_type to collection name based on your settings structure
def get_collection_name(vector_type):
    """Map vector type to collection name based on current QDRANT_COLLECTIONS structure"""
    collection_mapping = {
        'vibe': settings.QDRANT_COLLECTIONS.get("movies_vibe", "movies_vibe"),
        'narrative': settings.QDRANT_COLLECTIONS.get("movies_narrative", "movies_narrative"),
        'style': settings.QDRANT_COLLECTIONS.get("movies_style", "movies_style"),
    }
    return collection_mapping.get(vector_type)

# Replace the update_weighted_embedding function with this version
def update_weighted_embedding(new_embedding: list[float], id: int, payload: dict, vector_type: str, user_level: int):
    if not new_embedding:
        print(f"⚠️ Skipping {vector_type} update for movie {id}: new_embedding is empty or None")
        return

    collection = get_collection_name(vector_type)
    if not collection:
        raise ValueError(f"No collection configured for vector type '{vector_type}'")

    # Ensure collection exists
    existing_collections = [c.name for c in client.get_collections().collections]
    if collection not in existing_collections:
        print(f"Collection '{collection}' not found. Creating it now...")
        client.recreate_collection(
            collection_name=collection,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE
            )
        )

    # Try to retrieve existing vector
    existing_points = client.retrieve(collection_name=collection, ids=[id])
    if existing_points and len(existing_points) > 0 and existing_points[0].vector:
        existing_vector = existing_points[0].vector
        existing_payload = existing_points[0].payload or {}

        weight = min(user_level / 100, 1.0)
        if len(existing_vector) != len(new_embedding):
            print(f"⚠️ Vector size mismatch for movie {id}. Skipping merge, using new embedding.")
            merged_vector = new_embedding
        else:
            merged_vector = [
                existing_vector[i] * (1 - weight) + new_embedding[i] * weight
                for i in range(len(new_embedding))
            ]

        updated_payload = {**existing_payload, **payload}

        client.upsert(
            collection_name=collection,
            wait=True,
            points=[PointStruct(id=id, vector=merged_vector, payload=updated_payload)]
        )
        print(f"✅ Merged {vector_type} embedding for movie {id}")
    else:
        # First vector for this movie
        client.upsert(
            collection_name=collection,
            wait=True,
            points=[PointStruct(id=id, vector=new_embedding, payload=payload)]
        )
        print(f"✅ Created new {vector_type} embedding for movie {id}")
