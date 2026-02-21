# v4.8.1 — Finnish lemmatizer (voikko) + performance cache

**Date** : 2026-02-21
**Machine** : hauru (Xeon E5-2650 v2, 62 GB, openSUSE Tumbleweed)
**Agent** : Copilot (Claude Opus 4.6)
**Commit précédent** : `4045352` (v4.8)

## Contexte

Après la v4.8 qui a porté la couverture lexicale globale de 67.6% à 77.4%
(+9.8pp) grâce à 7 stratégies de matching dans `_is_covered_enhanced()`,
le finnois restait le maillon faible : **65.8%** de couverture alors qu'il
représente **21.2%** du corpus (27 768 mots de contenu sur 130 963 total).

Objectif : intégrer le lemmatiseur morphologique **voikko** pour le finnois
afin de réduire massivement les formes fléchies non couvertes.

## Décisions clés

### 1. Installation voikko natif

- **Constat** : Le module Python `libvoikko` nécessite la bibliothèque native
  `libvoikko1` et les dictionnaires finnois (`malaga-suomi`).
- **Décision** : Installation via `pip3 install libvoikko` + `zypper install
  libvoikko1 voikkospell` (5 paquets : libhfstospell11, malaga-suomi 2.5,
  libvoikko1 4.3.3, voikkospell, enchant-2-backend-voikko).
- **Impact** : `_HAS_VOIKKO = True` activé à l'import de
  `reconstruction_fidelity.py`. Stratégie #9 opérationnelle.

### 2. Cache de couverture mot-niveau (performance ×10)

- **Constat** : L'audit v4.8.1 prenait ~56s/fichier (vs 3s en v4.8) parce
  que `_is_covered_enhanced()` recalculait l'union des ensembles de keywords
  `_GLOBAL_KEYWORDS.get(lang) | _GLOBAL_KEYWORDS.get("_all")` à **chaque
  appel** (millions d'unions de sets).
- **Décision** :
  1. `_MERGED_KEYWORDS[lang]` — unions pré-calculées (singleton par langue)
  2. `_MERGED_STEMS[lang]` — idem pour les stems Snowball
  3. `_COVERAGE_CACHE[(word, lang)]` — cache booléen par mot/langue
     (stratégies 2-9 ne dépendent pas du `atom_words` paragraphe)
- **Impact** : Phase 2 (analyse de fidélité) passe de ~50s à **0.1s** pour
  810 paragraphes. Le goulot est maintenant le moteur 7 couches (Phase 1).

### 3. Expansion stop words finnois (+44 mots)

- **Constat** : Analyse corpus → les "mots non couverts" les plus fréquents
  sont des pronoms (hän ×1563, minä ×882), conjonctions (että ×471,
  mutta ×410), particules (niin ×372, vain ×126) — des mots fonctionnels
  qui ne portent pas de contenu sémantique.
- **Décision** : Ajout de 44 stop words finnois dans
  `vocabulary_expansion_v481.py` (pronoms déclinés, formes de olla,
  modaux, adverbes spatio-temporels). Total : 645 → 689 stop words FI.
- **Impact** : Réduit le dénominateur (mots de contenu) et améliore la
  précision de la métrique de couverture.

### 4. Expansion keywords finnois (+178 mots, ~15 atomes)

- **Constat** : Voikko résout les formes fléchies → formes de base, mais
  ces formes de base doivent aussi être dans les keywords atomiques pour
  être comptées comme "couvertes". Analyse : 148/188 mots courants déjà
  mappés, 40 manquants.
- **Décision** : `FINNISH_KEYWORDS_V481` — 178 nouveaux mots finnois
  mappés à ~15 atomes existants (NATURE, CORPS_PARTIES, MAISON, TEMPS,
  ANIMAL, VÊTEMENT, NOURRITURE, SENTIR, PENSÉE, VOLONTÉ, PARLER, SOCIAL,
  FAMILLE, etc.). Plus 14 noms propres littéraires (Liisa, Juhani, etc.).
- **Impact** : Keywords FI : 1206 → 1384 (+178). Keywords global :
  12667 → 12842 (+175).

## Fichiers modifiés

| Fichier | Raison |
|---------|--------|
| `vocabulary_expansion_v481.py` | **NOUVEAU** — Stop words (44), keywords (178), proper nouns (14), voikko function word filter |
| `reconstruction_fidelity.py` | Import v4.8.1, `_MERGED_KEYWORDS/STEMS`, `_COVERAGE_CACHE`, intégration `get_stop_words()`, `_build_global_keyword_index()`, `get_content_words()` |

## Tests effectués

### Validation voikko
```
talossa → talo ✅
sanoi → sanoa ✅
kirjoittamiseen → kirjoittaa ✅
tyttöjä → tyttö ✅
kauniita → kaunis ✅
```

### Corpus test (top 200 uncovered FI words)
- 191/200 (96%) résolus par voikko vers une forme de base

### Test suite
- **110 passed, 1 failed** (échec pré-existant `test_all_languages_present`)
- **0 régression** introduite par v4.8.1

### Couverture mesurée

| Métrique | v4.8 | v4.8.1 | Δ |
|----------|------|--------|---|
| **Global weighted** | 77.4% | **81.8%** | **+4.4pp** |
| FI (finnois) | 65.8% | **78.1%** | **+12.3pp** |
| EN (anglais) | 88.1% | 88.2% | +0.1 |
| FR (français) | 75.5% | 80.8% | +5.3 |
| DE (allemand) | 81.1% | 83.4% | +2.3 |
| EO (espéranto) | 82.7% | 86.1% | +3.4 |
| ES (espagnol) | 78.8% | 83.4% | +4.6 |
| IT (italien) | 77.1% | 80.1% | +3.0 |
| SA (sanscrit) | 43.5% | 43.7% | +0.2 |

**Le finnois n'est plus le maillon faible** — il est passé de la pire couverture
(65.8%) à un niveau comparable aux autres langues européennes (78.1%).

L'amélioration de toutes les langues provient du Snowball stemmer (stratégie #8)
+ cache de performance qui permet les 9 stratégies de matching sans régression.

## Prochaines étapes

1. **v4.8.2** — Base `panini-interpretations-db` : stocker les résultats
   d'interprétation dans une DB structurée pour analyse cross-document
2. **v4.9** — Export JSON-LD : sérialisation sémantique liée au web de données
3. **Objectif 90%** — Cible couverture lexicale globale ≥ 90%
   (nécessite expansion SA + amélioration FR/IT/ES)
4. **Performance** — Le moteur 7 couches prend ~56s/fichier. Explorer
   caching du pipeline `analyze_document()` ou parallélisation
