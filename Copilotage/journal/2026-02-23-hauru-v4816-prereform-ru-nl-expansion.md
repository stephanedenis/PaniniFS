## Contexte

Continuation du travail de couverture multilingue après v4.8.14 (percée ja/ru/nl)
et v4.8.15 (expansion européenne ciblée par un autre chat). Deux langues restent
bien en dessous des 50% : **russe (40.4%)** et **néerlandais (38.8%)**.

Diagnostic approfondi des fichiers faibles :
- **pg30774 (ru, 13.6%)** : Texte sur les voyageurs étrangers en Moscovie (Olearius,
  Herberstein, Korb) — rédigé en **orthographe pré-réforme russe de 1918** ! `въ`
  au lieu de `в`, `ѣ` au lieu de `е`, `і` au lieu de `и`. Le stemmer Snowball
  ne peut PAS traiter ces formes.
- **pg14741 (ru, 21.8%)** : Odes spirituelles de Derjavine — vocabulaire
  religieux/poétique massif + lacune énorme de stop words (`ты` 195×, `да` 61×...)
- **pg17525/pg18066 (nl, 37.9-41.7%)** : Orthographe néerlandaise pré-1947 (`zoo`,
  `groote`, `schoone`) + lacune massive de vocabulaire courant

## Décisions clés

### 1. Normaliseur d'orthographe pré-réforme russe

**Constat** : 35.3% des mots de pg30774 contiennent `ъ`, 11.8% `ѣ`, 11.7% `і`.
Le stemmer Snowball laisse `въ` → `въ` (au lieu de `в`).

**Décision** : Créer `normalize_prereform_ru(word)` — analogue à OpenCC pour le
chinois. Transformations :
- Suppression du `ъ` final (signe dur après consonnes)
- `ѣ` → `е` (yat), `і` → `и` (i décimal), `ѳ` → `ф` (fita)
- `-аго` → `-ого` (désinence génitive adjective pré-réforme)

**Impact** : Appliqué dans `get_content_words()` (avant filtrage stop words) ET
dans `_is_covered_enhanced()` (avant matching). Permet au stemmer de fonctionner
normalement sur les textes pré-réforme.

### 2. Expansion massive du vocabulaire russe (~450 mots-clés, ~250 stop words)

**Constat** : Aucun mot religieux/poétique russe couvert (`бог`, `дух`, `душа`,
`творец`, `ангел`, `грех` — tous ✗).

**Décision** : Ajout de mots-clés couvrant :
- Céleste/Nature/Eau/Éléments (60+ mots)
- Corps/Artefacts/Instruments/Créatures/Flore (90+ mots)
- Religieux/Spirituel/Émotions/Cognition (100+ mots)
- Qualités divines/morales/intensité (50+ mots)
- Abstraits temporels/structurels/sociaux (70+ mots)
- Agent divin + formes vocatives/obliques (30+ mots)
- Vocabulaire historique pg30774 (50+ mots)

Stop words massifs : pronoms (ты/мы/вы + déclinaisons), déictiques (сей/тот/этот),
relatifs (который+), prépositions (без/пред/под/над/меж/сквозь), particules
archaïques (яко/бысть/сый/паче), abréviations bibliques (ст/гл/матф/иоан).

### 3. Expansion massive du vocabulaire néerlandais (~350 mots-clés, ~180 stop words)

**Constat** : Verbes irréguliers au passé non couverts (kwam/sprak/liep/stond...),
le stemmer ne les réduit PAS à la racine (kwamen→kwaam ≠ kom).

**Décision** : Ajout des formes infinitif + prétérit + participe passé pour
20+ verbes irréguliers fréquents. Vocabulaire maritime/exploration (Columbus),
géographie, personnes, objets, qualités avec formes anciennes (groote, schoone).

Stop words : gij/ge, af/mee/heen/terug/voort, adverbes composés (waarvan/waardoor),
formes anciennes (zoo/zooals/dezer/dier), conjonctions.

### 4. Formes orthographiques néerlandaises pré-1947

**Constat** : `groote` (134×), `schoone` (36×), `zoo` (210×) — l'orthographe
néerlandaise pré-réforme de 1947 utilise des doubles voyelles là où le néerlandais
moderne n'en a pas.

**Décision** : Table de correspondance OLD_DUTCH_SPELLING (48 paires old→modern),
les deux formes enregistrées comme mots-clés.

## Fichiers modifiés

1. **`vocabulary_expansion_v4816.py`** (NOUVEAU, ~550 lignes)
   - `normalize_prereform_ru(word)` — normaliseur orthographique
   - `KEYWORDS_V4816_RU` — ~450 mots-clés russes (20+ catégories atomiques)
   - `KEYWORDS_V4816_NL` — ~350 mots-clés néerlandais (15+ catégories)
   - `STOP_WORDS_V4816_RU` — ~250 stop words russes
   - `STOP_WORDS_V4816_NL` — ~180 stop words néerlandais
   - `PROPER_NOUNS_V4816_RU/NL` — noms propres des corpus
   - `OLD_DUTCH_SPELLING` — 48 paires ancien→moderne

2. **`reconstruction_fidelity.py`** (modifié, +40 lignes)
   - Import block v4.8.16 (lignes ~306-327)
   - `_extend_global_with_v4816()` — enregistrement mots-clés/noms propres/formes
   - `get_stop_words()` — chaînage stop words v4.8.16
   - `_is_covered_enhanced()` — normalisation pré-réforme avant matching
   - `get_content_words()` — normalisation pré-réforme avant filtrage stop words

## Tests effectués

### Audit complet 62 fichiers / 12 langues

| Langue | Avant (v4.8.14) | Après (v4.8.16) | Δ |
|--------|-----------------|-----------------|---|
| **ru** | **40.4%** | **56.3%** | **+15.9pp** |
| **nl** | **38.8%** | **55.9%** | **+17.1pp** |
| de | 81.2% | 81.4% | +0.2pp |
| en | 81.3% | 81.4% | +0.1pp |
| fr | 79.4% | 79.4% | — |
| es | 68.6% | 68.7% | +0.1pp |
| it | 71.1% | 71.1% | — |
| fi | 71.7% | 71.7% | — |
| eo | 73.2% | 73.2% | — |
| ja | 74.1% | 74.1% | — |
| zh | 76.6% | 76.6% | — |
| sa | 10.7% | 10.7% | — |
| **Global** | **76.3%** | **76.8%** | **+0.5pp** |

### Détails fichiers cibles

| Fichier | Contenu | Avant | Après | Δ |
|---------|---------|-------|-------|---|
| pg14741 (ru) | Derjavine, odes spirituelles | 21.8% | 48.9% | **+27.1pp** |
| pg30774 (ru) | Voyageurs en Moscovie (pré-réforme) | 13.6% | 41.8% | **+28.2pp** |
| pg16527 (ru) | Texte commercial | 61.5% | 64.4% | +2.9pp |
| pg17525 (nl) | Buysse, prose flamande | 41.7% | 52.5% | +10.8pp |
| pg18066 (nl) | Columbus, exploration | 37.9% | 56.8% | **+18.9pp** |

### Vérification non-régression
Aucune régression sur les 12 langues. Toutes les langues européennes stables
ou en légère amélioration (spillover).

## Prochaines étapes

1. **ru reste à 56.3%** — pg30774 (41.8%) reste le plus faible. Le vocabulaire
   historique/culturel spécifique est très large. Possible d'atteindre 60%+ avec
   une troisième vague ciblée.
2. **nl à 55.9%** — pg17525 (52.5%) pourrait monter avec plus de verbes fréquents
   et vocabulaire littéraire flamand.
3. **Global 76.8%** — la cible de 80% nécessiterait des gains sur les langues
   de volume (en, fr, de, zh) ou des percées massives sur ru/nl/es.
4. **sa (10.7%)** — le sanskrit translittéré (IAST) reste un problème structurel
   non résolu (nécessiterait un mapping IAST→atomes dédié).
