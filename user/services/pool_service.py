import numpy as np
from collections import defaultdict, Counter
from django.db import transaction
from sklearn.cluster import DBSCAN
from qdrant_client import QdrantClient
from qdrant_client.models import ScoredPoint
from django.conf import settings

from movies.models import Movie
from user.models import UserPool, UserProfile

# ============================
# Qdrant Setup
# ============================
client = QdrantClient(url=settings.QDRANT_URL)

COLLECTION_MAP = {
    "vibe": "movies_vibe",
    "style": "movies_style",
    "plot": "movies_narrative"
}

# ============================
# Helpers
# ============================
def get_vector_from_qdrant(collection: str, movie_id: int):
    result = client.retrieve(collection_name=collection, ids=[movie_id], with_vectors=True)
    if not result:
        raise ValueError(f"Movie ID {movie_id} not found in {collection}")
    return result[0].vector

def search_similar_in_qdrant(collection: str, vector, limit: int, exclude_id=None):
    response = client.search(collection_name=collection, query_vector=vector, limit=limit*2)
    results = [(pt.id, pt.score) for pt in response if pt.id != exclude_id]
    return results[:limit]

# ============================
# Pool Management
# ============================
def get_user_pools(profile: UserProfile, dimension: str = None):
    pools = profile.user.pools.filter(is_active=True)
    if dimension:
        pools = pools.filter(dimension=dimension)
    return list(pools)

def cluster_favorites(favorite_vectors, eps=0.7, min_samples=2):
    """Cluster user favorites using DBSCAN."""
    if not favorite_vectors:
        return {}
    clustering = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine').fit(favorite_vectors)
    clusters = defaultdict(list)
    for idx, label in enumerate(clustering.labels_):
        if label != -1:
            clusters[label].append(idx)
    return clusters

@transaction.atomic
def recompute_user_pools(profile: UserProfile):
    """Recompute pools per dimension, clustering favorites and avoiding duplicates."""
    favorite_movies = list(profile.favorite_movies.all())
    if not favorite_movies:
        return

    movie_pool_count = defaultdict(int)
    for dim, collection in COLLECTION_MAP.items():
        favorite_vectors = [get_vector_from_qdrant(collection, m.id) for m in favorite_movies]
        clusters = cluster_favorites(favorite_vectors)

        # Create new pools per cluster
        for cluster_indices in clusters.values():
            cluster_movie_ids = []
            cluster_vectors = []
            for idx in cluster_indices:
                movie_id = favorite_movies[idx].id
                if movie_pool_count[movie_id] < 2:  # max 2 pools per movie
                    cluster_movie_ids.append(movie_id)
                    cluster_vectors.append(favorite_vectors[idx])
                    movie_pool_count[movie_id] += 1

            if not cluster_movie_ids:
                continue

            center = np.mean(np.array(cluster_vectors), axis=0).tolist()
            radius = max(np.linalg.norm(np.array(v)-np.array(center)) for v in cluster_vectors)
            pool_name = generate_pool_name_from_movies(dim, cluster_movie_ids)

            UserPool.objects.create(
                user=profile.user,
                dimension=dim,
                center=center,
                radius=radius,
                support_movie_ids=cluster_movie_ids,
                is_active=True,
                name=pool_name
            )

def generate_pool_name_from_movies(dimension, movie_ids):
    movies = Movie.objects.filter(id__in=movie_ids)
    genres, keywords = [], []
    for m in movies:
        if hasattr(m, 'genres') and isinstance(m.genres, list):
            genres.extend(m.genres)
        if hasattr(m, 'keywords') and isinstance(m.keywords, list):
            keywords.extend(m.keywords)

    parts = [g for g,_ in Counter(genres).most_common(2)]
    if keywords:
        parts.append(Counter(keywords).most_common(1)[0][0])
    if not parts:
        parts.append("Misc")
    return f"{' '.join(parts)} {dimension.capitalize()} Pool"

# ============================
# Pool Candidate Selection
# ============================
def get_pool_candidates(pool: UserPool, favorite_ids, top_n=20):
    collection = COLLECTION_MAP.get(pool.dimension)
    if not collection:
        return []

    expansion_factor = 1.0
    candidates = []

    while not candidates and expansion_factor < 5.0:
        raw_candidates = search_similar_in_qdrant(collection, pool.center, limit=top_n*3)
        raw_candidates = [(mid, score) for mid, score in raw_candidates if mid not in favorite_ids]

        scored = []
        for movie_id, _ in raw_candidates:
            dist = np.linalg.norm(np.array(get_vector_from_qdrant(collection, movie_id)) - np.array(pool.center))
            sigma = max(pool.radius * expansion_factor / 3.0, 0.1)
            gauß_score = np.exp(- (dist**2) / (2*sigma**2))
            scored.append((movie_id, gauß_score))

        candidates = scored
        expansion_factor *= 1.5

    return candidates

def assemble_recommendations(pool_candidates, top_n=20):
    sorted_pools = sorted(pool_candidates.items(), key=lambda x: len(x[1]), reverse=True)
    pool_indices = {pool_id: 0 for pool_id, _ in sorted_pools}
    recommendation_heap = []

    while len(recommendation_heap) < top_n:
        for pool_id, candidates in sorted_pools:
            idx = pool_indices[pool_id]
            if idx < len(candidates):
                movie_id, score = candidates[idx]
                recommendation_heap.append((score, movie_id))
                pool_indices[pool_id] += 1
            if len(recommendation_heap) >= top_n:
                break
        else:
            break

    seen = set()
    final_recs = []
    for score, movie_id in sorted(recommendation_heap, key=lambda x: x[0], reverse=True):
        if movie_id not in seen:
            final_recs.append({"movie_id": movie_id, "score": score})
            seen.add(movie_id)
        if len(final_recs) >= top_n:
            break
    return final_recs

# ============================
# Public API
# ============================
def get_recommendations(profile: UserProfile, top_n=20):
    recompute_user_pools(profile)
    favorite_movies = profile.favorite_movies.all()
    favorite_ids = list(favorite_movies.values_list("id", flat=True))
    pools = get_user_pools(profile)
    pool_candidates = {pool.id: get_pool_candidates(pool, favorite_ids, top_n) for pool in pools}
    return assemble_recommendations(pool_candidates, top_n)

def get_pool_debug_info(profile: UserProfile, dimension=None):
    pools = get_user_pools(profile, dimension)
    return [
        {
            "pool_id": pool.id,
            "dimension": pool.dimension,
            "center": pool.center,
            "radius": pool.radius,
            "num_movies": len(pool.support_movie_ids),
            "pos_weight_sum": getattr(pool, "pos_weight_sum", 0.0)
        }
        for pool in pools
    ]

# ============================
# Backward Compatibility
# ============================
def update_pools_with_movie(profile: UserProfile, movie):
    """Compatibility function for older commands."""
    recompute_user_pools(profile)
