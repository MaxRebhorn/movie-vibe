from datetime import datetime
from movies.models import Movie
from tags.service import get_tag_counts_for_movie  # Dein neuer Tagservice
from review.models import MovieQuizReview
import os

_model = None


def get_model():
    """
    Lazy-load SentenceTransformer only when actually needed.
    This avoids breaking CI or migrations if the package isn't installed.
    """
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise RuntimeError(
                "⚠️ sentence-transformers not available. "
                "Install it locally if you want to run embedding features."
            )
        model_name = os.getenv("SENTENCE_MODEL", "all-MiniLM-L6-v2")
        _model = SentenceTransformer(model_name)
    return _model


def process_quiz_review(quiz_data):
    """
    Process quiz answers and generate embeddings for narrative, style, and vibe
    using the provided vector_type information.
    """
    print(f"🔍 Processing quiz data with keys: {list(quiz_data.keys())}")

    answers = quiz_data['answers']
    print(f"📋 Answer keys: {list(answers.keys())}")

    narrative_bucket = []
    style_bucket = []
    vibe_bucket = []

    for key, value in answers.items():
        print(f"   Processing key: {key}, value: {value}")

        if isinstance(value, dict) and 'vector_type' in value:
            vector_type = value['vector_type']
            print(f"   → Vector type: {vector_type}, values: {value['values']}")

            if vector_type == 'narrative':
                narrative_bucket.extend(value['values'])
            elif vector_type == 'style':
                style_bucket.extend(value['values'])
            elif vector_type == 'vibe':
                vibe_bucket.extend(value['values'])
        else:
            print(f"   → Simple value: {value}")
            if key.startswith('narrative_'):
                narrative_bucket.append(value)
            elif key.startswith('style_'):
                style_bucket.append(value)
            elif key.startswith('vibe_'):
                vibe_bucket.append(value)

    print(f"📦 Narrative bucket: {narrative_bucket}")
    print(f"📦 Style bucket: {style_bucket}")
    print(f"📦 Vibe bucket: {vibe_bucket}")

    narrative_text = " ".join(narrative_bucket) if narrative_bucket else ""
    style_text = " ".join(style_bucket) if style_bucket else ""
    vibe_text = " ".join(vibe_bucket) if vibe_bucket else ""

    print(f"📝 Narrative text: '{narrative_text}'")
    print(f"📝 Style text: '{style_text}'")
    print(f"📝 Vibe text: '{vibe_text}'")

    if narrative_text or style_text or vibe_text:
        model = get_model()
    else:
        model = None

    narrative_embedding = model.encode(narrative_text).tolist() if model and narrative_text else []
    style_embedding = model.encode(style_text).tolist() if model and style_text else []
    vibe_embedding = model.encode(vibe_text).tolist() if model and vibe_text else []

    print(f"🧮 Narrative embedding length: {len(narrative_embedding)}")
    print(f"🧮 Style embedding length: {len(style_embedding)}")
    print(f"🧮 Vibe embedding length: {len(vibe_embedding)}")

    xp = quiz_data.get('xp', 0)
    user_level = xp // 100

    print(f"⭐ XP: {xp}, User level: {user_level}")

    return {
        'narrative_embedding': narrative_embedding,
        'style_embedding': style_embedding,
        'vibe_embedding': vibe_embedding,
        'user_level': user_level,
    }
