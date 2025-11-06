#!/bin/bash
# Monitoring automatique de l'ingestion Wikipedia
# Affiche les statistiques toutes les 15 minutes

set -euo pipefail

# Configuration
INTERVAL_SECONDS=900  # 15 minutes
API_URL="${PANINI_API_URL:-http://localhost:3000}"
STORAGE_DIR="${PANINI_STORAGE:-/home/stephane/panini-wikipedia-full}"
LOG_FILE="/tmp/wikipedia-ingestion.log"
MONITOR_LOG="/tmp/wikipedia-monitor.log"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

# Symboles
CLOCK="⏱"
ROCKET="🚀"
CHART="📊"
CHECK="✅"
WARN="⚠️"
FIRE="🔥"

timestamp() {
    date '+%Y-%m-%d %H:%M:%S'
}

log_monitor() {
    echo "[$(timestamp)] $1" | tee -a "$MONITOR_LOG"
}

print_banner() {
    clear
    echo -e "${BOLD}${CYAN}"
    cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║     📊 MONITORING INGESTION WIKIPEDIA - LIVE STATS 📊    ║
╚═══════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

format_size() {
    local bytes=$1
    if [ "$bytes" -lt 1024 ]; then
        echo "${bytes}B"
    elif [ "$bytes" -lt 1048576 ]; then
        echo "$((bytes / 1024))KB"
    elif [ "$bytes" -lt 1073741824 ]; then
        echo "$((bytes / 1048576))MB"
    else
        echo "$((bytes / 1073741824))GB"
    fi
}

format_duration() {
    local seconds=$1
    local hours=$((seconds / 3600))
    local mins=$(( (seconds % 3600) / 60 ))
    local secs=$((seconds % 60))
    
    if [ $hours -gt 0 ]; then
        printf "%dh%02dm%02ds" $hours $mins $secs
    elif [ $mins -gt 0 ]; then
        printf "%dm%02ds" $mins $secs
    else
        printf "%ds" $secs
    fi
}

get_storage_usage() {
    if [ -d "$STORAGE_DIR" ]; then
        du -sb "$STORAGE_DIR" 2>/dev/null | cut -f1 || echo "0"
    else
        echo "0"
    fi
}

get_storage_available() {
    df -B1 "$STORAGE_DIR" 2>/dev/null | tail -1 | awk '{print $4}' || echo "0"
}

extract_articles_from_log() {
    # Cherche la dernière ligne avec "articles traités"
    local articles=$(grep -oP '\d+(?= articles traités)' "$LOG_FILE" 2>/dev/null | tail -1 || echo "0")
    echo "$articles"
}

extract_speed_from_log() {
    # Cherche la dernière vitesse
    local speed=$(grep -oP 'Vitesse: \K[\d.]+' "$LOG_FILE" 2>/dev/null | tail -1 || echo "0")
    echo "$speed"
}

extract_language_from_log() {
    # Cherche la langue en cours
    local lang=$(grep -oP 'Ingestion Wikipedia \(\K[a-z]+' "$LOG_FILE" 2>/dev/null | tail -1 || echo "unknown")
    echo "$lang"
}

get_api_stats() {
    curl -s "$API_URL/api/dedup/stats" 2>/dev/null || echo "{}"
}

get_dhatu_stats() {
    curl -s "$API_URL/api/dhatu/stats" 2>/dev/null || echo "{}"
}

calculate_eta() {
    local current_articles=$1
    local speed=$2
    local total_estimate=12000000  # 12M articles total
    
    if [ "$speed" == "0" ] || [ $(echo "$speed == 0" | bc -l) -eq 1 ]; then
        echo "N/A"
        return
    fi
    
    local remaining=$((total_estimate - current_articles))
    local seconds_remaining=$(echo "$remaining / $speed" | bc)
    
    format_duration "$seconds_remaining"
}

display_stats() {
    local iteration=$1
    local start_time=$2
    
    print_banner
    
    echo -e "${BOLD}${PURPLE}═══ Monitoring #$iteration ═══${NC}"
    echo -e "${CYAN}Timestamp: $(timestamp)${NC}"
    echo -e "${CYAN}Uptime: $(format_duration $(($(date +%s) - start_time)))${NC}\n"
    
    # Stats depuis le log
    echo -e "${BOLD}${YELLOW}${ROCKET} Ingestion en cours:${NC}"
    
    local current_articles=$(extract_articles_from_log)
    local current_speed=$(extract_speed_from_log)
    local current_lang=$(extract_language_from_log)
    
    echo -e "  ${GREEN}Langue:${NC} $current_lang"
    echo -e "  ${GREEN}Articles traités:${NC} $(printf "%'d" $current_articles)"
    echo -e "  ${GREEN}Vitesse:${NC} $current_speed articles/sec"
    
    if [ "$current_speed" != "0" ]; then
        local eta=$(calculate_eta "$current_articles" "$current_speed")
        echo -e "  ${BLUE}ETA (estimé):${NC} $eta restant"
    fi
    
    # Stats API
    echo -e "\n${BOLD}${YELLOW}${CHART} Statistiques API:${NC}"
    
    local api_stats=$(get_api_stats)
    
    if [ "$api_stats" != "{}" ]; then
        local total_files=$(echo "$api_stats" | jq -r '.data.total_files // 0' 2>/dev/null || echo "0")
        local unique_atoms=$(echo "$api_stats" | jq -r '.data.unique_atoms // 0' 2>/dev/null || echo "0")
        local dedup_ratio=$(echo "$api_stats" | jq -r '.data.dedup_ratio // 0' 2>/dev/null || echo "0")
        local storage_saved=$(echo "$api_stats" | jq -r '.data.storage_saved // 0' 2>/dev/null || echo "0")
        
        echo -e "  ${GREEN}Fichiers totaux:${NC} $(printf "%'d" $total_files)"
        echo -e "  ${GREEN}Atoms uniques:${NC} $(printf "%'d" $unique_atoms)"
        echo -e "  ${GREEN}Ratio déduplication:${NC} $(printf "%.2f" $dedup_ratio)%"
        echo -e "  ${GREEN}Économie stockage:${NC} $(format_size $storage_saved)"
    else
        echo -e "  ${WARN} API non accessible"
    fi
    
    # Stats Dhātu
    echo -e "\n${BOLD}${YELLOW}${FIRE} Statistiques Dhātu:${NC}"
    
    local dhatu_stats=$(get_dhatu_stats)
    
    if [ "$dhatu_stats" != "{}" ]; then
        local total_profiles=$(echo "$dhatu_stats" | jq -r '.data.total_profiles // 0' 2>/dev/null || echo "0")
        local avg_arousal=$(echo "$dhatu_stats" | jq -r '.data.average_arousal // 0' 2>/dev/null || echo "0")
        local top_emotion=$(echo "$dhatu_stats" | jq -r '.data.top_emotion // "N/A"' 2>/dev/null || echo "N/A")
        
        echo -e "  ${GREEN}Profils émotionnels:${NC} $(printf "%'d" $total_profiles)"
        echo -e "  ${GREEN}Arousal moyen:${NC} $(printf "%.3f" $avg_arousal)"
        echo -e "  ${GREEN}Émotion dominante:${NC} $top_emotion"
    else
        echo -e "  ${WARN} Stats Dhātu non disponibles"
    fi
    
    # Stats stockage
    echo -e "\n${BOLD}${YELLOW}💾 Stockage:${NC}"
    
    local storage_used=$(get_storage_usage)
    local storage_avail=$(get_storage_available)
    local storage_percent=0
    
    if [ "$storage_avail" != "0" ]; then
        storage_percent=$(echo "scale=1; 100 * $storage_used / ($storage_used + $storage_avail)" | bc)
    fi
    
    echo -e "  ${GREEN}Utilisé:${NC} $(format_size $storage_used)"
    echo -e "  ${GREEN}Disponible:${NC} $(format_size $storage_avail)"
    echo -e "  ${GREEN}Utilisation:${NC} ${storage_percent}%"
    
    if [ $(echo "$storage_percent > 90" | bc -l) -eq 1 ]; then
        echo -e "  ${RED}${WARN} ALERTE: Espace disque faible!${NC}"
    fi
    
    # Dernières lignes du log
    echo -e "\n${BOLD}${YELLOW}📝 Dernières activités:${NC}"
    tail -5 "$LOG_FILE" 2>/dev/null | sed 's/^/  /' || echo "  (Log non disponible)"
    
    # Separator
    echo -e "\n${BOLD}${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}Prochain check dans 15 minutes...${NC}"
    echo -e "${BOLD}${CYAN}═══════════════════════════════════════════════════════════${NC}\n"
    
    # Log to file
    log_monitor "Articles: $current_articles | Speed: $current_speed/sec | Lang: $current_lang | Storage: $(format_size $storage_used)"
}

# Main monitoring loop
main() {
    local start_time=$(date +%s)
    local iteration=0
    
    log_monitor "=== Démarrage du monitoring ingestion Wikipedia ==="
    log_monitor "Intervalle: 15 minutes"
    log_monitor "API: $API_URL"
    log_monitor "Storage: $STORAGE_DIR"
    
    echo -e "${BOLD}${GREEN}${CHECK} Monitoring démarré!${NC}"
    echo -e "${CYAN}Stats toutes les 15 minutes${NC}"
    echo -e "${CYAN}Logs dans: $MONITOR_LOG${NC}\n"
    
    # Display immediately
    iteration=$((iteration + 1))
    display_stats "$iteration" "$start_time"
    
    # Loop every 15 minutes
    while true; do
        sleep "$INTERVAL_SECONDS"
        iteration=$((iteration + 1))
        display_stats "$iteration" "$start_time"
    done
}

# Handle Ctrl+C
cleanup() {
    echo -e "\n${YELLOW}Arrêt du monitoring...${NC}"
    log_monitor "=== Arrêt du monitoring ==="
    exit 0
}

trap cleanup SIGINT SIGTERM

main "$@"
