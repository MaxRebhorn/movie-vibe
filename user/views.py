# users/views.py
from django.contrib.auth import authenticate, login
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from movies.models import Movie
from movies.serializers import MovieSerializer
from review.models import Review
from review.serializer import ReviewSerializer
from .models import UserProfile
from .serializer import (  # Changed from relative import
    RegisterSerializer,
    UserSerializer,
    UpdateUserSerializer
)
# === Create Account ===
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

# === Login ===
class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"detail": "Logged in successfully"})
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# === Profile Page ===
class ProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

# === Change Profile Data ===
class UpdateProfileView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdateUserSerializer

    def get_object(self):
        return self.request.user

# === Favorite Movie List ===
class FavoriteMovieListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = UserProfile.objects.get(user=request.user)
        favorites = profile.favorite_movies.all()
        serializer = MovieSerializer(favorites, many=True)
        return Response(serializer.data)

# === Add Favorite Movie ===
class AddFavoriteMovieView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, movie_id):
        try:
            movie = Movie.objects.get(id=movie_id)
            profile = UserProfile.objects.get(user=request.user)
            profile.favorite_movies.add(movie)
            return Response({'detail': 'Movie added to favorites.'})
        except Movie.DoesNotExist:
            return Response({'error': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)

# === Remove Favorite Movie ===
class RemoveFavoriteMovieView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, movie_id):
        try:
            movie = Movie.objects.get(id=movie_id)
            profile = UserProfile.objects.get(user=request.user)
            profile.favorite_movies.remove(movie)
            return Response({'detail': 'Movie removed from favorites.'})
        except Movie.DoesNotExist:
            return Response({'error': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)

# === List of User's Reviews ===
class UserReviewListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user).select_related('movie')