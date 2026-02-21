

import traceback
from datetime import datetime

from rest_framework.decorators import action
from rest_framework import status, viewsets, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from movies.models import Movie
from .models import MovieQuizReview, VectorHistory
from review.services.embed_review import process_quiz_review
from review.services.vector_review import remove_review_influence, update_weighted_embedding

import json
import logging

from .serializer import ReviewSerializer

logger = logging.getLogger(__name__)


class MovieQuizReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=True, methods=['post'])
    def submit_quiz_review(self, request, movie_id=None):
        logger.info(f"📥 Received quiz review request for movie {movie_id}")
        logger.info(f"📦 Request data: {request.data}")
        logger.info(f"👤 User: {request.user} (authenticated: {request.user.is_authenticated})")

        try:
            movie = get_object_or_404(Movie, pk=movie_id)
            logger.info(f"🎬 Found movie: {movie.title} (ID: {movie.id})")

            user = request.user
            if not user.is_authenticated:
                from django.contrib.auth.models import User
                user, created = User.objects.get_or_create(
                    username="test_user_debug",
                    defaults={'is_active': True, 'password': 'test'}
                )
                logger.info(f"👤 Using debug user: {user.username} (created: {created})")

            existing_review = MovieQuizReview.objects.filter(user=user, movie=movie).first()
            if existing_review:
                logger.info(f"🔄 User already has a review. Removing old review influence.")
                remove_review_influence(existing_review, movie.id)
                existing_review.delete()
                logger.info(f"🗑️ Old review deleted.")

            quiz_data = request.data
            if 'answers' not in quiz_data:
                logger.warning("⚠️ No 'answers' key in quiz data")
                return Response({'error': 'Missing answers data'}, status=status.HTTP_400_BAD_REQUEST)

            results = process_quiz_review(quiz_data)
            logger.info(
                f"✅ Embeddings generated - Narrative: {len(results['narrative_embedding'])} dim, "
                f"Style: {len(results['style_embedding'])} dim, "
                f"Vibe: {len(results['vibe_embedding'])} dim"
            )

            xp = quiz_data.get('xp', 0)
            logger.info(f"⭐ XP to award: {xp}")

            quiz_review = MovieQuizReview.objects.create(
                user=user,
                movie=movie,
                answers=quiz_data['answers'],
                vibe_embedding=results['vibe_embedding'],
                narrative_embedding=results['narrative_embedding'],
                style_embedding=results['style_embedding']
            )
            logger.info(f"💾 New quiz review created: {quiz_review.id}")

            payload = {
                'movie_id': movie.id,
                'movie_title': movie.title,
                'last_updated': datetime.now().isoformat(),
                'user_id': user.id,
                'review_id': quiz_review.id
            }
            logger.info(f"📦 Vector DB payload: {payload}")

            for emb_type in ['vibe', 'narrative', 'style']:
                embedding = results.get(f'{emb_type}_embedding')
                if not embedding:
                    logger.warning(f"⚠️ {emb_type} embedding missing, skipping vector DB update")
                    continue
                try:
                    update_weighted_embedding(
                        embedding,
                        movie.id,
                        payload,
                        emb_type,
                        results['user_level']
                    )
                    logger.info(f"✅ {emb_type.capitalize()} embedding updated in vector DB")
                except Exception as e:
                    logger.error(f"❌ Vector DB error for {emb_type}: {str(e)}")
                    return Response({'error': f'Vector DB update failed for {emb_type}: {str(e)}'},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Update vector_effect per type
            for emb_type in ['vibe', 'narrative', 'style']:
                embedding = results.get(f'{emb_type}_embedding')
                if not embedding:
                    continue
                if f'{emb_type}_effect' not in quiz_review.vector_effect:
                    quiz_review.vector_effect[f'{emb_type}_effect'] = embedding

            quiz_review.user_level_at_review = results['user_level']
            quiz_review.save()

            # Create combined vector history snapshot
            VectorHistory.objects.create(
                movie=movie,
                vibe_vector=results['vibe_embedding'],
                narrative_vector=results['narrative_embedding'],
                style_vector=results['style_embedding'],
                source_id=quiz_review.id,
                change_source='review',
                description=f"Review by {user.username} (Level: {results['user_level']})"
            )

            response_data = {
                'AIContext.txt': 'quiz review submitted',
                'review_id': quiz_review.id,
                'movie_id': movie.id,
                'movie_title': movie.title,
                'user_id': user.id,
                'embeddings_generated': {
                    'narrative': len(results['narrative_embedding']) > 0,
                    'style': len(results['style_embedding']) > 0,
                    'vibe': len(results['vibe_embedding']) > 0
                },
                'user_level': results['user_level'],
                'xp_awarded': xp
            }
            logger.info(f"🎉 Success! Response: {response_data}")

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"💥 Critical error in submit_quiz_review: {str(e)}")
            logger.error(f"💥 Traceback: {traceback.format_exc()}")
            return Response({'error': f'Internal server error: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
