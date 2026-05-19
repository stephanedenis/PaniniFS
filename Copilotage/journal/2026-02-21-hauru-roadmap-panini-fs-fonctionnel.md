# 2026-02-21 — Roadmap complet Panini-FS fonctionnel

> Agent : GitHub Copilot (Claude Opus 4.6) · hauru · Session roadmap

## Contexte

Demande de préparer un roadmap complet pour atteindre un Panini-FS fonctionnel.
Un audit exhaustif du repo a été réalisé en préalable pour mesurer l'écart entre
la vision (README, `IDEAS_INVENTORY.md`, architecture plan) et la réalité sur disque.

## Décisions clés

### D1 — Diagnostic sans complaisance
- **Constat** : Le README décrit un système Rust avec 10 submodules, une architecture
  CORE/ECOSYSTEM/RESEARCH — **rien de tout ça n'existe**. Le `Cargo.toml` référence
  `crates/panini-core` et `crates/panini-api` qui n'ont jamais été créés. 29/31
  workflows CI sont désactivés. Le Web UI est 3 fichiers TSX orphelins sans backend.
- **Décision** : Documenter la réalité telle qu'elle est, pas telle qu'on la rêve.
- **Impact** : Le roadmap part de l'état réel, pas d'une fiction.

### D2 — Python d'abord, Rust ensuite
- **Constat** : Le moteur 7 couches (3 320 lignes), 91.2% de couverture sur 7 langues,
  34 atomes × 14 langues — tout est en Python et ça fonctionne.
- **Décision** : Le Panini-FS fonctionnel est un **package Python installable** avec CLI,
  pas un filesystem Rust/FUSE. Rust viendra éventuellement pour les hotpaths profilés.
- **Impact** : Élimine le blocage "on ne peut pas avancer tant que le Rust n'est pas fait".

### D3 — 6 phases, du nettoyage au scale
- **Constat** : 133 idées inventoriées dans `IDEAS_INVENTORY.md`, besoin de prioriser.
- **Décision** : Phase 0 (assainissement) → 1 (CI) → 2 (API) → 3 (pipeline) → 4 (recherche) → 5 (FS) → 6 (scale).
- **Impact** : Chaque phase produit un livrable concret et utilisable.

### D4 — Monorepo, pas de submodules
- **Constat** : 10 submodules déclarés, 0 clonés, jamais fonctionné.
- **Décision** : Package Python dans un monorepo. Si un module grandit trop, on sépare quand c'est justifié.
- **Impact** : Simplicité de gestion, CI unique, imports simples.

## Fichiers modifiés

| Fichier | Modification | Raison |
|---------|-------------|--------|
| `Copilotage/ROADMAP_PANINI_FS.md` | **CRÉÉ** | Roadmap complet en 6 phases + annexes |
| `Copilotage/journal/INDEX.md` | Mis à jour | Nouvelle entrée |

## Tests effectués

- Audit via subagent : 2 649 fichiers analysés, structure complète inventoriée
- Lecture complète de : README.md, IDEAS_INVENTORY.md, roadmap.md, architecture plan
- Croisement avec les 55 entrées de journal existantes

## Prochaines étapes

1. **Phase 0.1** : Commencer le nettoyage structurel (déplacer les fichiers orphelins)
2. **Phase 0.2** : Renommer SANDBOX → panini/, créer les `__init__.py`
3. **Phase 0.3** : Créer `pyproject.toml`, tester `pip install -e .`
