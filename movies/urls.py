from django.urls import path
from movies.views import (
    MovieListCreateView,
    MovieDetailView,
    MovieSimilarView,
    MovieSearch,
)

urlpatterns = [
    # Entferne das "movies/" vor jedem Pfad, weil es schon in der Haupt-URL ist!
    path('', MovieListCreateView.as_view(), name='movie_list_create'),
    path('<int:id>/', MovieDetailView.as_view(), name='movie_detail'),
    path('<int:id>/similar/', MovieSimilarView.as_view(), name='movie_similar'),
    path('search/', MovieSearch.as_view(), name='movie_search'),
]