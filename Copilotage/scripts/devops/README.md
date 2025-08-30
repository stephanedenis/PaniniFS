# DevOps utilitaires (Copilotage)

- fix_remotes.sh: bascule/normalise l'URL du remote (HTTPS <-> SSH)
- git_audit.sh: audit rapide (remotes, status, fetch, submodules, dernier commit)
- bootstrap_submodules.sh: ajoute/initialise les submodules de l'écosystème (modules/*)
- setup_dev_environment.sh: setup rapide de l'environnement local (requirements, audit, remotes)

Racine propre: aucun utilitaire ne doit rester à la racine. Placez tout ici.

## Usage rapide

```
# Normaliser les remotes et auditer
./fix_remotes.sh https
./git_audit.sh

# Initialiser les submodules (si réseau/accès OK)
./bootstrap_submodules.sh

# Setup global (optionnel)
./setup_dev_environment.sh
```