# MoVi Project Makefile
# Easy commands for Docker and Frontend management

.PHONY: help up down restart status logs frontend frontend-build frontend-logs clean migrate test shell backup restore swagger
.PHONY: start logs-web frontend-docker migrations dbshell test-coverage
.PHONY: es-nuke es-disable es-enable
.PHONY: vector-list vector-delete vector-embed vector-generate vector-update vector-map vector-info vector-rebuild-all
.PHONY: vector-delete-collections vector-update-full vector-map-movie vector-help
.PHONY: vlist vinfo vdel vembed vgen vup vmap
.PHONY: data-help data-import data-fill data-normalize data-normalize-test data-stats data-clean
.PHONY: data-import-delay data-fill-limit data-fill-dry-run data-normalize-batch data-normalize-advanced
.PHONY: data-import-all data-refresh-all

# Colors for help
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

help:
	@echo "$(BLUE)MoVi Project Commands:$(RESET)"
	@echo "$(GREEN)make up$(RESET)         - Start all Docker containers (backend + DBs)"
	@echo "$(GREEN)make down$(RESET)       - Stop all Docker containers"
	@echo "$(GREEN)make restart$(RESET)    - Restart all Docker containers"
	@echo "$(GREEN)make status$(RESET)     - Show container status"
	@echo "$(GREEN)make logs$(RESET)       - Show all logs (follow mode)"
	@echo "$(GREEN)make logs-web$(RESET)   - Show only Django backend logs"
	@echo "$(GREEN)make frontend$(RESET)   - Start React frontend (local)"
	@echo "$(GREEN)make frontend-docker$(RESET) - Start React frontend (in Docker)"
	@echo "$(GREEN)make frontend-build$(RESET) - Build React frontend"
	@echo "$(GREEN)make frontend-logs$(RESET) - Show frontend logs (Docker)"
	@echo "$(GREEN)make migrate$(RESET)    - Run Django migrations"
	@echo "$(GREEN)make migrations$(RESET) - Create Django migrations"
	@echo "$(GREEN)make shell$(RESET)      - Open Django shell"
	@echo "$(GREEN)make dbshell$(RESET)    - Open PostgreSQL shell"
	@echo "$(GREEN)make test$(RESET)       - Run Django tests"
	@echo "$(GREEN)make test-coverage$(RESET) - Run tests with coverage"
	@echo "$(GREEN)make clean$(RESET)      - Stop all containers and remove volumes"
	@echo "$(GREEN)make backup$(RESET)     - Run backup script"
	@echo "$(GREEN)make restore$(RESET)    - Run restore script (asks for file)"
	@echo "$(GREEN)make swagger$(RESET)    - Open Swagger UI in browser"
	@echo "$(GREEN)make es-nuke$(RESET)    - Delete Elasticsearch volume and restart"
	@echo "$(GREEN)make vector-help$(RESET)- Show vector management commands"
	@echo "$(GREEN)make data-help$(RESET)  - Show data management commands"
	@echo "$(GREEN)make help$(RESET)       - Show this help"

start:
	@echo "$(YELLOW)Starting Docker containers and frontend...$(RESET)"
	docker compose up -d
	cd frontend && npm install && npm start

# Docker Compose commands
up:
	@echo "$(YELLOW)Starting all Docker containers...$(RESET)"
	docker compose up -d
	@echo "$(GREEN)✅ Containers started. Frontend: http://localhost:3000, Backend: http://localhost:8000$(RESET)"

down:
	@echo "$(YELLOW)Stopping all Docker containers...$(RESET)"
	docker compose down
	@echo "$(GREEN)✅ Containers stopped.$(RESET)"

restart: down up

status:
	@echo "$(YELLOW)Container status:$(RESET)"
	docker compose ps

logs:
	@echo "$(YELLOW)Showing all logs (Ctrl+C to exit)...$(RESET)"
	docker compose logs -f

logs-web:
	@echo "$(YELLOW)Showing Django backend logs...$(RESET)"
	docker compose logs -f web

# Frontend commands
frontend:
	@echo "$(YELLOW)Starting React frontend on http://localhost:3000...$(RESET)"
	cd frontend && npm install && npm start

frontend-docker:
	@echo "$(YELLOW)Starting frontend in Docker...$(RESET)"
	docker compose up -d frontend
	@echo "$(GREEN)✅ Frontend started at http://localhost:3000$(RESET)"

frontend-build:
	@echo "$(YELLOW)Building React frontend...$(RESET)"
	cd frontend && npm install && npm run build
	@echo "$(GREEN)✅ Frontend built successfully$(RESET)"

frontend-logs:
	@echo "$(YELLOW)Showing frontend logs...$(RESET)"
	docker compose logs -f frontend

# Django commands
migrate:
	@echo "$(YELLOW)Running Django migrations...$(RESET)"
	docker compose exec web python manage.py migrate
	@echo "$(GREEN)✅ Migrations complete$(RESET)"

migrations:
	@echo "$(YELLOW)Creating Django migrations...$(RESET)"
	docker compose exec web python manage.py makemigrations

shell:
	@echo "$(YELLOW)Opening Django shell...$(RESET)"
	docker compose exec web python manage.py shell

dbshell:
	@echo "$(YELLOW)Opening PostgreSQL shell...$(RESET)"
	docker compose exec db psql -U django_user -d django_db

test:
	@echo "$(YELLOW)Running Django tests...$(RESET)"
	docker compose exec web python manage.py test

test-coverage:
	@echo "$(YELLOW)Running tests with coverage...$(RESET)"
	docker compose exec web bash -c "coverage run manage.py test && coverage report"

# Cleanup
clean:
	@echo "$(YELLOW)⚠️  Stopping all containers and removing volumes...$(RESET)"
	@read -p "Are you sure? (y/N) " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker compose down -v; \
		echo "$(GREEN)✅ Cleaned up all containers and volumes.$(RESET)"; \
	else \
		echo "$(YELLOW)Cleanup cancelled.$(RESET)"; \
	fi

# Backup/Restore
backup:
	@echo "$(YELLOW)Running backup script...$(RESET)"
	python3 backup_scripts/backup_manager.py
	@echo "$(GREEN)✅ Backup completed$(RESET)"

restore:
	@echo "$(YELLOW)Available backups:$(RESET)"
	@ls -la backups/ | grep tar.gz
	@read -p "Enter backup filename: " filename; \
	python3 backup_scripts/restore.py --backup-file backups/$$filename

# Elasticsearch Volume komplett löschen (wenn DB leer ist)
es-nuke:
	@echo "$(YELLOW)💥 Nuking Elasticsearch volume...$(RESET)"
	@docker compose stop elasticsearch
	@docker compose rm -f elasticsearch
	@docker volume rm movie-vibe_es_data 2>/dev/null || true
	@echo "$(GREEN)✅ Elasticsearch volume removed$(RESET)"
	@echo "$(YELLOW)Starting fresh elasticsearch...$(RESET)"
	@docker compose up -d elasticsearch
	@echo "$(GREEN)✅ Done! New empty Elasticsearch is running$(RESET)"

# ============================================
# VECTOR MANAGEMENT COMMANDS
# ============================================

# Vektor-Befehle Übersicht
vector-help:
	@echo "$(BLUE)🔷 Vektor-Management Befehle:$(RESET)"
	@echo "$(GREEN)make vector-list$(RESET)        - Zeige alle vorhandenen Collections in Qdrant"
	@echo "$(GREEN)make vector-info$(RESET)        - Zeige Statistiken zu Vektoren (Anzahl pro Collection)"
	@echo "$(GREEN)make vector-delete$(RESET)       - Lösche ALLE Vektor-Collections (mit Sicherheitsabfrage)"
	@echo "$(GREEN)make vector-delete-collections$(RESET) - Lösche spezifische Collections (fragt nach Namen)"
	@echo "$(GREEN)make vector-embed$(RESET)        - Embedde neue Filme (nur fehlende)"
	@echo "$(GREEN)make vector-generate$(RESET)     - Generiere Vektoren für ALLE Filme (komplett neu)"
	@echo "$(GREEN)make vector-update$(RESET)       - Aktualisiere Vektoren basierend auf neuen Reviews"
	@echo "$(GREEN)make vector-update-full$(RESET)  - Erzwinge komplettes Vektor-Update aller Filme"
	@echo "$(GREEN)make vector-map$(RESET)          - Erstelle 2D-Visualisierung für einen Film (fragt nach ID)"
	@echo "$(GREEN)make vector-map-movie$(RESET)    - Erstelle Map für bestimmten Film: make vector-map-movie ID=123"
	@echo "$(GREEN)make vector-rebuild-all$(RESET)  - Komplett-Neubau: Löschen + Generieren + Update"

# Collections anzeigen
vector-list:
	@echo "$(YELLOW)🔍 Verfügbare Qdrant Collections:$(RESET)"
	@docker exec django_web python -c " \
from django.conf import settings; \
from qdrant_client import QdrantClient; \
client = QdrantClient(url=settings.QDRANT_URL); \
collections = client.get_collections().collections; \
if collections: \
    for c in collections: \
        print(f'  📁 {c.name}'); \
else: \
    print('  ❌ Keine Collections gefunden') \
"

# Vektor-Statistiken
vector-info:
	@echo "$(YELLOW)📊 Vektor-Statistiken:$(RESET)"
	@docker exec django_web python -c " \
from django.conf import settings; \
from qdrant_client import QdrantClient; \
client = QdrantClient(url=settings.QDRANT_URL); \
collections = client.get_collections().collections; \
if collections: \
    for c in collections: \
        count = client.count(collection_name=c.name).count; \
        print(f'  📁 {c.name}: {count} Vektoren'); \
else: \
    print('  ❌ Keine Collections gefunden') \
"
	@echo ""
	@echo "$(YELLOW)🎬 Filme in Datenbank:$(RESET)"
	@docker exec django_web python manage.py shell -c "from movies.models import Movie; print(f'  📽️  {Movie.objects.count()} Filme total')"

# Alle Collections löschen (mit Sicherheitsabfrage)
vector-delete:
	@echo "$(YELLOW)⚠️  DAS LÖSCHT ALLE VEKTOR-COLLECTIONS IN QDRANT!$(RESET)"
	@read -p "Bist du sicher? (y/N) " -n 1 -r; \
	echo ""; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(YELLOW)Lösche Collections...$(RESET)"; \
		docker exec django_web python manage.py vector_delete; \
		echo "$(GREEN)✅ Alle Collections gelöscht$(RESET)"; \
	else \
		echo "$(YELLOW)Abgebrochen$(RESET)"; \
	fi

# Spezifische Collections löschen
vector-delete-collections:
	@echo "$(YELLOW)Verfügbare Collections:$(RESET)"
	@docker exec django_web python -c " \
from django.conf import settings; \
from qdrant_client import QdrantClient; \
client = QdrantClient(url=settings.QDRANT_URL); \
for c in client.get_collections().collections: \
    print(f'  📁 {c.name}') \
"
	@echo ""
	@read -p "Collections zum Löschen (mit Leerzeichen getrennt): " cols; \
	echo "$(YELLOW)Lösche: $$cols$(RESET)"; \
	docker exec django_web python manage.py vector_delete --collections $$cols; \
	echo "$(GREEN)✅ Fertig$(RESET)"

# Fehlende Filme embedden
vector-embed:
	@echo "$(YELLOW)🔨 Embedde fehlende Filme in Qdrant...$(RESET)"
	@docker exec django_web python manage.py vector_embed
	@echo "$(GREEN)✅ Embedding abgeschlossen$(RESET)"

# Alle Vektoren generieren (komplett neu)
vector-generate:
	@echo "$(YELLOW)🔄 Generiere Vektoren für ALLE Filme neu...$(RESET)"
	@echo "$(YELLOW)Das kann etwas dauern...$(RESET)"
	@docker exec django_web python manage.py vector_generate
	@echo "$(GREEN)✅ Vektorgenerierung abgeschlossen$(RESET)"

# Vektoren basierend auf Reviews aktualisieren
vector-update:
	@echo "$(YELLOW)📝 Aktualisiere Vektoren basierend auf neuen Reviews...$(RESET)"
	@docker exec django_web python manage.py vector_update
	@echo "$(GREEN)✅ Vektor-Update abgeschlossen$(RESET)"

# Vollständiges Vektor-Update erzwingen
vector-update-full:
	@echo "$(YELLOW)🔄 Erzwinge komplettes Vektor-Update aller Filme...$(RESET)"
	@docker exec django_web python manage.py vector_update --full
	@echo "$(GREEN)✅ Vollständiges Vektor-Update abgeschlossen$(RESET)"

# Movie Map für einen bestimmten Film erstellen
vector-map:
	@read -p "Movie ID für die Visualisierung: " id; \
	echo "$(YELLOW)🗺️  Erstelle Movie Map für Film $$id...$(RESET)"; \
	docker exec django_web python manage.py movie_map $$id; \
	echo "$(GREEN)✅ Map erstellt. Zu finden in media/plots/$(RESET)"

# Movie Map mit Parameter
vector-map-movie:
	@if [ -z "$(ID)" ]; then \
		echo "$(RED)❌ Bitte ID angeben: make vector-map-movie ID=123$(RESET)"; \
	else \
		echo "$(YELLOW)🗺️  Erstelle Movie Map für Film $(ID)...$(RESET)"; \
		docker exec django_web python manage.py movie_map $(ID); \
		echo "$(GREEN)✅ Map erstellt. Zu finden in media/plots/$(RESET)"; \
	fi

# Komplett-Neubau aller Vektoren
vector-rebuild-all:
	@echo "$(YELLOW)🔄 STARTE KOMPLETT-NEUBAU ALLER VEKTOREN...$(RESET)"
	@echo "$(YELLOW)Phase 1/3: Lösche alle Collections...$(RESET)"
	@docker exec django_web python manage.py vector_delete || true
	@echo ""
	@echo "$(YELLOW)Phase 2/3: Generiere neue Vektoren für alle Filme...$(RESET)"
	@docker exec django_web python manage.py vector_generate
	@echo ""
	@echo "$(YELLOW)Phase 3/3: Aktualisiere mit Reviews...$(RESET)"
	@docker exec django_web python manage.py vector_update
	@echo ""
	@echo "$(GREEN)✅✅ KOMPLETT-NEUBAU ABGESCHLOSSEN! ✅✅$(RESET)"
	@make vector-info

# Kurzform für häufige Befehle
vlist: vector-list
vinfo: vector-info
vdel: vector-delete
vembed: vector-embed
vgen: vector-generate
vup: vector-update
vmap: vector-map

# ============================================
# DATA IMPORT & NORMALIZATION COMMANDS
# ============================================

# Daten-Befehle Übersicht
data-help:
	@echo "$(BLUE)📊 Datenmanagement Befehle:$(RESET)"
	@echo "$(GREEN)make data-import FILE=movies.json$(RESET)  - Importiere Filme aus JSON-Datei (mit TMDB)"
	@echo "$(GREEN)make data-import-delay FILE=movies.json DELAY=2$(RESET) - Import mit Verzögerung (schonend)"
	@echo "$(GREEN)make data-fill$(RESET)                     - Fülle fehlende Daten aus TMDB nach"
	@echo "$(GREEN)make data-fill-limit LIMIT=10$(RESET)      - Fülle nur X Filme (zum Testen)"
	@echo "$(GREEN)make data-fill-dry-run$(RESET)             - Trockenlauf (zeigt Daten ohne zu speichern)"
	@echo "$(GREEN)make data-normalize$(RESET)                - Normalisiere alle Film-Plots (KI-gestützt)"
	@echo "$(GREEN)make data-normalize-test$(RESET)           - Teste Normalisierung an einem zufälligen Film"
	@echo "$(GREEN)make data-normalize-batch BATCH=50$(RESET) - Normalisiere in Batches (speicherschonend)"
	@echo "$(GREEN)make data-stats$(RESET)                    - Zeige Datenbank-Statistiken"
	@echo "$(GREEN)make data-clean$(RESET)                    - Zeige Filme mit fehlenden Daten"

# Daten-Import aus JSON
data-import:
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)❌ Bitte JSON-Datei angeben: make data-import FILE=movies.json$(RESET)"; \
	else \
		echo "$(YELLOW)📥 Importiere Filme aus $(FILE)...$(RESET)"; \
		docker exec django_web python manage.py import_movies $(FILE); \
		echo "$(GREEN)✅ Import abgeschlossen$(RESET)"; \
	fi

# Import mit Verzögerung (schonend für TMDB API)
data-import-delay:
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)❌ Bitte JSON-Datei angeben: make data-import-delay FILE=movies.json$(RESET)"; \
	else \
		DELAY=$${DELAY:-1.0}; \
		echo "$(YELLOW)📥 Importiere Filme aus $(FILE) mit $$DELAY s Verzögerung...$(RESET)"; \
		docker exec django_web python manage.py import_movies $(FILE) --delay=$$DELAY; \
		echo "$(GREEN)✅ Import abgeschlossen$(RESET)"; \
	fi

# Fehlende Daten aus TMDB nachfüllen
data-fill:
	@echo "$(YELLOW)🔄 Fülle fehlende Filmdaten aus TMDB nach...$(RESET)"
	@if [ -n "$(LIMIT)" ]; then \
		echo "$(YELLOW)Limit: $(LIMIT) Filme$(RESET)"; \
		docker exec django_web python manage.py fill_missing_data --limit=$(LIMIT); \
	else \
		docker exec django_web python manage.py fill_missing_data; \
	fi
	@echo "$(GREEN)✅ Daten-Nachfüllung abgeschlossen$(RESET)"

# Trockenlauf (zeigt was geändert würde)
data-fill-dry-run:
	@echo "$(YELLOW)🔄 Trockenlauf - Zeige zu ergänzende Daten...$(RESET)"
	@if [ -n "$(LIMIT)" ]; then \
		docker exec django_web python manage.py fill_missing_data --limit=$(LIMIT) --dry-run; \
	else \
		docker exec django_web python manage.py fill_missing_data --dry-run; \
	fi
	@echo "$(GREEN)✅ Trockenlauf abgeschlossen$(RESET)"

# Nur limitierte Anzahl Filme nachfüllen
data-fill-limit:
	@if [ -z "$(LIMIT)" ]; then \
		echo "$(RED)❌ Bitte Limit angeben: make data-fill-limit LIMIT=10$(RESET)"; \
	else \
		echo "$(YELLOW)🔄 Fülle $(LIMIT) Filme aus TMDB nach...$(RESET)"; \
		docker exec django_web python manage.py fill_missing_data --limit=$(LIMIT); \
		echo "$(GREEN)✅ Daten-Nachfüllung abgeschlossen$(RESET)"; \
	fi

# Plot-Normalisierung (alle Filme)
data-normalize:
	@echo "$(YELLOW)🧠 Normalisiere alle Film-Plots (KI-gestützt)...$(RESET)"
	@echo "$(YELLOW)Das kann lange dauern!$(RESET)"
	@if [ -n "$(BATCH)" ]; then \
		echo "$(YELLOW)Batch-Größe: $(BATCH)$(RESET)"; \
		docker exec django_web python manage.py normalize_plots --batch-size=$(BATCH); \
	else \
		docker exec django_web python manage.py normalize_plots; \
	fi
	@echo "$(GREEN)✅ Plot-Normalisierung abgeschlossen$(RESET)"

# Test-Normalisierung (ein zufälliger Film)
data-normalize-test:
	@echo "$(YELLOW)🧪 Teste Plot-Normalisierung an einem zufälligen Film...$(RESET)"
	@docker exec django_web python manage.py normalize_plots --test
	@echo "$(GREEN)✅ Test abgeschlossen$(RESET)"

# Normalisierung mit spezifischen Parametern
data-normalize-advanced:
	@echo "$(YELLOW)🧠 Normalisiere Plots mit erweiterten Parametern...$(RESET)"
	WORKERS=$${WORKERS:-2}; \
	CHUNK=$${CHUNK:-250}; \
	BATCH=$${BATCH:-10}; \
	echo "$(YELLOW)Workers: $$WORKERS, Chunk: $$CHUNK, Batch: $$BATCH$(RESET)"; \
	docker exec django_web python manage.py normalize_plots \
		--max-workers=$$WORKERS \
		--chunk-size=$$CHUNK \
		--batch-size=$$BATCH
	@echo "$(GREEN)✅ Normalisierung abgeschlossen$(RESET)"

# Datenbank-Statistiken
data-stats:
	@echo "$(YELLOW)📊 Datenbank-Statistiken:$(RESET)"
	@docker exec django_web python manage.py shell -c " \
from movies.models import Movie; \
from review.models import Review, MovieQuizReview; \
total = Movie.objects.count(); \
with_plot = Movie.objects.exclude(plot__isnull=True).exclude(plot='').count(); \
with_normalized = Movie.objects.exclude(plot_normalized__isnull=True).exclude(plot_normalized='').count(); \
with_poster = Movie.objects.exclude(poster_url__isnull=True).exclude(poster_url='').count(); \
with_trailer = Movie.objects.exclude(trailer_url__isnull=True).exclude(trailer_url='').count(); \
reviews = Review.objects.count(); \
quiz_reviews = MovieQuizReview.objects.count(); \
print(f'  📽️  Filme total: {total}'); \
print(f'  📝 Mit Plot: {with_plot}'); \
print(f'  ✨ Mit normalisiertem Plot: {with_normalized}'); \
print(f'  🖼️  Mit Poster: {with_poster}'); \
print(f'  🎬 Mit Trailer: {with_trailer}'); \
print(f'  ⭐ Reviews: {reviews}'); \
print(f'  📋 Quiz-Reviews: {quiz_reviews}'); \
"

# Zeige Filme mit fehlenden Daten
data-clean:
	@echo "$(YELLOW)🔍 Filme mit fehlenden Daten:$(RESET)"
	@docker exec django_web python manage.py shell -c " \
from movies.models import Movie; \
missing_plot = Movie.objects.filter(plot__isnull=True) | Movie.objects.filter(plot=''); \
missing_poster = Movie.objects.filter(poster_url__isnull=True) | Movie.objects.filter(poster_url=''); \
missing_trailer = Movie.objects.filter(trailer_url__isnull=True) | Movie.objects.filter(trailer_url=''); \
print(f'  📝 Ohne Plot: {missing_plot.count()}'); \
print(f'  🖼️  Ohne Poster: {missing_poster.count()}'); \
print(f'  🎬 Ohne Trailer: {missing_trailer.count()}'); \
"

# ============================================
# KOMBI-BEFEHLE
# ============================================

# Komplett-Import: JSON importieren + Daten nachfüllen
data-import-all:
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)❌ Bitte JSON-Datei angeben: make data-import-all FILE=movies.json$(RESET)"; \
	else \
		echo "$(YELLOW)📥 STARTE KOMPLETT-IMPORT...$(RESET)"; \
		echo "$(YELLOW)Phase 1/3: Importiere Filme aus $(FILE)...$(RESET)"; \
		docker exec django_web python manage.py import_movies $(FILE); \
		echo "$(YELLOW)Phase 2/3: Fülle fehlende Daten aus TMDB nach...$(RESET)"; \
		docker exec django_web python manage.py fill_missing_data; \
		echo "$(YELLOW)Phase 3/3: Normalisiere Plots...$(RESET)"; \
		docker exec django_web python manage.py normalize_plots; \
		echo "$(GREEN)✅✅ KOMPLETT-IMPORT ABGESCHLOSSEN! ✅✅$(RESET)"; \
		make data-stats; \
	fi

# Daten auffrischen: Nur fehlende nachfüllen + normalisieren
data-refresh-all:
	@echo "$(YELLOW)🔄 FRISCHE VORHANDENE DATEN AUF...$(RESET)"
	@echo "$(YELLOW)Phase 1/2: Fülle fehlende Daten aus TMDB nach...$(RESET)"
	@docker exec django_web python manage.py fill_missing_data
	@echo "$(YELLOW)Phase 2/2: Normalisiere Plots...$(RESET)"
	@docker exec django_web python manage.py normalize_plots
	@echo "$(GREEN)✅✅ DATEN-AUFFRISCHUNG ABGESCHLOSSEN! ✅✅$(RESET)"
	@make data-stats

# Open Swagger in browser
swagger:
	@echo "$(YELLOW)Opening Swagger UI...$(RESET)"
	@if command -v xdg-open > /dev/null; then \
		xdg-open http://localhost:8000/swagger/; \
	elif command -v open > /dev/null; then \
		open http://localhost:8000/swagger/; \
	else \
		echo "$(GREEN)Open http://localhost:8000/swagger/ in your browser$(RESET)"; \
	fi