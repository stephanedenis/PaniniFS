#!/bin/bash

# 🚀 SCRIPT SYNCHRONISATION PROJETS PANINIFS VERS GITHUB
# Créé et pousse tous les projets PaniniFS locaux vers GitHub

echo "🔥 SYNCHRONISATION ÉCOSYSTÈME PANINIFS VERS GITHUB"
echo "=================================================="

cd ~/GitHub

# Liste des projets PaniniFS locaux
PROJECTS=(
    "PaniniFS-AutonomousMissions"
    "PaniniFS-CloudOrchestrator" 
    "PaniniFS-CoLabController"
    "PaniniFS-PublicationEngine"
    "PaniniFS-SemanticCore"
    "PaniniFS-UltraReactive"
)

for PROJECT in "${PROJECTS[@]}"; do
    echo ""
    echo "📂 Traitement de $PROJECT..."
    
    if [ -d "$PROJECT" ]; then
        cd "$PROJECT"
        
        # Vérifier si c'est un repo git
        if [ ! -d ".git" ]; then
            echo "  🔧 Initialisation Git..."
            git init
            git add .
            git commit -m "🎯 Initial commit $PROJECT - Écosystème PaniniFS"
        fi
        
        # Vérifier le remote
        CURRENT_REMOTE=$(git remote get-url origin 2>/dev/null || echo "NONE")
        EXPECTED_REMOTE="https://github.com/stephanedenis/$PROJECT.git"
        
        if [ "$CURRENT_REMOTE" != "$EXPECTED_REMOTE" ]; then
            echo "  🔗 Configuration remote GitHub..."
            git remote remove origin 2>/dev/null || true
            git remote add origin "$EXPECTED_REMOTE"
        fi
        
        # Créer le repo sur GitHub (via API si possible)
        echo "  🌐 Création repo GitHub: $PROJECT"
        curl -s -X POST \
            -H "Accept: application/vnd.github.v3+json" \
            -H "Authorization: token $GITHUB_TOKEN" \
            https://api.github.com/user/repos \
            -d "{\"name\":\"$PROJECT\",\"description\":\"Module $PROJECT de l'écosystème PaniniFS\",\"private\":false}" \
            >/dev/null 2>&1
        
        # Push vers GitHub  
        echo "  📤 Push vers GitHub..."
        git branch -M main 2>/dev/null || git branch -M master
        git push -u origin main 2>/dev/null || git push -u origin master
        
        if [ $? -eq 0 ]; then
            echo "  ✅ $PROJECT synchronisé avec succès"
        else
            echo "  ⚠️  $PROJECT: push échoué (repo existe peut-être déjà)"
        fi
        
        cd ..
    else
        echo "  ❌ Dossier $PROJECT introuvable"
    fi
done

echo ""
echo "🎉 SYNCHRONISATION TERMINÉE!"
echo ""
echo "📋 Projets traités:"
for PROJECT in "${PROJECTS[@]}"; do
    echo "   - https://github.com/stephanedenis/$PROJECT"
done
echo ""
echo "🔍 Vérifiez sur GitHub: https://github.com/stephanedenis?tab=repositories"
