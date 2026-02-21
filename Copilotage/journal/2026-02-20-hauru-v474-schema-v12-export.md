# v4.7.4 — Schema v1.2 : export enrichi + illustrations multilingues

**Date** : 2026-02-20
**Host** : hauru
**Agent** : GitHub Copilot (Claude Opus 4.6)
**Commit parent** : `f3abc3d` (v4.7.3)

## Contexte

Suite directe de v4.7.3 (modèle de perte d'information). Objectif : propager
les métriques de perte dans l'export JSON sérialisé (schema v1.2) pour que
tout consommateur du pipeline ait accès aux dimensions structurelles et aux
scores de dégradation par format. Également améliorer la détection des marqueurs
d'illustration multilingues dans les TXT Gutenberg.

## Décisions clés

### 1. Schema v1.2 — SemanticExport enrichi

- **Constat** : `SemanticExport` (v1.1) n'avait aucune information sur les
  dimensions structurelles du format source ni sur les pertes inter-formats.
- **Décision** : Ajout de deux champs :
  - `information_layers: Dict[str, int]` — les 15 dimensions structurelles
    du fichier source (headings, emphasis, images, tables, etc.)
  - `format_consistency: Dict` — les métriques de perte quand des formats
    frères (HTML/EPUB) existent (`canonical_format`, `information_loss`, etc.)
- **Impact** : Chaque `.semantic.json` exporté est auto-descriptif sur sa
  qualité structurelle.

### 2. Illustrations multilingues

- **Constat** : Le corpus contient `[Illustration]` (EN, 221), `[Illustrazione]` (IT, 42),
  `[Ilustrajxo]` (EO, 2) — le pattern original ne capturait que la variante anglaise.
- **Décision** : Pattern étendu à 8 variantes :
  `Illustration|Illustrazione|Ilustrajxo|Abbildung|Ilustración|Figura|Gravure|Illustratie`
  + extraction des captions comme `image_alts`.
- **Impact** : La détection couvre maintenant IT, DE, FR, ES, PT, NL, EO en plus de EN.

### 3. InformationLayer.to_dict()

- **Constat** : Pas de sérialisation propre des dimensions numériques.
- **Décision** : Méthode `to_dict()` retournant les 15 dimensions numériques
  (sans les listes de texte `heading_texts`, `emphasis_texts`, `image_alts`).
- **Impact** : Sérialisation JSON propre pour l'export.

### 4. Batch multi-format dans analyze_all()

- **Constat** : `analyze_all()` n'exploitait que les .txt.
- **Décision** : Détection automatique des fichiers frères (`pg{gid}.html`,
  `pg{gid}.epub`, `pg{gid}-images.html`) dans le même répertoire.
  Si trouvés → `unify_editions()` + injection `info_layers` et
  `format_consistency` dans l'export.
- **Impact** : Les exports re-générés contiendront automatiquement les
  métriques de perte pour tout texte ayant un HTML/EPUB frère.

## Fichiers modifiés

- `semantic_serializer.py` — SCHEMA_VERSION 1.1→1.2, `information_layers` +
  `format_consistency` dans `SemanticExport`, params dans `export_document_atoms`
- `gutenberg_preamble_normalizer.py` — `ILLUSTRATION_PATTERN` multilingue (8 variantes),
  `InformationLayer.to_dict()`, `_extract_information_layers()` TXT branch enrichi,
  `classify_gutenberg_zones` caption metadata fixé
- `gutenberg_ingest.py` — `import re`, détection sibling formats dans `analyze_all()`
- `test_gutenberg_preamble.py` — `TestSchemaV12` (7 tests)

## Tests effectués

- 39/39 tests unitaires ✅ (49.43s — le test `test_real_export_with_loss_metrics`
  exécute le pipeline complet `export_document_atoms` sur pg11.txt)
- Validation intégration : export pg11.txt enrichi avec `information_layers`
  (30 headings, 235 emphasis, 1 image) et `format_consistency` (canonical=html,
  TXT avg_loss=66.7%, text_fidelity=89.5%)

## Prochaines étapes

- Re-exporter tout le corpus pour passer en schema v1.2 (supprimer le cache)
- Comparer les image_alts TXT vs HTML img alts pour mesurer la qualité des proxies
- Enrichir la matrice d'universalité avec les métriques de perte
- Explorer la reconstruction inverse (TXT → HTML via InformationLayer hints)
