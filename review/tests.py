from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from user.models import User
from movies.models import Movie
from review.models import Review


class ReviewViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='reviewer@example.com',
            full_name='Reviewer',
            password='reviewpass'
        )
        self.movie = Movie.objects.create(title="The Dark Knight")
        self.review_data = {
            'rating': 5,
            'text': 'Best superhero movie ever!'
        }
        self.client.force_authenticate(user=self.user)

    def test_create_review(self):
        url = reverse('movie_review_create', kwargs={'movie_id': self.movie.id})
        response = self.client.post(url, self.review_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Review.objects.filter(text=self.review_data['text']).exists())
        review = Review.objects.get(text=self.review_data['text'])
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.movie, self.movie)

    def test_list_reviews(self):
        # Create a test review
        Review.objects.create(
            user=self.user,
            movie=self.movie,
            rating=4,
            text="Excellent performance by Heath Ledger"
        )

        url = reverse('movie_review_list', kwargs={'movie_id': self.movie.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['text'], "Excellent performance by Heath Ledger")

    def test_create_review_unauthenticated(self):
        self.client.logout()
        url = reverse('movie_review_create', kwargs={'movie_id': self.movie.id})
        response = self.client.post(url, self.review_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_reviews_for_nonexistent_movie(self):
        url = reverse('movie_review_list', kwargs={'movie_id': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_invalid_rating(self):
        url = reverse('movie_review_create', kwargs={'movie_id': self.movie.id})
        invalid_data = {
            'rating': 6,  # Assuming max rating is 5
            'text': 'This should fail'
        }
        response = self.client.post(url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)