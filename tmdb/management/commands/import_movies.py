import json
import time

from django.core.management.base import BaseCommand, CommandError
from tmdb.services import  get_movie_by_name, get_movie_details, create_movie_from_tmdb_details

class Command(BaseCommand):
    help = "Imports a list of movies from a JSON file and adds them via the TMDb API"

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to JSON file with movie titles')
        parser.add_argument('--delay', type=float, default=1.0, help='Delay in seconds between requests')

    def handle(self, *args, **options):
        json_path = options["json_file"]
        delay = options["delay"]

        try:
            with open(json_path, 'r') as f:
                movie_titles = json.load(f)
        except Exception as e:
            raise CommandError(f"Failed to load JSON file: {e}")

        if not isinstance(movie_titles, list):
            raise CommandError("The JSON file must contain a list of movie titles.")

        for title in movie_titles:
            self.stdout.write(f"🔍 Searching: {title}")
            results = get_movie_by_name(title)
            if not results:
                self.stderr.write(f"❌ No match for '{title}'")
                continue

            movie_data = results[0]  # First result
            movie_id = movie_data.id

            try:
                details = get_movie_details(movie_id)
                movie = create_movie_from_tmdb_details(details)
                self.stdout.write(self.style.SUCCESS(f"✅ Added: {movie.title}"))
            except Exception as e:
                self.stderr.write(f"⚠️  Error adding '{title}': {e}")

            time.sleep(delay)
