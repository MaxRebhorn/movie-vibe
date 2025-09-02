from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from django.conf import settings

client = QdrantClient(url=settings.QDRANT_URL)


def get_collection_name(vector_type):
    """Map vector type to collection name based on current QDRANT_COLLECTIONS structure"""
    collection_mapping = {
        'vibe': settings.QDRANT_COLLECTIONS.get("movies_vibe", "movies_vibe"),
        'narrative': settings.QDRANT_COLLECTIONS.get("movies_narrative", "movies_narrative"),
        'style': settings.QDRANT_COLLECTIONS.get("movies_style", "movies_style"),
    }
    return collection_mapping.get(vector_type)


def update_weighted_embedding(new_embedding: list[float], movie_id: int, payload: dict, vector_type: str, user_level: int):
    """
    Update a single vector type in Qdrant with weighting, then save combined VectorHistory.
    """
    if not new_embedding:
        print(f"⚠️ Skipping {vector_type} update for movie {movie_id}: new_embedding is empty or None")
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
                size=len(new_embedding),
                distance=Distance.COSINE
            )
        )

    # Retrieve existing vector
    existing_points = client.retrieve(collection_name=collection, ids=[movie_id])
    if existing_points and len(existing_points) > 0 and existing_points[0].vector:
        existing_vector = existing_points[0].vector
        existing_payload = existing_points[0].payload or {}

        weight = min(user_level / 100, 1.0)
        if len(existing_vector) != len(new_embedding):
            print(f"⚠️ Vector size mismatch for movie {movie_id}. Using new embedding.")
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
            points=[PointStruct(id=movie_id, vector=merged_vector, payload=updated_payload)]
        )
        print(f"✅ Merged {vector_type} embedding for movie {movie_id}")
    else:
        # First vector for this movie
        client.upsert(
            collection_name=collection,
            wait=True,
            points=[PointStruct(id=movie_id, vector=new_embedding, payload=payload)]
        )
        print(f"✅ Created new {vector_type} embedding for movie {movie_id}")

    # After updating, create combined vector history snapshot
    create_combined_vector_history(movie_id, payload.get('review_id'))


def remove_review_influence(review, movie_id):
    """
    Remove the influence of a specific review from the vector store, then save combined VectorHistory.
    """
    print(f"🔍 remove_review_influence called for movie {movie_id}, review {review.id}")

    for vector_type in ['vibe', 'narrative', 'style']:
        embedding = getattr(review, f'{vector_type}_embedding', None)
        if not embedding:
            print(f"⚠️ No {vector_type} embedding found for review {review.id}")
            continue

        collection = get_collection_name(vector_type)
        if not collection:
            print(f"⚠️ No collection found for vector type {vector_type}")
            continue

        existing_points = client.retrieve(collection_name=collection, ids=[movie_id])
        if existing_points and len(existing_points) > 0 and existing_points[0].vector:
            existing_vector = existing_points[0].vector
            existing_payload = existing_points[0].payload or {}

            user_level = getattr(review, 'user_level_at_review', 0)
            weight = min(user_level / 100, 1.0)

            if len(existing_vector) == len(embedding):
                if 0 < weight < 1:
                    new_vector = [
                        (existing_vector[i] - embedding[i] * weight) / (1 - weight)
                        for i in range(len(existing_vector))
                    ]
                elif weight == 1:
                    new_vector = [0] * len(existing_vector)
                else:
                    new_vector = existing_vector

                client.upsert(
                    collection_name=collection,
                    wait=True,
                    points=[PointStruct(id=movie_id, vector=new_vector, payload=existing_payload)]
                )
                print(f"✅ Removed {vector_type} influence for movie {movie_id}")
        else:
            print(f"⚠️ No existing vector found for {vector_type} in movie {movie_id}")

    # Create combined vector history after removal
    print("📝 Creating combined vector history for removal")
    create_combined_vector_history(movie_id, review.id, change_source='review_removal')


def create_combined_vector_history(movie_id, source_id=None, change_source='review'):
    """
    Save a snapshot of all three vectors in one VectorHistory row.
    """
    from review.models import VectorHistory

    print(f"📝 Creating VectorHistory for movie {movie_id}, source {source_id}, change_source {change_source}")

    current_vectors = {}
    for vt in ['vibe', 'narrative', 'style']:
        points = client.retrieve(collection_name=get_collection_name(vt), ids=[movie_id])
        current_vectors[vt] = points[0].vector if points and points[0].vector else None
        print(f"   {vt} vector: {'found' if current_vectors[vt] is not None else 'not found'}")

    try:
        VectorHistory.objects.create(
            movie_id=movie_id,
            vibe_vector=current_vectors['vibe'],
            narrative_vector=current_vectors['narrative'],
            style_vector=current_vectors['style'],
            source_id=source_id,
            change_source=change_source,
            description=f"Snapshot of all vectors for movie {movie_id}"
        )
        print(f"✅ VectorHistory created successfully for movie {movie_id}")
    except Exception as e:
        print(f"❌ Failed to create VectorHistory: {e}")


def get_vector_history(movie_id, limit=10):
    """
    Retrieve combined vector history for a movie.
    """
    from review.models import VectorHistory
    return VectorHistory.objects.filter(movie_id=movie_id).order_by('-created_at')[:limit]