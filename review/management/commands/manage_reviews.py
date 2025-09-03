# management/commands/manage_reviews.py
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from movies.models import Movie
from review.models import MovieQuizReview
from review.services.vector_review import remove_review_influence
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
        reviews = self._build_queryset(options)
        count = reviews.count()

        self.stdout.write(f"Found {count} reviews matching criteria")

        if count == 0:
            return

        if options['export']:
            self._export_reviews(reviews, options['export'])

        if options['dry_run']:
            self._dry_run(reviews)
        else:
            self._delete_reviews(reviews)

    # ------------------------
    # Queryset / Filter
    # ------------------------
    def _build_queryset(self, options):
        """Build queryset based on command-line options."""
        reviews = MovieQuizReview.objects.all()

        if options['user']:
            user = self._get_user(options['user'])
            reviews = reviews.filter(user=user)
            self.stdout.write(f"Targeting reviews from user: {user.username} (ID: {user.id})")

        if options['movie']:
            movie = self._get_movie(options['movie'])
            reviews = reviews.filter(movie=movie)
            self.stdout.write(f"Targeting reviews for movie: {movie.title} (ID: {movie.id})")

        if options['review_ids']:
            review_ids = [int(i) for i in options['review_ids'].split(',')]
            reviews = reviews.filter(id__in=review_ids)
            self.stdout.write(f"Targeting specific review IDs: {review_ids}")

        if options['all_users']:
            self.stdout.write("Targeting all reviews from all users")

        if options['all_movies']:
            self.stdout.write("Targeting all reviews for all movies")

        return reviews

    def _get_user(self, user_arg):
        """Return a User object by ID or username."""
        try:
            if user_arg.isdigit():
                return User.objects.get(id=int(user_arg))
            return User.objects.get(username=user_arg)
        except User.DoesNotExist:
            raise CommandError(f"User '{user_arg}' not found")

    def _get_movie(self, movie_id):
        """Return a Movie object by ID."""
        try:
            return Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            raise CommandError(f"Movie with ID {movie_id} not found")

    # ------------------------
    # Actions
    # ------------------------
    def _dry_run(self, reviews):
        """List reviews that would be removed."""
        self.stdout.write("DRY RUN: Would remove the following reviews:")
        for r in reviews.only("id", "user__username", "movie__title", "created_at"):
            self.stdout.write(
                f"  - Review {r.id}: User '{r.user.username}' "
                f"on movie '{r.movie.title}' (created: {r.created_at})"
            )

    def _delete_reviews(self, reviews):
        """Remove reviews and their vector influence."""
        removed_count = 0
        for r in reviews.iterator():
            try:
                remove_review_influence(r, r.movie.id)
                r.delete()
                removed_count += 1
                self.stdout.write(
                    f"Removed review {r.id} (user: {r.user.username}, movie: {r.movie.title})"
                )
            except Exception as e:
                self.stderr.write(f"Error removing review {r.id}: {str(e)}")

        self.stdout.write(f"Successfully removed {removed_count} reviews")

    def _export_reviews(self, reviews, filename):
        """Export reviews to JSON file."""
        review_data = []
        for r in reviews.iterator():
            review_data.append({
                'id': r.id,
                'user_id': r.user.id,
                'username': r.user.username,
                'movie_id': r.movie.id,
                'movie_title': r.movie.title,
                'created_at': r.created_at.isoformat(),
                'updated_at': r.updated_at.isoformat(),
                'vibe_embedding': r.vibe_embedding,
                'narrative_embedding': r.narrative_embedding,
                'style_embedding': r.style_embedding,
                'answers': r.answers,
            })

        with open(filename, 'w') as f:
            json.dump(review_data, f, indent=2)

        self.stdout.write(f"Exported {len(review_data)} reviews to {filename}")
