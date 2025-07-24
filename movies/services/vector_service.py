from qdrant_client import QdrantClient
from movies.services.embed_service import embed_model
import uuid

# Qdrant-Client initialisieren (localhost + default port)
client = QdrantClient(url="http://vektor:6333")



COLLECTION_NAME = "movies"  # Name deiner Collection in Qdrant

def save_embedding(embedding: list[float], id: int, payload: dict = None):
    """
    Speichert ein einzelnes Embedding in Qdrant.
    :param embedding: Vektor als Liste von floats
    :param id: Eindeutige ID für den Eintrag (z.B. Movie-ID)
    :param payload: Optionale Metadaten (Titel, Genre etc.)
    """
    if payload is None:
        payload = {}

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[{
            "id": id,
            "vector": embedding,
            "payload": payload
        }]
    )

def embed_to_db(movie):
    """
    Embeddet einen Film und speichert alle Embeddings in Qdrant.
    """
    # embed_model gibt dir ein Dict zurück mit z.B. mehreren Embeddings
    embeddings = embed_model(movie)

    # Beispiel: Du speicherst alle drei Embeddings separat in Qdrant,
    # dabei kannst du unterschiedliche IDs nehmen (z.B. MovieID + suffix)
    for key, embedding in embeddings.items():
        # Generiere eine UUID (kannst du auch aus movie.tmdb_id + key hashen, aber einfacher erstmal so)
        point_id = str(uuid.uuid4())

        payload = {
            "title": movie.title,
            "type": key,
            "movie_tmdb_id": movie.tmdb_id,
        }
        save_embedding(embedding, point_id, payload)
