#!/bin/bash

echo "🔧 VÉRIFICATION GITHUB PAGES CONFIGURATION"
echo "=========================================="

# Instructions pour configurer GitHub Pages
cat << 'EOF'
📋 INSTRUCTIONS CONFIGURATION GITHUB PAGES:

1. 🌐 Aller sur: https://github.com/stephanedenis/PaniniFS/settings/pages

2. ⚙️ Configuration Source:
   - Source: "Deploy from a branch"
   - Branch: "master" 
   - Folder: "/site"

3. 🎯 Custom Domain:
   - Custom domain: "paninifs.org"
   - ✅ Enforce HTTPS: activé

4. 🔄 Attendre quelques minutes pour propagation

5. ✅ Vérifier: http://paninifs.org doit afficher MkDocs
EOF

echo ""
echo "🚀 Vérification état actuel:"
echo "Last-Modified sur paninifs.org:"
curl -s -I http://paninifs.org/ | grep -i last-modified

echo ""
echo "📊 Contenu détecté:"
if curl -s http://paninifs.org/ | grep -q "MDwiki"; then
    echo "❌ ANCIEN CONTENU: MDwiki encore présent"
    echo "➡️  GitHub Pages utilise encore l'ancienne source"
    echo "🔧 Action requise: Configurer source = master branch /site folder"
else
    echo "✅ NOUVEAU CONTENU: MkDocs déployé avec succès"
fi

echo ""
echo "🕐 Si MDwiki persiste:"
echo "   1. Vérifier configuration GitHub Pages settings"
echo "   2. Attendre 5-10 minutes pour propagation"
echo "   3. Vider cache navigateur (Ctrl+F5)"
