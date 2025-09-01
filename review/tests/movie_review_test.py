from django.test import TestCase
from django.contrib.auth.models import User
from movies.models import Movie
from user.models import UserProfile
from review.services.embed_review import process_quiz_review
from review.services.vector_review import update_weighted_embedding
import random
import numpy as np


def cosine_similarity(vec_a, vec_b):
    a = np.array(vec_a)
    b = np.array(vec_b)
    if len(a) == 0 or len(b) == 0:
        return 0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


class MovieVectorPushTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create anchor movie (fully populated)
        cls.movable = Movie.objects.create(
            title="Movable Movie",
            original_title="Movable Movie",
            synopsis="A test movie to move vectors",
            tagline="Movable tagline",
            language="English",
            country="US",
            release_date="2020-01-01",
            runtime=100,
            director="Director Name",
            cast=[],
            genres=[],
            keywords=[],
            composer=[],
            poster_url="https://example.com/poster.jpg",
            backdrop_url="https://example.com/backdrop.jpg",
            avg_rating=5.0,
            tmdb_id=9999
        )

        # Create users and attach profiles
        cls.users = []
        for i in range(3):
            user = User.objects.create(username=f"user{i}")
            # Ensure profile exists
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.xp = i * 50
            profile.save()
            cls.users.append(user)

        # Optional: create anchors if needed for similarity checks
        cls.anchors = []
        for j in range(2):
            anchor = Movie.objects.create(
                title=f"Anchor Movie {j}",
                original_title=f"Anchor Movie {j}",
                synopsis="Anchor movie for testing",
                tagline="Anchor tagline",
                language="English",
                country="US",
                release_date="2019-01-01",
                runtime=90,
                director="Anchor Director",
                cast=[],
                genres=[],
                keywords=[],
                composer=[],
                poster_url="https://example.com/anchor_poster.jpg",
                backdrop_url="https://example.com/anchor_backdrop.jpg",
                avg_rating=4.0,
                tmdb_id=1000 + j
            )
            cls.anchors.append(anchor)

    def generate_quiz_answers(self):
        return {
            "question1": {"values": ["action", "adventure"], "vector_type": "vibe"},
            "question2": {"values": ["twist", "complex"], "vector_type": "narrative"},
            "question3": {"values": ["romantic", "dramatic"], "vector_type": "style"}
        }

    def test_push_movable_movie(self):
        similarities_over_time = []

        for _ in range(10):
            user = random.choice(self.users)
            quiz_data = {"answers": self.generate_quiz_answers(), "xp": user.profile.xp}
            results = process_quiz_review(quiz_data)

            update_weighted_embedding(
                results['vibe_embedding'], self.movable.id, {"user_id": user.id}, 'vibe', results['user_level']
            )
            update_weighted_embedding(
                results['narrative_embedding'], self.movable.id, {"user_id": user.id}, 'narrative', results['user_level']
            )
            update_weighted_embedding(
                results['style_embedding'], self.movable.id, {"user_id": user.id}, 'style', results['user_level']
            )

            movable_vec = (results['vibe_embedding'] +
                           results['narrative_embedding'] +
                           results['style_embedding'])
            anchor_vecs = [[0.1] * len(movable_vec) for _ in self.anchors]

            sims = [cosine_similarity(movable_vec, a) for a in anchor_vecs]
            similarities_over_time.append(sims)

        print("Similarities over time:", similarities_over_time)
