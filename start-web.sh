#!/bin/bash
# Script pour démarrer le site Web Panini-FS

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB_UI_DIR="$SCRIPT_DIR/web-ui"

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         🌐 PANINI-FS WEB INTERFACE LAUNCHER 🌐          ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Vérifier si l'API est en cours d'exécution
echo -e "${YELLOW}⏳ Vérification de l'API Panini...${NC}"
if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API Panini détectée sur http://localhost:3000${NC}"
else
    echo -e "${YELLOW}⚠️  API Panini non détectée${NC}"
    echo -e "${YELLOW}   Lancez d'abord: PANINI_STORAGE=<path> cargo run --bin panini-api${NC}"
    echo ""
    read -p "Continuer quand même? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}📦 Installation des dépendances...${NC}"
cd "$WEB_UI_DIR"

if [ ! -d "node_modules" ]; then
    npm install
else
    echo -e "${GREEN}✅ Dépendances déjà installées${NC}"
fi

echo ""
echo -e "${BLUE}🚀 Démarrage du serveur de développement...${NC}"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}   Site Web disponible sur: ${BLUE}http://localhost:5173${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}📊 Pages disponibles:${NC}"
echo -e "   • Dashboard:      http://localhost:5173/"
echo -e "   • Concepts:       http://localhost:5173/concepts"
echo -e "   • Timeline:       http://localhost:5173/timeline"
echo -e "   • Snapshots:      http://localhost:5173/snapshots"
echo -e "   • Dhātu:          http://localhost:5173/dhatu"
echo -e "   • Graph Explorer: ${GREEN}http://localhost:5173/graph${NC} ⭐ NOUVEAU"
echo ""
echo -e "${YELLOW}🌟 Graph Explorer:${NC}"
echo -e "   Navigate the complete Panini content-addressed storage graph"
echo -e "   • View all atoms and their connections"
echo -e "   • Explore file relationships"
echo -e "   • Analyze deduplication patterns"
echo -e "   • Interactive network visualization"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

npm run dev
