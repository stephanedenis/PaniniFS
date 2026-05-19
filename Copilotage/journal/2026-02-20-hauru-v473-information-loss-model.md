# v4.7.3 — Modèle de perte d'information (HTML → TXT)

**Date** : 2026-02-20
**Host** : hauru
**Agent** : GitHub Copilot (Claude Opus 4.6)
**Commit parent** : `a501c3e` (v4.7.2)

## Contexte

Insight fondamental de l'utilisateur : « prendre le problème dans l'autre sens
pour avoir une correspondance du plus riche (html) au plus pauvre (txt) car on
perd de l'information et panini doit viser le bit perfect ».

Au lieu de gonfler le word count TXT pour le faire correspondre au HTML (53K vs
26K), on inverse le modèle : **le HTML est la référence canonique bit-perfect**,
et chaque format plus pauvre est mesuré par ce qu'il **perd**.

## Décisions clés

### 1. Hiérarchie de richesse des formats

- **Constat** : HTML contient toute l'information structurelle (headings, emphasis,
  images, liens, tables), EPUB la conserve quasi-intégralement, TXT perd ~70%.
- **Décision** : `FORMAT_RICHNESS = {"html": 100, "epub": 80, "docx": 70, "md": 50, "txt": 10}`
- **Impact** : Le format le plus riche est automatiquement sélectionné comme
  canonique dans `_compare_editions()`.

### 2. InformationLayer — dataclass 15 dimensions

- **Constat** : Alice EN HTML : 220 `<i>`, 19 headings, 1 image, 16 links, 5
  `<strong>`, 1 table — tout perdu en TXT sauf les `_italic_` markers.
- **Décision** : `InformationLayer` avec 15 dimensions structurelles + méthode
  `loss_vs(reference)` retournant un ratio 0.0–1.0 par dimension.
- **Impact** : On peut quantifier précisément la dégradation pour chaque
  conversion de format.

### 3. Comparison inversée (richest → poorest)

- **Constat** : L'ancien `_compare_editions()` faisait un pairwise symétrique.
- **Décision** : Refonte complète : le format le plus riche est la référence,
  chaque format inférieur reçoit un score de perte (`avg_structural_loss`,
  `dimensions_mostly_lost`, `text_fidelity`).
- **Impact** : Le format_consistency de UnifiedWork contient maintenant
  `canonical_format`, `canonical_layers`, et `information_loss` par format.

### 4. Téléchargement multi-format

- **Constat** : Seul `download_text()` existait pour le TXT.
- **Décision** : Ajout de `GUTENBERG_FORMAT_URLS`, `download_format()`, et
  `download_all_formats()` dans `gutenberg_ingest.py`.
- **Impact** : On peut récupérer HTML/EPUB/TXT pour n'importe quel Gutenberg ID.

## Résultats de validation

### Alice EN (HTML → EPUB → TXT)

| Dimension | EPUB loss | TXT loss |
|-----------|-----------|----------|
| headings | 0% | 0% (pseudo-headings `CHAPTER I`) |
| emphasis_spans | 0% | 0% (`_italic_` markers) |
| strong_spans | 0% | **100% LOST** |
| links | 0% | **100% LOST** |
| tables | 0% | **100% LOST** |
| text_fidelity | 100% | 89.5% |
| **avg structural loss** | **8.3%** | **66.7%** |

### Multi-langue

| Œuvre | TXT avg_loss | TXT text_fidelity | dims_lost |
|-------|-------------|-------------------|-----------|
| Alice EN | 66.7% | 89.5% | 8/13 |
| Germinal FR | 73.1% | 99.3% | 8/13 |
| Anna Karenina RU | 75.0% | 99.8% | 7/13 |

## Fichiers modifiés

- `gutenberg_preamble_normalizer.py` — `FORMAT_RICHNESS`, `InformationLayer`,
  `_extract_information_layers()`, `EditionFormat.info_layers`,
  `_compare_editions()` réécrit
- `gutenberg_ingest.py` — `GUTENBERG_FORMAT_URLS`, `download_format()`,
  `download_all_formats()`
- `test_gutenberg_preamble.py` — `TestInformationLayers` (6 tests), 32/32 pass

## Tests effectués

- 32/32 tests unitaires ✅ (0.45s)
- Validation corpus réel : Alice EN (3 formats), Germinal FR, Anna Karenina RU
- EPUB : perte quasi-nulle (8.3%, seul `preformatted` perdu)
- TXT : perte structurelle 66-75%, fidélité texte 89-100%

## Prochaines étapes

- Intégrer les métriques de perte dans l'export JSON enrichi (schema v1.2)
- Ajouter détection automatique des `[Illustration]` TXT comme proxy d'images
- Compléter le corpus HTML/EPUB pour DE, ES, IT, PT, NL
- Explorer la reconstruction inverse (TXT → HTML via InformationLayer hints)
