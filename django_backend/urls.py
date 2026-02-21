"""
django_backend URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Swagger/OpenAPI Schema View
schema_view = get_schema_view(
    openapi.Info(
        title="MoVi SOL API",
        default_version='v1',
        description="Movie Vibe - Semantic Movie Search API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@movievibe.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# API v1 URLs
api_v1_patterns = [
    path('movies/', include('movies.urls')),
    path('reviews/', include('review.urls')),
    path('tags/', include('tags.urls')),
    path('tmdb/', include('tmdb.urls')),
    path('users/', include('user.urls')),
    # JWT Authentication endpoints
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API v1
    path('api/v1/', include(api_v1_patterns)),
    
    # API v2 (für zukünftige Erweiterungen)
    # path('api/v2/', include('api_v2_urls')),
    
    # Swagger/OpenAPI Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)