# v4.3.1 — Néerlandais et Portugais : couverture 10 langues complète

- **Date** : 2026-02-20
- **Machine** : hauru (Xeon E5-2650, 62 GB RAM)
- **Agent** : Claude Opus 4, session VS Code Copilot
- **Commit précédent** : `422b497` (v4.3 CJK+cyrillique)

## Contexte

Après v4.3 qui a ajouté le chinois, le japonais et le russe avec un résultat de
34/34 atomes universels sur 8 langues, le néerlandais (nl) et le portugais (pt)
restaient brisés avec respectivement 1 et 3 atomes détectés. La cause était
double : **aucun mot-clé** dans ATOM_KEYWORDS et **aucun LANGUAGE_PROFILE** dans
le moteur d'analyse.

## Décisions clés

### 1. Fichier supplementary_keywords.py séparé

**Constat** : nl et pt sont des langues à écriture latine, comme les 7 langues
déjà couvertes. Pas besoin de tokenizer spécial (contrairement au CJK).

**Décision** : Créer un fichier `supplementary_keywords.py` distinct de
`exotic_keywords.py` pour maintenir la séparation des responsabilités :
- `exotic_keywords.py` = CJK + cyrillique (tokenizer spécial, kanji stems)
- `supplementary_keywords.py` = langues latines supplémentaires (nl, pt)

**Impact** : Architecture modulaire, facile d'ajouter d'autres langues latines
ultérieurement (sv, da, ro, pl...).

### 2. Densité de mots-clés alignée

**Constat** : Les langues existantes ont 390-545 mots-clés par langue.

**Décision** : Viser ~590 mots-clés par langue (nl=593, pt=594) avec 14-20
mots-clés par atome, couvrant verbes, noms, adjectifs et expressions.

**Impact** : Densité comparable aux langues les mieux couvertes (en=545, fr=503).

### 3. LANGUAGE_PROFILES complets

**Constat** : Sans LANGUAGE_PROFILE, le moteur utilise le profil anglais par
défaut, ce qui biaise les détections de mots structurels (déterminants,
prépositions, conjonctions, pronoms).

**Décision** : Profils linguistiques complets avec toutes les catégories :
- nl : SOV (V2 en principale), 24 prépositions, 23 conjonctions, 31 pronoms,
  genre commun/neutre (de/het), marqueurs archaïques (gij, ge, uwer...)
- pt : SVO, 20 prépositions, 22 conjonctions, 35 pronoms, infinitif personnel,
  futur subjonctif, distinction ser/estar

### 4. Mots structurels (négation, quantification, modalité)

**Décision** : Ajout de SUPPLEMENTARY_NEGATION_WORDS, SUPPLEMENTARY_QUANTIFIER_WORDS
et SUPPLEMENTARY_MODIFIER_WORDS pour nl et pt, mergés dans le moteur à côté des
mots exotiques.

## Fichiers créés

| Fichier | Lignes | Description |
|---------|--------|-------------|
| `supplementary_keywords.py` | ~400 | 34 atomes × nl/pt keywords + profils linguistiques + merge function |

## Fichiers modifiés

| Fichier | Modification |
|---------|-------------|
| `gutenberg_multilingual_validator.py` | Import + merge des supplementary keywords après exotic |
| `seven_layers_engine.py` | Import supplementary, merge LANGUAGE_PROFILES et NEG/QUANT/MOD words |

## Tests effectués

### Import et chargement
- ✅ nl : 34/34 atomes avec mots-clés, 593 keywords total
- ✅ pt : 34/34 atomes avec mots-clés, 594 keywords total
- ✅ LANGUAGE_PROFILES nl et pt correctement chargés
- ✅ NEG/QUANT/MOD words mergés pour nl et pt

### Analyse du corpus complet (51 textes)
- Textes ré-analysés : 3 (pg18066 nl, pg17525 pt, pg29668 pt)
- Résultats :
  - pg18066 (Max Havelaar, nl) : **34 atomes**, 120 concepts, 65 250 mots, 38.0s
  - pg29668 (Os Lusíadas, pt) : **32 atomes**, 24 concepts, 82 763 mots, 64.8s
  - pg17525 (Dom Casmurro, pt) : 21 atomes, 3 concepts, 16 967 mots, 13.5s

### Universalité

| Langue | Atomes (union textes) |
|--------|----------------------|
| de | 34/34 |
| en | 34/34 |
| es | 34/34 |
| fr | 34/34 |
| it | 34/34 |
| ja | 34/34 |
| nl | **34/34** ← était 1 |
| pt | **34/34** ← était 3 |
| ru | 34/34 |
| zh | 34/34 |

**Universalité : 34/34 atomes sur 10 langues = 100%**

### Similarité cosinus notable

| Paire | Cosinus |
|-------|---------|
| NL↔DE | 0.817 (germaniques) |
| NL↔EN | 0.824 (germaniques) |
| NL↔FR | 0.827 |
| PT↔ES | 0.707 (ibéro-romanes) |
| PT↔IT | 0.741 (romanes) |
| PT↔FR | 0.741 (romanes) |

## Prochaines étapes

- Explorer d'autres langues latines : suédois (sv), danois (da), roumain (ro)
- Ajouter un 3ᵉ texte portugais pour renforcer la couverture (Dom Casmurro est
  court avec 16K mots et ne couvre que 21 atomes individuellement)
- Explorer le coréen (ko) — l'infra CJK est déjà en place
- Stemmer morphologique pour les langues à haute flexion (ru, fi, pt)
