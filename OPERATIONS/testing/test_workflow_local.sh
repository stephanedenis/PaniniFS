#!/bin/bash
#
# 🧪 TEST WORKFLOW LOCAL - SIMULATION GITHUB ACTIONS
# ==================================================
#
# Simule localement l'exécution du workflow deploy-docs.yml
# pour détecter les problèmes AVANT qu'ils ne causent des échecs.
#

set -euo pipefail

echo "🧪 TEST WORKFLOW LOCAL - Simulation GitHub Actions"
echo "=================================================="

# Configuration
BASE_DIR="/home/stephane/GitHub/PaniniFS-1"
TEST_DIR="$BASE_DIR/TEST_WORKFLOW_OUTPUT"
LOG_FILE="$TEST_DIR/workflow_test.log"

# Couleurs pour la sortie
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction de log avec couleurs
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "INFO")  echo -e "${BLUE}[INFO]${NC} $message" | tee -a "$LOG_FILE" ;;
        "SUCCESS") echo -e "${GREEN}[SUCCESS]${NC} $message" | tee -a "$LOG_FILE" ;;
        "WARNING") echo -e "${YELLOW}[WARNING]${NC} $message" | tee -a "$LOG_FILE" ;;
        "ERROR") echo -e "${RED}[ERROR]${NC} $message" | tee -a "$LOG_FILE" ;;
        *) echo "[$timestamp] $message" | tee -a "$LOG_FILE" ;;
    esac
}

# Nettoyage et préparation
log "INFO" "🧹 Préparation environnement de test..."
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"
cd "$BASE_DIR"

# Simulation étape 1: Checkout (déjà fait localement)
log "INFO" "📥 Étape 1: Checkout (simulation locale)"
log "SUCCESS" "Checkout simulé - nous sommes déjà dans le repo"

# Simulation étape 2: Setup Python
log "INFO" "🐍 Étape 2: Setup Python"
python_version=$(python3 --version 2>&1 || echo "Python non trouvé")
log "INFO" "Version Python détectée: $python_version"

if ! command -v python3 &> /dev/null; then
    log "ERROR" "Python3 non trouvé - échec attendu sur GitHub Actions"
    exit 1
fi

# Simulation étape 3: Install dependencies
log "INFO" "📦 Étape 3: Installation dépendances"

# Test en environnement isolé
log "INFO" "Création environnement virtuel temporaire..."
python3 -m venv "$TEST_DIR/venv" || {
    log "ERROR" "Impossible de créer l'environnement virtuel"
    exit 1
}

source "$TEST_DIR/venv/bin/activate"

log "INFO" "Installation mkdocs-material..."
if pip install mkdocs-material 2>&1 | tee -a "$LOG_FILE"; then
    log "SUCCESS" "mkdocs-material installé"
else
    log "ERROR" "Échec installation mkdocs-material"
    exit 1
fi

log "INFO" "Installation mkdocs-git-revision-date-localized-plugin..."
if pip install mkdocs-git-revision-date-localized-plugin 2>&1 | tee -a "$LOG_FILE"; then
    log "SUCCESS" "Plugin git-revision installé"
else
    log "ERROR" "Échec installation plugin git-revision"
    exit 1
fi

# Simulation étape 4: Build site
log "INFO" "🏗️ Étape 4: Build site MkDocs"

# Vérifier présence mkdocs.yml
if [[ ! -f "mkdocs.yml" ]]; then
    log "ERROR" "mkdocs.yml non trouvé"
    exit 1
fi

# Vérifier présence docs_new
if [[ ! -d "docs_new" ]]; then
    log "ERROR" "Répertoire docs_new non trouvé"
    exit 1
fi

log "INFO" "Lancement mkdocs build..."
if mkdocs build --config-file mkdocs.yml --site-dir "$TEST_DIR/site" 2>&1 | tee -a "$LOG_FILE"; then
    log "SUCCESS" "Build MkDocs réussi"
    
    # Vérifier contenu généré
    if [[ -f "$TEST_DIR/site/index.html" ]]; then
        log "SUCCESS" "index.html généré"
    else
        log "WARNING" "index.html non trouvé dans le site généré"
    fi
    
    if [[ -f "$TEST_DIR/site/dashboard/index.html" ]]; then
        log "SUCCESS" "Dashboard généré"
    else
        log "WARNING" "Dashboard non trouvé"
    fi
    
    # Taille du site
    site_size=$(du -sh "$TEST_DIR/site" | cut -f1)
    log "INFO" "Taille du site généré: $site_size"
    
else
    log "ERROR" "Échec build MkDocs"
    
    # Diagnostic détaillé en cas d'échec
    log "INFO" "🔍 DIAGNOSTIC DÉTAILLÉ:"
    log "INFO" "Contenu docs_new/:"
    ls -la docs_new/ | tee -a "$LOG_FILE"
    
    log "INFO" "Contenu mkdocs.yml (10 premières lignes):"
    head -10 mkdocs.yml | tee -a "$LOG_FILE"
    
    exit 1
fi

# Simulation étape 5: Test du résultat
log "INFO" "🧪 Étape 5: Tests de validation"

# Test 1: Vérifier structure HTML
if grep -q "PaniniFS" "$TEST_DIR/site/index.html" 2>/dev/null; then
    log "SUCCESS" "Contenu PaniniFS trouvé dans index.html"
else
    log "WARNING" "Contenu PaniniFS non trouvé dans index.html"
fi

# Test 2: Vérifier présence dashboard
if [[ -d "$TEST_DIR/site/dashboard" ]]; then
    log "SUCCESS" "Répertoire dashboard créé"
else
    log "WARNING" "Répertoire dashboard manquant"
fi

# Test 3: Vérifier JSON monitoring
if [[ -f "$TEST_DIR/site/data/system_status.json" ]]; then
    log "SUCCESS" "Fichier monitoring JSON présent"
else
    log "WARNING" "Fichier monitoring JSON manquant"
fi

# Simulation étape 6: Deploy (simulation)
log "INFO" "🚀 Étape 6: Deploy (simulation)"
log "INFO" "En production: peaceiris/actions-gh-pages@v3 serait utilisé"
log "INFO" "Fichiers à déployer:"
find "$TEST_DIR/site" -name "*.html" | head -10 | tee -a "$LOG_FILE"

# Désactiver environnement virtuel
deactivate

# Rapport final
log "INFO" "📋 RAPPORT FINAL"
echo "===================="

if [[ -f "$TEST_DIR/site/index.html" ]]; then
    log "SUCCESS" "✅ WORKFLOW DEVRAIT RÉUSSIR"
    log "INFO" "Toutes les étapes ont été simulées avec succès"
    log "INFO" "Site généré dans: $TEST_DIR/site/"
    
    echo ""
    log "INFO" "🌐 PREVIEW LOCAL POSSIBLE:"
    echo "cd $TEST_DIR/site && python3 -m http.server 8000"
    echo "Puis ouvrir: http://localhost:8000"
    
else
    log "ERROR" "❌ WORKFLOW VA PROBABLEMENT ÉCHOUER"
    log "ERROR" "Des problèmes ont été détectés"
fi

echo ""
log "INFO" "📄 Log détaillé: $LOG_FILE"
log "INFO" "🗂️ Artéfacts test: $TEST_DIR/"

echo ""
log "INFO" "🏕️ CAMPING STRATEGY: Test local terminé"
log "INFO" "Vous pouvez maintenant pousser en confiance !"

exit 0
