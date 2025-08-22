#!/bin/bash
#
# 🔍 MONITORING WORKFLOWS GITHUB EN TEMPS RÉEL
# =============================================
#
# Script pour surveiller les workflows GitHub sans attendre
# les notifications par email. Utilise l'API GitHub.
#

set -euo pipefail

echo "🔍 Monitoring Workflows GitHub - Temps Réel"
echo "=========================================="

# Configuration
REPO_OWNER="stephanedenis"
REPO_NAME="PaniniFS"
API_BASE="https://api.github.com/repos/$REPO_OWNER/$REPO_NAME"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Fonction pour afficher avec couleurs
status_color() {
    local status="$1"
    case "$status" in
        "success"|"completed") echo -e "${GREEN}$status${NC}" ;;
        "failure"|"failed") echo -e "${RED}$status${NC}" ;;
        "in_progress"|"queued") echo -e "${YELLOW}$status${NC}" ;;
        *) echo -e "${BLUE}$status${NC}" ;;
    esac
}

# Fonction pour récupérer les workflows
get_workflows() {
    echo "📡 Récupération des workflows en cours..."
    
    # Utiliser curl avec gestion d'erreur
    local response
    if ! response=$(curl -s "$API_BASE/actions/runs?per_page=10" 2>/dev/null); then
        echo "❌ Erreur: Impossible de contacter l'API GitHub"
        echo "💡 Vérifiez votre connexion internet"
        return 1
    fi
    
    # Vérifier si la réponse contient des données
    if echo "$response" | grep -q '"message".*"API rate limit exceeded"'; then
        echo "⏳ Rate limit API GitHub atteint"
        echo "💡 Attendez quelques minutes ou configurez un token GitHub"
        return 1
    fi
    
    if echo "$response" | grep -q '"workflow_runs"'; then
        echo "$response"
    else
        echo "⚠️ Réponse API inattendue:"
        echo "$response" | head -3
        return 1
    fi
}

# Fonction pour parser et afficher les workflows
display_workflows() {
    local response="$1"
    
    echo ""
    echo "📊 ÉTAT DES WORKFLOWS"
    echo "===================="
    
    # Utiliser Python pour parser le JSON (plus fiable que jq)
    python3 << EOF
import json
import sys
from datetime import datetime, timezone

try:
    data = json.loads('''$response''')
    runs = data.get('workflow_runs', [])
    
    if not runs:
        print("ℹ️ Aucun workflow trouvé")
        sys.exit(0)
    
    print(f"🔍 {len(runs)} workflows récents trouvés\n")
    
    for i, run in enumerate(runs[:5]):  # Top 5
        name = run.get('name', 'Unknown')
        status = run.get('status', 'unknown')
        conclusion = run.get('conclusion', '')
        
        # Formatage date
        created = run.get('created_at', '')
        if created:
            try:
                dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                created_fmt = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                created_fmt = created[:19]
        else:
            created_fmt = 'Unknown'
        
        # Déterminer l'état final
        if status == 'completed':
            final_status = conclusion or 'completed'
        else:
            final_status = status
        
        # Icône selon le statut
        if final_status == 'success':
            icon = '✅'
        elif final_status in ['failure', 'failed']:
            icon = '❌'
        elif final_status in ['in_progress', 'queued']:
            icon = '🔄'
        else:
            icon = '❓'
        
        print(f"{icon} {name}")
        print(f"   📅 {created_fmt}")
        print(f"   📊 Status: {final_status}")
        
        # URL du workflow
        html_url = run.get('html_url', '')
        if html_url:
            print(f"   🔗 {html_url}")
        
        print()

except json.JSONDecodeError as e:
    print(f"❌ Erreur parsing JSON: {e}")
    print("🔍 Contenu reçu:")
    print('''$response'''[:200] + "...")
except Exception as e:
    print(f"❌ Erreur: {e}")
EOF
}

# Fonction pour surveiller en continu
monitor_continuous() {
    echo "🔄 Mode surveillance continue (Ctrl+C pour arrêter)"
    echo "=================================================="
    
    local count=0
    while true; do
        ((count++))
        echo -e "\n🔍 Vérification #$count - $(date '+%H:%M:%S')"
        
        if response=$(get_workflows); then
            display_workflows "$response"
        else
            echo "⚠️ Échec de récupération des workflows"
        fi
        
        echo "⏳ Attente 30 secondes... (Ctrl+C pour arrêter)"
        sleep 30 || break
    done
}

# Fonction pour vérification unique
check_once() {
    echo "📡 Vérification unique des workflows..."
    
    if response=$(get_workflows); then
        display_workflows "$response"
        
        echo ""
        echo "💡 CONSEILS:"
        echo "   • Pour surveillance continue: $0 --watch"
        echo "   • Workflows GitHub: https://github.com/$REPO_OWNER/$REPO_NAME/actions"
        echo "   • Statut en temps réel sans attendre les emails!"
        
    else
        echo "❌ Impossible de récupérer les workflows"
        echo ""
        echo "🔧 SOLUTIONS:"
        echo "   1. Vérifiez votre connexion internet"
        echo "   2. Configurez un token GitHub (GITHUB_TOKEN)"
        echo "   3. Consultez directement: https://github.com/$REPO_OWNER/$REPO_NAME/actions"
    fi
}

# Fonction principale
main() {
    case "${1:-}" in
        "--watch"|"-w")
            monitor_continuous
            ;;
        "--help"|"-h")
            echo "Usage: $0 [--watch|--help]"
            echo ""
            echo "Options:"
            echo "  --watch, -w    Surveillance continue"
            echo "  --help, -h     Afficher cette aide"
            echo ""
            echo "🏕️ Camping Strategy: Monitoring workflows sans notifications email!"
            ;;
        "")
            check_once
            ;;
        *)
            echo "❌ Option inconnue: $1"
            echo "💡 Utilisez --help pour l'aide"
            exit 1
            ;;
    esac
}

# Détection Ctrl+C
trap 'echo -e "\n🏕️ Surveillance interrompue. À bientôt!"; exit 0' INT

# Lancement
main "$@"
