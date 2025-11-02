#!/bin/bash
# Start Panini-FS API for Wikipedia testing

set -e

PANINI_DIR="/home/stephane/GitHub/Panini-FS"
STORAGE_DIR="${PANINI_STORAGE:-/tmp/panini-wikipedia-test}"
LOG_FILE="/tmp/panini-wikipedia-api.log"

echo "🚀 Lancement de l'API Panini-FS pour tests Wikipedia"
echo "   Storage: $STORAGE_DIR"
echo "   Logs: $LOG_FILE"

# Créer le storage
mkdir -p "$STORAGE_DIR"

# Arrêter les processus existants
pkill -f panini-api && echo "✓ Processus existants arrêtés" || true
sleep 2

# Compiler en mode release pour la performance
echo "⚙️  Compilation en mode release..."
cd "$PANINI_DIR"
cargo build --bin panini-api --release 2>&1 | tail -10

# Lancer l'API
echo "🚀 Démarrage de l'API..."
PANINI_STORAGE="$STORAGE_DIR" \
RUST_LOG=info \
"$PANINI_DIR/target/release/panini-api" > "$LOG_FILE" 2>&1 &

API_PID=$!
echo "$API_PID" > /tmp/panini-api.pid
echo "   PID: $API_PID"

# Attendre le démarrage
echo "⏳ Attente du démarrage (10 secondes)..."
sleep 10

# Vérifier que l'API répond
if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✅ API démarrée avec succès!"
    echo "   Health: http://localhost:3000/api/health"
    echo "   Dedup: http://localhost:3000/api/dedup/stats"
    echo "   Dhātu: http://localhost:3000/api/dhatu/stats"
    echo
    echo "📝 Logs en temps réel: tail -f $LOG_FILE"
    echo "🛑 Arrêter l'API: kill $API_PID"
else
    echo "❌ Erreur: L'API ne répond pas"
    echo "Derniers logs:"
    tail -20 "$LOG_FILE"
    exit 1
fi
