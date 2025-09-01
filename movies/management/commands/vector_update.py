# movies/management/commands/vector_update.py
from django.core.management.base import BaseCommand
from django.db.models import Max, F, Q
from django.utils import timezone
from django.conf import settings

import numpy as np

from movies.models import Movie
from review.models import MovieQuizReview  # passe an, falls Dein App-Name anders ist
from movies.services.embed_service import generate_review_embeddings
from movies.services.vector_service import save_embedding

# question config mapping (question_id -> {"vector_type": ...})


def _user_level_from_instance_or_xp(user):
    """
    Liefert level: wenn User eine level()-Methode hat, nutze sie,
    sonst xp // 100, mindestens 1.
    """
    lvl_attr = getattr(user, "level", None)
    if callable(lvl_attr):
        try:
            lvl = lvl_attr()
            return max(1, int(lvl))
        except Exception:
            pass
    xp = getattr(user, "xp", None) or 0
    try:
        return max(1, int(xp) // 100)
    except Exception:
        return 1


def _aggregate_movie_vectors(movie):
    """
    Lädt alle Reviews zum Film, erzeugt Embeddings pro Review (mit Level-Gewichtung)
    und bildet pro Kategorie (vibe/narrative/style) das gewichtete Mittel.
    Rückgabe: dict { "vibe": list|None, "narrative": list|None, "style": list|None }
    """
    sums = {"vibe": None, "narrative": None, "style": None}
    weights = {"vibe": 0.0, "narrative": 0.0, "style": 0.0}

    # Hole alle Quiz-Reviews für den Film (sicherer: Query auf Model)
    reviews_qs = MovieQuizReview.objects.filter(movie=movie).select_related("user")
    if not reviews_qs.exists():
        return {"vibe": None, "narrative": None, "style": None}

    for r in reviews_qs.iterator():
        # Bestimme Level (Versuche: review xps -> user.xp, fallback minimal 1)
        lvl = _user_level_from_instance_or_xp(getattr(r, "user", None) or {})
        emb = generate_review_embeddings(r, user_level=lvl, question_config=QUESTION_CONFIG)

        for key in ("vibe", "narrative", "style"):
            vec = emb.get(key)
            if vec is None:
                continue
            if sums[key] is None:
                sums[key] = np.array(vec, dtype=float)
            else:
                sums[key] = sums[key] + np.array(vec, dtype=float)
            weights[key] += float(max(1, int(lvl)))

    result = {}
    for key in ("vibe", "narrative", "style"):
        if sums[key] is not None and weights[key] > 0:
            avg = (sums[key] / weights[key]).tolist()  # zu Python-List für Qdrant
            result[key] = avg
        else:
            result[key] = None
    return result


class Command(BaseCommand):
    help = "Aktualisiert Vektoren für alle Filme mit neuen Reviews (Level-gewichtete Aggregation)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--full",
            action="store_true",
            help="Erzwingt Rebuild für alle Filme mit Reviews, ignoriert 'zuletzt aktualisiert'-Marker.",
        )

    def handle(self, *args, **options):
        full = options.get("full", False)

        # Prüfe, ob Movie ein Feld hat, das den letzten Vektor-Update-Zeitpunkt speichert.
        movie_has_marker = any(f.name == "quiz_vectors_updated_at" for f in Movie._meta.get_fields())

        # Annotiere pro Movie das max(updated_at) aus den Quiz-Reviews
        base_qs = (
            Movie.objects.annotate(last_review_ts=Max("quiz_reviews__updated_at"))
            .filter(last_review_ts__isnull=False)  # nur Filme mit mindestens 1 Review
            .distinct()
        )

        if not full and movie_has_marker:
            movies_qs = base_qs.filter(
                Q(quiz_vectors_updated_at__isnull=True) | Q(last_review_ts__gt=F("quiz_vectors_updated_at"))
            )
        else:
            movies_qs = base_qs

        count = movies_qs.count()
        if count == 0:
            self.stdout.write(self.style.WARNING("Keine Filme mit neuen Reviews gefunden."))
            return

        self.stdout.write(self.style.NOTICE(f"Updating vectors für {count} Film(e)..."))

        updated = 0
        for movie in movies_qs.iterator():
            aggregated = _aggregate_movie_vectors(movie)

            any_vec = False
            for key, vec in aggregated.items():
                if vec is None:
                    continue
                payload = {
                    "movie_id": movie.id,
                    "type": key,
                    "title": getattr(movie, "title", None),
                }
                # save_embedding erwartet: (embedding: list[float], id: int, payload: dict, vector_type: str)
                save_embedding(vec, movie.id, payload, vector_type=key)
                any_vec = True

            if any_vec and movie_has_marker:
                # Marker auf dem Movie setzen, damit wir beim nächsten Lauf filtern können
                try:
                    movie.quiz_vectors_updated_at = timezone.now()
                    movie.save(update_fields=["quiz_vectors_updated_at"])
                except Exception:
                    pass

            updated += 1

        self.stdout.write(self.style.SUCCESS(f"Vektor-Update abgeschlossen. {updated} Film(e) verarbeitet."))
