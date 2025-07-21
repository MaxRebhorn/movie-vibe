# services/search_service.py
from ..document import MovieDocument


class MovieSearchService:
    @staticmethod
    def fuzzy_search(query, fuzziness="AUTO"):
        """Führt eine Fuzzy-Suche durch"""
        return MovieDocument.search().query(
            "match",
            title={
                "query": query,
                "fuzziness": fuzziness
            }
        )

    @staticmethod
    def suggest(query):
        """Gibt Vorschläge für unvollständige Queries"""
        return MovieDocument.search().suggest(
            "suggestions",
            query,
            completion={"field": "title_suggest"}
        )

    @staticmethod
    def multi_match(query, fields=["title^3", "description"]):
        """Such in mehreren Feldern mit Gewichtung"""
        return MovieDocument.search().query(
            "multi_match",
            query=query,
            fields=fields
        )