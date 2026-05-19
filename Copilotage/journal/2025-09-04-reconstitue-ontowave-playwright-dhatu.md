# 📓 Journal reconstitué — 2025-09-04

**Host**: totoro
**Source**: Reconstitué depuis `git log` le 2026-02-18
**Auteur commits**: Stéphane Denis

> ⚠️ Ce journal a été reconstitué rétrospectivement depuis l'historique Git.

---

## Contexte

Journée dédiée à la stabilisation des sous-modules, au rebrand OntoWave,
aux premiers tests e2e Playwright, et à la recherche sur la typologie Dhātu.

## Décisions clés

### 1. Recherche Dhātu v0.1 (#75)

Première typologie des dhātu avec génération automatique et mode autopilote.
Scripts d'expérimentation dans `experiments/dhatu/`.

### 2. Stabilisation des sous-modules

Nettoyage de `.gitmodules` (duplicats supprimés, entrée RESEARCH invalide retirée).
Déclaration explicite de RESEARCH et `copilotage/shared`. CI Pages sans checkout
récursif pour éviter les échecs sur sous-modules optionnels.

### 3. Rebrand mdwiki-next → OntoWave

Renommage du dossier, du package, et des labels UI. L'application SPA de wiki
sémantique est désormais « OntoWave ».

### 4. Tests e2e Playwright

Premiers tests Playwright : smoke test + vérification que `research/whats-new`
et `feed.xml` retournent 200. CI intégrée.

### 5. Corrections mkdocs strict

Ajout de placeholders `OPERATIONS/DevOps/roadmap.md` (FR+EN) pour satisfaire
les liens relatifs en mode strict.

## Fichiers modifiés

- `.gitmodules` — Nettoyé et corrigé
- `experiments/dhatu/` — Nouveau : `report.py`, `validator.py`
- `docs_new/research/experiences-dhatu-typologie-v0-1.md` — Dhātu v0.1
- `e2e/` — Nouveau : `playwright.config.js`, `tests/smoke.spec.js`, `tests/research.spec.js`
- `ontowave/` → renommé depuis `mdwiki-next/`
- `docs_new/OPERATIONS/DevOps/roadmap.md` — Placeholder strict

## Tests effectués

- Playwright e2e : smoke + research pages → 200
- Build MkDocs strict : liens résolus
- Sous-modules : CI passe sans récursion

## Prochaines étapes

- Ajouter OntoWave comme sous-module
- Unifier la doc via agrégation des sous-modules
- Intégrer la gouvernance et le triage automatique
