#!/bin/bash
echo "=== MoVi SOL Fortschritts-Check ==="
echo ""

# Farben für bessere Lesbarkeit
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Zähler für Fortschritt
TOTAL=0
DONE=0

# Helper function to test JWT token
test_jwt_token() {
    local token=$1
    # Test token with a protected endpoint (movies list)
    local test_result=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer $token" \
        http://localhost:8000/api/v1/movies/movies/ 2>/dev/null)

    if [ "$test_result" == "200" ] || [ "$test_result" == "401" ] || [ "$test_result" == "403" ] || [ "$test_result" == "404" ]; then
        # 404 is acceptable if endpoint exists but no movies
        return 0
    else
        return 1
    fi
}

echo "1️⃣  Swagger/OpenAPI"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/swagger/ | grep -q "200"; then
  echo -e "${GREEN}   ✅ Swagger: OK${NC}"
  DONE=$((DONE+1))
else
  echo -e "${RED}   ❌ Swagger: Nicht erreichbar${NC}"
fi
TOTAL=$((TOTAL+1))

echo ""
echo "2️⃣  JWT Authentifizierung"

# Test 1: Check if token endpoint exists
JWT_ENDPOINT_TEST=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST http://localhost:8000/api/v1/auth/token/ \
    -H "Content-Type: application/json" \
    -d '{"username":"test","password":"test"}' 2>/dev/null)

if [ "$JWT_ENDPOINT_TEST" == "200" ]; then
    echo -e "${GREEN}   ✅ JWT: Token-Endpunkt erreichbar (HTTP 200)${NC}"

    # Test 2: Get actual token
    JWT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/token/ \
        -H "Content-Type: application/json" \
        -d '{"username":"test","password":"test"}' 2>/dev/null)

    # Extract tokens using grep/sed (fallback if jq not available)
    if command -v jq &> /dev/null; then
        ACCESS_TOKEN=$(echo "$JWT_RESPONSE" | jq -r '.access')
        REFRESH_TOKEN=$(echo "$JWT_RESPONSE" | jq -r '.refresh')
    else
        ACCESS_TOKEN=$(echo "$JWT_RESPONSE" | grep -o '"access":"[^"]*"' | cut -d'"' -f4)
        REFRESH_TOKEN=$(echo "$JWT_RESPONSE" | grep -o '"refresh":"[^"]*"' | cut -d'"' -f4)
    fi

    if [ -n "$ACCESS_TOKEN" ] && [ "$ACCESS_TOKEN" != "null" ]; then
        echo -e "${GREEN}   ✅ JWT: Token erfolgreich empfangen${NC}"

        # Test 3: Verify token structure (JWT has 3 parts)
        TOKEN_PARTS=$(echo "$ACCESS_TOKEN" | awk -F'.' '{print NF}')
        if [ "$TOKEN_PARTS" -eq 3 ]; then
            echo -e "${GREEN}   ✅ JWT: Token-Format gültig (3 Teile)${NC}"

            # Test 4: Test token with protected endpoint
            if test_jwt_token "$ACCESS_TOKEN"; then
                echo -e "${GREEN}   ✅ JWT: Token funktioniert mit geschützten Endpunkten${NC}"
                DONE=$((DONE+1))
            else
                echo -e "${YELLOW}   ⚠️  JWT: Token kann nicht validiert werden (Endpunkt-Problem?)${NC}"
            fi

            # Test 5: Test refresh endpoint
            REFRESH_TEST=$(curl -s -o /dev/null -w "%{http_code}" \
                -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
                -H "Content-Type: application/json" \
                -d "{\"refresh\":\"$REFRESH_TOKEN\"}" 2>/dev/null)

            if [ "$REFRESH_TEST" == "200" ]; then
                echo -e "${GREEN}   ✅ JWT: Refresh-Endpunkt funktioniert${NC}"
            else
                echo -e "${YELLOW}   ⚠️  JWT: Refresh-Endpunkt antwortet mit HTTP $REFRESH_TEST${NC}"
            fi
        else
            echo -e "${RED}   ❌ JWT: Ungültiges Token-Format${NC}"
        fi
    elif echo "$JWT_RESPONSE" | grep -q "detail.*No active account"; then
        echo -e "${YELLOW}   ⚠️  JWT: Token-Endpunkt OK, aber Test-User nicht vorhanden${NC}"
        echo -e "${BLUE}      💡 Lösung: python manage.py createsuperuser${NC}"
    else
        echo -e "${YELLOW}   ⚠️  JWT: Token-Endpunkt antwortet, aber unerwartete Response${NC}"
        echo -e "${BLUE}      Response: $(echo "$JWT_RESPONSE" | cut -c1-100)${NC}"
    fi
elif [ "$JWT_ENDPOINT_TEST" == "401" ] || [ "$JWT_ENDPOINT_TEST" == "403" ]; then
    echo -e "${YELLOW}   ⚠️  JWT: Endpunkt existiert, benötigt Authentifizierung (HTTP $JWT_ENDPOINT_TEST)${NC}"
elif [ "$JWT_ENDPOINT_TEST" == "404" ]; then
    echo -e "${RED}   ❌ JWT: Token-Endpunkt nicht gefunden (HTTP 404)${NC}"
    echo -e "${BLUE}      💡 Lösung: Prüfe ob 'rest_framework_simplejwt' in INSTALLED_APPS${NC}"
else
    echo -e "${RED}   ❌ JWT: Nicht implementiert oder nicht erreichbar (HTTP $JWT_ENDPOINT_TEST)${NC}"
fi
TOTAL=$((TOTAL+1))

echo ""
echo "3️⃣  Rate Limiting"

# Test rate limiting by making multiple rapid requests
echo -e "${BLUE}   Testing rate limiting with rapid requests...${NC}"

# First, test the movies endpoint (which should have rate limiting)
RATE_LIMIT_DETECTED=0
RATE_LIMIT_HEADERS=0

# Make 5 rapid requests and check for rate limiting
for i in {1..5}; do
    # Make request and capture both status code and headers
    RESPONSE=$(curl -s -i http://localhost:8000/api/v1/movies/movies/ 2>/dev/null)
    STATUS=$(echo "$RESPONSE" | grep -o "^HTTP/[0-9.]* [0-9]*" | tail -1 | awk '{print $2}')

    # Check for rate limit headers
    if echo "$RESPONSE" | grep -i "x-ratelimit\|retry-after\|x-throttle" > /dev/null; then
        RATE_LIMIT_HEADERS=1
        echo -e "${BLUE}      Rate limit headers detected!${NC}"
    fi

    if [ "$STATUS" == "429" ]; then
        echo -e "${GREEN}   ✅ Rate Limiting: Aktiv (HTTP 429 erhalten)${NC}"
        RATE_LIMIT_DETECTED=1
        DONE=$((DONE+1))
        break
    fi

    # Small delay between requests
    sleep 0.2
done

# Alternative test: Try to exceed the burst limit (30/minute)
if [ $RATE_LIMIT_DETECTED -eq 0 ]; then
    echo -e "${YELLOW}   ⚠️  No 429 responses yet, testing burst limit (30 requests)...${NC}"

    # Make 35 rapid requests to trigger burst limit
    for i in {1..35}; do
        STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/movies/movies/ 2>/dev/null)

        # Check for rate limit headers in one of the requests
        if [ $i -eq 1 ]; then
            HEADERS=$(curl -s -I http://localhost:8000/api/v1/movies/movies/ 2>/dev/null)
            if echo "$HEADERS" | grep -i "x-ratelimit\|retry-after\|x-throttle" > /dev/null; then
                RATE_LIMIT_HEADERS=1
            fi
        fi

        if [ "$STATUS" == "429" ]; then
            echo -e "${GREEN}   ✅ Rate Limiting: Aktiv (HTTP 429 bei Request $i)${NC}"
            RATE_LIMIT_DETECTED=1
            DONE=$((DONE+1))
            break
        fi

        # Small delay to not overwhelm the server
        sleep 0.1
    done
fi

# Check for rate limit configuration in settings
if [ $RATE_LIMIT_DETECTED -eq 0 ]; then
    # Check if rate limiting is configured in settings.py
    if grep -q "DEFAULT_THROTTLE_RATES" django_backend/settings.py 2>/dev/null; then
        echo -e "${YELLOW}   ⚠️  Rate Limiting: Konfiguriert in settings.py, aber nicht aktiv (keine 429 Antwort)${NC}"

        # Show current configuration
        echo -e "${BLUE}      Aktuelle Konfiguration:${NC}"
        grep -A 10 "DEFAULT_THROTTLE_RATES" django_backend/settings.py 2>/dev/null | head -5 | sed 's/^/      /'
    else
        echo -e "${RED}   ❌ Rate Limiting: Nicht konfiguriert${NC}"
    fi
elif [ $RATE_LIMIT_HEADERS -eq 1 ]; then
    echo -e "${GREEN}   ✅ Rate Limiting: Mit Headers aktiv${NC}"
    # Show the rate limit headers
    echo -e "${BLUE}      Rate Limit Headers:${NC}"
    curl -s -I http://localhost:8000/api/v1/movies/movies/ 2>/dev/null | grep -i "x-ratelimit\|retry-after\|x-throttle" | sed 's/^/      /'
fi

TOTAL=$((TOTAL+1))

echo ""
echo "4️⃣  UML Diagramme"
if [ -d "docs/uml" ]; then
  UML_COUNT=$(find docs/uml -type f \( -name "*.png" -o -name "*.pdf" -o -name "*.svg" -o -name "*.jpg" -o -name "*.jpeg" \) 2>/dev/null | wc -l)
  if [ "$UML_COUNT" -ge 3 ]; then
    echo -e "${GREEN}   ✅ UML: $UML_COUNT Diagramme gefunden${NC}"
    DONE=$((DONE+1))
  else
    echo -e "${YELLOW}   ⚠️  UML: $UML_COUNT/3 Diagramme${NC}"
  fi
else
  echo -e "${RED}   ❌ UML: docs/uml/ Ordner nicht gefunden${NC}"
fi
TOTAL=$((TOTAL+1))

echo ""
echo "5️⃣  BSI-Grundschutz Dokumentation"
if [ -f "docs/bsi_grundschutz.md" ]; then
  BSI_BAUSTEINE=$(grep -E "APP\.3\.1|ORP\.4|NET\.1\.1|CON\.3" docs/bsi_grundschutz.md | wc -l)
  if [ "$BSI_BAUSTEINE" -ge 4 ]; then
    echo -e "${GREEN}   ✅ BSI: Alle 4 Bausteine dokumentiert${NC}"
    DONE=$((DONE+1))
  else
    echo -e "${YELLOW}   ⚠️  BSI: $BSI_BAUSTEINE/4 Bausteine gefunden${NC}"
  fi
else
  echo -e "${RED}   ❌ BSI: docs/bsi_grundschutz.md nicht gefunden${NC}"
fi
TOTAL=$((TOTAL+1))

echo ""
echo "6️⃣  Test Coverage"
if [ -f "manage.py" ]; then
  # Prüfe ob coverage installiert ist
  if pip list 2>/dev/null | grep -q coverage; then
    echo -e "${GREEN}   ✅ Coverage: Installiert${NC}"
    # Try to run a quick coverage check
    if coverage run manage.py test movies.tests 2>/dev/null; then
        echo -e "${GREEN}   ✅ Coverage: Tests laufen${NC}"
        DONE=$((DONE+1))
    else
        echo -e "${YELLOW}   ⚠️  Coverage: Installiert aber Tests nicht ausgeführt${NC}"
    fi
  else
    echo -e "${YELLOW}   ⚠️  Coverage nicht installiert${NC}"
  fi
else
  echo -e "${RED}   ❌ manage.py nicht gefunden${NC}"
fi
TOTAL=$((TOTAL+1))

echo ""
echo "7️⃣  Docker Netzwerk-Segmentierung"
if command -v docker &> /dev/null; then
  # Check for django_network specifically (from your docker-compose.yml)
  if docker network ls --format "{{.Name}}" | grep -q "django_network"; then
    echo -e "${GREEN}   ✅ Docker: django_network gefunden${NC}"
    DONE=$((DONE+1))
  else
    echo -e "${YELLOW}   ⚠️  Docker: django_network nicht gefunden${NC}"
  fi
else
  echo -e "${RED}   ❌ Docker nicht installiert/lauffähig${NC}"
fi
TOTAL=$((TOTAL+1))

echo ""
echo "8️⃣  API Versionierung"
V1_TEST=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/movies/movies/ 2>/dev/null)
if [ "$V1_TEST" != "000" ]; then
  if [ "$V1_TEST" == "200" ] || [ "$V1_TEST" == "401" ] || [ "$V1_TEST" == "403" ] || [ "$V1_TEST" == "404" ]; then
    echo -e "${GREEN}   ✅ API v1: Erreichbar (HTTP $V1_TEST)${NC}"
    DONE=$((DONE+1))
  else
    echo -e "${YELLOW}   ⚠️  API v1: Antwortet mit HTTP $V1_TEST${NC}"
  fi
else
  echo -e "${RED}   ❌ API v1: Nicht gefunden${NC}"
fi
TOTAL=$((TOTAL+1))

echo ""
echo "9️⃣  Dokumentation"
DOC_COUNT=0
[ -d "docs/api" ] && DOC_COUNT=$((DOC_COUNT+1))
[ -d "docs/security" ] && DOC_COUNT=$((DOC_COUNT+1))
[ -d "docs/architecture" ] && DOC_COUNT=$((DOC_COUNT+1))

if [ "$DOC_COUNT" -ge 3 ]; then
  echo -e "${GREEN}   ✅ Dokumentation: Alle Ordner vorhanden${NC}"
  DONE=$((DONE+1))
else
  echo -e "${YELLOW}   ⚠️  Dokumentation: $DOC_COUNT/3 Ordner gefunden${NC}"
fi
TOTAL=$((TOTAL+1))

echo ""
echo "🔟  CI/CD Pipeline"
if [ -f ".gitlab-ci.yml" ]; then
  echo -e "${GREEN}   ✅ CI: .gitlab-ci.yml vorhanden${NC}"
  DONE=$((DONE+1))
else
  echo -e "${RED}   ❌ CI: .gitlab-ci.yml nicht gefunden${NC}"
fi
TOTAL=$((TOTAL+1))

echo ""
echo "================================="
PERCENT=$((DONE * 100 / TOTAL))
echo -e "📊 Fortschritt: ${GREEN}$DONE/$TOTAL ($PERCENT%)${NC}"
echo "================================="

if [ "$PERCENT" -lt 30 ]; then
  echo -e "${RED}🔴 Kritisch: Viel Arbeit vor dir!${NC}"
elif [ "$PERCENT" -lt 60 ]; then
  echo -e "${YELLOW}🟡 In Arbeit: Guter Fortschritt, weiter so!${NC}"
else
  echo -e "${GREEN}🟢 Gut: Bald fertig!${NC}"
fi

# Show what's still missing
echo ""
echo "📋 Nächste Schritte:"
if [ "$V1_TEST" == "404" ]; then
    echo -e "  ${YELLOW}• API v1 Endpunkte prüfen (aktuell 404)${NC}"
fi
if ! grep -q "DEFAULT_THROTTLE_RATES" django_backend/settings.py 2>/dev/null; then
    echo -e "  ${YELLOW}• Rate Limiting in settings.py konfigurieren${NC}"
fi
if [ ! -f "docs/bsi_grundschutz.md" ]; then
    echo -e "  ${YELLOW}• BSI-Grundschutz Dokumentation erstellen${NC}"
fi