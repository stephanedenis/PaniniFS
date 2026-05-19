# 2026-02-21 — Intégration du text_normalizer.py dans le pipeline

> Agent : GitHub Copilot (Claude Opus 4.6) · hauru · Session normalisation Phase 2

## Contexte

Suite à l'étude des normes ISO/Unicode (Phase 1 → `LANGUAGE_STANDARDS_ISO_UNICODE.md`),
l'audit complet du pipeline a révélé que **zéro normalisation NFC Unicode** n'existait
dans le codebase. Le module `unicodedata` n'était importé dans aucun fichier `.py`.

Cela signifie qu'un mot comme « été » stocké en NFD (`e` + U+0301 + `t` + `e` + U+0301)
ne correspondrait **jamais** à sa forme NFC (`\u00e9t\u00e9`) dans `ATOM_KEYWORDS` — causant
des **faux négatifs silencieux** dans l'alignement mot→atome.

## Décisions clés

### D1 — Module dédié `text_normalizer.py`
- **Constat** : La normalisation touche 6+ fichiers avec des besoins différents (léger vs complet)
- **Décision** : Créer un module unique avec deux points d'entrée :
  - `normalize_nfc(text)` → NFC minimal, zéro dépendance externe, O(n)
  - `normalize_text(text, lang_hint)` → NFC + mojibake + scripts + époque + BCP 47
- **Impact** : Interface stable pour tous les consommateurs, fallback gracieux si le module est absent

### D2 — NFC au point de passage unique (`_clean_paragraphs`)
- **Constat** : `_clean_paragraphs()` dans `text_extractor.py` est le goulot par lequel TOUT texte transite
- **Décision** : Injecter `text = normalize_nfc(text)` comme première opération après normalisation des fins de ligne
- **Impact** : Garantit que tout texte est NFC avant toute comparaison en aval

### D3 — NFC aussi dans `_extract_txt()` après décodage chardet
- **Constat** : Les fichiers TXT Gutenberg sont décodés via chardet mais jamais NFC-normalisés
- **Décision** : Double NFC : une fois au décodage (corrige cp1252 mojibake), une fois à la sortie
- **Impact** : Idempotent (NFC∘NFC = NFC), donc pas de risque de double traitement

### D4 — Correction du fallback mapping obsolète dans `detect_language()`
- **Constat** : `pt→es` et `nl→de` dans le mapping de fallback datent d'avant l'ajout de pt et nl à SUPPORTED_LANGS
- **Décision** : Supprimer ces deux entrées, ajouter `af→nl` (afrikaans) et `gl→pt` (galicien)
- **Impact** : Le portugais et le néerlandais ne sont plus mal classifiés

### D5 — NFC dans `align_words_to_atoms()` et `analyze_syntax()`
- **Constat** : `align_words_to_atoms()` compare les mots aux clés de `ATOM_KEYWORDS` — c'est le point LE PLUS CRITIQUE
- **Décision** : NFC avant le split en mots dans les deux fonctions
- **Impact** : Élimine les faux négatifs silencieux dans le matching sémantique

### D6 — Métadonnées enrichies dans `gutenberg_ingest.py`
- **Constat** : Les textes Gutenberg sont téléchargés en bytes bruts sans métadonnées de normalisation
- **Décision** : NFC au téléchargement + sidecar `.meta.json` avec scripts, époque, BCP 47
- **Impact** : Chaque texte du corpus a désormais ses métadonnées de normalisation persistées

## Fichiers modifiés

| Fichier | Modification | Raison |
|---------|-------------|--------|
| `text_normalizer.py` | **CRÉÉ** (~600 lignes) | Module unifié de normalisation |
| `text_extractor.py` | Import `normalize_nfc`, injection dans `_clean_paragraphs()` et `_extract_txt()` | NFC au point de passage unique |
| `document_analyzer.py` | Import `normalize_nfc`, NFC dans `detect_language()`, correction fallback mapping | Détection langue fiable |
| `seven_layers_engine.py` | Import `normalize_nfc`, NFC dans `analyze_syntax()` et `align_words_to_atoms()` | Matching mot→atome correct |
| `gutenberg_ingest.py` | Import `normalize_text`, NFC + `.meta.json` dans `download_text()` | Métadonnées enrichies |

## Tests effectués

### Self-tests `text_normalizer.py` (10/10 ✅)
1. NFD→NFC conversion (14 changements détectés)
2. Idempotence (normalize∘normalize = normalize)
3. Détection scripts multi-écriture (Latn, Cyrl, Hani, Deva)
4. Détection époque (de-1901:0.89, fr-1694:1.00, en-early_modern:0.53)
5. Tags BCP 47 (fr, zh-Hant, de-1901, sa-Latn, ja)
6. Conversion ISO 639 (fre→fr, dut→nl, fr→fra)
7. Réparation mojibake (cp1252 double-encoding)
8. Mapping script→langues (Deva→[hi,sa,mr,ne], Hani→[zh,ja])
9. Normalisation espaces Unicode
10. `normalize_nfc()` rapide

### Tests de régression pipeline (5/5 ✅)
1. `text_normalizer` : imports OK
2. `text_extractor._clean_paragraphs` : texte NFD → sortie NFC confirmée
3. `document_analyzer.detect_language` : texte NFD français → détecté "fr"
4. `seven_layers_engine.analyze_syntax` : texte NFD allemand → 6 tokens analysés
5. `gutenberg_ingest` : imports OK

## Architecture de normalisation

```
                    ┌─────────────────────────────┐
                    │   text_normalizer.py         │
                    │                              │
                    │  normalize_nfc(text)  ←─ léger, partout
                    │  normalize_text(text) ←─ complet, ingestion
                    │                              │
                    │  • NFC (unicodedata)          │
                    │  • Mojibake repair (cp1252)   │
                    │  • Script detection (15924)   │
                    │  • Epoch detection (BCP 47)   │
                    │  • BOM removal                │
                    │  • Whitespace normalization   │
                    └──────────┬──────────────────┘
                               │
          ┌────────────────────┼───────────────────────┐
          │                    │                        │
          ▼                    ▼                        ▼
  text_extractor.py    seven_layers_engine.py   gutenberg_ingest.py
  ├─_clean_paragraphs  ├─analyze_syntax()       ├─download_text()
  │  (NFC chokepoint)  ├─align_words_to_atoms() │  (NFC + .meta.json)
  └─_extract_txt()     │  (NFC avant matching)  └──────────────────
     (NFC après decode) └──────────────────
                               │
                    document_analyzer.py
                    └─detect_language()
                       (NFC + fallback fixé)
```

## Prochaines étapes

1. **Valider les dictionnaires ATOM_KEYWORDS en NFC** — exécuter `validate_nfc_keywords()` sur les 14 langues
2. **Ajouter `normalize_text()` complet dans `document_analyzer.analyze_paragraph()`** pour exposer les métadonnées d'époque/script dans les résultats d'analyse
3. **Test E2E** : re-télécharger un texte Gutenberg (ex: pg55456 FR) et vérifier que le `.meta.json` est créé avec les bonnes métadonnées
4. **Benchmark performance** : mesurer l'overhead NFC sur un corpus de 50 textes
5. **Documenter dans `LANGUAGE_STANDARDS_ISO_UNICODE.md`** : ajouter une section "Implémentation" avec les points d'injection
