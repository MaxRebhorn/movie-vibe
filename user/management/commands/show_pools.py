from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from user.models import UserProfile, UserPool
from movies.models import Movie
import numpy as np
from scipy.spatial.distance import cosine
from qdrant_client import QdrantClient
from django.conf import settings

client = QdrantClient(url=settings.QDRANT_URL)
COLLECTION_MAP = {
    "vibe": "movies_vibe",
    "style": "movies_style",
    "plot": "movies_narrative"
}

def average_pairwise_cosine(vectors):
    if len(vectors) < 2:
        return 1.0
    sims = [1 - cosine(vectors[i], vectors[j])
            for i in range(len(vectors)) for j in range(i + 1, len(vectors))]
    return float(np.mean(sims)) if sims else 1.0

def get_vector_from_qdrant(collection, movie_id, fallback_dim=384):
    result = client.retrieve(collection_name=collection, ids=[movie_id], with_vectors=True)
    if not result or not hasattr(result[0], "vector") or result[0].vector is None:
        return np.zeros(fallback_dim)
    return np.array(result[0].vector)

class Command(BaseCommand):
    help = "Display all pools for a user with vectors and cluster similarity"

    def add_arguments(self, parser):
        parser.add_argument("--email", type=str, help="User email", required=False)
        parser.add_argument("--username", type=str, help="Username", required=False)

    def handle(self, *args, **options):
        email = options.get("email")
        username = options.get("username")

        if not email and not username:
            self.stdout.write(self.style.ERROR("❌ Provide either --email or --username"))
            return

        # Fetch user
        try:
            user = User.objects.get(email=email) if email else User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ User not found"))
            return

        # Fetch profile
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ User {user.username} has no profile"))
            return

        # Recompute pools
        from user.services.pool_service import recompute_user_pools
        recompute_user_pools(profile)

        # Fetch pools
        pools = UserPool.objects.filter(user=user, is_active=True)
        if not pools.exists():
            self.stdout.write(self.style.WARNING(f"⚠️ User {user.username} has no pools"))
            return

        self.stdout.write(self.style.SUCCESS(f"\n🔎 Pools for user {user.username} ({user.email}):\n"))

        for dim in ['vibe', 'style', 'plot']:
            dim_pools = [p for p in pools if p.dimension == dim]
            if not dim_pools:
                continue

            self.stdout.write(self.style.MIGRATE_HEADING(f"=== Dimension: {dim.upper()} ==="))
            header = f"{'Pool ID':<8} {'Name':<25} {'Movies':<6} {'Radius':<8} {'Avg Cosine':<12}"
            self.stdout.write(header)
            self.stdout.write("-" * len(header))

            all_pool_movie_ids = set()
            for pool in dim_pools:
                collection = COLLECTION_MAP.get(pool.dimension)
                movies = Movie.objects.filter(id__in=pool.support_movie_ids)
                vectors = [get_vector_from_qdrant(collection, m.id) for m in movies]
                avg_similarity = average_pairwise_cosine(vectors)

                all_pool_movie_ids.update(pool.support_movie_ids)

                self.stdout.write(
                    f"{pool.id:<8} {pool.name[:25]:<25} {len(vectors):<6} {pool.radius:<8.4f} {avg_similarity:<12.4f}"
                )

            # Show favorites not in any pool
            favorite_ids = set(profile.favorite_movies.values_list("id", flat=True))
            missing_favorites = favorite_ids - all_pool_movie_ids
            if missing_favorites:
                self.stdout.write("\n⚠️ Favorite movies not in any pool:")
                for m in Movie.objects.filter(id__in=missing_favorites):
                    self.stdout.write(f"  • {m.title} (ID: {m.id})")
            self.stdout.write("\n")
