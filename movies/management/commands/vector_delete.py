from django.conf import settings
from django.core.management.base import BaseCommand
from qdrant_client import QdrantClient

VECTOR_SIZE = settings.QDRANT_VECTOR_SIZE
COLLECTIONS = settings.QDRANT_COLLECTIONS
QDRANT_URL = settings.QDRANT_URL

class Command(BaseCommand):
    help = "Löscht Vektor-Collections in Qdrant. Ohne Argument: alle Collections löschen. Mit --collections: spezifische Collections löschen."

    def add_arguments(self, parser):
        parser.add_argument(
            '--collections',
            nargs='+',
            type=str,
            help='Liste von Collections, die gelöscht werden sollen. Ohne dieses Argument werden alle Collections aus settings gelöscht.'
        )

    def handle(self, *args, **options):
        client = QdrantClient(url=QDRANT_URL)
        existing_collections = [c.name for c in client.get_collections().collections]

        collections_to_delete = options['collections']
        if collections_to_delete:
            # Delete only specified collections if they exist
            for col in collections_to_delete:
                if col in existing_collections:
                    client.delete_collection(collection_name=col)
                    self.stdout.write(self.style.SUCCESS(f"Collection '{col}' gelöscht."))
                else:
                    self.stdout.write(self.style.WARNING(f"Collection '{col}' existiert nicht."))
        else:
            # Delete all collections defined in settings.QDRANT_COLLECTIONS
            for col in COLLECTIONS.values():
                if col in existing_collections:
                    client.delete_collection(collection_name=col)
                    self.stdout.write(self.style.SUCCESS(f"Collection '{col}' gelöscht."))
                else:
                    self.stdout.write(self.style.WARNING(f"Collection '{col}' existiert nicht."))
