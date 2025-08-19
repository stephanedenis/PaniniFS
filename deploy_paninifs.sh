#!/bin/bash

# 🚀 SCRIPT DÉPLOIEMENT PANINIFS.ORG
# Déploie le site MkDocs vers GitHub Pages

echo "🔥 DÉPLOIEMENT PANINIFS.ORG DÉMARRÉ"
echo "================================="

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

# 5. Ajouter CNAME
echo "🌐 Configuration domaine personnalisé..."
echo "paninifs.org" > site/CNAME

# 6. Déploiement via mkdocs gh-deploy
echo "🚀 Déploiement GitHub Pages..."
mkdocs gh-deploy --force --clean

echo "✅ DÉPLOIEMENT TERMINÉ!"
echo "📡 Le site sera disponible sur http://paninifs.org dans quelques minutes"
echo "🔄 Cache navigateur: Ctrl+F5 pour forcer le refresh"
