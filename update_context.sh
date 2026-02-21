#!/bin/bash
# update_context.sh – Collect project structure and key files for AI context

OUTPUT="AIContext.txt"
PROJECT_ROOT=$(pwd)

echo "=== Updating AI context for Movie Vibe project ==="
echo "Output file: $OUTPUT"

# Start fresh
> "$OUTPUT"

# Helper to add section headers
section() {
    echo -e "\n[$1]" >> "$OUTPUT"
}

# 1. Basic project overview
section "PROJECT OVERVIEW"
echo "Date: $(date)" >> "$OUTPUT"
echo "User: $(whoami)" >> "$OUTPUT"
echo "Path: $PROJECT_ROOT" >> "$OUTPUT"

# 2. Directory listing
section "DIRECTORY LISTING (ls -la)"
ls -la >> "$OUTPUT" 2>&1

# 3. Tree structure (if available)
section "TREE STRUCTURE (level 3, ignoring noise)"
if command -v tree &> /dev/null; then
    tree -L 3 -I 'node_modules|__pycache__|*.pyc|.git|__pycache__' >> "$OUTPUT" 2>&1
else
    echo "tree command not installed – skipping" >> "$OUTPUT"
fi

# 4. Key configuration files
section "REQUIREMENTS.TXT"
if [ -f requirements.txt ]; then
    cat requirements.txt >> "$OUTPUT"
else
    echo "requirements.txt not found" >> "$OUTPUT"
fi

section "DOCKER-COMPOSE.YML"
if [ -f docker-compose.yml ]; then
    cat docker-compose.yml >> "$OUTPUT"
else
    echo "docker-compose.yml not found" >> "$OUTPUT"
fi

section "DOCKERFILE (docker/Dockerfile)"
if [ -f docker/Dockerfile ]; then
    cat docker/Dockerfile >> "$OUTPUT"
else
    echo "docker/Dockerfile not found" >> "$OUTPUT"
fi

# 5. Django project settings (try common locations)
section "DJANGO SETTINGS"
if [ -f django_backend/settings.py ]; then
    echo "=== django_backend/settings.py ===" >> "$OUTPUT"
    cat django_backend/settings.py >> "$OUTPUT"
elif [ -f movie_vibe/settings.py ]; then
    echo "=== movie_vibe/settings.py ===" >> "$OUTPUT"
    cat movie_vibe/settings.py >> "$OUTPUT"
else
    echo "No settings.py found in django_backend/ or movie_vibe/" >> "$OUTPUT"
fi

section "DJANGO URLS (main)"
if [ -f django_backend/urls.py ]; then
    cat django_backend/urls.py >> "$OUTPUT"
elif [ -f movie_vibe/urls.py ]; then
    cat movie_vibe/urls.py >> "$OUTPUT"
else
    echo "No main urls.py found" >> "$OUTPUT"
fi

# 6. Models and views per app
APPS="movies review tags tmdb user"
for app in $APPS; do
    if [ -d "$app" ]; then
        section "APP: $app"
        echo "--- models.py ---" >> "$OUTPUT"
        if [ -f "$app/models.py" ]; then
            cat "$app/models.py" >> "$OUTPUT"
        else
            echo "No models.py" >> "$OUTPUT"
        fi

        echo -e "\n--- views.py ---" >> "$OUTPUT"
        if [ -f "$app/views.py" ]; then
            cat "$app/views.py" >> "$OUTPUT"
        else
            echo "No views.py" >> "$OUTPUT"
        fi

        echo -e "\n--- serializers.py (if any) ---" >> "$OUTPUT"
        if [ -f "$app/serializers.py" ]; then
            cat "$app/serializers.py" >> "$OUTPUT"
        elif [ -f "$app/serializer.py" ]; then
            cat "$app/serializer.py" >> "$OUTPUT"
        else
            echo "No serializers.py" >> "$OUTPUT"
        fi

        echo -e "\n--- urls.py ---" >> "$OUTPUT"
        if [ -f "$app/urls.py" ]; then
            cat "$app/urls.py" >> "$OUTPUT"
        else
            echo "No urls.py" >> "$OUTPUT"
        fi

        echo -e "\n--- apps.py ---" >> "$OUTPUT"
        if [ -f "$app/apps.py" ]; then
            cat "$app/apps.py" >> "$OUTPUT"
        fi
    fi
done

# 7. Frontend information
section "FRONTEND PACKAGE.JSON"
if [ -f frontend/package.json ]; then
    cat frontend/package.json >> "$OUTPUT"
else
    echo "frontend/package.json not found" >> "$OUTPUT"
fi

section "FRONTEND SRC (if exists)"
if [ -d frontend/src ]; then
    echo "frontend/src directory structure:" >> "$OUTPUT"
    ls -la frontend/src >> "$OUTPUT" 2>&1
    if [ -f frontend/src/App.js ]; then
        echo -e "\n--- App.js ---" >> "$OUTPUT"
        head -50 frontend/src/App.js >> "$OUTPUT"  # limit size
    fi
    if [ -f frontend/src/api/api.js ]; then
        echo -e "\n--- api.js ---" >> "$OUTPUT"
        cat frontend/src/api/api.js >> "$OUTPUT"
    fi
else
    echo "frontend/src not found" >> "$OUTPUT"
fi

# 8. Run the status check (MoVi progress)
section "MOVI PROGRESS CHECK (status)"
if [ -x ./status ]; then
    ./status >> "$OUTPUT" 2>&1
else
    echo "status script not found or not executable" >> "$OUTPUT"
fi

# 9. Any other useful files
section "ENVIRONMENT (.env) – filtered"
if [ -f .env ]; then
    grep -v 'PASSWORD\|SECRET\|KEY' .env >> "$OUTPUT"  # hide secrets
else
    echo ".env not found" >> "$OUTPUT"
fi

section "GITLAB CI"
if [ -f .gitlab-ci.yml ]; then
    cat .gitlab-ci.yml >> "$OUTPUT"
fi

echo ""
echo "✅ Context file updated: $OUTPUT"
echo "You can now share it with the AI assistant."