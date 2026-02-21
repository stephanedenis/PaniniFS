# 🌏 v4.7.2 — Extension trigrammes multi-scripts + re-synthèse multi-format

**Date** : 2026-02-20  
**Hôte** : hauru (Intel Xeon E5-2650 v2, 62 GB RAM)  
**Agent** : GitHub Copilot (Claude Opus 4.6)  
**Branche** : master  

## Contexte

Suite de v4.7.1 (intégration pipeline + correction faux positifs). Le module
`gutenberg_preamble_normalizer.py` détectait uniquement les langues
**latines** par trigrammes (en/fr/de/es/it/pt/nl/la). Pour les écritures
non-latines (cyrillique, CJK, hiragana), la détection retombait sur un simple
seuil de ratio de script sans discrimination fine. Objectif : étendre le
support linguistique pour les 3 corpus existants non-latins (ru, zh, ja) et
valider la re-synthèse multi-format sur des éditions HTML/EPUB.

## Décisions clés

### 1. Trigrams cyrilliques russes (36 trigrams)

- **Constat** : Le corpus russe (pg14741, Tolstoï, 17 817 mots cyrilliques)
  utilise `ё` fréquemment, mais les trigrams de référence doivent utiliser `е`
  (variante orthographique standard). Le top-25 des trigrams du corpus montre
  `тво`, `ост`, `все`, `что` comme les plus fréquents.
- **Décision** : 36 trigrams russes incluant particules courantes (`что`, `его`,
  `все`, `как`, `это`), suffixes (`ать`, `ить`, `ова`, `ной`) et morphèmes
  fréquents. Normalisation `ё→е` dans l'extracteur de mots cyrilliques.
- **Impact** : Détection confirmée sur texte réel (conf > 0.1). 0 faux positifs
  de citations étrangères dans le corpus Tolstoï.

### 2. Trigrams hiragana japonais (32 trigrams)

- **Constat** : Le japonais utilise 3 systèmes d'écriture (hiragana, katakana,
  kanji CJK). Les hiragana portent la grammaire (particules, auxiliaires).
  Top-25 du corpus (pg1982) : `である`, `ていた`, `ながら`, `ように`.
- **Décision** : 32 trigrams hiragana incluant auxiliaires (`である`, `ある`,
  `てい`), connecteurs (`から`, `こと`, `もの`), particules longues (`ばか`,
  `かり`). Le hiragana ratio > 0.05 déclenche l'extraction spécialisée.
- **Impact** : Discrimination ja vs zh fiable — hiragana → ja, CJK pur → zh.

### 3. Bigrammes CJK chinois (32 bigrammes)

- **Constat** : Le chinois n'utilise pas de syllabes comme unités — les
  caractères individuels portent le sens. Les trigrams de 3 idéogrammes sont
  trop spécifiques. Les bigrammes fonctionnels (`不是`, `一個`, `沒有`)
  sont plus discriminants.
- **Décision** : `LANGUAGE_NGRAM_CONFIG` avec `"zh": 2` (bigrammes). 32
  bigrammes haute-fréquence tirés du corpus pg24264 (紅樓夢, 126K runs CJK).
  L'extracteur génère à la fois bigrams et trigrams, chaque langue utilise
  la taille configurée.
- **Impact** : Détection zh correcte (conf 0.188). Pas de collision avec ja.

### 4. Architecture multi-script refactorisée

- **Constat** : `_detect_language_trigram()` n'extrayait que des mots latins
  (`[a-zàâäéèêëïîôùûüçœæñ¿¡áíóúäöüß]+`).
- **Décision** : Extraction multi-script via `_WORD_EXTRACTORS` (4 regex :
  latin, cyrillic, hiragana, cjk). Détection en 3 phases :
  1. Script sans trigrams (devanagari/grec/arabe/hébreu) → retour immédiat
  2. Extraction n-grammes multi-scripts selon script dominant
  3. Scoring multi-langues + fallback script si trigrams insuffisants
- **Impact** : Compatible ascendant — tous les 21 tests existants passent.

### 5. Re-synthèse multi-format validée

- **Constat** : `unify_editions()` était implémentée mais jamais appelée.
- **Décision** : Téléchargement HTML de 4 œuvres (pg11 EN, pg55456 FR,
  pg22367 DE, pg14741 RU) + EPUB pg11 EN. Validation cross-format et
  cross-langue via `unify_editions()`.
- **Impact** :
  - Alice EN : TXT 26 508 / HTML 53 773 / EPUB 28 742 mots (CV=0.34)
  - Zone consistency : BODY présent dans 3/3 formats
  - Cross-langue Alice EN/FR : détection correcte des 2 langues

## Fichiers modifiés

| Fichier | Raison |
|---------|--------|
| `gutenberg_preamble_normalizer.py` | +ru/ja/zh trigrams, `LANGUAGE_NGRAM_CONFIG`, `_WORD_EXTRACTORS`, refactoring `_detect_language_trigram()` 3 phases, fallback script, normalisation ё→е |
| `test_gutenberg_preamble.py` | +5 tests : `test_detect_russian`, `test_detect_japanese`, `test_detect_chinese`, `test_russian_in_french_context`, `test_cjk_vs_hiragana_discrimination` |
| `gutenberg_corpus/en/pg11.html` | HTML téléchargé pour test multi-format |
| `gutenberg_corpus/en/pg11.epub` | EPUB téléchargé pour test multi-format |
| `gutenberg_corpus/fr/pg55456.html` | HTML FR téléchargé |
| `gutenberg_corpus/de/pg22367.html` | HTML DE téléchargé |
| `gutenberg_corpus/ru/pg14741.html` | HTML RU téléchargé |

## Tests effectués

- **26/26 tests** passent (21 originaux + 5 nouveaux) en 0.13s
- Validation corpus réel :
  - **RU pg14741** : header en 0.90, footer en 1.00, body ru — 0 faux positifs
  - **ZH pg24264** : header en 0.90, footer en 1.00, body zh
  - **JA pg1982** : header en 0.90, footer en 1.00, body ja
- Re-synthèse multi-format Alice EN : 3 formats, word count CV=0.34
- Re-synthèse cross-langue Alice EN+FR : 2 langues détectées correctement

## Prochaines étapes

- [ ] Ajouter des trigrams pour le coréen (ko) quand corpus disponible
- [ ] Hindi/Sanskrit — pas de corpus Gutenberg local, à télécharger
- [ ] Exploiter `unify_editions()` dans le pipeline `gutenberg_ingest.py`
- [ ] Réduire l'écart HTML word count (53K vs 26K TXT) — strip HTML tags avant comptage
- [ ] Intégrer les nouveaux formats HTML/EPUB dans le catalogue d'ingestion
