#!/usr/bin/env bash
set -euo pipefail

# bootstrap_submodules.sh — Ajoute/initialise les submodules cibles s'ils n'existent pas.
declare -A MODULES=(
  [modules/ultra-reactive]="https://github.com/stephanedenis/PaniniFS-UltraReactive"
  [modules/colab-controller]="https://github.com/stephanedenis/PaniniFS-CoLabController"
  [modules/autonomous-missions]="https://github.com/stephanedenis/PaniniFS-AutonomousMissions"
  [modules/semantic-core]="https://github.com/stephanedenis/PaniniFS-SemanticCore"
  [modules/publication-engine]="https://github.com/stephanedenis/PaniniFS-PublicationEngine"
  [modules/cloud-orchestrator]="https://github.com/stephanedenis/PaniniFS-CloudOrchestrator"
)

mkdir -p modules

for path in "${!MODULES[@]}"; do
  url="${MODULES[$path]}"
  if [ ! -d "$path" ]; then
    echo "Ajout submodule: $path -> $url"
    git submodule add "$url" "$path" || true
  else
    echo "Dossier déjà présent: $path"
  fi
done

echo "Sync et init submodules (best-effort)"
git submodule sync --recursive || true
git submodule update --init --recursive || true
git submodule status --recursive || true
