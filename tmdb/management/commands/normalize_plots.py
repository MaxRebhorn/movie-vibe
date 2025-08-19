# movies/management/commands/normalize_plots.py

import spacy
from django.core.management.base import BaseCommand
from movies.models import Movie
import pycountry
import re
from collections import defaultdict


class Command(BaseCommand):
    help = "Normalize movie plots and save them to plot_normalized"

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of movies to process at once'
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Run in test mode with one movie only (prints original and normalized plot)'
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        test_mode = options['test']

        nlp = spacy.load("en_core_web_sm")

        # Add patterns to recognize common entity types
        ruler = nlp.add_pipe("entity_ruler", before="ner")
        patterns = [
            {"label": "SCIENTIFIC_TERM", "pattern": [{"LOWER": {"in": ["dna", "rna", "genetic", "clone", "mutated"]}}]},
            {"label": "VEHICLE", "pattern": [{"LOWER": {"in": ["helicopter", "boat", "ship", "car", "jeep", "utv"]}}]},
            {"label": "WEAPON", "pattern": [{"LOWER": {"in": ["gun", "rifle", "pistol", "flare"]}}]}
        ]
        ruler.add_patterns(patterns)

        # Prepare list of country names
        country_names = {c.name.lower() for c in pycountry.countries}

        # Common first names for gender detection
        common_male_names = {"john", "michael", "david", "james", "robert", "william", "richard", "thomas", "charles",
                             "paul"}
        common_female_names = {"mary", "jennifer", "lisa", "susan", "nancy", "karen", "betty", "helen", "sandra",
                               "donna"}

        def detect_gender(name):
            first_name = name.split()[0].lower()
            if first_name in common_female_names:
                return "female"
            elif first_name in common_male_names:
                return "male"
            return "unknown"

        def normalize_plot(plot_text, main_characters=None):
            if not plot_text:
                return None

            # Reset counters for each plot
            counters = defaultdict(int)
            entity_map = {}  # Track entities to maintain consistency

            main_characters = main_characters or []
            doc = nlp(plot_text)
            normalized_tokens = []

            # First pass: identify important entities
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    if ent.text in main_characters:
                        entity_map[
                            ent.text] = f"[MAIN_CHARACTER_{len([k for k in entity_map.values() if k.startswith('MAIN')]) + 1}]"
                    else:
                        gender = detect_gender(ent.text)
                        if gender == "female":
                            entity_map[
                                ent.text] = f"[SIDE_CHARACTER_FEMALE_{len([k for k in entity_map.values() if 'FEMALE' in k]) + 1}]"
                        else:
                            entity_map[
                                ent.text] = f"[SIDE_CHARACTER_{len([k for k in entity_map.values() if 'SIDE_CHARACTER_' in k and 'FEMALE' not in k]) + 1}]"
                elif ent.label_ in {"GPE", "LOC"}:
                    if ent.text.lower() not in country_names:
                        entity_map[
                            ent.text] = f"[LOCATION_{len([k for k in entity_map.values() if 'LOCATION' in k]) + 1}]"
                elif ent.label_ == "ORG":
                    entity_map[ent.text] = f"[ORG_{len([k for k in entity_map.values() if 'ORG' in k]) + 1}]"

            # Second pass: build normalized text
            for token in doc:
                # Handle entities
                if token.ent_type_:
                    ent_text = doc[token.i:token.i + 1].text
                    if ent_text in entity_map:
                        normalized_tokens.append(entity_map[ent_text])
                    else:
                        normalized_tokens.append(token.text)
                # Handle numbers and dates
                elif token.like_num or token.ent_type_ == "DATE":
                    if re.match(r'^\d{4}$', token.text):  # Year
                        normalized_tokens.append("[YEAR]")
                    else:
                        normalized_tokens.append("[NUMBER]")
                # Handle other special cases
                elif token.text.lower() in ["he", "him", "his"]:
                    normalized_tokens.append("[PRONOUN_MALE]")
                elif token.text.lower() in ["she", "her", "hers"]:
                    normalized_tokens.append("[PRONOUN_FEMALE]")
                elif token.text.lower() in ["they", "them", "their"]:
                    normalized_tokens.append("[PRONOUN_PLURAL]")
                else:
                    normalized_tokens.append(token.text)

            return " ".join(normalized_tokens)

        qs = Movie.objects.exclude(plot__isnull=True).exclude(plot__exact="")

        if test_mode:
            movie = qs.first()
            if not movie:
                self.stdout.write("No movie with a plot found.")
                return

            main_characters = [actor.name for actor in getattr(movie, "cast", [])[:3]]
            normalized = normalize_plot(movie.plot, main_characters)

            self.stdout.write("=== Original Plot ===")
            self.stdout.write(movie.plot)
            self.stdout.write("\n=== Normalized Plot ===")
            self.stdout.write(normalized)
            return

        total = qs.count()
        self.stdout.write(f"Normalizing {total} movies...")

        for i in range(0, total, batch_size):
            batch = qs[i:i + batch_size]
            for movie in batch:
                main_characters = [actor.name for actor in getattr(movie, "cast", [])[:3]]
                movie.plot_normalized = normalize_plot(movie.plot, main_characters)
                movie.save(update_fields=["plot_normalized"])
            self.stdout.write(f"Processed {min(i + batch_size, total)} / {total}")

        self.stdout.write(self.style.SUCCESS("All plots normalized!"))