#!/usr/bin/env bash
set -euo pipefail

# fix_remotes.sh — Bascule l'URL du remote entre HTTPS et SSH (par défaut: origin)
# Usage:
#   ./fix_remotes.sh ssh   [remote]
#   ./fix_remotes.sh https [remote]
# Sans argument, affiche l'état actuel et une suggestion.

mode="${1:-}"
remote="${2:-origin}"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
	echo "Erreur: ce dossier n'est pas un dépôt git" >&2
	exit 1
fi

current_url=$(git remote get-url "$remote" 2>/dev/null || true)
if [[ -z "${current_url:-}" ]]; then
	echo "Remote '$remote' introuvable. Remotes disponibles :" >&2
	git remote -v
	exit 2
fi

to_ssh() {
	# https://github.com/owner/repo(.git) -> git@github.com:owner/repo.git
	local url="$1"
	if [[ "$url" =~ ^https://github.com/([^/]+)/([^/]+)(\.git)?$ ]]; then
		local owner="${BASH_REMATCH[1]}"
		local name="${BASH_REMATCH[2]}"
		echo "git@github.com:${owner}/${name}.git"
	else
		echo "$url"
	fi
}

to_https() {
	# git@github.com:owner/repo(.git) -> https://github.com/owner/repo.git
	local url="$1"
	if [[ "$url" =~ ^git@github.com:([^/]+)/([^/]+)(\.git)?$ ]]; then
		local owner="${BASH_REMATCH[1]}"
		local name="${BASH_REMATCH[2]}"
		echo "https://github.com/${owner}/${name}.git"
	else
		echo "$url"
	fi
}

case "${mode}" in
	ssh)
		new_url=$(to_ssh "$current_url")
		if [[ "$new_url" == "$current_url" ]]; then
			echo "Remote déjà en SSH ou format non reconnu: $current_url"
		else
			echo "Mise à jour du remote '$remote' -> $new_url"
			git remote set-url "$remote" "$new_url"
			# Réécriture locale optionnelle: préférer SSH pour github.com
			git config url."ssh://git@github.com/".insteadOf https://github.com/ || true
		fi
		;;
	https)
		new_url=$(to_https "$current_url")
		if [[ "$new_url" == "$current_url" ]]; then
			echo "Remote déjà en HTTPS ou format non reconnu: $current_url"
		else
			echo "Mise à jour du remote '$remote' -> $new_url"
			git remote set-url "$remote" "$new_url"
			# Nettoyage optionnel de la règle insteadOf
			git config --unset url.ssh://git@github.com/.insteadof || true
		fi
		;;
	"")
		echo "Remote actuel ($remote): $current_url"
		echo "Astuce: ./fix_remotes.sh ssh | ./fix_remotes.sh https"
		;;
	*)
		echo "Usage: $0 [ssh|https] [remote]" >&2
		exit 3
		;;
esac

echo
echo "Remotes:"
git remote -v

