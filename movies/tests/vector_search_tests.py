import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from movies.services.vector_search import (
    get_vector_from_qdrant,
    search_similar,
    get_similar_movies,
    unpack_movies
)
from qdrant_client.http.exceptions import UnexpectedResponse
import requests

class VectorSearchTests(TestCase):
    @patch('movies.services.vector_search.requests.post')
    def test_get_vector_from_qdrant_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": {
                "points": [{"vector": [0.1, 0.2, 0.3]}]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = get_vector_from_qdrant("test_collection", 123)
        self.assertEqual(result, [0.1, 0.2, 0.3])

    @patch('movies.services.vector_search.requests.post')
    def test_get_vector_from_qdrant_no_points(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": {"points": []}}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        with self.assertRaises(ValueError):
            get_vector_from_qdrant("test_collection", 123)

    @patch('movies.services.vector_search.requests.post')
    def test_search_similar_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": [
                {"id": 1, "payload": {}},
                {"id": 2, "payload": {}}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = search_similar("test_collection", [0.1, 0.2, 0.3], 2, 999)
        self.assertEqual(result, [1, 2])

    @patch('movies.services.vector_search.requests.post')
    def test_search_similar_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_post.return_value = mock_response

        with self.assertRaises(requests.exceptions.HTTPError):
            search_similar("test_collection", [0.1, 0.2, 0.3], 2, 999)

    @patch('movies.services.vector_search.client.query_points')
    def test_get_similar_movies_success(self, mock_query):
        mock_query.return_value = MagicMock(points=[
            MagicMock(payload={"movie_id": 1}),
            MagicMock(payload={"movie_id": 2})
        ])
        result = get_similar_movies(123, 2, "test_collection")
        self.assertEqual(result, [1, 2])

    @patch('movies.services.vector_search.client.query_points')
    def test_get_similar_movies_failure(self, mock_query):
        mock_query.side_effect = UnexpectedResponse("Qdrant error")
        with self.assertRaises(UnexpectedResponse):
            get_similar_movies(123, 2, "test_collection")

    def test_unpack_movies(self):
        mock_points = [
            MagicMock(payload={"movie_id": 1}),
            MagicMock(payload={"movie_id": 2}),
            MagicMock(payload={"movie_id": 3})
        ]
        result = unpack_movies(MagicMock(points=mock_points))
        self.assertEqual(result, [1, 2, 3])

    def test_unpack_movies_empty(self):
        result = unpack_movies(MagicMock(points=[]))
        self.assertEqual(result, [])