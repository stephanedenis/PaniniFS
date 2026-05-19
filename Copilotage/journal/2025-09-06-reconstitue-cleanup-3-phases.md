# 📓 Journal reconstitué — 2025-09-06

**Host**: totoro
**Source**: Reconstitué depuis `git log` le 2026-02-18
**Auteur commits**: Stéphane Denis + github-actions

> ⚠️ Ce journal a été reconstitué rétrospectivement depuis l'historique Git.

---

## Contexte

Grand nettoyage du repo en 3 phases : externalisation vers les sous-modules,
gouvernance du triage, suppression des contenus MAJUSCULES legacy.

## Décisions clés

### 1. Indépendance des sous-modules + triage auto (#77)

Templates, docs, auto-triage (issues + backfill) externalisés vers les
sous-modules. Label `[agent:auto]` pour le triage automatique.

### 2. Cleanup phase 1 : ECOSYSTEM (#77)

Externalisation du contenu `ECOSYSTEM/` vers les sous-modules. Backup
dans `cleanup/backup_20250906_140652/`.

### 3. Cleanup phase 2 : DevOps/publications/architecture (#78)

Externalisation de DevOps, publications, architecture, scaffolds.
Backup dans `cleanup/backup_20250906_143516/`.

### 4. Cleanup phase 3 : MAJUSCULES (#80)

Purge des dossiers en MAJUSCULES et contenus externalisés restants.
Tous les backups conservés dans `cleanup/`.

### 5. Alignement workflows CI (#79)

Suppression du workflow `publications.yml`. Ajout du workflow
`docs-pages` build/deploy unifié.

## Fichiers modifiés

- `ECOSYSTEM/` — Externalisé (backup dans `cleanup/`)
- `ARCHITECTURE/` — Externalisé
- `cleanup/backup_*/` — Sauvegardes de sécurité
- `.github/workflows/` — Alignés, publications supprimé
- `.github/ISSUE_TEMPLATE/` — Mis à jour (chemins corrigés)
- `docs_new/` — Liens cassés retirés

## Tests effectués

- PR #77, #78, #79, #80 : toutes mergées
- Index modules auto-régénéré
- Build MkDocs strict : liens résolus après nettoyage

## Prochaines étapes

- Pause de ~2 mois (aucun commit entre sept 6 et nov 12)
- Reprendre avec le système de journalisation et la réorg modules
