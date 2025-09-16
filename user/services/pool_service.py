from typing import List, Dict
from user.models import UserPool, UserProfile
from movies.models import Movie
import numpy as np
import heapq
from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint
from django.conf import settings

# Qdrant Client
client = QdrantClient(url=settings.QDRANT_URL)
COLLECTION_MAP = {"vibe": "movies_vibe", "style": "movies_style", "plot": "movies_narrative"}

# ----------------------------------------
# Qdrant Helpers
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

# ----------------------------------------
# Pool Management
# ----------------------------------------

def update_pools_with_movie(profile: UserProfile, movie: Movie):
    pools = profile.user.pools.filter(is_active=True)
    for pool in pools:
        collection = COLLECTION_MAP.get(pool.dimension)
        if not collection:
            continue

        vector = get_vector_from_qtron(collection, movie.id)

        if not pool.center:
            pool.center = vector
            all_vectors = [vector]
        else:
            existing_vectors = [get_vector_from_qtron(collection, mid) for mid in pool.support_movie_ids]
            all_vectors = existing_vectors + [vector]
            pool.center = np.mean(np.array(all_vectors), axis=0).tolist()

        distances = [np.linalg.norm(np.array(vec) - np.array(pool.center)) for vec in all_vectors]
        pool.radius = max(distances) if distances else 0.0

        if movie.id not in pool.support_movie_ids:
            pool.support_movie_ids.append(movie.id)
        pool.save()

def get_user_pools(profile: UserProfile, dimension: str = None):
    pools = profile.user.pools.all()
    if not pools.exists():
        # Auto-create default pools
        for dim in COLLECTION_MAP.keys():
            UserPool.objects.create(
                user=profile.user,
                dimension=dim,
                center=[0.0] * 300,
                radius=0.7
            )
        pools = profile.user.pools.all()
    if dimension:
        pools = pools.filter(dimension=dimension)
    return list(pools)

def recompute_pool_centers(pools: List[UserPool], favorite_movies):
    """Recompute each pool center based on all favorite movies."""
    for pool in pools:
        collection = COLLECTION_MAP.get(pool.dimension)
        if not collection:
            continue
        vectors = [get_vector_from_qtron(collection, m.id) for m in favorite_movies]
        if vectors:
            pool.center = np.mean(np.array(vectors), axis=0).tolist()
            pool.save()

# ----------------------------------------
# Recommendation Helpers
# ----------------------------------------

def get_pool_candidates(pool: UserPool, favorite_ids: List[int], top_n: int) -> List[tuple]:
    """Fetch candidates for a pool, excluding favorites, expanding radius if needed."""
    collection = COLLECTION_MAP.get(pool.dimension)
    if not collection:
        return []

    expansion_factor = 1.0
    candidates = []

    while not candidates and expansion_factor < 5.0:  # avoid infinite loop
        raw_candidates = search_similar_in_qtron(collection, pool.center, limit=top_n*3)
        raw_candidates = [(mid, score) for mid, score in raw_candidates if mid not in favorite_ids]

        scored = []
        for movie_id, _ in raw_candidates:
            dist = np.linalg.norm(np.array(get_vector_from_qtron(collection, movie_id)) - np.array(pool.center))
            sigma = (pool.radius * expansion_factor) / 3.0 or 1.0
            gauß_score = np.exp(- (dist ** 2) / (2 * sigma ** 2))
            scored.append((movie_id, gauß_score))

        if scored:
            candidates = scored
        else:
            expansion_factor *= 1.5  # grow step by step

    return candidates

def assemble_recommendations(pool_candidates: Dict[int, List[tuple]], top_n: int) -> List[Dict]:
    """Round-robin assembly of recommendations from pools."""
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

# ----------------------------------------
# Public API
# ----------------------------------------

def get_recommendations(profile: UserProfile, top_n: int = 20) -> List[Dict]:
    favorite_movies = profile.favorite_movies.all()
    if not favorite_movies:
        return []

    pools = get_user_pools(profile)
    if not pools:
        return []

    # Update centers
    recompute_pool_centers(pools, favorite_movies)

    # Collect candidates
    favorite_ids = list(favorite_movies.values_list("id", flat=True))
    pool_candidates: Dict[int, List[tuple]] = {
        pool.id: get_pool_candidates(pool, favorite_ids, top_n)
        for pool in pools
    }

    # Assemble recommendations
    return assemble_recommendations(pool_candidates, top_n)

def get_pool_debug_info(profile: UserProfile, dimension: str = None) -> List[Dict]:
    pools = get_user_pools(profile, dimension)
    debug_info = []
    for pool in pools:
        debug_info.append({
            "pool_id": pool.id,
            "dimension": pool.dimension,
            "center": pool.center,
            "radius": pool.radius,
            "surface_tension": pool.surface_tension,
            "num_candidates": len(pool.support_movie_ids),
        })
    return debug_info
