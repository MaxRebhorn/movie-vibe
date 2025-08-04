from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from movies.models import Movie
from review.models import Review
from datetime import date


class ReviewViewSetTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test user
        User = get_user_model()
        cls.user = User.objects.create_user(
            username='reviewer',
            email='reviewer@example.com',
            password='reviewpass',
            first_name='Test',
            last_name='User'
        )

        # Create complete test movie
        cls.movie = Movie.objects.create(
            title="The Dark Knight",
            original_title="The Dark Knight",
            synopsis="Test synopsis",
            tagline="Test tagline",
            language="en",
            country="US",
            release_date=date(2008, 7, 18),
            runtime=152,
            director="Christopher Nolan",
            cast=["Christian Bale", "Heath Ledger"],
            genres=["Action", "Crime"],
            keywords=["superhero", "batman"],
            composer=["Hans Zimmer"],
            poster_url="http://example.com/poster.jpg",
            backdrop_url="http://example.com/backdrop.jpg",
            tmdb_id=155
        )

    def setUp(self):
        self.valid_review_data = {
            'rating': 5,
            'text': 'Best superhero movie ever!',
            'tags': ['action', 'superhero']
        }
        self.client.force_authenticate(user=self.user)

    def test_create_review(self):
        url = reverse('movie-review-create', kwargs={'movie_id': self.movie.id})
        response = self.client.post(
            url,
            data=self.valid_review_data,
            format='json'  # Explicitly set format
        )

        # Debug output if test fails
        if response.status_code != status.HTTP_201_CREATED:
            print("Response errors:", response.json())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Review.objects.filter(text=self.valid_review_data['text']).exists())

    def test_list_reviews(self):
        # Create a test review first
        Review.objects.create(
            user=self.user,
            movie=self.movie,
            rating=4,
            text="Excellent performance",
            tags=['drama']
        )

        url = reverse('movie-review-list', kwargs={'movie_id': self.movie.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)