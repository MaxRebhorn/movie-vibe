# movies/diagnostics/database_check.py
from django.conf import settings
from qdrant_client import QdrantClient

from movies.models import Movie
from movies.services.vector_service import COLLECTIONS
from qdrant_client.http import models as qmodels
from django.db import connection

def run_diagnostics(movie_id=45):
    print("\n" + "="*60)
    print("🔍 MOVIE DATABASE DIAGNOSTICS")
    print("="*60)

    # --- Step 1: Check Django DB Connection + Movie by ID ---
    print("\n🔍 Step 1: Checking Django DB and Movie")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Django DB connection: OK")
    except Exception as e:
        print(f"❌ Django DB connection failed: {e}")
        return

    try:
        movie = Movie.objects.get(id=movie_id)
        print(f"✅ Movie ID {movie_id} found: '{movie.title}' ({movie.release_date})")
    except Movie.DoesNotExist:
        print(f"❌ Movie ID {movie_id} not found.")
        return

    total_movies = Movie.objects.count()
    print(f"📊 Total movies in relational DB: {total_movies}")

    # --- Step 2: Connect to Qdrant ---
    print("\n🔍 Step 2: Connecting to Qdrant and Checking Collections")
    client = QdrantClient(url=settings.QDRANT_URL)

    try:
        qdrant_collections = client.get_collections().collections
        existing_collections = [c.name for c in qdrant_collections]
        print(f"✅ Qdrant connected. Available collections: {existing_collections}")
    except Exception as e:
        print(f"❌ Qdrant connection failed: {e}")
        return

    # --- Step 3: Check presence of vectors & payloads ---
    for vector_key, collection_name in COLLECTIONS.items():
        print(f"\n🔎 Checking collection '{vector_key}' (Qdrant name '{collection_name}') for movie ID {movie_id}")
        if collection_name not in existing_collections:
            print(f"❌ Collection '{collection_name}' does not exist in Qdrant. Skipping.")
            continue

        try:
            result = client.scroll(
                collection_name=collection_name,
                scroll_filter=qmodels.Filter(
                    must=[qmodels.FieldCondition(
                        key="movie_id",
                        match=qmodels.MatchValue(value=movie_id)
                    )]
                ),
                with_vectors=True,
                with_payload=True,
                limit=1
            )

            if not result or len(result[0]) == 0:
                print(f"❌ No entry found for movie ID {movie_id} in collection '{collection_name}'.")
                continue

            point = result[0][0]
            vector = point.vector
            payload = point.payload

            if vector is None or len(vector) == 0:
                print("❌ Vector is missing or empty.")
            else:
                print(f"✅ Vector exists. Length: {len(vector)}")

            if not payload:
                print("❌ Payload is missing.")
            else:
                print(f"✅ Payload keys: {list(payload.keys())}")

        except Exception as e:
            print(f"❌ Error checking vector: {e}")

    # --- Step 4: Count vectors in Qdrant collections ---
    print("\n📦 Counting vectors in Qdrant collections")
    for vector_key, collection_name in COLLECTIONS.items():
        if collection_name not in existing_collections:
            print(f"❌ Collection '{collection_name}' does not exist in Qdrant. Skipping count.")
            continue
        try:
            count = client.count(collection_name=collection_name, exact=True).count
            print(f"📊 Collection '{collection_name}': {count} vectors")
        except Exception as e:
            print(f"❌ Error counting vectors in '{collection_name}': {e}")

    # --- Step 5: Nearest neighbor search for movie ID 45 ---
    print("\n🤝 Step 5: Similarity search test")
    for vector_key, collection_name in COLLECTIONS.items():
        if collection_name not in existing_collections:
            print(f"❌ Collection '{collection_name}' does not exist in Qdrant. Skipping similarity search.")
            continue

        print(f"\n🔍 Searching similar vectors in collection '{collection_name}' for movie ID {movie_id}")
        try:
            result = client.scroll(
                collection_name=collection_name,
                scroll_filter=qmodels.Filter(
                    must=[qmodels.FieldCondition(
                        key="movie_id",
                        match=qmodels.MatchValue(value=movie_id)
                    )]
                ),
                with_vectors=True,
                with_payload=True,
                limit=1
            )
            if not result[0]:
                print("❌ Cannot search: movie vector not found.")
                continue

            query_vector = result[0][0].vector

            if not query_vector:
                print("❌ No query vector found for similarity search.")
                continue

            search_result = client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=5
            )

            if not search_result:
                print("❌ No similar vectors found.")
            else:
                print(f"✅ Found {len(search_result)} similar vectors:")
                for hit in search_result:
                    print(f"   → ID: {hit.id} | Score: {hit.score:.4f}")

        except Exception as e:
            print(f"❌ Error during similarity search: {e}")

    print("\n" + "="*60)
    print("✅ DIAGNOSTICS COMPLETE")
    print("="*60)
