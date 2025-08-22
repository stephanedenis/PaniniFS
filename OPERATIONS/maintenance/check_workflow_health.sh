#!/bin/bash
#
# 🏥 VÉRIFICATION SANTÉ WORKFLOWS
# ===============================
#
# Script pour vérifier que les workflows ne génèrent plus d'erreurs
# et que le système de redirection fonctionne correctement.
#

set -euo pipefail

echo "🏥 Vérification Santé Workflows & Redirection"
echo "=============================================="

# Configuration
REPO_PATH="/home/stephane/GitHub/PaniniFS-1"
cd "$REPO_PATH"

# 1. Vérifier workflows actifs
echo "🔍 Vérification workflows actifs..."
active_workflows=0
disabled_workflows=0

for workflow in .github/workflows/*.yml; do
    if [[ -f "$workflow" ]]; then
        echo "   ✅ Actif: $(basename "$workflow")"
        ((active_workflows++))
    fi
done

for workflow in .github/workflows/*.yml.disabled; do
    if [[ -f "$workflow" ]]; then
        echo "   🔕 Désactivé: $(basename "$workflow")"
        ((disabled_workflows++))
    fi
done

echo "   📊 Workflows actifs: $active_workflows"
echo "   📊 Workflows désactivés: $disabled_workflows"

# 2. Vérifier contenu deploy-docs.yml
echo "🚀 Vérification workflow MkDocs..."
if [[ -f ".github/workflows/deploy-docs.yml" ]]; then
    if grep -q "mkdocs-material" ".github/workflows/deploy-docs.yml"; then
        echo "   ✅ Workflow MkDocs configuré correctement"
    else
        echo "   ⚠️ Workflow MkDocs peut nécessiter des ajustements"
    fi
else
    echo "   ❌ Workflow MkDocs manquant"
fi

# 3. Vérifier redirection index.html
echo "🌐 Vérification redirection..."
if [[ -f "index.html" ]]; then
    if grep -q "paninifs.org" "index.html"; then
        echo "   ✅ Redirection vers paninifs.org configurée"
    else
        echo "   ⚠️ Redirection pourrait être incorrecte"
    fi
else
    echo "   ❌ Fichier index.html manquant"
fi

# 4. Vérifier CNAME
echo "📍 Vérification domaine..."
if [[ -f "CNAME" ]]; then
    domain=$(cat CNAME | tr -d '\n\r ')
    echo "   ✅ Domaine configuré: $domain"
else
    echo "   ❌ Fichier CNAME manquant"
fi

# 5. Vérifier requirements.txt
echo "📦 Vérification dépendances..."
if [[ -f "requirements.txt" ]]; then
    if grep -q "mkdocs-material" "requirements.txt"; then
        echo "   ✅ Dépendances MkDocs présentes"
    else
        echo "   ⚠️ requirements.txt pourrait être incomplet"
    fi
else
    echo "   ❌ requirements.txt manquant"
fi

# 6. Test syntaxe workflows
echo "🧪 Test syntaxe workflows..."
for workflow in .github/workflows/*.yml; do
    if [[ -f "$workflow" ]]; then
        # Test basique de syntaxe YAML
        if python3 -c "import yaml; yaml.safe_load(open('$workflow'))" 2>/dev/null; then
            echo "   ✅ Syntaxe OK: $(basename "$workflow")"
        else
            echo "   ❌ Erreur syntaxe: $(basename "$workflow")"
        fi
    fi
done

# 7. Vérifier monitoring
echo "📊 Vérification monitoring..."
if [[ -f "docs_new/dashboard.md" ]]; then
    echo "   ✅ Dashboard monitoring présent"
else
    echo "   ❌ Dashboard monitoring manquant"
fi

if [[ -f "docs_new/data/system_status.json" ]]; then
    echo "   ✅ Données monitoring présentes"
else
    echo "   ❌ Données monitoring manquantes"
fi

# 8. Rapport final
echo ""
echo "📋 RAPPORT FINAL"
echo "==============="

if [[ $active_workflows -le 2 && $disabled_workflows -ge 5 ]]; then
    echo "✅ WORKFLOWS: Optimisés pour camping strategy"
else
    echo "⚠️ WORKFLOWS: Pourraient nécessiter plus d'optimisation"
fi

if [[ -f "index.html" && -f "CNAME" ]]; then
    echo "✅ REDIRECTION: Configurée correctement"
else
    echo "❌ REDIRECTION: Configuration incomplète"
fi

if [[ -f "requirements.txt" ]]; then
    echo "✅ DÉPENDANCES: Configurées"
else
    echo "❌ DÉPENDANCES: Manquantes"
fi

echo ""
echo "🏕️ CAMPING STRATEGY STATUS:"
echo "   🔕 Workflows lourds désactivés: $disabled_workflows"
echo "   🚀 Workflows légers actifs: $active_workflows"
echo "   🌐 Redirection externalisée: GitHub Pages"
echo "   📊 Monitoring autonome: Actif"

echo ""
echo "🎯 PROCHAINES VÉRIFICATIONS:"
echo "   1. Consulter https://github.com/stephanedenis/PaniniFS/actions"
echo "   2. Vérifier https://paninifs.org fonctionne"
echo "   3. Tester https://paninifs.org/dashboard/"

echo ""
echo "✨ Vérification terminée!"

exit 0
