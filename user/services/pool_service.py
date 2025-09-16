from typing import List, Dict
from user.models import UserPool, UserProfile
from movies.models import Movie
import numpy as np
import heapq
from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint
from django.conf import settings

# Qdrant (Qtron) Client initialisieren
client = QdrantClient(url=settings.QDRANT_URL)
COLLECTIONS = ["movies_narrative", "movies_style", "movies_vibe"]

# ----------------------------------------
# Intern: Pool-Management / Datenpflege
# ----------------------------------------

def get_vector_from_qtron(collection: str, movie_id: int) -> List[float]:
    result = client.retrieve(collection_name=collection, ids=[movie_id], with_vectors=True)
    if not result:
        raise ValueError(f"Movie ID {movie_id} not found in {collection}")
    return result[0].vector

def search_similar_in_qtron(collection: str, vector: List[float], limit: int, exclude_id: int = None) -> List[tuple]:
    response: List[ScoredPoint] = client.search(collection_name=collection, query_vector=vector, limit=limit*2)
    results = [(pt.id, pt.score) for pt in response if pt.id != exclude_id]
    return results[:limit]

def update_pools_with_movie(user: UserProfile, movie: Movie):
    pools = get_user_pools(user)
    for pool in pools:
        collection_map = {"vibe": "movies_vibe", "style": "movies_style", "plot": "movies_narrative"}
        collection = collection_map.get(pool.dimension)
        if not collection:
            continue

        vector = get_vector_from_qtron(collection, movie.id)

        if not pool.center:
            pool.center = vector
        else:
            existing_vectors = [get_vector_from_qtron(collection, m.id) for m in pool.support_movies]
            all_vectors = existing_vectors + [vector]
            pool.center = np.mean(np.array(all_vectors), axis=0).tolist()

        distances = [np.linalg.norm(np.array(vec) - np.array(pool.center)) for vec in all_vectors]
        pool.radius = max(distances) if distances else 0.0

        if movie not in pool.support_movies:
            pool.support_movies.append(movie)
        pool.save()

# ----------------------------------------
# Öffentlich: Empfehlungen / Pool-Abfragen
# ----------------------------------------

def get_user_pools(user: UserProfile, dimension: str = None) -> List[UserPool]:
    pools = user.pools.filter(is_active=True)
    if dimension:
        pools = pools.filter(dimension=dimension)
    return list(pools)

def get_recommendations(user: UserProfile, top_n: int = 20) -> List[Dict]:
    favorite_movies = user.favorite_movies.all()
    if not favorite_movies:
        return []

    pools = get_user_pools(user)
    if not pools:
        return []

    # Pool-Zentren neu berechnen
    for pool in pools:
        collection_map = {"vibe": "movies_vibe", "style": "movies_style", "plot": "movies_narrative"}
        collection = collection_map.get(pool.dimension)
        if not collection:
            continue
        vectors = [get_vector_from_qtron(collection, m.id) for m in favorite_movies]
        if vectors:
            pool.center = np.mean(np.array(vectors), axis=0).tolist()
            pool.save()

    # Kandidaten pro Pool
    pool_candidates: Dict[int, List[tuple]] = {}
    for pool in pools:
        collection_map = {"vibe": "movies_vibe", "style": "movies_style", "plot": "movies_narrative"}
        collection = collection_map.get(pool.dimension)
        candidates = search_similar_in_qtron(collection, pool.center, limit=top_n*3)
        scored_candidates = []
        for movie_id, _ in candidates:
            dist = np.linalg.norm(np.array(get_vector_from_qtron(collection, movie_id)) - np.array(pool.center))
            sigma = pool.radius / 3.0 if pool.radius > 0 else 1.0
            gauß_score = np.exp(- (dist ** 2) / (2 * sigma ** 2))
            scored_candidates.append((movie_id, gauß_score))
        pool_candidates[pool.id] = scored_candidates

    # Rotierende Zusammenstellung
    sorted_pools = sorted(pool_candidates.items(), key=lambda x: len(x[1]), reverse=True)
    pool_indices = {pool_id: 0 for pool_id, _ in sorted_pools}
    recommendation_heap: List[tuple] = []

    while len(recommendation_heap) < top_n:
        for pool_id, candidates in sorted_pools:
            idx = pool_indices[pool_id]
            if idx < len(candidates):
                movie_id, score = candidates[idx]
                heapq.heappush(recommendation_heap, (score, movie_id))
                pool_indices[pool_id] += 1
            if len(recommendation_heap) >= top_n:
                break
        else:
            break

    seen = set()
    final_recommendations = []
    for score, movie_id in sorted(recommendation_heap, key=lambda x: x[0], reverse=True):
        if movie_id not in seen:
            final_recommendations.append({"movie_id": movie_id, "score": score})
            seen.add(movie_id)
        if len(final_recommendations) >= top_n:
            break

    return final_recommendations

def get_pool_debug_info(user: UserProfile, dimension: str = None) -> List[Dict]:
    pools = get_user_pools(user, dimension)
    debug_info = []
    for pool in pools:
        debug_info.append({
            "pool_id": pool.id,
            "dimension": pool.dimension,
            "center": pool.center,
            "radius": pool.radius,
            "surface_tension": pool.surface_tension,
            "num_candidates": len(pool.support_movies),
        })
    return debug_info
