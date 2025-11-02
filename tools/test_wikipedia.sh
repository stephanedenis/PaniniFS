#!/bin/bash
# Test complet Wikipedia avec Panini-FS
# Commence avec Sanskrit, puis teste les autres langues

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PANINI_FS_DIR="${SCRIPT_DIR}/.."
WIKI_DUMPS_DIR="/home/stephane/GitHub/Panini/wikipedia_dumps"
API_URL="http://localhost:3030/api"
STORAGE_DIR="${PANINI_STORAGE:-/tmp/panini-wikipedia-test}"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Vérifier que l'API est lancée
check_api() {
    log_info "Vérification de l'API Panini-FS..."
    
    if curl -s "${API_URL}/health" > /dev/null 2>&1; then
        log_success "API accessible à ${API_URL}"
    else
        log_error "API non accessible. Lancez d'abord: PANINI_STORAGE=${STORAGE_DIR} cargo run --bin panini-api"
        exit 1
    fi
}

# Test avec Sanskrit (plus petit, 19M)
test_sanskrit() {
    log_info "========================================="
    log_info "TEST 1: WIKIPEDIA SANSKRIT (sa) - 19M"
    log_info "========================================="
    
    DUMP="${WIKI_DUMPS_DIR}/sawiki-latest-pages-articles.xml.bz2"
    
    if [ ! -f "$DUMP" ]; then
        log_warning "Dump Sanskrit introuvable: $DUMP"
        return 1
    fi
    
    # Ingérer 100 articles pour test
    log_info "Ingestion de 100 articles Sanskrit..."
    python3 "${SCRIPT_DIR}/wikipedia_ingestion.py" \
        --dump "$DUMP" \
        --lang sa \
        --limit 100 \
        --api "$API_URL" \
        --classify \
        --output "${SCRIPT_DIR}/../reports/wikipedia_sa_test.json"
    
    log_success "Ingestion Sanskrit terminée!"
    
    # Validation bit-perfect
    log_info "Validation bit-perfect (10 articles aléatoires)..."
    python3 "${SCRIPT_DIR}/validate_bitperfect.py" \
        --dump "$DUMP" \
        --lang sa \
        --sample 10 \
        --api "$API_URL"
    
    log_success "Validation Sanskrit terminée!"
}

# Test avec Hindi (217M)
test_hindi() {
    log_info "========================================="
    log_info "TEST 2: WIKIPEDIA HINDI (hi) - 217M"
    log_info "========================================="
    
    DUMP="${WIKI_DUMPS_DIR}/hiwiki-latest-pages-articles.xml.bz2"
    
    if [ ! -f "$DUMP" ]; then
        log_warning "Dump Hindi introuvable: $DUMP"
        return 1
    fi
    
    log_info "Ingestion de 500 articles Hindi..."
    python3 "${SCRIPT_DIR}/wikipedia_ingestion.py" \
        --dump "$DUMP" \
        --lang hi \
        --limit 500 \
        --api "$API_URL" \
        --output "${SCRIPT_DIR}/../reports/wikipedia_hi_test.json"
    
    log_success "Ingestion Hindi terminée!"
}

# Test multilangue (articles similaires)
test_multilang_dedup() {
    log_info "========================================="
    log_info "TEST 3: DÉDUPLICATION INTER-LANGUES"
    log_info "========================================="
    
    log_info "Test avec articles 'France', 'Pāṇini', 'Sanskrit' en plusieurs langues"
    
    # Articles à tester
    declare -A ARTICLES=(
        ["fr"]="France,Pāṇini,Sanskrit"
        ["en"]="France,Pāṇini,Sanskrit"
        ["de"]="Frankreich,Panini,Sanskrit"
        ["sa"]="फ़्रान्स,पाणिनि,संस्कृत"
    )
    
    # Extraire et ingérer les articles similaires
    for lang in fr en de sa; do
        DUMP="${WIKI_DUMPS_DIR}/${lang}wiki-latest-pages-articles.xml.bz2"
        
        if [ -f "$DUMP" ]; then
            log_info "Ingestion articles similaires (${lang})..."
            # TODO: Implémenter filtre par titre
            # Pour l'instant, on ingère un échantillon
            python3 "${SCRIPT_DIR}/wikipedia_ingestion.py" \
                --dump "$DUMP" \
                --lang "$lang" \
                --limit 50 \
                --api "$API_URL" || true
        fi
    done
    
    # Vérifier les stats de déduplication
    log_info "Récupération des statistiques de déduplication..."
    curl -s "${API_URL}/dedup/stats" | python3 -m json.tool
}

# Test Dhātu multilingue
test_dhatu_multilang() {
    log_info "========================================="
    log_info "TEST 4: ANALYSE DHĀTU MULTILINGUE"
    log_info "========================================="
    
    log_info "Récupération des statistiques émotionnelles..."
    curl -s "${API_URL}/dhatu/stats" | python3 -m json.tool
    
    log_info "Analyse émotionnelle par langue à implémenter..."
}

# Statistiques finales
show_final_stats() {
    log_info "========================================="
    log_info "STATISTIQUES FINALES"
    log_info "========================================="
    
    # Stats déduplication
    log_info "Déduplication:"
    curl -s "${API_URL}/dedup/stats" | python3 -c "
import sys, json
stats = json.load(sys.stdin)
print(f\"  Total fichiers: {stats.get('total_files', 0)}\")
print(f\"  Total atoms: {stats.get('total_atoms', 0)}\")
print(f\"  Taille totale: {stats.get('total_size', 0) / (1024**2):.1f} MB\")
print(f\"  Taille dédupliquée: {stats.get('dedup_size', 0) / (1024**2):.1f} MB\")
if stats.get('total_size', 0) > 0:
    ratio = (1 - stats.get('dedup_size', 0) / stats.get('total_size', 1)) * 100
    print(f\"  Économie d'espace: {ratio:.1f}%\")
" || log_warning "Erreur récupération stats"
    
    # Stats Dhātu
    log_info "Dhātu (Émotions):"
    curl -s "${API_URL}/dhatu/stats" | python3 -c "
import sys, json
stats = json.load(sys.stdin)
print(f\"  Total profils: {stats.get('total_profiles', 0)}\")
print(f\"  Arousal moyen: {stats.get('average_arousal', 0):.3f}\")
print(f\"  Émotion dominante: {stats.get('top_emotion', 'N/A')}\")
" || log_warning "Erreur récupération stats Dhātu"
    
    # Rapports sauvegardés
    log_info "Rapports disponibles dans: ${PANINI_FS_DIR}/reports/"
    ls -lh "${PANINI_FS_DIR}/reports/"wikipedia_*.json 2>/dev/null || true
}

# Menu principal
main() {
    log_info "🕉️  TEST WIKIPEDIA AVEC PANINI-FS 🕉️"
    log_info "Storage: ${STORAGE_DIR}"
    
    # Créer le répertoire de rapports
    mkdir -p "${PANINI_FS_DIR}/reports"
    
    # Vérifier l'API
    check_api
    
    # Tests progressifs
    log_info "\nChoisissez le test à exécuter:"
    echo "  1) Sanskrit uniquement (rapide, 100 articles)"
    echo "  2) Sanskrit + Hindi (moyen, 600 articles)"
    echo "  3) Tous les tests (complet, ~1000 articles)"
    echo "  4) Test de déduplication inter-langues"
    echo "  5) Statistiques uniquement"
    echo "  0) Quitter"
    
    read -p "Votre choix [1-5]: " choice
    
    case $choice in
        1)
            test_sanskrit
            show_final_stats
            ;;
        2)
            test_sanskrit
            test_hindi
            show_final_stats
            ;;
        3)
            test_sanskrit
            test_hindi
            test_multilang_dedup
            test_dhatu_multilang
            show_final_stats
            ;;
        4)
            test_multilang_dedup
            show_final_stats
            ;;
        5)
            show_final_stats
            ;;
        0)
            log_info "Au revoir!"
            exit 0
            ;;
        *)
            log_error "Choix invalide"
            exit 1
            ;;
    esac
    
    log_success "\n🎉 Tests terminés avec succès!"
    log_info "Les données Wikipedia sont maintenant dans Panini-FS"
    log_info "Accédez-y via l'API ou montez le système FUSE:"
    log_info "  PANINI_STORAGE=${STORAGE_DIR} cargo run --bin panini-mount /tmp/panini-mount"
}

# Exécuter
main "$@"
