from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Review

User = get_user_model()

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Shows username instead of ID
    movie = serializers.StringRelatedField()  # Shows movie title instead of ID

    class Meta:
        model = Review
        fields = [
            'id',
            'user',
            'movie',
            'rating',
            'text',
            'tags',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'movie', 'created_at', 'updated_at']

    def validate_rating(self, value):
        if not 1 <= value <= 10:
            raise serializers.ValidationError("Rating must be between 1 and 10.")
        return value

    def validate_tags(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Tags must be a list.")
        if any(not isinstance(tag, str) for tag in value):
            raise serializers.ValidationError("All tags must be strings.")
        return value