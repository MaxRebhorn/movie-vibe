from datetime import datetime
from movies.models import Movie
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_data(data):
    text_to_be_embedded = []
    for text in data:
        if not text:  # None, leere Strings, leere Listen etc. rausfiltern
            continue
        if isinstance(text, list):
            text_to_be_embedded.extend([str(item) for item in text if item])
        elif isinstance(text, (str, datetime)):
            text_to_be_embedded.append(str(text))
    if not text_to_be_embedded:
        return None  # Kein valider Input → kein Embedding
    embed_string = " ".join(text_to_be_embedded)
    return model.encode(embed_string)

def embed_model(movie):
    vibe_data = [movie.tagline, movie.genres, movie.composer, movie.language,movie.keywords]
    narrative_data = [movie.plot or movie.synopsis]  # Fallback wenn plot None
    style_data = [movie.director, movie.cast, movie.release_date, movie.country]

    vibe_embedding = embed_data(vibe_data)
    narrative_embedding = embed_data(narrative_data)
    style_embedding = embed_data(style_data)

    embeddings = {}
    if vibe_embedding is not None:
        embeddings["vibe"] = vibe_embedding
    if narrative_embedding is not None:
        embeddings["narrative"] = narrative_embedding
    if style_embedding is not None:
        embeddings["style"] = style_embedding

    return embeddings
