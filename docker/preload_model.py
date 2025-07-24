import os
from sentence_transformers import SentenceTransformer


def preload_models():
    print("🔮 Preloading embedding models...")

    # Create cache directory if needed
    os.makedirs("/app/model_cache", exist_ok=True)

    # Preload small default model (80MB)
    model = SentenceTransformer(
        'all-MiniLM-L6-v2',
        cache_folder="/app/model_cache",
        device='cpu'
    )
    print(f"✅ Preloaded: {model._model_name}")


if __name__ == "__main__":
    preload_models()