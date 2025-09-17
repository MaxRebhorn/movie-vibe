from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from user.models import UserProfile, UserPool
from movies.models import Movie
import numpy as np
from scipy.spatial.distance import cosine

# ===============================
# Helper function for similarity
# ===============================
def average_pairwise_cosine(vectors):
    if len(vectors) < 2:
        return 1.0  # trivially similar
    sims = []
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            sims.append(1 - cosine(vectors[i], vectors[j]))
    return np.mean(sims) if sims else 1.0

# ===============================
# Management command
# ===============================
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

        # Fetch pools
        pools = UserPool.objects.filter(user=user)
        if not pools.exists():
            self.stdout.write(self.style.WARNING(f"⚠️ User {user.username} has no pools"))
            return

        self.stdout.write(self.style.SUCCESS(f"🔎 Pools for user {user.username} ({user.email}):"))

        for pool in pools:
            vectors = []
            movies = Movie.objects.filter(id__in=pool.support_movie_ids)
            for m in movies:
                if hasattr(m, 'vector'):  # ensure the movie has vector field or method
                    vectors.append(np.array(m.vector))
                else:
                    vectors.append(np.zeros(len(pool.center)))  # fallback

            avg_similarity = average_pairwise_cosine(vectors)
            split_likelihood = min(1.0, (pool.radius / (pool.surface_tension or 1.0)) * (len(pool.support_movie_ids)/4)) if pool.surface_tension else 0.0

            self.stdout.write(
                f"\n  - Pool ID: {pool.id}, Name: {pool.name}\n"
                f"    Dimension: {pool.dimension}\n"
                f"    Radius: {pool.radius:.4f}, Active: {pool.is_active}\n"
                f"    Movies: {len(pool.support_movie_ids)}, Split Likelihood: {split_likelihood:.2%}\n"
                f"    Avg Pairwise Cosine Similarity: {avg_similarity:.4f}"
            )

            for m, vec in zip(movies, vectors):
                first_dims = ', '.join(f"{x:.4f}" for x in vec[:5])
                self.stdout.write(f"      • {m.title} (ID: {m.id}) | Vector (first 5 dims): [{first_dims} ...]")

        # Show favorites not in any pool
        favorite_ids = set(profile.favorite_movies.values_list("id", flat=True))
        pool_movie_ids = set(pid for pool in pools for pid in pool.support_movie_ids)
        missing_favorites = favorite_ids - pool_movie_ids
        if missing_favorites:
            self.stdout.write(self.style.WARNING("\n⚠️ Favorite movies not in any pool:"))
            for m in Movie.objects.filter(id__in=missing_favorites):
                self.stdout.write(f"      • {m.title} (ID: {m.id})")
