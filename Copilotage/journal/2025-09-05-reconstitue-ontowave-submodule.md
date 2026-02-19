# 📓 Journal reconstitué — 2025-09-05

**Host**: totoro
**Source**: Reconstitué depuis `git log` le 2026-02-18
**Auteur commits**: Stéphane Denis + github-actions

> ⚠️ Ce journal a été reconstitué rétrospectivement depuis l'historique Git.

---

## Contexte

Intégration d'OntoWave comme sous-module et unification de la documentation
via agrégation automatique des docs des sous-modules.

## Décisions clés

### 1. OntoWave comme sous-module

Ajout de `modules/ontowave-app` comme sous-module Git. Documentation de la vision
et du rôle d'OntoWave (SPA wiki sémantique) dans l'écosystème.

### 2. Unification doc via agrégation

Script `scripts/aggregate_submodule_docs.py` pour collecter automatiquement les
docs des sous-modules. CI Pages initialise les sous-modules via HTTPS et agrège
les docs avant le build MkDocs.

### 3. Section Écosystème dans la nav

Ajout de la page OntoWave (FR/EN) dans la navigation MkDocs sous « Écosystème ».

## Fichiers modifiés

- `.gitmodules` — Ajout `modules/ontowave-app`
- `docs_new/ecosystem/ontowave.md` — Vision OntoWave (FR)
- `docs_new/en/ecosystem/ontowave.md` — Vision OntoWave (EN)
- `scripts/aggregate_submodule_docs.py` — Agrégation docs sous-modules
- `scripts/generate_modules_docs_index.py` — Index modules auto
- `.github/workflows/deploy-pages-mkdocs.yml` — Init submodules HTTPS
- `mkdocs.yml` — Nav Écosystème

## Tests effectués

- Index modules auto-généré par github-actions
- Build MkDocs avec docs agrégées

## Prochaines étapes

- Gouvernance et triage automatique
- Nettoyage des contenus root (MAJUSCULES)
