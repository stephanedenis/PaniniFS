# 📓 Journal reconstitué — 2025-09-03

**Host**: totoro
**Source**: Reconstitué depuis `git log` le 2026-02-18
**Auteur commits**: Stéphane Denis + github-actions

> ⚠️ Ce journal a été reconstitué rétrospectivement depuis l'historique Git.

---

## Contexte

Journée marathon (24 commits) : migration complète vers GitHub Pages via MkDocs,
nettoyage massif des workflows CI legacy, enrichissement du site (livre, recherche,
RSS, i18n).

## Décisions clés

### 1. Déploiement MkDocs via actions/deploy-pages

Remplacement de tous les workflows Peaceiris legacy par le déploiement officiel
`actions/deploy-pages` avec `build_type=workflow`. Suppression des workflows
archivés (`*.disabled`).

### 2. Intégration du livre Leanpub au site

Les contenus du livre (préface, lecture intégrale) sont intégrés au site MkDocs
via des wrappers FR/EN avec includes relatifs. Slug unifié : `lecture-integrale`.

### 3. Section Recherche enrichie

Ajout de la vue d'ensemble recherche (FR/EN), flux RSS RESEARCH avec page HTML
dynamique, et correction de la navigation (indentation Recherche & Livre).

### 4. Nettoyage CI radical

Suppression de : `deploy-docs-auto.yml`, `auto-pr-merge`, tous les `*.disabled`,
les workflows Peaceiris legacy. Ne reste que le Pages officiel.

### 5. Sous-modules et templates

Script `split_to_submodule` + template workspace VS Code, docs, Peacock.
Sous-module RESEARCH tracké sur `main`.

### 6. Stabilité terminale (#72)

Diagnostics et snapshot pour la stabilité des terminaux VS Code.

## Fichiers modifiés

- `.github/workflows/deploy-pages-mkdocs.yml` — Nouveau workflow Pages
- `mkdocs.yml` — Navigation enrichie (Livre, Recherche, Publications)
- `docs_new/` — Pages FR/EN : vision-sociale, avancement, licences
- `docs_new/research/` — Vue d'ensemble, what's-new, feed RSS
- `docs_new/en/` — Miroirs i18n anglais
- `index.html` — Redirection minimale + `.nojekyll`
- `scripts/` — `split_to_submodule` + template
- Multiples workflows CI supprimés

## Tests effectués

- Site MkDocs build strict validé
- Pages GitHub déployées avec succès
- Index modules régénéré automatiquement

## Prochaines étapes

- Rebrand mdwiki-next → OntoWave
- Tests e2e Playwright
- Nettoyage des contenus root MAJUSCULES
