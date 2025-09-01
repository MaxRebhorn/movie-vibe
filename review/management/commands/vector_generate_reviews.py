from django.core.management.base import BaseCommand
from django.db.models import Count
from movies.models import Movie
from review.models import MovieQuizReview
from review.services.embed_review import process_quiz_review
from review.services.vector_review import update_weighted_embedding
from django.conf import settings
import logging

# Set up logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Processes movie quiz reviews and updates vectors in Qdrant with weighted embeddings"

    def add_arguments(self, parser):
        parser.add_argument(
            '--movie-id',
            type=int,
            help='Process only a specific movie ID',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reprocessing of all reviews, even if already processed',
        )

    def handle(self, *args, **options):
        movie_id = options.get('movie_id')
        force_reprocess = options.get('force')

        # Get movies to process
        if movie_id:
            movies = Movie.objects.filter(id=movie_id)
            self.stdout.write(self.style.SUCCESS(f"Processing only movie ID: {movie_id}"))
        else:
            movies = Movie.objects.all()
            self.stdout.write(self.style.SUCCESS("Processing all movies"))

        total_processed = 0
        total_reviews = 0

        for movie in movies:
            self.stdout.write(self.style.NOTICE(f"\nProcessing movie: {movie.title} (ID: {movie.id})"))

            # Get all quiz reviews for this movie
            quiz_reviews = MovieQuizReview.objects.filter(movie=movie)

            if not quiz_reviews.exists():
                self.stdout.write(self.style.WARNING("  No quiz reviews found for this movie"))
                continue

            self.stdout.write(self.style.SUCCESS(f"  Found {quiz_reviews.count()} quiz reviews"))

            # Process each review
            for review in quiz_reviews:
                # Skip if already processed (unless forced)
                if not force_reprocess and review.vibe_embedding and review.narrative_embedding and review.style_embedding:
                    self.stdout.write(self.style.WARNING(f"  Review {review.id} already processed, skipping"))
                    continue

                self.stdout.write(
                    self.style.NOTICE(f"  Processing review ID: {review.id} by user: {review.user.username}"))

                try:
                    # Prepare quiz data for processing
                    quiz_data = {
                        'answers': review.answers,
                        'xp': review.user.xp if hasattr(review.user, 'xp') else 0
                    }

                    self.stdout.write(self.style.NOTICE(f"    User XP: {quiz_data['xp']}"))

                    # Process the quiz data
                    results = process_quiz_review(quiz_data)

                    self.stdout.write(self.style.SUCCESS("    Successfully generated embeddings"))
                    self.stdout.write(
                        self.style.NOTICE(f"    Narrative embedding length: {len(results['narrative_embedding'])}"))
                    self.stdout.write(
                        self.style.NOTICE(f"    Style embedding length: {len(results['style_embedding'])}"))
                    self.stdout.write(self.style.NOTICE(f"    Vibe embedding length: {len(results['vibe_embedding'])}"))
                    self.stdout.write(self.style.NOTICE(f"    User level: {results['user_level']}"))

                    # Update the review with embeddings
                    review.vibe_embedding = results['vibe_embedding']
                    review.narrative_embedding = results['narrative_embedding']
                    review.style_embedding = results['style_embedding']
                    review.save()

                    self.stdout.write(self.style.SUCCESS("    Saved embeddings to review"))

                    # Prepare payload for vector DB
                    payload = {
                        'movie_id': movie.id,
                        'movie_title': movie.title,
                        'review_id': review.id,
                        'user_id': review.user.id,
                        'user_level': results['user_level'],
                        'source': 'quiz_review'
                    }

                    # Update vectors with weighted embeddings
                    if results['vibe_embedding']:
                        self.stdout.write(self.style.NOTICE("    Updating vibe vector..."))
                        update_weighted_embedding(
                            results['vibe_embedding'],
                            movie.id,
                            payload,
                            'vibe',
                            results['user_level']
                        )

                    if results['narrative_embedding']:
                        self.stdout.write(self.style.NOTICE("    Updating narrative vector..."))
                        update_weighted_embedding(
                            results['narrative_embedding'],
                            movie.id,
                            payload,
                            'narrative',
                            results['user_level']
                        )

                    if results['style_embedding']:
                        self.stdout.write(self.style.NOTICE("    Updating style vector..."))
                        update_weighted_embedding(
                            results['style_embedding'],
                            movie.id,
                            payload,
                            'style',
                            results['user_level']
                        )

                    self.stdout.write(self.style.SUCCESS("    Successfully updated all vectors"))
                    total_reviews += 1

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"    Error processing review {review.id}: {str(e)}"))
                    logger.error(f"Error processing review {review.id}: {str(e)}")

            total_processed += 1

        self.stdout.write(self.style.SUCCESS(f"\nProcessing complete!"))
        self.stdout.write(self.style.SUCCESS(f"Processed {total_processed} movies"))
        self.stdout.write(self.style.SUCCESS(f"Updated {total_reviews} reviews"))