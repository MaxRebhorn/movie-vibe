import requests
from django.conf import settings
from django.utils.dateparse import parse_date
from tmdbv3api import Movie as tmdbMovie
from tmdbv3api import TMDb
from tmdbv3api import Search
from tmdb.services.wikipedia_service import get_movie_plot
from movies.models import Movie, StreamingProvider, MovieProviderLink

tmdb = TMDb()
tmdb.api_key = settings.API_KEY
tmdb.language = "en"
tmdb.debug = True

TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
YOUTUBE_URL = "https://www.youtube.com/watch?v="
TMDB_BASE_URL = "https://api.themoviedb.org/3"


# ----------- Helper Functions -----------

def get_movie_by_name(name):
    if not isinstance(name, str):
        raise TypeError
    return Search().movies(name)


def get_movie_details(id):
    tmbd_movie_result = tmdbMovie()
    return tmbd_movie_result.details(movie_id=id)


def extract_further_details(id):
    tmbd_movie_result = tmdbMovie()
    credits = tmbd_movie_result.credits(id)
    cast_uncleaned = credits["cast"]
    cast = [actor["name"] for actor in cast_uncleaned]

    director = ""
    composer = []
    for crewmate in credits["crew"]:
        if crewmate["job"] == "Director":
            director = crewmate["name"]
        elif crewmate["job"] == "Original Music Composer":
            composer.append(crewmate["name"])
    return {"director": director, "composer": composer, "cast": cast}


def get_watch_providers(movie_id, country="DE"):
    """
    Calls TMDb /watch/providers endpoint.
    Returns dictionary for the given country (flatrate, buy, rent, link).
    """
    url = f"{TMDB_BASE_URL}/movie/{movie_id}/watch/providers"
    params = {"api_key": settings.API_KEY}
    response = requests.get(url, params=params)
    data = response.json()
    return data.get("results", {}).get(country, {})


# ----------- Main Import Function -----------

def create_movie_from_tmdb_details(details: dict, country="DE") -> Movie:
    # Fallbacks
    country_code = (
        details.production_countries[0].get("iso_3166_1")
        if details.production_countries else "N/A"
    )

    genres = [genre["name"] for genre in details.genres] if details.genres else []

    # Credits
    director = ""
    composer = []
    cast = []

    if hasattr(details, "credits"):
        for person in details.credits["crew"]:
            if person["job"] == "Director":
                director = person["name"]
            elif person["job"] == "Original Music Composer":
                composer.append(person["name"])

        cast = [actor["name"] for actor in details.credits["cast"][:10]]

    # Keywords
    keywords = (
        [kw["name"] for kw in details.keywords["keywords"]]
        if hasattr(details, "keywords") else []
    )

    # Extract the year correctly
    year = int(details.release_date[:4]) if details.release_date else None

    # Wikipedia plot
    plot = get_movie_plot(
        title=details.title,
        original_title=details.original_title,
        year=year
    )

    # Trailer
    trailer_url = None
    if hasattr(details, "videos"):
        for video in details.videos["results"]:
            if video["site"] == "YouTube" and video["type"] == "Trailer":
                trailer_url = YOUTUBE_URL + video["key"]
                break

    # Create Movie
    movie = Movie.objects.create(
        title=details.title,
        original_title=details.original_title,
        synopsis=details.overview or "",
        tagline=details.tagline or "",
        language=details.original_language,
        country=country_code,
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
        tmdb_id=details.id,
        plot=plot
    )

    # --- Streaming Providers ---
    providers_data = get_watch_providers(details.id, country=country)

    for access_type in ["flatrate", "buy", "rent"]:
        for provider in providers_data.get(access_type, []):
            provider_obj, _ = StreamingProvider.objects.get_or_create(
                tmdb_id=provider["provider_id"],
                defaults={
                    "name": provider["provider_name"],
                    "logo_path": provider.get("logo_path"),
                },
            )
            MovieProviderLink.objects.create(
                movie=movie,
                provider=provider_obj,
                access_type=access_type,
                link=providers_data.get("link"),
                country=country,
            )

    return movie
