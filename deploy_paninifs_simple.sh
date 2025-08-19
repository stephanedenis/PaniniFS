#!/bin/bash

# 🚀 SCRIPT DÉPLOIEMENT PANINIFS.ORG - VERSION MASTER/SITE
# Déploie le site MkDocs directement depuis le dossier /site de master

echo "🔥 DÉPLOIEMENT PANINIFS.ORG (master/site)"
echo "========================================"

# 1. Vérifier que nous sommes dans le bon répertoire
if [ ! -f "mkdocs.yml" ]; then
    echo "❌ Erreur: mkdocs.yml non trouvé. Exécuter depuis la racine du projet."
    exit 1
fi

# 2. Activer l'environnement virtuel
if [ -d "mkdocs_env" ]; then
    echo "📦 Activation environnement MkDocs..."
    source mkdocs_env/bin/activate
else
    echo "❌ Environnement mkdocs_env non trouvé"
    exit 1
fi

# 3. Build propre
echo "🏗️ Build MkDocs clean..."
mkdocs build --clean

# 4. Vérifier que le site a été généré
if [ ! -f "site/index.html" ]; then
    echo "❌ Erreur: site/index.html non généré"
    exit 1
fi

# 5. Ajouter CNAME pour domaine personnalisé
echo "🌐 Configuration domaine personnalisé..."
echo "paninifs.org" > site/CNAME

# 6. Commit et push du dossier site/
echo "💾 Commit et push dossier site/..."
git add site/
git commit -m "🚀 Update site MkDocs pour paninifs.org - $(date '+%Y-%m-%d %H:%M')"
git push origin master

echo ""
echo "✅ DÉPLOIEMENT TERMINÉ!"
echo ""
echo "📋 CONFIGURATION GITHUB PAGES REQUISE:"
echo "   1. Aller sur: https://github.com/stephanedenis/PaniniFS/settings/pages"
echo "   2. Source: 'Deploy from a branch'"
echo "   3. Branch: 'master'"
echo "   4. Folder: '/site'"
echo "   5. Custom domain: 'paninifs.org'"
echo ""
echo "📡 Le site sera disponible sur http://paninifs.org dans quelques minutes"
echo "🔄 Cache navigateur: Ctrl+F5 pour forcer le refresh"
