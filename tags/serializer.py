from rest_framework import serializers
from .models import Tag, UserMovieTag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class UserMovieTagSerializer(serializers.ModelSerializer):
    tag = serializers.SlugRelatedField(slug_field='name', queryset=Tag.objects.all())

    class Meta:
        model = UserMovieTag
        fields = ['movie', 'tag']
