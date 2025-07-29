from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from movies.models import Movie
from review.models import Review

User = get_user_model()

class UserAuthTests(APITestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'full_name': 'Test User',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.movie = Movie.objects.create(title="Inception")

    def test_user_registration(self):
        url = reverse('register')
        data = {
            'email': 'new@example.com',
            'full_name': 'New User',
            'password': 'newpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='new@example.com').exists())

    def test_user_login(self):
        url = reverse('login')
        data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Logged in successfully')

    def test_invalid_login(self):
        url = reverse('login')
        data = {
            'email': self.user_data['email'],
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class UserProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='profile@example.com',
            full_name='Profile User',
            password='profilepass'
        )
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'profile@example.com')

    def test_update_profile(self):
        url = reverse('update-profile')
        data = {
            'full_name': 'Updated Name',
            'email': 'updated@example.com'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, 'Updated Name')
        self.assertEqual(self.user.email, 'updated@example.com')

class FavoriteMovieTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='favorites@example.com',
            full_name='Favorites User',
            password='favoritespass'
        )
        self.movie1 = Movie.objects.create(title="The Shawshank Redemption")
        self.movie2 = Movie.objects.create(title="The Godfather")
        self.client.force_authenticate(user=self.user)

    def test_add_favorite_movie(self):
        url = reverse('add-favorite-movie', args=[self.movie1.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.favorite_movies.filter(id=self.movie1.id).exists())

    def test_remove_favorite_movie(self):
        self.user.favorite_movies.add(self.movie1)
        url = reverse('remove-favorite-movie', args=[self.movie1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.user.favorite_movies.filter(id=self.movie1.id).exists())

    def test_list_favorite_movies(self):
        self.user.favorite_movies.add(self.movie1, self.movie2)
        url = reverse('favorite-movies')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        titles = [movie['title'] for movie in response.data]
        self.assertIn("The Shawshank Redemption", titles)
        self.assertIn("The Godfather", titles)

class UserReviewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='reviews@example.com',
            full_name='Reviews User',
            password='reviewspass'
        )
        self.movie = Movie.objects.create(title="Pulp Fiction")
        self.review = Review.objects.create(
            user=self.user,
            movie=self.movie,
            rating=5,
            text="Great movie!"
        )
        self.client.force_authenticate(user=self.user)

    def test_list_user_reviews(self):
        url = reverse('user-reviews')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['text'], "Great movie!")