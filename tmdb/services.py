import tmdbv3api
from django.conf import settings
from django.utils.dateparse import parse_date
from tmdbv3api import Movie as tmdbMovie
from tmdbv3api import TMDb

from movies.models import Movie

tmdb = TMDb()
tmdb.api_key = settings.API_KEY
tmdb.language = "en"
tmdb.debug = True
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
YOUTUBE_URL = "https://www.youtube.com/watch?v="
def get_movie_by_name(name):
    if not isinstance(name,str):
        raise TypeError
    result = tmdbv3api.Search().movies(name)
    return result

def get_movie_details(id):
    tmbd_movie_result = tmdbMovie()

    details = tmbd_movie_result.details(movie_id=id)
    return details

def extract_further_details(id):
    tmbd_movie_result = tmdbMovie()
    credits = tmbd_movie_result.credits(id)
    cast_uncleaned = credits["cast"]
    cast = []
    crew = credits["crew"]
    for actor in cast_uncleaned:
        cast.append(actor["name"])

    director = ""
    composer = []
    for crewmate in crew:
        if crewmate["job"] == "Director":
            director = crewmate["name"]
        elif crewmate["job"] == "Original Music Composer":
            composer.append(crewmate["name"])
    return {"director":director,"composer":composer,"cast":cast}

def create_movie_from_tmdb_details(details: dict) -> Movie:
    # Fallbacks
    country = details.production_countries[0].get("iso_3166_1") if details.production_countries else "N/A"

    genres = [genre["name"] for genre in details.genres] if details.genres else []

    # Credits (requires extra API call: /movie/{id}/credits)
    director = ""
    composer = []
    cast = []

    if hasattr(details, "credits"):
        for person in details.credits["crew"]:
            if person["job"] == "Director":
                director = person["name"]
            elif person["job"] == "Original Music Composer":
                composer.append(person["name"])

        cast = [actor["name"] for actor in details.credits["cast"][:10]]  # Top 10 actors

    # Keywords (requires extra API call: /movie/{id}/keywords)
    keywords = [kw["name"] for kw in details.keywords["keywords"]] if hasattr(details, "keywords") else []

    # Trailer (from /movie/{id}/videos)
    trailer_url = None
    if hasattr(details, "videos"):
        for video in details.videos["results"]:
            if video["site"] == "YouTube" and video["type"] == "Trailer":
                trailer_url = YOUTUBE_URL + video["key"]
                break

    movie = Movie.objects.create(
        title=details.title,
        original_title=details.original_title,
        synopsis=details.overview or "",
        tagline=details.tagline or "",
        language=details.original_language,
        country=country,
        release_date=parse_date(details.release_date) if details.release_date else None,
        runtime=details.runtime or 0,
        director=director,
        cast=cast,
        genres=genres,
        keywords=keywords,
        composer=composer,
        poster_url=TMDB_IMAGE_BASE + details.poster_path if details.poster_path else "",
        backdrop_url=TMDB_IMAGE_BASE + details.backdrop_path if details.backdrop_path else "",
        trailer_url=trailer_url,
        avg_rating=details.vote_average or 0.0,
        tmdb_id=details.id
    )

    return movie

