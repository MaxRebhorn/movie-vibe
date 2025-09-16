from django.test import TestCase
from django.contrib.auth.models import User
from movies.models import Movie
from user.models import UserPool, UserProfile, POOL_MIN_RADIUS, POOL_SURFACE_TENSION
from user.recommendations import (
    update_pools_with_movie,
    get_recommendations,
    get_user_pools,
    get_vector_from_qtron,
    search_similar_in_qtron,
)
import numpy as np


class PoolTests(TestCase):

    def setUp(self):
        # Testuser + Profil
        self.user = User.objects.create_user(username="tester", password="secret")
        self.profile = UserProfile.objects.create(user=self.user)

        # Testfilme
        self.movies = []
        for i in range(5):
            m = Movie.objects.create(id=100 + i, title=f"Movie {i}")
            self.movies.append(m)

    # --------------------------------------------
    # 1. Pools werden korrekt in DB gespeichert
    # --------------------------------------------
    def test_pools_are_created(self):
        pools = get_user_pools(self.profile)
        self.assertEqual(len(pools), 3)  # vibe, style, plot
        for pool in pools:
            self.assertAlmostEqual(pool.radius, POOL_MIN_RADIUS)
            self.assertAlmostEqual(pool.surface_tension, POOL_SURFACE_TENSION)

    # ---------------------------------------------------
    # 2. Neue Filme aktualisieren Zentrum und Radius
    # ---------------------------------------------------
    def test_update_pools_with_movie(self):
        def fake_get_vector(collection, movie_id):
            return [float(movie_id % 10)] * 300

        # Patch Qdrant-Funktion
        self._old_get_vector = get_vector_from_qtron
        import user.recommendations as rec
        rec.get_vector_from_qtron = fake_get_vector

        pool = get_user_pools(self.profile, "vibe")[0]
        old_center = pool.center.copy()

        update_pools_with_movie(self.profile, self.movies[0])
        pool.refresh_from_db()

        self.assertNotEqual(pool.center, old_center)
        self.assertIn(self.movies[0].id, pool.support_movie_ids)

        # Restore
        rec.get_vector_from_qtron = self._old_get_vector

    # ---------------------------------------------------
    # 3. SurfaceTension -> neuer Pool entsteht
    # ---------------------------------------------------
    def test_surface_tension_split_creates_pool(self):
        pool = get_user_pools(self.profile, "vibe")[0]

        # Dummy-Kandidaten weit außerhalb
        far_vectors = [[100.0] * 300 for _ in range(15)]

        def fake_split(self, candidate_vectors):
            if len(candidate_vectors) > 10:
                return UserPool.objects.create(
                    user=self.user,
                    dimension=self.dimension,
                    center=[1.0] * 300,
                    radius=1.0,
                    parent_pool=self,
                )

        # Patch Methode
        old_split = UserPool.check_surface_tension_and_split
        UserPool.check_surface_tension_and_split = fake_split

        new_pool = pool.check_surface_tension_and_split(far_vectors)
        self.assertIsInstance(new_pool, UserPool)
        self.assertEqual(new_pool.parent_pool, pool)

        # Restore
        UserPool.check_surface_tension_and_split = old_split

    # ---------------------------------------------------
    # 4. Empfehlungen liefern Top-N Filme
    # ---------------------------------------------------
    def test_recommendations(self):
        self.profile.favorite_movies.add(*self.movies[:2])

        def fake_get_vector(collection, movie_id):
            return [float(movie_id %_]()
