#!/bin/bash
# 🎭 SCRIPT DE CONTRÔLE SESSION GITHUB
# Gestion du processus Playwright autonome

SCRIPT_DIR="/home/stephane/GitHub/PaniniFS-1/ECOSYSTEM/tools"
VENV_PATH="/home/stephane/GitHub/PaniniFS-1/venv_playwright"
SERVER_SCRIPT="$SCRIPT_DIR/github_session_manager.py"
CLIENT_SCRIPT="$SCRIPT_DIR/github_session_client.py"
PID_FILE="/tmp/github_session_manager.pid"

# Couleurs pour le terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_session_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0  # Running
        else
            rm -f "$PID_FILE"
            return 1  # Not running
        fi
    else
        return 1  # Not running
    fi
}

start_session() {
    log_info "Démarrage du GitHub Session Manager..."
    
    if check_session_running; then
        log_warning "Session déjà en cours"
        return 0
    fi
    
    # Activer l'environnement et démarrer en arrière-plan
    cd /home/stephane/GitHub/PaniniFS-1
    source "$VENV_PATH/bin/activate"
    
    nohup python3 "$SERVER_SCRIPT" > /tmp/github_session_manager.log 2>&1 &
    echo $! > "$PID_FILE"
    
    # Attendre que le serveur démarre
    sleep 3
    
    if check_session_running; then
        log_success "Session Manager démarré (PID: $(cat $PID_FILE))"
        log_info "WebSocket Server: ws://localhost:8765"
        log_info "Logs: tail -f /tmp/github_session_manager.log"
        return 0
    else
        log_error "Échec du démarrage"
        return 1
    fi
}

stop_session() {
    log_info "Arrêt du GitHub Session Manager..."
    
    if check_session_running; then
        PID=$(cat "$PID_FILE")
        kill "$PID"
        rm -f "$PID_FILE"
        log_success "Session arrêtée"
    else
        log_warning "Aucune session en cours"
    fi
}

status_session() {
    if check_session_running; then
        PID=$(cat "$PID_FILE")
        log_success "Session active (PID: $PID)"
        log_info "WebSocket: ws://localhost:8765"
        
        # Test de connexion
        python3 -c "
import asyncio
import websockets
import json

async def test_connection():
    try:
        async with websockets.connect('ws://localhost:8765') as ws:
            await ws.send(json.dumps({'command': 'status'}))
            response = await ws.recv()
            data = json.loads(response)
            print(f'  📊 URL: {data.get(\"url\", \"N/A\")}')
            print(f'  🔐 Connecté: {data.get(\"logged_in\", False)}')
            print(f'  ⏱️  Durée: {data.get(\"session_duration\", \"N/A\")}')
    except Exception as e:
        print(f'  ❌ Erreur connexion: {e}')

asyncio.run(test_connection())
        " 2>/dev/null
    else
        log_error "Aucune session active"
    fi
}

restart_session() {
    stop_session
    sleep 2
    start_session
}

demo_client() {
    log_info "Démarrage du client de démonstration..."
    
    if ! check_session_running; then
        log_error "Session Manager non démarré. Utilisez: $0 start"
        return 1
    fi
    
    cd /home/stephane/GitHub/PaniniFS-1
    source "$VENV_PATH/bin/activate"
    python3 "$CLIENT_SCRIPT"
}

quick_labels() {
    log_info "Création rapide de labels..."
    
    if ! check_session_running; then
        log_error "Session Manager non démarré. Utilisez: $0 start"
        return 1
    fi
    
    cd /home/stephane/GitHub/PaniniFS-1
    source "$VENV_PATH/bin/activate"
    python3 "$CLIENT_SCRIPT" quick
}

show_logs() {
    if [ -f "/tmp/github_session_manager.log" ]; then
        tail -f /tmp/github_session_manager.log
    else
        log_error "Aucun fichier de log trouvé"
    fi
}

case "$1" in
    start)
        start_session
        ;;
    stop)
        stop_session
        ;;
    status)
        status_session
        ;;
    restart)
        restart_session
        ;;
    demo)
        demo_client
        ;;
    labels)
        quick_labels
        ;;
    logs)
        show_logs
        ;;
    *)
        echo "🎭 GITHUB SESSION CONTROLLER"
        echo "Usage: $0 {start|stop|status|restart|demo|labels|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Démarrer le Session Manager"
        echo "  stop    - Arrêter le Session Manager"
        echo "  status  - Afficher l'état de la session"
        echo "  restart - Redémarrer le Session Manager"
        echo "  demo    - Lancer le client de démonstration"
        echo "  labels  - Création rapide de labels"
        echo "  logs    - Afficher les logs en temps réel"
        exit 1
        ;;
esac
