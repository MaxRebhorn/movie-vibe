# myapp/management/commands/fill_movies.py
import json
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from movies.models import Movie

TMDB_API_KEY = settings.API_KEY
TMDB_BASE_URL = "https://api.themoviedb.org/3/movie/"

class Command(BaseCommand):
    help = "Fill missing movie data from TMDB"

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of movies to process'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show output without saving changes'
        )

    def handle(self, *args, **options):
        movies = Movie.objects.all()
        if options['limit']:
            movies = movies[:options['limit']]

        for i, movie in enumerate(movies, 1):
            self.stdout.write(f"\n[{i}/{len(movies)}] Processing: {movie.title} (TMDB ID: {movie.tmdb_id})")

            url = f"{TMDB_BASE_URL}{movie.tmdb_id}?api_key={TMDB_API_KEY}&append_to_response=credits,videos,keywords"
            try:
                response = requests.get(url)
                data = response.json()

                if options['dry_run']:
                    self.stdout.write(json.dumps(data, indent=2))
                    self.stdout.write("[DRY-RUN] Skipping save")
                    continue

                # Basic fields
                movie.synopsis = movie.synopsis or data.get('overview', '')
                movie.plot = movie.plot or data.get('overview', '')
                movie.tagline = movie.tagline or data.get('tagline', '')
                movie.language = movie.language or data.get('original_language', '')
                movie.release_date = movie.release_date or data.get('release_date', None)
                movie.runtime = movie.runtime or data.get('runtime', 0)
                movie.poster_url = movie.poster_url or (f"https://image.tmdb.org/t/p/original{data.get('poster_path')}" if data.get('poster_path') else None)
                movie.backdrop_url = movie.backdrop_url or (f"https://image.tmdb.org/t/p/original{data.get('backdrop_path')}" if data.get('backdrop_path') else None)

                # Crew
                crew = data.get('credits', {}).get('crew', [])
                directors = [c['name'] for c in crew if c['job'] == 'Director']
                movie.director = movie.director or (directors[0] if directors else '')

                composer = next((c['name'] for c in data.get('credits', {}).get('crew', []) if
                                 c['job'] == 'Original Music Composer'), None)
                if composer:
                    movie.composer = movie.composer or [composer]
                # Cast
                cast = data.get('credits', {}).get('cast', [])
                movie.cast = movie.cast or [c['name'] for c in cast[:10]]

                # Genres
                genres = data.get('genres', [])
                movie.genres = movie.genres or [g['name'] for g in genres]

                # Keywords
                keywords = data.get('keywords', {}).get('keywords', [])
                movie.keywords = movie.keywords or [k['name'] for k in keywords]

                # Videos / Trailer
                videos = data.get('videos', {}).get('results', [])
                trailers = [v for v in videos if v['type'] == 'Trailer' and v['site'] == 'YouTube']
                movie.trailer_url = movie.trailer_url or (f"https://www.youtube.com/watch?v={trailers[0]['key']}" if trailers else None)

                movie.save()
                self.stdout.write(self.style.SUCCESS(f"Updated {movie.title}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed {movie.title}: {e}"))
