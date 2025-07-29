from rest_framework import serializers
from movies.serializers import MovieSerializer
from review.serializer import ReviewSerializer  # Uncommented
from .models import User

class UserSerializer(serializers.ModelSerializer):
    favorite_movies = MovieSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)  # Uncommented

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'favorite_movies', 'reviews']



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'full_name', 'password']

    def create(self, validated_data):
        # Use create_user method to handle password hashing etc.
        return User.objects.create_user(**validated_data)

class UpdateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['email', 'full_name', 'password']

    def update(self, instance, validated_data):
        # Update email and full_name normally
        instance.email = validated_data.get('email', instance.email)
        instance.full_name = validated_data.get('full_name', instance.full_name)

        # If password provided, set it properly (hashing)
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)

        instance.save()
        return instance