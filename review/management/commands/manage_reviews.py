# [file name]: management/commands/manage_reviews.py
# [file content begin]
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from movies.models import Movie
from review.models import MovieQuizReview
from review.services.vector_review import remove_review_influence
from datetime import datetime
import json


class Command(BaseCommand):
    help = 'Manage movie reviews - remove specific reviews or all reviews for user/movie'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Username or user ID to target reviews'
        )
        parser.add_argument(
            '--movie',
            type=int,
            help='Movie ID to target reviews'
        )
        parser.add_argument(
            '--review-ids',
            type=str,
            help='Comma-separated list of specific review IDs to remove'
        )
        parser.add_argument(
            '--all-users',
            action='store_true',
            help='Remove all reviews from all users (use with caution)'
        )
        parser.add_argument(
            '--all-movies',
            action='store_true',
            help='Remove all reviews for all movies (use with caution)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be removed without actually removing anything'
        )
        parser.add_argument(
            '--export',
            type=str,
            help='Export reviews to JSON file before removal'
        )

    def handle(self, *args, **options):
        # Determine which reviews to target
        reviews = MovieQuizReview.objects.all()

        if options['user']:
            try:
                if options['user'].isdigit():
                    user = User.objects.get(id=int(options['user']))
                else:
                    user = User.objects.get(username=options['user'])
                reviews = reviews.filter(user=user)
                self.stdout.write(f"Targeting reviews from user: {user.username} (ID: {user.id})")
            except User.DoesNotExist:
                raise CommandError(f"User '{options['user']}' not found")

        if options['movie']:
            try:
                movie = Movie.objects.get(id=options['movie'])
                reviews = reviews.filter(movie=movie)
                self.stdout.write(f"Targeting reviews for movie: {movie.title} (ID: {movie.id})")
            except Movie.DoesNotExist:
                raise CommandError(f"Movie with ID {options['movie']} not found")

        if options['review_ids']:
            review_ids = [int(id) for id in options['review_ids'].split(',')]
            reviews = reviews.filter(id__in=review_ids)
            self.stdout.write(f"Targeting specific review IDs: {review_ids}")

        if options['all_users']:
            self.stdout.write("Targeting all reviews from all users")

        if options['all_movies']:
            self.stdout.write("Targeting all reviews for all movies")

        # Count reviews before any action
        count_before = reviews.count()
        self.stdout.write(f"Found {count_before} reviews matching criteria")

        if count_before == 0:
            self.stdout.write("No reviews found matching criteria")
            return

        # Export reviews if requested
        if options['export']:
            self.export_reviews(reviews, options['export'])

        # Dry run - just show what would be done
        if options['dry_run']:
            self.stdout.write("DRY RUN: Would remove the following reviews:")
            for review in reviews:
                self.stdout.write(
                    f"  - Review {review.id}: User '{review.user.username}' "
                    f"on movie '{review.movie.title}' "
                    f"(created: {review.created_at})"
                )
            return

        # Actually remove the reviews
        removed_count = 0
        for review in reviews:
            try:
                # Remove influence from vector store
                remove_review_influence(review, review.movie.id)

                # Delete the review
                review.delete()
                removed_count += 1
                self.stdout.write(
                    f"Removed review {review.id} (user: {review.user.username}, "
                    f"movie: {review.movie.title})"
                )
            except Exception as e:
                self.stderr.write(f"Error removing review {review.id}: {str(e)}")

        self.stdout.write(f"Successfully removed {removed_count} reviews")

    def export_reviews(self, reviews, filename):
        """Export reviews to JSON file"""
        review_data = []
        for review in reviews:
            review_data.append({
                'id': review.id,
                'user_id': review.user.id,
                'username': review.user.username,
                'movie_id': review.movie.id,
                'movie_title': review.movie.title,
                'created_at': review.created_at.isoformat(),
                'updated_at': review.updated_at.isoformat(),
                'vibe_embedding': review.vibe_embedding,
                'narrative_embedding': review.narrative_embedding,
                'style_embedding': review.style_embedding,
                'answers': review.answers
            })

        with open(filename, 'w') as f:
            json.dump(review_data, f, indent=2)

        self.stdout.write(f"Exported {len(review_data)} reviews to {filename}")
# [file content end]