#!/bin/sh
# ================================================
# API_test.sh - Tests fixes avec compteur de succès
# ================================================

if [ -f .env ]; then
    . ./.env
fi

# ====================== CONFIGURATION ======================
API_BASE_URL="http://localhost:7000/api"
USERNAME="admin"
PASSWORD="admin"
PROJECT_NAME="admin"

TEST_BUCKET="test-shell-$(date +%s)"
TEST_OBJECT_KEY="test-file.txt"
TEST_FILE_CONTENT="Hello from shell test API ! $(date)"

AUTH_HEADERS="-H X-Username:${USERNAME} -H X-Password:${PASSWORD} -H Project:${PROJECT_NAME}"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Compteurs
TESTS_TOTAL=0
TESTS_SUCCESS=0

log() { echo "[TEST] $1"; }
success() { echo "${GREEN}✓ $1${NC}"; TESTS_SUCCESS=$((TESTS_SUCCESS + 1)); }
error()   { echo "${RED}✗ $1${NC}"; }

check_http_status() {
    local status="$1"
    case $status in
        ''|*[!0-9]*)
            echo "[ERREUR] Code HTTP invalide : '$status'"
            return 1 ;;
    esac
    if [ "$status" -ge 200 ] && [ "$status" -le 299 ]; then
        echo "[OK] Success (Code $status)"
        return 0
    else
        echo "[FAIL] Fail (Code $status)"
        return 1
    fi
}

log "API test (curl) - $(date)"

# ====================== TESTS FIXES ======================

TESTS_TOTAL=$((TESTS_TOTAL + 1))
log "2. GET Login (/)"
STATUS=$(curl --silent --output /dev/null ${AUTH_HEADERS} ${API_BASE_URL}/ -w "%{http_code}")
check_http_status $STATUS
[ $? -eq 0 ] && success "Login OK" || error "Login KO"

TESTS_TOTAL=$((TESTS_TOTAL + 1))
log "3. GET List buckets"
STATUS=$(curl --silent --output /dev/null ${AUTH_HEADERS} ${API_BASE_URL}/buckets -w "%{http_code}")
check_http_status $STATUS
[ $? -eq 0 ] && success "List buckets OK" || error "List buckets KO"

TESTS_TOTAL=$((TESTS_TOTAL + 1))
log "4. POST Create bucket"
STATUS=$(curl --silent --output /dev/null -X POST ${AUTH_HEADERS} ${API_BASE_URL}/buckets/${TEST_BUCKET} -w "%{http_code}")
check_http_status $STATUS
[ $? -eq 0 ] && success "Create bucket OK" || error "Create bucket KO"

TESTS_TOTAL=$((TESTS_TOTAL + 1))
log "5. GET List buckets (after create)"
STATUS=$(curl --silent --output /dev/null ${AUTH_HEADERS} ${API_BASE_URL}/buckets -w "%{http_code}")
check_http_status $STATUS
[ $? -eq 0 ] && success "List buckets after OK" || error "List buckets after KO"

# Upload
echo "${TEST_FILE_CONTENT}" > "/tmp/${TEST_OBJECT_KEY}"
TESTS_TOTAL=$((TESTS_TOTAL + 1))
log "6. POST Upload object"
STATUS=$(curl --silent --output /dev/null -X POST ${AUTH_HEADERS} \
    -F "file=@/tmp/${TEST_OBJECT_KEY}" \
    -F "key=${TEST_OBJECT_KEY}" \
    -F "contentType=text/plain" \
    ${API_BASE_URL}/buckets/${TEST_BUCKET}/objects -w "%{http_code}")
check_http_status $STATUS
[ $? -eq 0 ] && success "Upload OK" || error "Upload KO"

TESTS_TOTAL=$((TESTS_TOTAL + 1))
log "7. GET List objects"
STATUS=$(curl --silent --output /dev/null ${AUTH_HEADERS} ${API_BASE_URL}/buckets/${TEST_BUCKET}/objects?prefix= -w "%{http_code}")
check_http_status $STATUS
[ $? -eq 0 ] && success "List objects OK" || error "List objects KO"

TESTS_TOTAL=$((TESTS_TOTAL + 1))
log "8. GET Download object"
STATUS=$(curl --silent --output /dev/null ${AUTH_HEADERS} ${API_BASE_URL}/buckets/${TEST_BUCKET}/objects/${TEST_OBJECT_KEY} -w "%{http_code}")
check_http_status $STATUS
[ $? -eq 0 ] && success "Download OK" || error "Download KO"

TESTS_TOTAL=$((TESTS_TOTAL + 1))
log "9. DELETE Delete object"
STATUS=$(curl --silent --output /dev/null -X DELETE ${AUTH_HEADERS} ${API_BASE_URL}/buckets/${TEST_BUCKET}/objects/${TEST_OBJECT_KEY} -w "%{http_code}")
check_http_status $STATUS
[ $? -eq 0 ] && success "Delete object OK" || error "Delete object KO"

TESTS_TOTAL=$((TESTS_TOTAL + 1))
log "10. DELETE Delete bucket"
STATUS=$(curl --silent --output /dev/null -X DELETE ${AUTH_HEADERS} ${API_BASE_URL}/buckets/${TEST_BUCKET} -w "%{http_code}")
check_http_status $STATUS
[ $? -eq 0 ] && success "Delete bucket OK" || error "Delete bucket KO"

# ====================== RÉSUMÉ ======================
echo
echo "=================================================="
echo "                   RÉSUMÉ DES TESTS"
echo "=================================================="
echo "Test number : $TESTS_TOTAL"
echo "Success   : $TESTS_SUCCESS / $TESTS_TOTAL"
echo "Fail   : $((TESTS_TOTAL - TESTS_SUCCESS))"

if [ "$TESTS_SUCCESS" -eq "$TESTS_TOTAL" ]; then
    echo "${GREEN}SUCCESS. !${NC}"
else
    echo "${RED}FAIL.${NC}"
fi
echo "=================================================="

rm -f "/tmp/${TEST_OBJECT_KEY}" 2>/dev/null