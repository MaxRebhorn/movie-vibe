# movies/documents.py
from django_elasticsearch_dsl     import Document
from django_elasticsearch_dsl.registries import registry
from .models import Movie

@registry.register_document
class MovieDocument(Document):
    class Index:
        name = 'movies'

    class Django:
        model = Movie
        fields = [
            'title',
            'director',
            'language',
            'cast',
        ]
