from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from user.models import UserProfile, UserPool
from movies.models import Movie
from user.services.pool_service import (
    update_pools_with_movie,
    get_recommendations,
    get_user_pools, check_surface_tension_and_split,
)
import numpy as np


class RecommendationServiceTest(TestCase):
    def setUp(self):
        # User + Profile
        self.user = User.objects.create_user(username="tester", password="pw123")
        self.profile = UserProfile.objects.create(user=self.user)

        # Movies
        self.movie1 = Movie.objects.create(title="Matrix")
        self.movie2 = Movie.objects.create(title="Inception")
        self.movie3 = Movie.objects.create(title="Interstellar")

        # Qdrant-Mock
        patcher_client = patch('user.services.recommendations.client')
        self.mock_client = patcher_client.start()
        self.addCleanup(patcher_client.stop)

        # Mock retrieve: return dummy vector
        self.mock_client.retrieve.side_effect = lambda collection_name, ids, with_vectors=True: [
            MagicMock(vector=np.ones(300).tolist()) for _ in ids
        ]

        # Mock search: return dummy scored points
        def mock_search(collection_name, query_vector, limit):
            return [MagicMock(id=self.movie2.id, score=0.9),
                    MagicMock(id=self.movie3.id, score=0.8)]
        self.mock_client.search.side_effect = mock_search

    def test_pools_are_created_and_updated(self):
        pools = get_user_pools(self.profile)
        self.assertEqual(len(pools), 3)  # vibe, style, plot

        update_pools_with_movie(self.profile, self.movie1)
        for pool in self.profile.user.pools.all():
            self.assertIn(self.movie1.id, pool.support_movie_ids)
            self.assertTrue(pool.radius >= 0.0)

    def test_incremental_update_with_new_movie(self):
        update_pools_with_movie(self.profile, self.movie1)
        radius_before = self.profile.user.pools.first().radius

        update_pools_with_movie(self.profile, self.movie2)
        radius_after = self.profile.user.pools.first().radius

        self.assertGreaterEqual(radius_after, radius_before)

    def test_recommendations_exclude_favorites(self):
        self.profile.favorite_movies.add(self.movie1)

        recs = get_recommendations(self.profile, top_n=2)
        rec_ids = [r["movie_id"] for r in recs]

        self.assertNotIn(self.movie1.id, rec_ids)  # exclude favorite
        self.assertIn(self.movie2.id, rec_ids)
        self.assertIn(self.movie3.id, rec_ids)

    def test_surface_tension_triggers_new_pool(self):
        pool = UserPool.objects.create(
            user=self.user,
            dimension="vibe",
            center=np.zeros(300).tolist(),
            radius=2.0,
            surface_tension=1.0,
        )
        # Radius > surface_tension, sollte theoretisch Split auslösen
        self.assertTrue(pool.radius > pool.surface_tension)
        # Hier könntest du deine Funktion `check_surface_tension_and_split(pool)` testen,
        # wenn du die implementierst


def test_surface_tension_triggers_split(self):
    # Vorher: 3 Pools
    initial_pool_count = UserPool.objects.filter(user=self.user).count()

    # Pool mit kritischer Surface Tension erstellen
    pool = UserPool.objects.create(
        user=self.user,
        dimension="vibe",
        center=np.zeros(300).tolist(),
        radius=2.0,
        surface_tension=1.0,
    )

    # Surface Tension check auslösen (muss implementiert werden)
    check_surface_tension_and_split(pool)

    # Nachher: sollte 4 Pools haben (original + 1 neuer)
    final_pool_count = UserPool.objects.filter(user=self.user).count()
    self.assertEqual(final_pool_count, initial_pool_count + 1)