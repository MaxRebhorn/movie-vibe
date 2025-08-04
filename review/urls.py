"""
URL configuration for django_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import MovieReviewViewSet

review_create = MovieReviewViewSet.as_view({'post': 'create'})
review_list = MovieReviewViewSet.as_view({'get': 'list'})

urlpatterns = [
    path('movies/<int:movie_id>/reviews/', review_list, name='movie-review-list'),
    path('movies/<int:movie_id>/reviews/create/', review_create, name='movie-review-create'),
]
