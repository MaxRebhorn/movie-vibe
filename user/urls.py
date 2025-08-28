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
    get_csrf_token
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='update-profile'),

    path('favorites/', FavoriteMovieListView.as_view(), name='favorite-movies'),
    path('favorites/add/<int:movie_id>/', AddFavoriteMovieView.as_view(), name='add-favorite-movie'),
    path('favorites/remove/<int:movie_id>/', RemoveFavoriteMovieView.as_view(), name='remove-favorite-movie'),
    path('get-csrf/', get_csrf_token, name='get-csrf-token'),
    path('reviews/', UserReviewListView.as_view(), name='user-reviews'),
]
