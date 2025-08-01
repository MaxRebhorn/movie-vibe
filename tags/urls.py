from django.urls import path
from .views import AddTagView

urlpatterns = [
    path('add/', AddTagView.as_view(), name='add-tag'),
]
