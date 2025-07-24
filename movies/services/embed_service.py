from datetime import datetime

from movies.models import Movie
from sentence_transformers import SentenceTransformer


model = SentenceTransformer('all-MiniLM-L6-v2')


def embed_data(data):
    text_to_be_embedded = []
    for text in data:
        if isinstance(text,list):
            for item in text:
                text_to_be_embedded.append(item)
        elif isinstance(text,str):
            text_to_be_embedded.append(text)
        elif isinstance(text,datetime):
            text_to_be_embedded.append(str(text))
    embed_string = " ".join(text_to_be_embedded)
    embeddings = model.encode(embed_string)
    return embeddings

def embed_model(movie):
    #vibe embedding -> Tags, genre, composer,language,tagline
    vibe_embedding = embed_data([movie.tagline,movie.genres,movie.composer,movie.language])
    #narrative embedding -> Plot, Synopsis
    narrative_embedding = embed_data([movie.plot])
    #Style -> director,cast,release Date, country
    style_embedding = embed_data([movie.director,movie.cast,movie.synopsis])

    return {"vibe":vibe_embedding,"narrative":narrative_embedding,"style":style_embedding}