# users/tests.py
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from movies.models import Movie
from review.models import Review
from .models import UserProfile


class UserViewsTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.user = User.objects.create_user(**self.user_data)
        # Create the profile manually since signals might not be loaded in tests
        self.profile = UserProfile.objects.create(user=self.user)

        # Create a test movie with all required fields
        self.movie = Movie.objects.create(
            title='Test Movie',
            original_title='Test Movie Original',
            synopsis='Test synopsis',
            plot='Test plot',
            tagline='Test tagline',
            language='English',
            country='US',
            release_date='2023-01-01',
            runtime=120,
            director='Test Director',
            cast=['Actor 1', 'Actor 2'],
            genres=['Action', 'Drama'],
            keywords=['keyword1', 'keyword2'],
            composer=['Composer 1'],
            poster_url='https://example.com/poster.jpg',
            backdrop_url='https://example.com/backdrop.jpg',
            trailer_url='https://example.com/trailer.mp4',
            avg_rating=7.5,
            tmdb_id=12345
        )

        # Create a test review with all required fields
        self.review = Review.objects.create(
            user=self.user,
            movie=self.movie,
            rating=5,
            text='Great movie!',
            tags=['awesome', 'must-watch']
        )

        # URLs
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.profile_url = reverse('profile')
        self.update_profile_url = reverse('update-profile')
        self.favorites_url = reverse('favorite-movies')
        self.add_favorite_url = reverse('add-favorite-movie', args=[self.movie.id])
        self.remove_favorite_url = reverse('remove-favorite-movie', args=[self.movie.id])
        self.user_reviews_url = reverse('user-reviews')

    def test_register_view(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

        # Verify profile was created
        user = User.objects.get(username='newuser')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_login_view_success(self):
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Logged in successfully')

    def test_login_view_failure(self):
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Invalid credentials')

    def test_profile_view_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['full_name'], 'Test User')

    def test_profile_view_unauthenticated(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_profile_view(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.client.put(self.update_profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh user from db
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')

    def test_update_profile_password(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'newpassword123'
        }
        response = self.client.put(self.update_profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_favorite_movie_list_view(self):
        # Add movie to favorites
        self.profile.favorite_movies.add(self.movie)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.favorites_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Movie')

    def test_add_favorite_movie_view(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.add_favorite_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Movie added to favorites.')

        # Verify movie was added
        self.assertTrue(self.profile.favorite_movies.filter(id=self.movie.id).exists())

    def test_add_favorite_movie_view_invalid_movie(self):
        invalid_url = reverse('add-favorite-movie', args=[999])
        self.client.force_authenticate(user=self.user)
        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Movie not found')

    def test_remove_favorite_movie_view(self):
        # Add movie first
        self.profile.favorite_movies.add(self.movie)

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.remove_favorite_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Movie removed from favorites.')

        # Verify movie was removed
        self.assertFalse(self.profile.favorite_movies.filter(id=self.movie.id).exists())

    def test_remove_favorite_movie_view_invalid_movie(self):
        invalid_url = reverse('remove-favorite-movie', args=[999])
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Movie not found')

    def test_user_review_list_view(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.user_reviews_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['text'], 'Great movie!')
        self.assertEqual(response.data[0]['rating'], 5)