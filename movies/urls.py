from django.contrib import admin
from django.urls import path
from movies.views import (
    MovieListCreateView,
    MovieDetailView,
    MovieSimilarView,
    MovieSearch,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('movies/', MovieListCreateView.as_view(), name='movie_list_create'),
    path('movies/<int:id>/', MovieDetailView.as_view(), name='movie_detail'),
    path('movies/<int:id>/similar/', MovieSimilarView.as_view(), name='movie_similar'),
    path('movies/search/', MovieSearch.as_view(), name='movie_search'),
]
