#!/bin/bash
#
# 🔍 SURVEILLANCE TEMPS RÉEL - ATTENTE CORRECTION GITHUB PAGES
# ============================================================
#
# Surveille en continu jusqu'à ce que les échecs "pages build and deployment" cessent
#

echo "🔍 Surveillance temps réel des workflows"
echo "========================================"
echo ""
echo "🎯 Objectif: Détecter quand la configuration GitHub Pages sera corrigée"
echo "⏳ En attente que les échecs 'pages build and deployment' cessent..."
echo ""

# Compteurs
check_count=0
last_failure_time=""

while true; do
    ((check_count++))
    current_time=$(date '+%H:%M:%S')
    
    echo "🔍 Vérification #$check_count - $current_time"
    
    # Récupérer les 3 derniers workflows
    response=$(curl -s "https://api.github.com/repos/stephanedenis/PaniniFS/actions/runs?per_page=3" 2>/dev/null)
    
    if echo "$response" | grep -q "workflow_runs"; then
        
        # Analyser avec Python
        analysis=$(echo "$response" | python3 -c "
import json, sys
from datetime import datetime

try:
    data = json.load(sys.stdin)
    runs = data.get('workflow_runs', [])
    
    pages_failures = 0
    mkdocs_successes = 0
    latest_pages_fail = None
    latest_mkdocs_success = None
    
    for run in runs:
        name = run.get('name', '')
        status = run.get('status', '')
        conclusion = run.get('conclusion', '')
        created = run.get('created_at', '')
        
        if 'pages build' in name and conclusion == 'failure':
            pages_failures += 1
            if latest_pages_fail is None:
                latest_pages_fail = created[:19]
        
        if 'Deploy MkDocs' in name and conclusion == 'success':
            mkdocs_successes += 1
            if latest_mkdocs_success is None:
                latest_mkdocs_success = created[:19]
    
    print(f'PAGES_FAIL:{pages_failures}')
    print(f'MKDOCS_OK:{mkdocs_successes}') 
    print(f'LAST_PAGES_FAIL:{latest_pages_fail or \"none\"}')
    print(f'LAST_MKDOCS_OK:{latest_mkdocs_success or \"none\"}')
    
except Exception as e:
    print(f'ERROR:{e}')
" 2>/dev/null)
        
        if echo "$analysis" | grep -q "PAGES_FAIL:0"; then
            echo "🎉 SUCCÈS! Plus d'échec 'pages build and deployment' détecté!"
            echo "✅ Configuration GitHub Pages corrigée avec succès"
            echo ""
            echo "🏕️ Camping Strategy: Infrastructure maintenant 100% fonctionnelle!"
            break
        else
            pages_fail_count=$(echo "$analysis" | grep "PAGES_FAIL:" | cut -d: -f2)
            mkdocs_ok_count=$(echo "$analysis" | grep "MKDOCS_OK:" | cut -d: -f2)
            
            echo "   📊 Échecs 'pages build': $pages_fail_count"
            echo "   ✅ Succès MkDocs: $mkdocs_ok_count"
            
            latest_fail=$(echo "$analysis" | grep "LAST_PAGES_FAIL:" | cut -d: -f2)
            if [[ "$latest_fail" != "none" && "$latest_fail" != "$last_failure_time" ]]; then
                echo "   ⚠️ Nouvel échec détecté à: $latest_fail"
                echo "   🔧 Configuration GitHub Pages toujours à corriger"
                last_failure_time="$latest_fail"
            fi
        fi
        
    else
        echo "   ❌ Erreur API GitHub"
    fi
    
    echo "   ⏳ Attente 30 secondes... (Ctrl+C pour arrêter)"
    sleep 30 || break
    echo ""
done

echo ""
echo "📊 MONITORING TERMINÉ"
echo "===================="
echo "Total vérifications: $check_count"
echo "🏕️ Infrastructure camping strategy opérationnelle!"

exit 0
