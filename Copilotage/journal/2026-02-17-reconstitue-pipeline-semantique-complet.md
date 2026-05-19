# 📓 Journal reconstitué — 2026-02-17

**Host**: hauru
**Source**: Reconstitué depuis `git log` le 2026-02-18
**Auteur commits**: Stephane Denis

> ⚠️ Ce journal a été reconstitué rétrospectivement depuis l'historique Git.

---

## Contexte

Journée la plus dense du projet : 15 commits construisant l'ensemble du pipeline
sémantique depuis l'infrastructure Dolt jusqu'à l'analyse phrase-level. Évolution
de v2 → v2.2 → v3-alpha en une seule journée.

## Décisions clés

### 1. Infrastructure corpus multilingue Gutenberg

Mise en place du téléchargement automatique des textes Gutenberg (Alice + Candide)
en 7 langues. Infrastructure de test multilingue.

### 2. Architecture unifiée 3 couches — POC Dolt

Stockage unifié à 3 niveaux dans Dolt : 17 tables, isolation par branches vérifiée.
Architecture documentée dans `ARCHITECTURE_UNIFIED_DOLT.md`.

### 3. ACL Dolt — Fork vs Branches vs dolt_branch_control

Analyse comparative des modèles d'accès. Implémentation du `sql-server` ACL
avec 14/14 tests passés.

### 4. Topologie de distribution cascade

POC de distribution cascade entre nœuds Dolt. 20/20 tests validés.

### 5. Revue interdisciplinaire — 72 références

Document de revue croisant linguistique, neurosciences, philosophie et
informatique sur les universaux sémantiques.

### 6. Architecture v2 — 23 primitifs universels

Refonte majeure : 23 primitifs sémantiques universels, 107 concepts importés
depuis le dictionnaire PanLang. 38/38 tests. Fichier clé : `import_panlang_v2.py`.

### 7. Revalidation — Quarantaine de concepts

Retrait de 3 substantifs, mise en quarantaine de 10 concepts douteux.
44/44 tests après revalidation.

### 8. Validation multilingue Gutenberg

Validation des concepts contre le corpus Gutenberg avec provenance
édition/traducteur/époque. Correction de 46 mappings v2 IDs + marqueurs FI/EO.

### 9. Sous-primitifs émotionnels

Proposition fondée sur les neurosciences affectives (Panksepp) : 8 axes
émotionnels (SEEKING, FEAR, CARE, GRIEF, RAGE, DISGUST, PLAY, TEDIUM).
Implémentation dans tous les fichiers (v2.2).

### 10. V3-alpha — Analyse gaps + POC phrase-level

Analyse des gaps de reconstruction et premier POC d'analyse au niveau phrase
pour préparer le moteur 7 couches.

## Fichiers modifiés

- `SANDBOX/dolt-concept-store/import_panlang_v2.py` — Architecture v2 + émotions
- `SANDBOX/dolt-concept-store/gutenberg_multilingual_validator.py` — Validation multilingue
- `SANDBOX/dolt-concept-store/dolt_unified_storage.py` — Stockage unifié
- `SANDBOX/dolt-concept-store/setup_dolt_acl.py` — ACL setup
- `SANDBOX/dolt-concept-store/test_branch_acl.py` — Tests ACL (14/14)
- `SANDBOX/dolt-concept-store/test_cascade_topology.py` — Tests cascade (20/20)
- `SANDBOX/dolt-concept-store/quarantine_tier_c.py` — Quarantaine concepts
- `SANDBOX/dolt-concept-store/poc_reconstruction_phrases.py` — POC phrase-level
- `SANDBOX/dolt-concept-store/ARCHITECTURE_UNIFIED_DOLT.md` — Doc architecture
- `SANDBOX/dolt-concept-store/PROPOSITION_SOUS_PRIMITIFS_EMOTIONNELS.md` — RFC émotions
- `SANDBOX/dolt-concept-store/SYNTHESE_GUTENBERG_VALIDATION.md` — Synthèse Gutenberg
- `SANDBOX/dolt-concept-store/ANALYSE_GAPS_RECONSTRUCTION.md` — Gaps v3
- `SANDBOX/dolt-concept-store/schema_*.sql` — 5 schémas SQL

## Tests effectués

- ✅ Architecture v2 : 38/38 tests
- ✅ Revalidation : 44/44 tests
- ✅ ACL Dolt : 14/14 tests
- ✅ Cascade topology : 20/20 tests
- ✅ Gutenberg validation multilingue
- ✅ Sous-primitifs émotionnels intégrés

## Prochaines étapes

- Moteur 7 couches au niveau paragraphe (v3)
- Pont morpho-sémantique
- Couverture 100% des paragraphes
