# services/search_service.py
from ..document import MovieDocument


class MovieSearchService:
    @staticmethod
    def search(query):
        """Basic search across name and description"""
        return MovieDocument.search().query(
            'multi_match',
            query=query,
            fields=[
                'title^4',
                'original_title^3',
                'title_autocomplete^5',
                'cast',
                'director',
                'synopsis',
                'tagline',
                'genres',
                'keywords',
                'composer',
                'country'
            ]
        )

    @staticmethod
    def autocomplete(query):
        """Instant search suggestions"""
        return MovieDocument.search().suggest(
            'suggestions',
            query,
            completion={'field': 'title_autocomplete'}
        )

    @staticmethod
    def filter_ingredients(ingredients):
        """Find cakes containing specific ingredients"""
        return MovieDocument.search().filter(
            'actors', ingredients=ingredients
        )