#!/bin/bash
#
# 🚫 CONFIGURATION ANTI-PAGER PERMANENTE
# =====================================
#
# Désactive TOUS les pagers pour l'autonomie maximale des opérations terminal
#

echo "🚫 Configuration anti-pager permanente"
echo "======================================"
echo ""

# 1. Variables d'environnement globales
echo "📝 Configuration des variables d'environnement..."

# Fichier de configuration permanent
BASHRC_FILE="$HOME/.bashrc"
PROFILE_FILE="$HOME/.profile"

# Fonction pour ajouter une ligne si elle n'existe pas
add_env_var() {
    local var="$1"
    local file="$2"
    
    if ! grep -q "$var" "$file" 2>/dev/null; then
        echo "export $var" >> "$file"
        echo "   ✅ Ajouté: $var dans $file"
    else
        echo "   ⚡ Existe: $var dans $file"
    fi
}

# Variables anti-pager essentielles
echo "🔧 Variables git..."
add_env_var "GIT_PAGER=''" "$BASHRC_FILE"
add_env_var "PAGER=''" "$BASHRC_FILE"
add_env_var "LESS=''" "$BASHRC_FILE"
add_env_var "MORE=''" "$BASHRC_FILE"

echo "🔧 Variables GitHub CLI..."
add_env_var "GH_PAGER=''" "$BASHRC_FILE"
add_env_var "GITHUB_PAGER=''" "$BASHRC_FILE"

echo "🔧 Variables système..."
add_env_var "SYSTEMD_PAGER=''" "$BASHRC_FILE"
add_env_var "BAT_PAGER=''" "$BASHRC_FILE"

# 2. Configuration git globale
echo ""
echo "⚙️ Configuration git globale..."
git config --global core.pager ""
git config --global pager.branch false
git config --global pager.status false
git config --global pager.log false
git config --global pager.diff false
git config --global pager.show false
echo "   ✅ Git configuré sans pager"

# 3. Configuration GitHub CLI
echo ""
echo "🐙 Configuration GitHub CLI..."
gh config set pager ""
echo "   ✅ GitHub CLI configuré sans pager"

# 4. Aliases utiles
echo ""
echo "🔗 Création d'aliases anti-pager..."
add_env_var "alias git='git --no-pager'" "$BASHRC_FILE"
add_env_var "alias gh='gh --paginate=false'" "$BASHRC_FILE"
add_env_var "alias less='cat'" "$BASHRC_FILE"
add_env_var "alias more='cat'" "$BASHRC_FILE"

# 5. Application immédiate
echo ""
echo "⚡ Application immédiate des variables..."
export GIT_PAGER=''
export PAGER=''
export LESS=''
export MORE=''
export GH_PAGER=''
export GITHUB_PAGER=''
export SYSTEMD_PAGER=''
export BAT_PAGER=''

echo "   ✅ Variables actives dans la session actuelle"

# 6. Vérification
echo ""
echo "🧪 Test de configuration..."
echo "Git pager: $(git config --get core.pager || echo 'non défini')"
echo "GH pager: $(gh config get pager || echo 'non défini')"
echo "Variable GIT_PAGER: '${GIT_PAGER}'"
echo "Variable PAGER: '${PAGER}'"

echo ""
echo "✅ CONFIGURATION TERMINÉE"
echo "========================"
echo "🎯 Résultat:"
echo "   ✅ Tous les pagers désactivés de façon permanente"
echo "   ✅ Configuration appliquée immédiatement"
echo "   ✅ Persistance assurée dans .bashrc"
echo "   ✅ Autonomie maximale restaurée"

echo ""
echo "🏕️ L'agent peut maintenant opérer sans interruption!"
echo "   Pour recharger: source ~/.bashrc"

exit 0
