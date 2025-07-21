from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Movie

@registry.register_document
class MovieDocument(Document):
    title_autocomplete = fields.TextField(
        analyzer='autocomplete',
        search_analyzer='standard'
    )

    cast = fields.TextField(multi=True, attr='cast')
    genres = fields.TextField(multi=True, attr='genres')
    keywords = fields.TextField(multi=True, attr='keywords')
    composer = fields.TextField(multi=True, attr='composer')

    class Index:
        name = 'movies'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'analysis': {
                'analyzer': {
                    'autocomplete': {
                        'tokenizer': 'autocomplete_tokenizer'
                    }
                },
                'tokenizer': {
                    'autocomplete_tokenizer': {
                        'type': 'edge_ngram',
                        'min_gram': 2,
                        'max_gram': 15,
                        'token_chars': ['letter']
                    }
                }
            }
        }

    class Django:
        model = Movie
        fields = [
            'title',
            'original_title',
            'synopsis',
            'tagline',
            'language',
            'country',
            'release_date',
            'runtime',
            'director',
            'avg_rating'
        ]

    def prepare_title_autocomplete(self, instance):
        return instance.title.lower()

    def prepare_cast(self, instance):
        return [actor.lower() for actor in instance.cast]

    def prepare_genres(self, instance):
        return [genre.lower() for genre in instance.genres]

    def prepare_keywords(self, instance):
        return [kw.lower() for kw in instance.keywords]

    def prepare_composer(self, instance):
        return [c.lower() for c in instance.composer]
