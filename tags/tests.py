from django.test import TestCase
from django.contrib.auth import get_user_model
from movies.models import Movie
from tags.models import Tag, UserMovieTag, MovieTagAggregate
from .service import get_tag_counts_for_movie

User = get_user_model()

class TagServiceTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="test")
        self.user2 = User.objects.create_user(username="user2", password="test")

        self.movie = Movie.objects.create(
            title="Test Movie",
            original_title="Test Movie",
            synopsis="A test synopsis",
            plot="A test plot",
            tagline="Test tagline",
            language="EN",
            country="US",
            release_date="2020-01-01",
            runtime=90,
            director="Test Director",
            cast=[],
            genres=[],
            keywords=[],
            composer=[],
            poster_url="http://example.com/poster.jpg",
            backdrop_url="http://example.com/backdrop.jpg",
            trailer_url=None,
            avg_rating=7.5,
            tmdb_id=1001
        )

        self.tag1 = Tag.objects.create(name="cute")
        self.tag2 = Tag.objects.create(name="depressing")

        # Create UserMovieTags
        UserMovieTag.objects.create(user=self.user1, movie=self.movie, tag=self.tag1)
        UserMovieTag.objects.create(user=self.user2, movie=self.movie, tag=self.tag1)
        UserMovieTag.objects.create(user=self.user1, movie=self.movie, tag=self.tag2)

        # Create corresponding MovieTagAggregate records
        MovieTagAggregate.objects.create(movie=self.movie, tag=self.tag1, count=2)
        MovieTagAggregate.objects.create(movie=self.movie, tag=self.tag2, count=1)

    def test_tag_counting_service(self):
        counts = get_tag_counts_for_movie(self.movie)
        self.assertEqual(counts["cute"], 2)
        self.assertEqual(counts["depressing"], 1)
