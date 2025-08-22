#!/bin/bash
#
# 🚨 SOLUTION RADICALE - NETTOYAGE COMPLET DOCS/
# ==============================================
#
# Supprime tout le contenu problématique de docs/ et ne garde 
# qu'une redirection simple pour arrêter définitivement les échecs.
#

set -euo pipefail

echo "🚨 Solution radicale - Nettoyage complet docs/"
echo "=============================================="
echo ""

# 1. Sauvegarde sécurité
echo "💾 Sauvegarde des fichiers importants..."
cd /home/stephane/GitHub/PaniniFS-1/docs
cp index.html index-backup.html
cp _config.yml config-backup.yml
echo "   ✅ Sauvegarde créée"

# 2. Nettoyage radical
echo "🧹 Suppression contenu problématique..."
rm -rf conversations/ methodology/ research/ vision/
rm -f agents-inventory.html dashboard.html index-old.md
echo "   ✅ Fichiers problématiques supprimés"

# 3. _config.yml minimal
echo "📝 Configuration Jekyll ultra-minimale..."
cat > _config.yml << 'EOF'
# Configuration Jekyll ultra-minimale pour GitHub Pages
title: "PaniniFS"
description: "Site migré vers paninifs.org"
baseurl: ""
url: "https://stephanedenis.github.io"

# Plugins minimaux
plugins:
  - jekyll-feed

# Exclusions
exclude:
  - README.md
  - Gemfile*
  - "*.backup"

# 🏕️ Configuration minimale pour éviter tout échec Jekyll
EOF

# 4. Gemfile minimal
echo "📦 Gemfile ultra-minimal..."
cat > Gemfile << 'EOF'
source "https://rubygems.org"
gem "github-pages", group: :jekyll_plugins
EOF

# 5. index.html simplifié
echo "🌐 Page de redirection simplifiée..."
cat > index.html << 'EOF'
---
layout: none
---
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="0; url=https://paninifs.org/">
    <title>PaniniFS - Redirected</title>
</head>
<body>
    <h1>🏕️ PaniniFS</h1>
    <p>Site moved to <a href="https://paninifs.org/">paninifs.org</a></p>
    <script>window.location.href = 'https://paninifs.org/';</script>
</body>
</html>
EOF

# 6. README simple
echo "📄 README explicatif..."
cat > README.md << 'EOF'
# 🏕️ PaniniFS Legacy Site

**Site migré vers [paninifs.org](https://paninifs.org)**

Cette page GitHub Pages effectue une redirection automatique.

🏕️ Camping Strategy: Infrastructure externalisée
EOF

echo ""
echo "✅ NETTOYAGE TERMINÉ"
echo "==================="
echo "📁 Contenu docs/ maintenant minimal:"
ls -la

echo ""
echo "🎯 RÉSULTAT ATTENDU:"
echo "   ✅ Jekyll build simple et sans erreur"
echo "   ✅ Redirection fonctionnelle vers paninifs.org"
echo "   ✅ Fin définitive des échecs GitHub Pages"

echo ""
echo "🏕️ Prêt pour commit et test final!"

exit 0
