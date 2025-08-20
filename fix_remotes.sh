#!/bin/bash

# 🔧 CORRECTION DES REMOTES PANINIFS
# Fixe les remotes incorrects et synchronise tout

echo "🛠️  CORRECTION REMOTES ÉCOSYSTÈME PANINIFS"
echo "=========================================="

cd ~/GitHub

# Projets avec leurs remotes corrects
declare -A PROJECT_REMOTES
PROJECT_REMOTES["PaniniFS-1"]="https://github.com/stephanedenis/PaniniFS.git"
PROJECT_REMOTES["PaniniFS-AutonomousMissions"]="https://github.com/stephanedenis/PaniniFS-AutonomousMissions.git"
PROJECT_REMOTES["PaniniFS-CloudOrchestrator"]="https://github.com/stephanedenis/PaniniFS-CloudOrchestrator.git"
PROJECT_REMOTES["PaniniFS-CoLabController"]="https://github.com/stephanedenis/PaniniFS-CoLabController.git"
PROJECT_REMOTES["PaniniFS-PublicationEngine"]="https://github.com/stephanedenis/PaniniFS-PublicationEngine.git"
PROJECT_REMOTES["PaniniFS-SemanticCore"]="https://github.com/stephanedenis/PaniniFS-SemanticCore.git"
PROJECT_REMOTES["PaniniFS-UltraReactive"]="https://github.com/stephanedenis/PaniniFS-UltraReactive.git"

for PROJECT in "${!PROJECT_REMOTES[@]}"; do
    echo ""
    echo "🔧 Correction $PROJECT..."
    
    if [ -d "$PROJECT" ]; then
        cd "$PROJECT"
        
        EXPECTED_REMOTE="${PROJECT_REMOTES[$PROJECT]}"
        CURRENT_REMOTE=$(git remote get-url origin 2>/dev/null || echo "NONE")
        
        if [ "$CURRENT_REMOTE" != "$EXPECTED_REMOTE" ]; then
            echo "  🔄 Remote incorrect: $CURRENT_REMOTE"
            echo "  ✅ Correction vers: $EXPECTED_REMOTE"
            
            git remote remove origin 2>/dev/null || true
            git remote add origin "$EXPECTED_REMOTE"
            
            echo "  📝 Remote corrigé!"
        else
            echo "  ✅ Remote correct: $EXPECTED_REMOTE"
        fi
        
        # Vérifier s'il y a des modifications à commit
        if [ -n "$(git status --porcelain)" ]; then
            echo "  📦 Commit des modifications en cours..."
            git add .
            git commit -m "🔄 Sync $(date '+%Y-%m-%d %H:%M') - Corrections et mises à jour"
        fi
        
        cd ..
    else
        echo "  ❌ Projet $PROJECT introuvable"
    fi
done

echo ""
echo "🎯 REMOTES CORRIGÉS!"
echo ""
echo "🚀 Pour synchroniser maintenant:"
echo "   cd ~/GitHub/PaniniFS-1"
echo "   ./sync_paninifs_ecosystem.sh"
