# users/urls.py

from django.urls import path
from django.urls import path
from .views import (  # Ensure this is a relative import
    RegisterView,
    ProfileView,
    UpdateProfileView,
    FavoriteMovieListView,
    AddFavoriteMovieView,
    RemoveFavoriteMovieView,
    UserReviewListView,
    LoginView,
    get_csrf_token,
    check_auth,
    FavoriteMovieView,
is_favorite_movie
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='update-profile'),



    path('get-csrf/', get_csrf_token, name='get-csrf-token'),
    path('check-auth/', check_auth, name='check-auth'),
    path('favorites/', FavoriteMovieView.as_view(), name='favorite-movies'),  # Handles GET & POST
    path('favorites/check/<int:movie_id>/', is_favorite_movie, name='check-favorite-movie'),
    path('reviews/', UserReviewListView.as_view(), name='user-reviews'),
]
