from .models import MovieTagAggregate, UserMovieTag, Tag
from movies.models import Movie

def get_tag_counts_for_movie(movie: Movie) -> dict[str, int]:
    """
    Gibt ein Dict {tag_name: count} zurück.
    """
    aggregates = MovieTagAggregate.objects.filter(movie=movie)
    return {agg.tag.name: agg.count for agg in aggregates}


def add_user_movie_tag(user, movie, tag_name: str) -> None:
    """
    Fügt einem Film einen neuen Tag durch einen User hinzu.
    Falls der Tag nicht existiert, wird er erstellt.
    Zählt automatisch die Aggregation hoch.
    """
    tag, _ = Tag.objects.get_or_create(name=tag_name.strip().capitalize())
    obj, created = UserMovieTag.objects.get_or_create(user=user, movie=movie, tag=tag)
    if created:
        agg, agg_created = MovieTagAggregate.objects.get_or_create(movie=movie, tag=tag)
        if not agg_created:
            agg.count += 1
        else:
            agg.count = 1
        agg.save()
