#!/bin/bash
# Ingestion massive de TOUTES les Wikipédias disponibles
# Sauvegarde du modèle Panini complet pour étude ultérieure

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PANINI_FS_DIR="${SCRIPT_DIR}/.."
WIKI_DUMPS_DIR="/home/stephane/GitHub/Panini/wikipedia_dumps"
API_URL="http://localhost:3000/api"
STORAGE_DIR="${PANINI_STORAGE:-/mnt/data/panini-wikipedia-full}"
REPORTS_DIR="${PANINI_FS_DIR}/reports/wikipedia_full"
CHECKPOINT_DIR="${STORAGE_DIR}/checkpoints"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() {
    echo -e "${CYAN}ℹ${NC} $(date '+%H:%M:%S') $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $(date '+%H:%M:%S') $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $(date '+%H:%M:%S') $1"
}

log_error() {
    echo -e "${RED}✗${NC} $(date '+%H:%M:%S') $1"
}

log_highlight() {
    echo -e "${MAGENTA}★${NC} $(date '+%H:%M:%S') $1"
}

# Vérifier l'espace disque nécessaire
check_disk_space() {
    log_info "Vérification de l'espace disque..."
    
    local available=$(df -BG "$STORAGE_DIR" 2>/dev/null | tail -1 | awk '{print $4}' | sed 's/G//')
    local needed=300  # Au moins 300GB pour tout Wikipedia
    
    if [ -z "$available" ]; then
        mkdir -p "$STORAGE_DIR"
        available=$(df -BG "$(dirname "$STORAGE_DIR")" | tail -1 | awk '{print $4}' | sed 's/G//')
    fi
    
    log_info "Espace disponible: ${available}G"
    log_info "Espace recommandé: ${needed}G"
    
    if [ "$available" -lt "$needed" ]; then
        log_warning "Espace insuffisant! Continuer quand même? (y/N)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            log_error "Arrêt. Libérez de l'espace ou changez PANINI_STORAGE"
            exit 1
        fi
    fi
    
    log_success "Espace disque vérifié"
}

# Créer la structure de répertoires
setup_directories() {
    log_info "Création de la structure de répertoires..."
    
    mkdir -p "$STORAGE_DIR"
    mkdir -p "$REPORTS_DIR"
    mkdir -p "$CHECKPOINT_DIR"
    
    log_success "Répertoires créés"
}

# Détecter tous les dumps disponibles
detect_dumps() {
    log_info "Détection des dumps Wikipedia..."
    
    local dumps=()
    
    for dump in "$WIKI_DUMPS_DIR"/*wiki-latest-pages-articles.xml.bz2; do
        if [ -f "$dump" ]; then
            local basename=$(basename "$dump")
            local lang=$(echo "$basename" | sed 's/wiki-latest-pages-articles.xml.bz2//')
            local size=$(du -h "$dump" | cut -f1)
            
            dumps+=("$lang:$dump:$size")
            log_info "  → ${lang}: ${size}"
        fi
    done
    
    echo "${dumps[@]}"
}

# Estimer le nombre total d'articles
estimate_articles() {
    local dump="$1"
    local lang="$2"
    
    log_info "Estimation du nombre d'articles pour ${lang}..."
    
    # Compter rapidement les balises <page> dans les 100 premiers MB
    local sample_count=$(bzcat "$dump" | head -c 100000000 | grep -c '<page>' || echo 0)
    local dump_size=$(stat -c%s "$dump")
    local sample_size=100000000
    
    if [ "$sample_count" -gt 0 ] && [ "$dump_size" -gt "$sample_size" ]; then
        local estimated=$((sample_count * dump_size / sample_size))
        echo "$estimated"
    else
        echo "unknown"
    fi
}

# Ingérer une langue complète
ingest_language() {
    local lang="$1"
    local dump="$2"
    local size="$3"
    
    log_highlight "========================================="
    log_highlight "INGESTION: ${lang} (${size})"
    log_highlight "========================================="
    
    local checkpoint_file="${CHECKPOINT_DIR}/${lang}_checkpoint.json"
    local report_file="${REPORTS_DIR}/${lang}_report.json"
    local start_time=$(date +%s)
    
    # Vérifier si déjà fait
    if [ -f "$report_file" ]; then
        log_warning "${lang} déjà ingéré. Passer? (Y/n)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]] || [ -z "$response" ]; then
            log_info "Saut de ${lang}"
            return 0
        fi
    fi
    
    # Estimer le nombre d'articles
    local estimated=$(estimate_articles "$dump" "$lang")
    if [ "$estimated" != "unknown" ]; then
        log_info "Estimation: ~${estimated} articles"
    fi
    
    # Ingérer avec classification Dhātu
    log_info "Démarrage de l'ingestion..."
    
    python3 "${SCRIPT_DIR}/wikipedia_ingestion.py" \
        --dump "$dump" \
        --lang "$lang" \
        --all \
        --api "$API_URL" \
        --classify \
        --output "$report_file" 2>&1 | tee "${REPORTS_DIR}/${lang}_ingestion.log"
    
    local exit_code=${PIPESTATUS[0]}
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    if [ $exit_code -eq 0 ]; then
        log_success "${lang} ingéré en ${duration}s"
        
        # Sauvegarder checkpoint
        echo "{\"lang\": \"${lang}\", \"completed\": true, \"timestamp\": $(date +%s), \"duration\": ${duration}}" > "$checkpoint_file"
    else
        log_error "Erreur lors de l'ingestion de ${lang} (code: ${exit_code})"
        echo "{\"lang\": \"${lang}\", \"completed\": false, \"error\": ${exit_code}, \"timestamp\": $(date +%s)}" > "$checkpoint_file"
        
        # Continuer avec la langue suivante?
        log_warning "Continuer avec les autres langues? (Y/n)"
        read -r response
        if [[ "$response" =~ ^[Nn]$ ]]; then
            log_error "Arrêt demandé par l'utilisateur"
            exit 1
        fi
    fi
}

# Générer un rapport global
generate_global_report() {
    log_info "Génération du rapport global..."
    
    local total_articles=0
    local total_size=0
    local total_deduplicated=0
    local total_profiles=0
    local langs_processed=0
    
    local report_file="${REPORTS_DIR}/GLOBAL_REPORT.md"
    
    cat > "$report_file" << 'HEADER'
# 🌍 Rapport Global: Toutes les Wikipédias dans Panini-FS

**Date de génération**: $(date '+%Y-%m-%d %H:%M:%S')
**Système**: Panini-FS v1.0.0 avec CAS + Dhātu

---

## 📊 Statistiques Globales

HEADER
    
    # Agréger les stats de tous les rapports JSON
    for report in "${REPORTS_DIR}"/*_report.json; do
        if [ -f "$report" ]; then
            local lang=$(basename "$report" | sed 's/_report.json//')
            
            # Parser JSON (nécessite jq ou python)
            if command -v jq &> /dev/null; then
                local articles=$(jq -r '.total_articles // 0' "$report")
                local size=$(jq -r '.total_bytes // 0' "$report")
                local dedup=$(jq -r '.deduplicated_bytes // 0' "$report")
                
                total_articles=$((total_articles + articles))
                total_size=$((total_size + size))
                total_deduplicated=$((total_deduplicated + dedup))
                langs_processed=$((langs_processed + 1))
            fi
        fi
    done
    
    # Statistiques API actuelles
    local api_stats=$(curl -s "$API_URL/dedup/stats" 2>/dev/null || echo '{}')
    local dhatu_stats=$(curl -s "$API_URL/dhatu/stats" 2>/dev/null || echo '{}')
    
    # Compléter le rapport
    cat >> "$report_file" << STATS

### Articles Ingérés
- **Total articles**: $(printf "%'d" $total_articles)
- **Langues traitées**: ${langs_processed}
- **Taille brute**: $(numfmt --to=iec-i --suffix=B $total_size 2>/dev/null || echo "${total_size} bytes")
- **Taille dédupliquée**: $(numfmt --to=iec-i --suffix=B $total_deduplicated 2>/dev/null || echo "${total_deduplicated} bytes")

### Déduplication CAS
\`\`\`json
${api_stats}
\`\`\`

### Classification Dhātu
\`\`\`json
${dhatu_stats}
\`\`\`

---

## 📈 Par Langue

| Langue | Articles | Taille | Dédup | Émotion Dominante |
|--------|----------|--------|-------|-------------------|
STATS
    
    # Tableau par langue
    for report in "${REPORTS_DIR}"/*_report.json; do
        if [ -f "$report" ] && command -v jq &> /dev/null; then
            local lang=$(basename "$report" | sed 's/_report.json//')
            local articles=$(jq -r '.total_articles // 0' "$report")
            local size=$(jq -r '.total_bytes // 0' "$report")
            local dedup_ratio=$(jq -r '.deduplication_ratio * 100 // 0' "$report")
            
            echo "| ${lang} | ${articles} | $(numfmt --to=iec-i --suffix=B $size 2>/dev/null || echo $size) | ${dedup_ratio}% | - |" >> "$report_file"
        fi
    done
    
    cat >> "$report_file" << 'FOOTER'

---

## 🗂️ Structure du Modèle Panini Sauvegardé

Le corpus complet est disponible dans:
```
STORAGE_DIR/
├── atoms/           # Atoms CAS dédupliqués
├── index/           # Index RocksDB + Tantivy
├── dhatu/           # Profils émotionnels persistés
└── checkpoints/     # Points de reprise par langue
```

### Utilisation du Modèle

**Montage FUSE:**
```bash
PANINI_STORAGE=STORAGE_DIR cargo run --bin panini-mount /mnt/wikipedia
ls /mnt/wikipedia/concepts/
```

**Requêtes API:**
```bash
# Statistiques
curl http://localhost:3000/api/dedup/stats
curl http://localhost:3000/api/dhatu/stats

# Recherche d'atoms
curl http://localhost:3000/api/atoms/search?query=Pāṇini

# Analyse émotionnelle
curl -X POST http://localhost:3000/api/dhatu/classify \
  -H "Content-Type: application/json" \
  -d '{"path": "/wikipedia/sa/0/पाणिनि", "content": "..."}'
```

---

## 🔬 Analyses Possibles

1. **Déduplication Inter-Langues**: Identifier les atoms partagés entre langues
2. **Profils Émotionnels Culturels**: Comparer les distributions Dhātu par langue
3. **Concepts Universels**: Trouver les articles présents dans toutes les langues
4. **Évolution Temporelle**: Analyser les changements via timestamps
5. **Graphe de Connaissances**: Construire un graphe multilingue unifié

---

**Généré par**: Panini-FS v1.0.0
**Corpus**: Wikipedia multilingue complet
**Total**: LANG_COUNT langues, ARTICLE_COUNT articles

FOOTER
    
    # Remplacer les placeholders
    sed -i "s/STORAGE_DIR/${STORAGE_DIR//\//\\/}/g" "$report_file"
    sed -i "s/LANG_COUNT/${langs_processed}/g" "$report_file"
    sed -i "s/ARTICLE_COUNT/$(printf "%'d" $total_articles)/g" "$report_file"
    
    log_success "Rapport global généré: ${report_file}"
}

# Sauvegarder le modèle complet
backup_model() {
    log_info "Sauvegarde du modèle Panini complet..."
    
    local backup_dir="/mnt/backup/panini-wikipedia-$(date +%Y%m%d)"
    local backup_file="${backup_dir}.tar.gz"
    
    log_info "Création d'une archive: ${backup_file}"
    
    tar -czf "$backup_file" \
        -C "$(dirname "$STORAGE_DIR")" \
        "$(basename "$STORAGE_DIR")" \
        2>&1 | while read line; do
            if [[ "$line" =~ ^tar: ]]; then
                log_info "$line"
            fi
        done
    
    local size=$(du -h "$backup_file" | cut -f1)
    log_success "Modèle sauvegardé: ${backup_file} (${size})"
    
    # Checksum
    log_info "Calcul du checksum SHA-256..."
    sha256sum "$backup_file" > "${backup_file}.sha256"
    log_success "Checksum: $(cat "${backup_file}.sha256" | cut -d' ' -f1)"
}

# Menu principal
main() {
    clear
    echo -e "${MAGENTA}"
    cat << 'BANNER'
╔═══════════════════════════════════════════════════════════╗
║   🕉️  INGESTION MASSIVE WIKIPEDIA DANS PANINI-FS  🕉️    ║
║                                                           ║
║   Corpus Complet Multilingue avec Dhātu                  ║
╚═══════════════════════════════════════════════════════════╝
BANNER
    echo -e "${NC}"
    
    log_info "Storage: ${STORAGE_DIR}"
    log_info "Rapports: ${REPORTS_DIR}"
    
    # Vérifications préliminaires
    check_disk_space
    setup_directories
    
    # Vérifier que l'API est lancée
    log_info "Vérification de l'API Panini-FS..."
    if ! curl -s "${API_URL}/health" > /dev/null 2>&1; then
        log_error "API non accessible à ${API_URL}"
        log_info "Lancer d'abord: ${SCRIPT_DIR}/start_api_wikipedia.sh"
        exit 1
    fi
    log_success "API accessible"
    
    # Détecter les dumps
    log_info "Détection des dumps Wikipedia..."
    mapfile -t dumps_info < <(detect_dumps)
    
    if [ ${#dumps_info[@]} -eq 0 ]; then
        log_error "Aucun dump Wikipedia trouvé dans ${WIKI_DUMPS_DIR}"
        exit 1
    fi
    
    log_success "${#dumps_info[@]} dumps détectés"
    
    # Confirmation
    log_warning "Prêt à ingérer ${#dumps_info[@]} Wikipédias complètes"
    log_warning "Cela peut prendre plusieurs heures/jours selon la taille"
    log_warning "Continuer? (y/N)"
    read -r response
    
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        log_info "Annulé par l'utilisateur"
        exit 0
    fi
    
    # Ingestion de chaque langue
    local start_global=$(date +%s)
    
    for dump_info in "${dumps_info[@]}"; do
        IFS=':' read -r lang dump size <<< "$dump_info"
        ingest_language "$lang" "$dump" "$size"
    done
    
    local end_global=$(date +%s)
    local duration_global=$((end_global - start_global))
    
    log_highlight "========================================="
    log_highlight "INGESTION GLOBALE TERMINÉE"
    log_highlight "Durée totale: ${duration_global}s ($(date -u -d @${duration_global} +%H:%M:%S))"
    log_highlight "========================================="
    
    # Génération du rapport global
    generate_global_report
    
    # Sauvegarde du modèle
    log_warning "Sauvegarder le modèle complet? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        backup_model
    fi
    
    # Statistiques finales
    log_info "Statistiques finales:"
    curl -s "$API_URL/dedup/stats" | python3 -m json.tool | head -20
    echo
    curl -s "$API_URL/dhatu/stats" | python3 -m json.tool | head -20
    
    log_success "🎉 TERMINÉ! Modèle Panini Wikipedia complet disponible dans ${STORAGE_DIR}"
}

# Gestion des interruptions
trap 'log_warning "Interruption détectée. État sauvegardé dans ${CHECKPOINT_DIR}"; exit 130' INT TERM

# Exécution
main "$@"
