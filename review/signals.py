from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MovieQuizReview
from movies.services.vector_service import embed_data, save_embedding


@receiver(post_save, sender=MovieQuizReview)
def update_movie_embedding(sender, instance: MovieQuizReview, created, **kwargs):
    if not created:
        return  # nur neue Reviews behandeln

    movie = instance.movie

    # Embedding der neuen Review erzeugen
    narrative_data = instance.answers.get('narrative', [])
    vibe_data = instance.answers.get('vibe', [])
    style_data = instance.answers.get('style', [])

    vibe_embedding = embed_data(vibe_data)
    narrative_embedding = embed_data(narrative_data)
    style_embedding = embed_data(style_data)

    # Level-basiertes Gewicht
    user_weight = max(1, instance.user.level)  # z.B. Level 1 minimaler Einfluss

    # Embedding mit Gewicht in Qdrant speichern
    if vibe_embedding is not None:
        weighted_vibe = vibe_embedding * user_weight
        save_embedding(weighted_vibe.tolist(), id=movie.id, payload={"type": "vibe"}, vector_type="vibe")

    if narrative_embedding is not None:
        weighted_narrative = narrative_embedding * user_weight
        save_embedding(weighted_narrative.tolist(), id=movie.id, payload={"type": "narrative"}, vector_type="narrative")

    if style_embedding is not None:
        weighted_style = style_embedding * user_weight
        save_embedding(weighted_style.tolist(), id=movie.id, payload={"type": "style"}, vector_type="style")
