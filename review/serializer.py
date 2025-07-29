from rest_framework import serializers
from .models import Review
from user.models import User  # Add this import

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    movie = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = [
            'id',
            'user',  # Uncommented
            'movie',
            'tags',
            'rating',
            'text',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_tags(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Tags must be a list.")
        if any(not isinstance(tag, str) for tag in value):
            raise serializers.ValidationError("All tags must be strings.")
        return value

    def validate_rating(self, value):
        if not (1 <= value <= 10):
            raise serializers.ValidationError("Rating must be between 1 and 10.")
        return value