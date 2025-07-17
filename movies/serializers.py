from django.utils import timezone
from rest_framework import serializers

from movies.models import Movie


class MovieSerializer(serializers.ModelSerializer):
    # ===== JSON-FELDER VALIDIERUNG =====
    # Stell sicher, dass JSON-Felder tatsächlich Listen sind
    def validate_cast(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Cast muss eine Liste sein")
        return value

    # Wiederholung für alle JSON-Felder
    validate_genres = validate_cast
    validate_keywords = validate_cast
    validate_composer = validate_cast

    # ===== DATUMS-VALIDIERUNG =====
    def validate_release_date(self, value):
        """Prüft, ob Release-Datum nicht in der Zukunft liegt"""
        if value > timezone.now().date():
            raise serializers.ValidationError("Release-Datum kann nicht in der Zukunft liegen")
        return value

    # ===== ZAHLEN-BEREICHE VALIDIERUNG =====
    def validate_runtime(self, value):
        """Prüft Filmlänge"""
        if value < 1 or value > 1000:
            raise serializers.ValidationError("Laufzeit muss zwischen 1-1000 Minuten liegen")
        return value

    def validate_avg_rating(self, value):
        """Prüft Bewertung"""
        if value < 0.0 or value > 10.0:
            raise serializers.ValidationError("Bewertung muss zwischen 0.0-10.0 liegen")
        return value

    # ===== STRING-FELDER VALIDIERUNG =====
    def validate_title(self, value):
        """Prüft Titel auf Mindestlänge"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Titel muss mindestens 2 Zeichen haben")
        return value

    # Wiederholung für ähnliche Felder
    validate_original_title = validate_title
    validate_director = validate_title

    # ===== URL-VALIDIERUNG =====
    def validate_poster_url(self, value):
        """Stell sicher, dass es sich um eine Bild-URL handelt"""
        if not value.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            raise serializers.ValidationError("Ungültiges Bildformat. Erlaubt: JPG, PNG, WebP")
        return value

    validate_backdrop_url = validate_poster_url

    def validate_trailer_url(self, value):
        """Prüft Trailer-URLs"""
        if value and 'youtube.com' not in value and 'vimeo.com' not in value:
            raise serializers.ValidationError("Nur YouTube/Vimeo-Links erlaubt")
        return value

    # ===== LÄNDERCODE-VALIDIERUNG =====
    def validate_country(self, value):
        """Prüft ISO-Ländercodes"""
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