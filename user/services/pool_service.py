import numpy as np
from collections import defaultdict, Counter
from django.db import transaction
from qdrant_client import QdrantClient
from django.conf import settings
from movies.models import Movie
from user.models import UserPool, UserProfile
from user.settings.pool_settings import (
    POOL_GROW_FACTOR,
    POOL_MAX_GROW_STEPS,
    POOL_MIN_CANDIDATES,
    FAVORITE_CLUSTER_EPS,
    FAVORITE_CLUSTER_MIN_SAMPLES,
    POOL_RADIUS_FACTOR,
    POOL_SPLIT_SIMILARITY_THRESHOLD,
    POOL_MIN_MOVIES_FOR_SPLIT,
    CANDIDATE_EXPANSION_FACTOR,
    CANDIDATE_EXPANSION_MAX,
    CANDIDATE_TOP_N,
    GAUSS_SIGMA_DIVISOR

)

# ============================
# Hyperparameters / Tuning
# ============================
# How tight the favorite clusters are


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
    response = client.search(collection_name=collection, query_vector=vector, limit=limit * 2)
    results = [(pt.id, pt.score) for pt in response if pt.id != exclude_id]
    return results[:limit]

def average_pairwise_cosine(vectors):
    if len(vectors) < 2:
        return 1.0
    sims = []
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            sim = 1 - np.dot(vectors[i], vectors[j]) / (np.linalg.norm(vectors[i]) * np.linalg.norm(vectors[j]))
            sims.append(sim)
    return np.mean(sims) if sims else 1.0

# ============================
# Pool Management
# ============================
def get_user_pools(profile: UserProfile, dimension: str = None):
    pools = profile.user.pools.filter(is_active=True)
    if dimension:
        pools = pools.filter(dimension=dimension)
    return list(pools)

def cluster_favorites(favorite_vectors, eps=FAVORITE_CLUSTER_EPS, min_samples=FAVORITE_CLUSTER_MIN_SAMPLES):
    """Cluster favorites tightly with DBSCAN."""
    from sklearn.cluster import DBSCAN
    if not favorite_vectors:
        return {}
    clustering = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine').fit(favorite_vectors)
    clusters = defaultdict(list)
    for idx, label in enumerate(clustering.labels_):
        if label != -1:
            clusters[label].append(idx)
    return clusters

@transaction.atomic
def build_pools_from_favorites(profile: UserProfile):
    """Main function: cluster favorites into pools."""
    for dim in COLLECTION_MAP.keys():
        favorite_movies = profile.favorite_movies.all()
        if not favorite_movies:
            continue

        # Fetch vectors
        vectors = []
        movie_ids = []
        for movie in favorite_movies:
            try:
                vec = get_vector_from_qdrant(COLLECTION_MAP[dim], movie.id)
                vectors.append(vec)
                movie_ids.append(movie.id)
            except ValueError:
                continue
        if not vectors:
            continue

        # Cluster favorites
        clusters = cluster_favorites(vectors)
        for label, indices in clusters.items():
            cluster_movie_ids = [movie_ids[i] for i in indices]
            cluster_vectors = [vectors[i] for i in indices]
            center = np.mean(cluster_vectors, axis=0).tolist()
            radius = max(np.linalg.norm(np.array(vec) - np.array(center)) for vec in cluster_vectors) * POOL_RADIUS_FACTOR

            # Create pool
            UserPool.objects.create(
                user=profile.user,
                dimension=dim,
                center=center,
                radius=radius,
                support_movie_ids=cluster_movie_ids,
                is_active=True,
                name=f"{Movie.objects.get(id=cluster_movie_ids[0]).title} {dim.capitalize()} Pool"
            )

# ============================
# Pool Refinement
# ============================
@transaction.atomic
def split_pool_if_needed(pool: UserPool):
    """Split a pool if its internal similarity is too low."""
    if len(pool.support_movie_ids) < POOL_MIN_MOVIES_FOR_SPLIT:
        return False

    collection = COLLECTION_MAP[pool.dimension]
    vectors = []
    for mid in pool.support_movie_ids:
        try:
            vec = get_vector_from_qdrant(collection, mid)
            vectors.append(vec)
        except ValueError:
            continue
    if not vectors:
        return False

    avg_similarity = average_pairwise_cosine(vectors)
    if avg_similarity > POOL_SPLIT_SIMILARITY_THRESHOLD:
        return False

    # Split using KMeans into 2 subclusters
    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=2, random_state=42).fit(vectors)
    clusters = defaultdict(list)
    for i, label in enumerate(kmeans.labels_):
        clusters[label].append(pool.support_movie_ids[i])

    any_split = False
    for label, mids in clusters.items():
        if len(mids) < 2:
            continue
        cluster_vectors = []
        for mid in mids:
            try:
                vec = get_vector_from_qdrant(collection, mid)
                cluster_vectors.append(vec)
            except ValueError:
                continue
        if not cluster_vectors:
            continue
        center = np.mean(cluster_vectors, axis=0).tolist()
        radius = max(np.linalg.norm(np.array(vec) - np.array(center)) for vec in cluster_vectors)

        UserPool.objects.create(
            user=pool.user,
            dimension=pool.dimension,
            center=center,
            radius=radius,
            support_movie_ids=mids,
            parent_pool=pool,
            is_active=True,
            name=f"{pool.name} Split {label+1}"
        )
        any_split = True

    if any_split:
        pool.is_active = False
        pool.save()

    return any_split

# ============================
# Recommendations
# ============================
def get_pool_candidates(pool: UserPool, favorite_ids, top_n=CANDIDATE_TOP_N):
    collection = COLLECTION_MAP.get(pool.dimension)
    if not collection:
        return []

    expansion_factor = 1.0
    candidates = []

    while not candidates and expansion_factor < CANDIDATE_EXPANSION_MAX:
        raw_candidates = search_similar_in_qdrant(collection, pool.center, limit=top_n * 3)
        raw_candidates = [(mid, score) for mid, score in raw_candidates if mid not in favorite_ids]

        scored = []
        for movie_id, _ in raw_candidates:
            try:
                vec = get_vector_from_qdrant(collection, movie_id)
                dist = np.linalg.norm(np.array(vec) - np.array(pool.center))
                sigma = max(pool.radius * expansion_factor / GAUSS_SIGMA_DIVISOR, 0.1)
                gauß_score = np.exp(- (dist ** 2) / (2 * sigma ** 2))
                scored.append((movie_id, gauß_score))
            except ValueError:
                continue

        candidates = scored
        expansion_factor *= CANDIDATE_EXPANSION_FACTOR

    return candidates

def assemble_recommendations(pool_candidates, top_n=CANDIDATE_TOP_N):
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
def get_recommendations(profile: UserProfile, top_n=CANDIDATE_TOP_N):
    """Build pools from favorites, refine, and return recommendations."""
    # 1. Build tight pools from favorites
    build_pools_from_favorites(profile)

    # 2. Split pools if too diverse
    for pool in UserPool.objects.filter(user=profile.user, is_active=True):
        split_pool_if_needed(pool)

    # 3. Generate candidate recommendations from each pool
    favorite_ids = list(profile.favorite_movies.values_list("id", flat=True))
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


@transaction.atomic
def recompute_user_pools(profile: UserProfile):
    """
    Rebuild all pools for a user:
      1. Build pools from favorite movies
      2. Split pools if needed
    """
    # Step 1: Build / refresh pools
    build_pools_from_favorites(profile)

    # Step 2: Split pools if diversity is too high
    for pool in UserPool.objects.filter(user=profile.user, is_active=True):
        split_pool_if_needed(pool)