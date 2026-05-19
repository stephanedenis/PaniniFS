#!/bin/bash
# Installation de Dolt avec notifications utilisateur

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NOTIFY="$SCRIPT_DIR/notify_user.sh"

chmod +x "$NOTIFY"

echo "🚀 Installation de Dolt..."
echo ""

# Vérifie si Dolt est déjà installé
if command -v dolt &> /dev/null; then
    CURRENT_VERSION=$(dolt version | head -n1)
    echo "✅ Dolt est déjà installé: $CURRENT_VERSION"
    "$NOTIFY" "Dolt déjà installé: $CURRENT_VERSION" "Installation Dolt"
    exit 0
fi

echo "📥 Téléchargement du script d'installation..."
curl -L https://github.com/dolthub/dolt/releases/latest/download/install.sh -o /tmp/dolt_install.sh

echo ""
echo "🔐 Installation système requise (sudo nécessaire)..."
"$NOTIFY" "Mot de passe sudo requis pour installer Dolt" "Installation Dolt"
sleep 2

sudo bash /tmp/dolt_install.sh

echo ""
if command -v dolt &> /dev/null; then
    VERSION=$(dolt version | head -n1)
    echo "✅ Dolt installé avec succès!"
    echo "   Version: $VERSION"
    "$NOTIFY" "Dolt installé avec succès: $VERSION" "Installation Dolt"
else
    echo "❌ Échec de l'installation"
    "$NOTIFY" "Échec de l'installation de Dolt" "Installation Dolt"
    exit 1
fi

# Nettoyage
rm -f /tmp/dolt_install.sh

echo ""
echo "🎯 Prochaines étapes:"
echo "   1. python3 init_dolt.py          # Initialiser la base"
echo "   2. python3 demo_workflow.py      # Tester les workflows"
echo "   3. python3 test_multilingual_corpus.py  # Tester le corpus"
