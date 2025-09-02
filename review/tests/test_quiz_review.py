from django.test import TestCase
from unittest.mock import patch, MagicMock
from review.services import vector_review

class RemoveReviewInfluenceTest(TestCase):

    @patch("review.services.vector_review.client")  # Mock Qdrant client
    @patch("review.services.vector_review.create_combined_vector_history")  # Mock history creation
    def test_remove_review_influence_runs(self, mock_history, mock_client):
        # --- Setup fake review and movie_id ---
        class FakeReview:
            id = 1
            user_level_at_review = 50
            vibe_embedding = [0.1, 0.1, 0.1]
            narrative_embedding = [0.2, 0.2, 0.2]
            style_embedding = [0.3, 0.3, 0.3]

        review = FakeReview()
        movie_id = 42

        # --- Mock Qdrant retrieve to always return an existing vector ---
        fake_point = MagicMock()
        fake_point.vector = [0.5, 0.5, 0.5]
        fake_point.payload = {"review_id": 1}
        mock_client.retrieve.return_value = [fake_point]
        mock_client.upsert.return_value = None
        mock_client.get_collections.return_value.collections = [
            MagicMock(name="movies_vibe"),
            MagicMock(name="movies_narrative"),
            MagicMock(name="movies_style")
        ]

        # --- Call the function under test ---
        vector_review.remove_review_influence(review, movie_id)

        # --- Assertions ---
        self.assertEqual(mock_client.upsert.call_count, 3)
        mock_history.assert_called_once_with(movie_id, review.id, change_source='review_removal')
