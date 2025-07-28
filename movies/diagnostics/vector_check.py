from qdrant_client import QdrantClient
from qdrant_client.http import models
import pprint

def run_diagnostics():
    client = QdrantClient(host="vektor", port=6333)
    print("HTTP Request: GET http://vektor:6333")

    collection_name = "movies_vibe"
    print(f"Starting diagnostics for collection: '{collection_name}'\n")

    try:
        collections = client.get_collections()
        print("HTTP Request: GET http://vektor:6333/collections")
        print("Collections available:", [col.name for col in collections.collections])

        info = client.get_collection(collection_name=collection_name)
        print(f"HTTP Request: GET http://vektor:6333/collections/{collection_name}")
        print(f"Collection status: {info.status}")

        count = client.count(collection_name=collection_name, exact=True)
        print(f"Number of vectors in '{collection_name}': {count.count}")

        print("\nFetching some vectors for manual inspection...\n")
        results = client.scroll(
            collection_name=collection_name,
            limit=5,
            with_payload=True,
            with_vectors=True
        )
        for point in results[0]:
            pprint.pprint({
                "id": point.id,
                "vector_len": len(point.vector) if point.vector else 0,
                "payload": point.payload
            })

    except Exception as e:
        print(f"ERROR: Could not get collection info: {e}")
