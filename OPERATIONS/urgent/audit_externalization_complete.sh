#!/bin/bash
#
# 🔍 AUDIT EXTERNALISATION COMPLÈTE
# ================================
#
# Vérification si l'externalisation est réellement 100% fonctionnelle
#

set -euo pipefail

echo "🔍 AUDIT EXTERNALISATION COMPLÈTE"
echo "================================="
echo ""

cd /home/stephane/GitHub/PaniniFS-1

# 1. État GitHub Actions - workflows externalisés
echo "🌐 1. GITHUB ACTIONS (Infrastructure externalisée)"
echo "=================================================="
gh run list --limit 10 --json displayTitle,conclusion,status,createdAt --template '{{range .}}{{.displayTitle}} | {{.status}} | {{.conclusion}} | {{timeago .createdAt}}{{"\n"}}{{end}}'

echo ""
echo "📊 Analyse des workflows:"
SUCCESS_COUNT=$(gh run list --limit 20 --json conclusion --template '{{range .}}{{.conclusion}}{{"\n"}}{{end}}' | grep -c "success" || echo "0")
FAILURE_COUNT=$(gh run list --limit 20 --json conclusion --template '{{range .}}{{.conclusion}}{{"\n"}}{{end}}' | grep -c "failure" || echo "0")
echo "   ✅ Succès: $SUCCESS_COUNT"
echo "   ❌ Échecs: $FAILURE_COUNT"

if [ "$FAILURE_COUNT" -gt 0 ]; then
    echo "   🚨 PROBLÈME: Des workflows échouent encore"
    EXTERNALIZATION_OK=false
else
    echo "   ✅ Workflows stables"
    EXTERNALIZATION_OK=true
fi

# 2. Sites déployés - paninifs.org
echo ""
echo "🌐 2. SITES DÉPLOYÉS (paninifs.org)"
echo "==================================="
if command -v curl >/dev/null 2>&1; then
    SITE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://paninifs.org/ || echo "000")
    if [ "$SITE_STATUS" = "200" ]; then
        echo "   ✅ paninifs.org: Accessible ($SITE_STATUS)"
    else
        echo "   ❌ paninifs.org: Problème ($SITE_STATUS)"
        EXTERNALIZATION_OK=false
    fi
else
    echo "   ⚠️ curl non disponible - vérification manuelle requise"
fi

# Vérification GitHub Pages
PAGES_STATUS=$(gh run list --workflow="pages-build-deployment" --limit 1 --json conclusion --template '{{range .}}{{.conclusion}}{{end}}')
if [ "$PAGES_STATUS" = "success" ]; then
    echo "   ✅ GitHub Pages: Opérationnel"
else
    echo "   ❌ GitHub Pages: Problème ($PAGES_STATUS)"
    EXTERNALIZATION_OK=false
fi

# 3. Monitoring automatique
echo ""
echo "📊 3. MONITORING AUTOMATIQUE"
echo "============================"
if [ -f "OPERATIONS/monitoring/scripts/update_system_status.py" ]; then
    echo "   ✅ Scripts monitoring: Présents"
    # Test rapide du monitoring
    if python3 OPERATIONS/monitoring/scripts/update_system_status.py --check 2>/dev/null; then
        echo "   ✅ Monitoring: Fonctionnel"
    else
        echo "   ⚠️ Monitoring: À tester"
    fi
else
    echo "   ❌ Scripts monitoring: Manquants"
    EXTERNALIZATION_OK=false
fi

# 4. Configuration cloud
echo ""
echo "☁️ 4. CONFIGURATION CLOUD"
echo "========================="
if [ -d ".github/workflows" ]; then
    WORKFLOW_COUNT=$(ls .github/workflows/*.yml 2>/dev/null | wc -l)
    echo "   ✅ GitHub Actions workflows: $WORKFLOW_COUNT fichiers"
else
    echo "   ❌ Workflows GitHub Actions: Manquants"
    EXTERNALIZATION_OK=false
fi

# Vérification des secrets/tokens
if gh auth status >/dev/null 2>&1; then
    echo "   ✅ GitHub CLI: Authentifié"
else
    echo "   ❌ GitHub CLI: Non authentifié"
    EXTERNALIZATION_OK=false
fi

# 5. Documentation externalisée
echo ""
echo "📚 5. DOCUMENTATION EXTERNALISÉE"
echo "================================"
if [ -d "docs_new" ] && [ -f "mkdocs.yml" ]; then
    echo "   ✅ MkDocs: Configuré"
    if [ -f "docs_new/index.md" ]; then
        echo "   ✅ Documentation: Structure présente"
    else
        echo "   ⚠️ Documentation: Structure à vérifier"
    fi
else
    echo "   ❌ MkDocs: Configuration manquante"
    EXTERNALIZATION_OK=false
fi

# 6. Autonomie complète
echo ""
echo "🤖 6. AUTONOMIE COMPLÈTE"
echo "======================="

# Vérification missions autonomes
if [ -d "ECOSYSTEM/autonomous-missions" ]; then
    AUTONOMOUS_SCRIPTS=$(find ECOSYSTEM/autonomous-missions -name "*.py" | wc -l)
    echo "   📝 Scripts autonomes: $AUTONOMOUS_SCRIPTS"
    
    # Si l'externalisation est complète, ces scripts sont redondants
    if [ "$EXTERNALIZATION_OK" = true ]; then
        echo "   🎯 VERDICT: Scripts autonomes locaux REDONDANTS"
        echo "      → Externalisation complète = Plus besoin de missions locales"
    else
        echo "   🎯 VERDICT: Scripts autonomes locaux NÉCESSAIRES"
        echo "      → Externalisation incomplète = Missions locales requises"
    fi
else
    echo "   ⚠️ Scripts autonomes: Dossier manquant"
fi

# VERDICT FINAL
echo ""
echo "🎯 VERDICT FINAL EXTERNALISATION"
echo "==============================="

if [ "$EXTERNALIZATION_OK" = true ]; then
    echo "✅ EXTERNALISATION COMPLÈTE ET FONCTIONNELLE"
    echo ""
    echo "📋 ACTIONS RECOMMANDÉES:"
    echo "   1. 🗑️ SUPPRIMER missions nocturnes locales (redondantes)"
    echo "   2. 🏕️ ACTIVER mode camping complet"
    echo "   3. 📊 GARDER uniquement monitoring minimal"
    echo "   4. 🚀 FAIRE confiance à l'infrastructure cloud"
    echo ""
    echo "🏕️ Camping Strategy: PRÊTE - Totoro peut être éteint !"
else
    echo "❌ EXTERNALISATION INCOMPLÈTE"
    echo ""
    echo "🚨 PRIORITÉ ABSOLUE - PROBLÈMES À RÉSOUDRE:"
    echo "   1. 🔧 Réparer workflows GitHub qui échouent"
    echo "   2. 🌐 Valider déploiement sites"
    echo "   3. 📊 Tester monitoring automatique"
    echo "   4. ☁️ Finaliser configuration cloud"
    echo ""
    echo "⚠️ GARDER missions nocturnes jusqu'à résolution complète"
fi

echo ""
echo "🔍 Audit terminé - Actions claires identifiées"

exit 0
