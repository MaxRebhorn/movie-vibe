# movies/services/vector_service.py

from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from django.conf import settings
import uuid
from qdrant_client.http.models import VectorParams, Distance

client = QdrantClient(url=settings.QDRANT_URL)
COLLECTIONS = settings.QDRANT_COLLECTIONS

def save_embedding(embedding: list[float], id: str, payload: dict, vector_type: str):
    collection = COLLECTIONS.get(vector_type)
    if not collection:
        raise ValueError(f"No collection configured for vector type '{vector_type}'")

    # Ensure collection exists
    existing_collections = [c.name for c in client.get_collections().collections]
    if collection not in existing_collections:
        print(f"Collection '{collection}' not found. Creating it now...")
        client.recreate_collection(
            collection_name=collection,
            vectors_config=VectorParams(
                size=len(embedding),
                distance=Distance.COSINE
            )
        )

    print(f"Saving vector to collection: {collection}")
    print(f"ID: {id}")
    print(f"Payload: {payload}")
    print(f"Vector length: {len(embedding)}")

    # Convert id to int if possible, else raise error or handle UUID
    try:
        point_id = int(id)
    except ValueError:
        # Try UUID or raise
        try:
            point_id = uuid.UUID(id)
        except ValueError:
            raise ValueError(f"Point id '{id}' is invalid. Must be int or UUID.")

    client.upsert(
        collection_name=collection,
        points=[{
            "id": point_id,
            "vector": embedding,
            "payload": payload
        }]
    )

