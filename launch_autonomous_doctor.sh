#!/bin/bash
"""
🚀 Launcher Doctor Autonome
===========================

Lance le doctor en mode surveillance continue
Gestion des redémarrages automatiques
"""

DOCTOR_SCRIPT="autonomous_workflow_doctor.py"
LOG_DIR="OPERATIONS/logs"
PID_FILE="doctor.pid"

# Crée le répertoire de logs
mkdir -p "$LOG_DIR"

# Fonction de nettoyage
cleanup() {
    echo "🛑 Arrêt du Doctor..."
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        kill $PID 2>/dev/null
        rm -f "$PID_FILE"
        echo "✅ Doctor arrêté (PID: $PID)"
    fi
    exit 0
}

# Gestion des signaux
trap cleanup SIGTERM SIGINT

echo "🚀 LANCEMENT DOCTOR AUTONOME"
echo "============================"
echo "📅 $(date)"
echo "🎯 Surveillance continue des workflows GitHub"
echo "⏱️ Intervalle: 5 minutes"
echo "🛑 Ctrl+C pour arrêter"
echo ""

# Vérifie que le script existe
if [ ! -f "$DOCTOR_SCRIPT" ]; then
    echo "❌ Script non trouvé: $DOCTOR_SCRIPT"
    exit 1
fi

# Lance le doctor en arrière-plan
python3 "$DOCTOR_SCRIPT" &
DOCTOR_PID=$!

# Sauvegarde le PID
echo $DOCTOR_PID > "$PID_FILE"

echo "✅ Doctor lancé (PID: $DOCTOR_PID)"
echo "📁 Logs: $LOG_DIR/workflow_doctor_$(date +%Y-%m-%d).log"
echo "🔍 Surveillance: stephanedenis/PaniniFS"
echo ""
echo "💡 Pour arrêter: Ctrl+C ou kill $DOCTOR_PID"
echo ""

# Attend que le processus se termine
wait $DOCTOR_PID

# Nettoyage automatique
cleanup
