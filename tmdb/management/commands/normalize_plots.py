import re
import threading
from concurrent.futures import ThreadPoolExecutor

import torch
from django.core.management.base import BaseCommand
from movies.models import Movie
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util


class Command(BaseCommand):
    help = "Normalize movie plots with semantic intelligence"

    def __init__(self):
        super().__init__()
        self.character_embedding_cache = {}
        self.canonical_character_map = {}
        self.lock = threading.Lock()

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='Run normalization on a single random movie for debugging',
        )
        parser.add_argument(
            '--max-workers',
            type=int,
            default=2,
            help='Number of threads to use for parallel processing',
        )
        parser.add_argument(
            '--chunk-size',
            type=int,
            default=250,
            help='Size of text chunks for processing',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Number of movies to process in each batch',
        )

    def handle(self, *args, **options):
        test_mode = options['test']
        max_workers = options['max_workers']
        chunk_size = options['chunk_size']
        batch_size = options['batch_size']

        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.stdout.write(f"Using device: {device}")

        # Load models with CPU optimization
        ner_pipeline = pipeline(
            "ner",
            model="elastic/distilbert-base-uncased-finetuned-conll03-english",
            aggregation_strategy="simple",
            device=-1,  # Force CPU
        )

        # SentenceTransformer doesn't accept torch_dtype parameter
        embed_model = SentenceTransformer('all-MiniLM-L6-v2', device=device)

        movies = Movie.objects.exclude(plot__isnull=True).exclude(plot='')
        if not movies.exists():
            self.stdout.write(self.style.WARNING("No movies with plots found."))
            return

        if test_mode:
            movie = movies.order_by('?').first()
            self.stdout.write(self.style.NOTICE(f"Testing normalization on movie: {movie.title}"))
            normalized_plot = self.normalize_plot(movie.plot, ner_pipeline, embed_model, chunk_size)
            self.stdout.write("=== ORIGINAL PLOT ===")
            self.stdout.write(movie.plot)
            self.stdout.write("\n=== NORMALIZED PLOT ===")
            self.stdout.write(normalized_plot)
        else:
            def process_movie(movie):
                try:
                    normalized_plot = self.normalize_plot(movie.plot, ner_pipeline, embed_model, chunk_size)
                    movie.plot_normalized = normalized_plot
                    movie.save(update_fields=['plot_normalized'])
                    return movie.id, True
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing movie {movie.id}: {str(e)}"))
                    return movie.id, False

            # Process in batches to manage memory
            movie_ids = list(movies.values_list('id', flat=True))
            total_batches = (len(movie_ids) - 1) // batch_size + 1

            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = start_idx + batch_size
                batch_ids = movie_ids[start_idx:end_idx]
                batch_movies = Movie.objects.filter(id__in=batch_ids)

                self.stdout.write(f"Processing batch {batch_num + 1}/{total_batches} ({len(batch_movies)} movies)")

                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    results = list(executor.map(process_movie, batch_movies))

                success_count = sum(1 for _, success in results if success)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Batch {batch_num + 1} complete - Success: {success_count}/{len(batch_movies)}"
                    )
                )

            self.stdout.write(self.style.SUCCESS("All plots processed successfully!"))

    def normalize_plot(self, plot, ner_pipeline, embed_model, chunk_size):
        if not plot or not isinstance(plot, str):
            return ""

        # Clean and preprocess text
        plot = self.clean_text(plot)

        if len(plot.split()) < 10:  # Skip very short plots
            return plot

        # Split plot into manageable chunks
        sentences = re.split(r'(?<=[.!?])\s+', plot)
        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence.split())
            if current_length + sentence_length > chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        # Process NER on chunks to find character names
        character_names = set()
        for chunk in chunks:
            try:
                ner_results = ner_pipeline(chunk)
                if not isinstance(ner_results, list):
                    continue

                for ent in ner_results:
                    if ent.get('entity_group') == 'PER':
                        name = self.clean_name(ent['word'])
                        if name and 1 <= len(name.split()) <= 4:  # Reasonable name length
                            character_names.add(name)
            except Exception as e:
                continue

        if not character_names:
            return plot

        # Process character normalization
        character_mapping = self.process_characters(character_names, embed_model)

        # Apply replacements to the full plot
        return self.replace_characters(plot, character_mapping)

    def clean_text(self, text):
        """Clean and normalize text formatting"""
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        # Fix punctuation spacing
        text = re.sub(r'\s([.,!?;:](?:\s|$))', r'\1', text)
        text = re.sub(r'([\"\'])\s+([^"]+?)\s+([\"\'])', r'\1\2\3', text)
        # Normalize quotes
        text = text.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
        # Normalize dashes
        text = re.sub(r'[–—]', '-', text)
        return text.strip()

    def clean_name(self, name):
        """Clean and normalize character names"""
        name = re.sub(r'[^\w\s]', '', name.strip())
        name = re.sub(r'\s+', ' ', name)
        # Remove common titles and prefixes
        name = re.sub(r'^(Mr|Mrs|Ms|Dr|Prof|Sir|Lord|Lady|Dame)\s+', '', name, flags=re.IGNORECASE)
        return name

    def process_characters(self, character_names, embed_model):
        """Process character names and create mapping to standardized tags"""
        local_mapping = {}
        tag_counter = 1

        with self.lock:
            # Get embeddings for new names
            new_names = [n for n in character_names if n not in self.character_embedding_cache]
            if new_names:
                try:
                    new_embeddings = embed_model.encode(
                        new_names,
                        convert_to_tensor=True,
                        show_progress_bar=False,
                        batch_size=4  # Small batch for CPU
                    )
                    for name, emb in zip(new_names, new_embeddings):
                        self.character_embedding_cache[name] = emb
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Error encoding names: {str(e)}"))
                    # Fallback: assign unique tags without similarity matching
                    for name in new_names:
                        self.character_embedding_cache[name] = None

            # Create similarity matrix for names that have embeddings
            names_with_embeddings = [n for n in character_names if
                                     n in self.character_embedding_cache and self.character_embedding_cache[
                                         n] is not None]

            if names_with_embeddings:
                embeddings = [self.character_embedding_cache[n] for n in names_with_embeddings]
                embeddings_tensor = torch.stack(embeddings)
                cos_scores = util.cos_sim(embeddings_tensor, embeddings_tensor)

                # Group similar characters
                used_indices = set()
                for i, name1 in enumerate(names_with_embeddings):
                    if i in used_indices:
                        continue

                    tag = f"MAIN_CHARACTER_{tag_counter}"
                    tag_counter += 1
                    local_mapping[name1] = tag
                    used_indices.add(i)

                    # Find similar characters
                    for j in range(i + 1, len(names_with_embeddings)):
                        if j in used_indices:
                            continue
                        if cos_scores[i][j] > 0.8:
                            local_mapping[names_with_embeddings[j]] = tag
                            used_indices.add(j)

            # Handle names without embeddings (fallback)
            for name in character_names:
                if name not in local_mapping:
                    tag = f"MAIN_CHARACTER_{tag_counter}"
                    tag_counter += 1
                    local_mapping[name] = tag

        return local_mapping

    def replace_characters(self, text, character_mapping):
        """Replace character names with standardized tags in text"""
        if not character_mapping:
            return text

        # Sort by length to replace longer names first (avoid partial replacements)
        sorted_names = sorted(character_mapping.keys(), key=lambda x: len(x), reverse=True)

        for name in sorted_names:
            tag = character_mapping[name]
            # Use word boundaries for precise replacement
            pattern = re.compile(rf'\b{re.escape(name)}\b', re.IGNORECASE)
            text = pattern.sub(tag, text)

        return text