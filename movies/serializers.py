from django.utils import timezone
from rest_framework import serializers
from .models import Movie, MovieProviderLink  # both models are in the same app

class MovieSerializer(serializers.ModelSerializer):
    # ===== Streaming providers (nested) =====
    streaming_providers = serializers.SerializerMethodField()

    def get_streaming_providers(self, obj):
        # Get all MovieProviderLink related to this movie
        links = MovieProviderLink.objects.filter(movie=obj)
        result = []
        for link in links:
            result.append({
                "provider_name": link.provider.name,
                "logo_url": f"https://image.tmdb.org/t/p/w92{link.provider.logo_path}" if link.provider.logo_path else None,
                "access_type": link.access_type,
                "link": link.link,
                "country": link.country
            })
        return result

    # ===== JSON-FELDER VALIDIERUNG =====
    def validate_cast(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Cast muss eine Liste sein")
        return value

    validate_genres = validate_cast
    validate_keywords = validate_cast
    validate_composer = validate_cast

    # ===== DATUMS-VALIDIERUNG =====
    def validate_release_date(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError("Release-Datum kann nicht in der Zukunft liegen")
        return value

    # ===== ZAHLEN-BEREICHE VALIDIERUNG =====
    def validate_runtime(self, value):
        if value < 1 or value > 1000:
            raise serializers.ValidationError("Laufzeit muss zwischen 1-1000 Minuten liegen")
        return value

    def validate_avg_rating(self, value):
        if value < 0.0 or value > 10.0:
            raise serializers.ValidationError("Bewertung muss zwischen 0.0-10.0 liegen")
        return value

    # ===== STRING-FELDER VALIDIERUNG =====
    def validate_title(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Titel muss mindestens 2 Zeichen haben")
        return value

    validate_original_title = validate_title
    validate_director = validate_title

    # ===== URL-VALIDIERUNG =====
    def validate_poster_url(self, value):
        if not value.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            raise serializers.ValidationError("Ungültiges Bildformat. Erlaubt: JPG, PNG, WebP")
        return value

    validate_backdrop_url = validate_poster_url

    def validate_trailer_url(self, value):
        if value and 'youtube.com' not in value and 'vimeo.com' not in value:
            raise serializers.ValidationError("Nur YouTube/Vimeo-Links erlaubt")
        return value

    # ===== LÄNDERCODE-VALIDIERUNG =====
    def validate_country(self, value):
        if len(value) != 2:
            raise serializers.ValidationError("Ländercode muss 2-stellig sein (z.B. US, DE)")
        return value.upper()

    class Meta:
        model = Movie
        fields = '__all__'
        extra_kwargs = {
            'runtime': {
                'error_messages': {
                    'min_value': 'Laufzeit muss mindestens 1 Minute betragen',
                    'max_value': 'Laufzeit darf maximal 1000 Minuten betragen'
                }
            },
            'tmdb_id': {
                'error_messages': {
                    'unique': "Film mit dieser TMDB-ID existiert bereits"
                }
            }
        }
