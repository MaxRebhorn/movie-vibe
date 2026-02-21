import json
import time

from django.core.management.base import BaseCommand, CommandError

from movies.document import MovieDocument
from movies.signals import update_movie_index, delete_movie_index
from tmdb.services.api_service import (
    get_movie_by_name,
    get_movie_details,
    create_movie_from_tmdb_details
)
from movies.models import Movie


#Example command python main.py import_movies



class Command(BaseCommand):
    help = "Imports a list of movies from a JSON file and adds them via the TMDb API"

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to JSON file with movie titles')
        parser.add_argument('--delay', type=float, default=1.0, help='Delay in seconds between requests')

    def handle(self, *args, **options):
        json_path = options["json_file"]
        delay = options["delay"]
        imported_movies = []  # Track successfully imported movies

        try:
            with open(json_path, 'r') as f:
                movie_titles = json.load(f)
        except Exception as e:
            raise CommandError(f"Failed to load JSON file: {e}")

        if not isinstance(movie_titles, list):
            raise CommandError("The JSON file must contain a list of movie titles.")

        # Disconnect signals to prevent automatic indexing
        from django.db.models import signals
        from movies.signals import update_movie_index, delete_movie_index
        signals.post_save.disconnect(update_movie_index, sender=Movie)
        signals.post_delete.disconnect(delete_movie_index, sender=Movie)

        try:
            for title in movie_titles:
                self.stdout.write(f"🔍 Searching: {title}")
                results = get_movie_by_name(title)
                if not results:
                    self.stderr.write(f"❌ No match for '{title}'")
                    continue

                movie_data = results[0]
                movie_id = movie_data.id

                try:
                    details = get_movie_details(movie_id)

                    # Delete existing movie if it exists (without triggering signals)
                    Movie.objects.filter(tmdb_id=movie_id).delete()

                    # Create new movie
                    movie = create_movie_from_tmdb_details(details)
                    imported_movies.append(movie)
                    self.stdout.write(f"✅ Imported: {movie.title}")

                except Exception as e:
                    self.stderr.write(f"⚠️ Error updating '{title}': {e}")

                time.sleep(delay)

            # Bulk index all imported movies at the end
            if imported_movies:
                self.stdout.write("\n🚀 Starting bulk indexing...")
                from django_elasticsearch_dsl.registries import registry
                success_count = 0

                for movie in imported_movies:
                    try:
                        registry.update(movie)
                        success_count += 1
                    except Exception as e:
                        self.stderr.write(f"⚠️ Failed to index {movie.title}: {e}")

                self.stdout.write(self.style.SUCCESS(
                    f"\n🎉 Successfully indexed {success_count}/{len(imported_movies)} movies"
                ))

        finally:
            # Always reconnect signals when done
            signals.post_save.connect(update_movie_index, sender=Movie)
            signals.post_delete.connect(delete_movie_index, sender=Movie)
