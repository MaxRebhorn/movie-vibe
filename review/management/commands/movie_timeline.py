from django.core.management.base import BaseCommand
from movies.models import Movie
from review.models import MovieQuizReview
from review.services.vector_review import get_collection_name
from qdrant_client import QdrantClient
from django.conf import settings
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import numpy as np
from datetime import datetime
import json

client = QdrantClient(url=settings.QDRANT_URL)


class Command(BaseCommand):
    help = 'Visualize how a movie has moved in vector space over time based on reviews'

    def add_arguments(self, parser):
        parser.add_argument(
            'movie_id',
            type=int,
            help='Movie ID to analyze'
        )
        parser.add_argument(
            '--vector-types',
            type=str,
            nargs='+',
            default=['vibe'],
            choices=['vibe', 'narrative', 'style'],
            help='Types of vectors to analyze (can pass multiple, e.g. --vector-types vibe narrative style)'
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output file for the visualization (PNG format)'
        )
        parser.add_argument(
            '--export-data',
            type=str,
            help='Export timeline data to JSON file'
        )

    def handle(self, *args, **options):
        movie_id = options['movie_id']
        vector_types = options['vector_types']

        try:
            movie = Movie.objects.get(id=movie_id)
            self.stdout.write(f"Analyzing movie: {movie.title} (ID: {movie.id})")
        except Movie.DoesNotExist:
            self.stderr.write(f"Movie with ID {movie_id} not found")
            return

        reviews = MovieQuizReview.objects.filter(movie=movie).order_by('created_at')

        if not reviews.exists():
            self.stderr.write(f"No reviews found for movie {movie.title}")
            return

        self.stdout.write(f"Found {reviews.count()} reviews for this movie")

        all_timelines = {}

        for vector_type in vector_types:
            collection = get_collection_name(vector_type)
            if not collection:
                self.stderr.write(f"Invalid vector type: {vector_type}")
                continue

            current_points = client.retrieve(collection_name=collection, ids=[movie_id])
            if not current_points:
                self.stderr.write(f"No vector found for movie {movie_id} in collection {collection}")
                continue

            current_vector = current_points[0].vector
            self.stdout.write(f"Current {vector_type} vector dimension: {len(current_vector)}")

            timeline_data = []

            timeline_data.append({
                'date': reviews.first().created_at.date().isoformat(),
                'event': 'initial_state',
                'vector': None,
                'review_id': None,
                'user': None
            })

            for review in reviews:
                vector = getattr(review, f'{vector_type}_embedding')
                if vector and len(vector) > 0:
                    timeline_data.append({
                        'date': review.created_at.date().isoformat(),
                        'event': 'review_added',
                        'vector': vector,
                        'review_id': review.id,
                        'user': review.user.username
                    })

            timeline_data.append({
                'date': datetime.now().date().isoformat(),
                'event': 'current_state',
                'vector': current_vector,
                'review_id': None,
                'user': None
            })

            all_timelines[vector_type] = timeline_data

            # Export per vector-type
            if options['export_data']:
                filename = options['export_data'].replace('.json', f'_{vector_type}.json')
                with open(filename, 'w') as f:
                    export_data = []
                    for item in timeline_data:
                        export_item = item.copy()
                        if export_item['vector'] is not None:
                            export_item['vector'] = (
                                export_item['vector'].tolist()
                                if hasattr(export_item['vector'], 'tolist')
                                else export_item['vector']
                            )
                        export_data.append(export_item)
                    json.dump(export_data, f, indent=2)
                self.stdout.write(f"Exported timeline data to {filename}")

            # Visualization
            if options['output']:
                filename = options['output'].replace('.png', f'_{vector_type}.png')
                self.create_visualization(timeline_data, vector_type, filename)

            # Print summary
            self.stdout.write(f"\nTimeline for {movie.title} ({vector_type} vectors):")
            for i, event in enumerate(timeline_data):
                if event['event'] == 'initial_state':
                    self.stdout.write(f"{i + 1}. {event['date']}: Initial state")
                elif event['event'] == 'review_added':
                    self.stdout.write(f"{i + 1}. {event['date']}: Review by {event['user']} (ID: {event['review_id']})")
                elif event['event'] == 'current_state':
                    self.stdout.write(f"{i + 1}. {event['date']}: Current state")

            self.stdout.write(f"\nTotal vector movements ({vector_type}): {len(timeline_data) - 1}")

    def create_visualization(self, timeline_data, vector_type, output_file):
        vectors = [item['vector'] for item in timeline_data if item['vector'] is not None]

        if len(vectors) < 2:
            self.stderr.write(f"Not enough vector data to create visualization for {vector_type}")
            return

        pca = PCA(n_components=2)
        vectors_2d = pca.fit_transform(vectors)

        plt.figure(figsize=(10, 8))
        plt.plot(vectors_2d[:, 0], vectors_2d[:, 1], 'o-', alpha=0.5)

        vector_idx = 0
        for i, item in enumerate(timeline_data):
            if item['vector'] is not None:
                if item['event'] == 'initial_state':
                    plt.scatter(vectors_2d[vector_idx, 0], vectors_2d[vector_idx, 1],
                                color='green', s=100, label='Initial', marker='s')
                elif item['event'] == 'review_added':
                    plt.scatter(vectors_2d[vector_idx, 0], vectors_2d[vector_idx, 1],
                                color='blue', s=50, label='Review' if vector_idx == 1 else "")
                elif item['event'] == 'current_state':
                    plt.scatter(vectors_2d[vector_idx, 0], vectors_2d[vector_idx, 1],
                                color='red', s=100, label='Current', marker='D')

                if i == 0 or i == len(timeline_data) - 1 or i % 5 == 0:
                    plt.annotate(item['date'],
                                 (vectors_2d[vector_idx, 0], vectors_2d[vector_idx, 1]),
                                 xytext=(5, 5), textcoords='offset points')

                vector_idx += 1

        plt.title(f'Vector Movement Timeline ({vector_type})')
        plt.xlabel('PCA Component 1')
        plt.ylabel('PCA Component 2')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        self.stdout.write(f"Visualization saved to {output_file}")
