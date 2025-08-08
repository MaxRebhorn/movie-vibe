from datetime import datetime
from movies.models import Movie
from sentence_transformers import SentenceTransformer
from tags.services import get_tag_counts_for_movie  # Dein neuer Tagservice

model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_data(data):
    text_to_be_embedded = []
    for text in data:
        if not text:
            continue
        if isinstance(text, list):
            text_to_be_embedded.extend([str(item) for item in text if item])
        elif isinstance(text, (str, datetime)):
            text_to_be_embedded.append(str(text))
    if not text_to_be_embedded:
        return None
    embed_string = " ".join(text_to_be_embedded)
    return model.encode(embed_string)

def embed_weighted_tags(tag_counts):
    weighted_tags = []
    for tag, count in tag_counts.items():
        weighted_tags.extend([tag] * count)
    if not weighted_tags:
        return None
    return embed_data(weighted_tags)

def embed_model(movie):
    vibe_data = [movie.tagline, movie.genres, movie.composer, movie.language, movie.keywords]
    narrative_data = [movie.plot or movie.synopsis]
    style_data = [movie.director, movie.cast, movie.release_date, movie.country]

    tag_counts = get_tag_counts_for_movie(movie)
    tag_embedding = embed_weighted_tags(tag_counts)

    vibe_embedding = embed_data(vibe_data)
    narrative_embedding = embed_data(narrative_data)
    style_embedding = embed_data(style_data)

    embeddings = {}
    if vibe_embedding is not None and tag_embedding is not None:
        embeddings["vibe"] = 0.6 * vibe_embedding + 0.4 * tag_embedding
    elif vibe_embedding is not None:
        embeddings["vibe"] = vibe_embedding
    elif tag_embedding is not None:
        embeddings["vibe"] = tag_embedding

    if narrative_embedding is not None:
        embeddings["narrative"] = narrative_embedding
    if style_embedding is not None:
        embeddings["style"] = style_embedding

    return embeddings
