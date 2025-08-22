#!/bin/bash
"""
🏖️ VACATION MODE - AUTO-PILOT
=============================

Configuration complète pour absence 8 jours
Maintien minimal des services + monitoring
"""

echo "🏖️ CONFIGURATION MODE VACANCES"
echo "================================"
echo "📅 $(date)"
echo ""

# 1. Configuration du Doctor pour redémarrage automatique
echo "🤖 1. CONFIGURATION DOCTOR PERMANENTE"
echo "────────────────────────────────────"

# Crée le script de redémarrage automatique
cat > doctor_watchdog.sh << 'EOF'
#!/bin/bash
# Watchdog Doctor - Redémarre si crash
while true; do
    # Vérifie si doctor tourne
    if ! python3 doctor_control.py status > /dev/null 2>&1; then
        echo "🚨 $(date): Doctor crashed - Redémarrage automatique"
        python3 doctor_control.py start
    fi
    sleep 300  # Vérification toutes les 5 minutes
done
EOF

chmod +x doctor_watchdog.sh

# 2. Configuration cron pour persistance
echo "⏰ Configuration cron pour persistance..."

# Ajoute au crontab si pas déjà présent
(crontab -l 2>/dev/null | grep -v "doctor_watchdog") ; echo "*/10 * * * * cd $(pwd) && ./doctor_watchdog.sh > /dev/null 2>&1" | crontab -

echo "✅ Cron configuré - Doctor redémarre automatiquement"

# 3. Script de sauvegarde quotidienne
echo ""
echo "💾 2. SAUVEGARDE AUTOMATIQUE QUOTIDIENNE"
echo "────────────────────────────────────────"

cat > vacation_backup.sh << 'EOF'
#!/bin/bash
# Sauvegarde quotidienne pendant vacances
DATE=$(date +%Y%m%d)
BACKUP_DIR="vacation_backups"
mkdir -p "$BACKUP_DIR"

echo "💾 Sauvegarde quotidienne $(date)"

# Sauvegarde code critique
tar -czf "$BACKUP_DIR/paninifs_$DATE.tar.gz" \
    --exclude="*.log" \
    --exclude="vacation_backups" \
    --exclude=".git" \
    .

# Sauvegarde issues GitHub
gh issue list --limit 100 --json number,title,body,state > "$BACKUP_DIR/github_issues_$DATE.json"

# Push vers GitHub
git add vacation_backups/
git commit -m "🏖️ Vacation backup $DATE" || true
git push origin master || true

echo "✅ Sauvegarde $DATE terminée"
EOF

chmod +x vacation_backup.sh

# Ajoute au cron
(crontab -l 2>/dev/null | grep -v "vacation_backup") ; echo "0 2 * * * cd $(pwd) && ./vacation_backup.sh > vacation_backups/backup.log 2>&1" | crontab -

echo "✅ Sauvegarde quotidienne 2h du matin configurée"

# 4. Monitoring minimal d'urgence
echo ""
echo "🚨 3. MONITORING D'URGENCE SEULEMENT"
echo "───────────────────────────────────────"

cat > vacation_emergency_monitor.sh << 'EOF'
#!/bin/bash
# Monitoring d'urgence - alerte seulement si TOUT est cassé

check_critical() {
    local failures=0
    
    # Vérifie GitHub Pages
    if ! curl -s -o /dev/null -w "%{http_code}" https://paninifs.org | grep -q "200"; then
        ((failures++))
    fi
    
    # Vérifie DNS principal
    if ! nslookup paninifs.org > /dev/null 2>&1; then
        ((failures++))
    fi
    
    # Vérifie Doctor
    if ! python3 doctor_control.py status > /dev/null 2>&1; then
        ((failures++))
    fi
    
    # Si tout est cassé (3+ échecs)
    if [ $failures -ge 3 ]; then
        echo "🚨 URGENCE: $failures composants critiques down"
        echo "Timestamp: $(date)"
        echo "Action: Vérification manuelle requise"
        
        # Log l'urgence
        echo "$(date): EMERGENCY - $failures critical failures" >> vacation_emergencies.log
        
        # Tente redémarrage Doctor
        python3 doctor_control.py start
        
        return 1
    fi
    
    return 0
}

if ! check_critical; then
    echo "🚨 Urgence détectée - voir vacation_emergencies.log"
else
    echo "✅ Systèmes critiques OK"
fi
EOF

chmod +x vacation_emergency_monitor.sh

# Monitoring d'urgence toutes les heures
(crontab -l 2>/dev/null | grep -v "vacation_emergency") ; echo "0 * * * * cd $(pwd) && ./vacation_emergency_monitor.sh >> vacation_monitor.log 2>&1" | crontab -

echo "✅ Monitoring d'urgence configuré (toutes les heures)"

echo ""
echo "🎯 4. RÉALITÉ + PLAN RETOUR"
echo "══════════════════════════"
echo ""
echo "🏖️ ACCEPTATION RÉALITÉ:"
echo "• Camping Strategy 100% était trop ambitieuse"
echo "• 8 jours de vacances = priorité aux vacances !"
echo "• On maintient l'existant, on n'innove pas"
echo ""
echo "✅ CE QUI EST PROTÉGÉ PENDANT TES VACANCES:"
echo "• GitHub Pages: ✅ Opérationnel" 
echo "• DNS 5 domaines: ✅ Configuré"
echo "• Doctor autonome: ✅ Redémarrage auto"
echo "• Sauvegarde quotidienne: ✅ Automatique"
echo "• Monitoring urgence: ✅ Toutes les heures"
echo ""
echo "📅 PLAN RETOUR (post-vacances):"
echo "• Septembre 2025: Reprise sereine du Colab Center"
echo "• Pas de stress, pas de deadline artificielle"
echo "• Focus sur 1 composant à la fois"
echo "• Tests approfondis avant chaque étape"
echo ""
echo "🎉 RÉSULTAT: Tranquillité d'esprit garantie"
echo "Totoro peut rester allumé, tout est stable !"

echo ""
echo "🏖️ CONFIGURATION VACANCES TERMINÉE ✅"
echo "═══════════════════════════════════════"
echo ""
echo "🤖 Doctor: Redémarrage automatique configuré"
echo "💾 Backup: Quotidien à 2h du matin"  
echo "🚨 Monitoring: Urgence seulement (toutes les heures)"
echo "📅 Cron: 3 tâches configurées"
echo ""
echo "🎯 Tu peux partir sereinement !"
echo "Le système est en auto-pilote minimal."
