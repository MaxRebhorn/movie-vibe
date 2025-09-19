# ============================
# Pool Hyperparameters
# ============================

# Radius / distance controls
POOL_MIN_RADIUS = 1.0             # Minimum radius of a pool
POOL_GROW_FACTOR = 1.2            # How much the pool grows when adding nearby movies
POOL_MAX_GROW_STEPS = 10          # Max times a pool can grow

# Candidate selection / scoring
POOL_MIN_CANDIDATES = 3           # Minimum number of candidates before expanding search
POOL_SIGMA_DIVISOR = 3.0          # Controls Gaussian score decay
POOL_SURFACE_TENSION = 0.1        # Tightness of pool boundaries
POOL_MAX_MOVIE_DUPLICATES = 2     # Max number of pools a movie can belong to
POOL_VECTOR_SIZE = 384

FAVORITE_CLUSTER_EPS = 0.6       # DBSCAN cosine distance threshold for clustering favorites
FAVORITE_CLUSTER_MIN_SAMPLES = 2  # Minimum favorites per cluster

# Pool boundaries
POOL_RADIUS_FACTOR = 1.0          # Multiply favorite cluster radius to get pool radius
POOL_SPLIT_SIMILARITY_THRESHOLD = 0.5  # If average similarity < this, consider splitting
POOL_MIN_MOVIES_FOR_SPLIT = 4

# Recommendation behavior
CANDIDATE_EXPANSION_FACTOR = 1.5
CANDIDATE_EXPANSION_MAX = 5.0
CANDIDATE_TOP_N = 20
GAUSS_SIGMA_DIVISOR = 3.0