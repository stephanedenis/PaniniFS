# Normes ISO & Unicode pour les langues — Référence Panini-FS

> **Audience** : Agents Copilot et développeurs travaillant sur le pipeline multilingue.  
> **Objectif** : Que le système connaisse les normes, sache ce qu'il utilise, ce qu'il n'utilise pas, et pourquoi.  
> **Dernière mise à jour** : 2026-02-21

---

## Table des matières

1. [Vue d'ensemble des normes](#1-vue-densemble-des-normes)
2. [ISO 639 — Codes de langues](#2-iso-639--codes-de-langues)
3. [ISO 15924 — Codes d'écritures](#3-iso-15924--codes-décritures)
4. [BCP 47 — Étiquettes de langues IETF](#4-bcp-47--étiquettes-de-langues-ietf)
5. [Unicode — Normes techniques applicables](#5-unicode--normes-techniques-applicables)
6. [État actuel de Panini-FS](#6-état-actuel-de-panini-fs)
7. [Analyse des écarts (Gap Analysis)](#7-analyse-des-écarts-gap-analysis)
8. [Recommandations](#8-recommandations)
9. [Tables de référence](#9-tables-de-référence)

---

## 1. Vue d'ensemble des normes

Le traitement multilingue repose sur un empilement de normes complémentaires :

```
┌─────────────────────────────────────────────────────┐
│  BCP 47 (RFC 5646)                                  │
│  Étiquette complète : fr-Latn-CA-1990               │
│  ┌──────────┬──────────┬──────────┬───────────────┐  │
│  │ ISO 639  │ ISO 15924│ ISO 3166 │  Variantes    │  │
│  │ Langue   │ Écriture │ Région   │  Extensions   │  │
│  │ fr       │ Latn     │ CA       │  1990         │  │
│  └──────────┴──────────┴──────────┴───────────────┘  │
└─────────────────────────────────────────────────────┘
        ▼                   ▼
   Unicode CLDR        Unicode UCD
   (données locales)   (propriétés caractères)
```

| Norme | Portée | Granularité | Entrées |
|-------|--------|-------------|---------|
| **ISO 639-1** | Langues majeures | 2 lettres (alpha-2) | ~184 codes |
| **ISO 639-2** | Langues + collections | 3 lettres (alpha-3) | ~487 codes |
| **ISO 639-3** | Toutes les langues connues | 3 lettres (alpha-3) | ~7 900+ codes |
| **ISO 639-5** | Familles de langues | 3 lettres (alpha-3) | ~115 codes |
| **ISO 15924** | Systèmes d'écriture | 4 lettres (Xxxx) | ~200 codes |
| **BCP 47** | Étiquettes composites | Variable | ∞ (combinatoire) |
| **Unicode CLDR** | Données locales | Structurées (LDML/XML) | ~700+ locales |

---

## 2. ISO 639 — Codes de langues

### 2.1 ISO 639-1 (alpha-2)

- **Usage** : Le standard que Panini-FS utilise actuellement (`en`, `fr`, `de`, …).
- **Couverture** : ~184 langues majeures (celles ayant une terminologie spécialisée).
- **Limite** : Ne couvre pas les langues minoritaires, anciennes ou construites rares.
- **Autorité** : Infoterm (Vienne).

**Suffisant pour Panini ?** ✅ Oui pour les 14 langues actuelles.
Tous nos codes (`en`, `fr`, `de`, `it`, `es`, `eo`, `fi`, `pt`, `nl`, `zh`, `ja`, `ru`, `hi`, `sa`) ont un code ISO 639-1.

### 2.2 ISO 639-2 (alpha-3, terminologique + bibliographique)

- **Couverture** : ~487 codes, incluant des **collections** (ex. `ber` = langues berbères).
- **Particularité** : Deux variantes pour certaines langues :
  - Bibliographique (B) : `fre` pour français, `ger` pour allemand
  - Terminologique (T) : `fra` pour français, `deu` pour allemand
- **Convention** : Toujours utiliser la forme **terminologique** (T).

**Pertinence Panini** : Utile pour les métadonnées Gutenberg (le Project Gutenberg utilise ISO 639-2).

### 2.3 ISO 639-3 (exhaustif)

- **Couverture** : ~7 900+ codes pour **toutes les langues connues** (vivantes, éteintes, anciennes, construites).
- **Autorité** : SIL International (Ethnologue).
- **Distingue** : Les langues individuelles uniquement (pas les collections → voir 639-5).
- **Exemples notables** :
  - `san` = sanskrit (pas de code 639-1 `sa` … en fait si, `sa` existe en 639-1)
  - `grc` = grec ancien (pas de code 639-1)
  - `ang` = vieil anglais (pas de code 639-1)
  - `pal` = pali (pas de code 639-1, seulement `pi`)

**Pertinence Panini** : Nécessaire dès qu'on traiterait des textes en langues anciennes
(ex. textes pali, vieux norrois, akkadien) qui n'ont pas de code 639-1.

### 2.4 ISO 639-5 (familles)

- **Couverture** : ~115 codes pour les **familles et groupes** de langues.
- **Exemples** : `ine` = langues indo-européennes, `sem` = langues sémitiques.
- **Usage** : Classification typologique, pas d'identification de textes.

**Pertinence Panini** : Utile pour les métadonnées d'universalité (ex. : un atome est-il présent
dans les familles `ine`, `sit`, `jpx`, `dra` ?)

### 2.5 Tableau de correspondance pour les 14 langues Panini

| Langue | ISO 639-1 | ISO 639-2/T | ISO 639-3 | Famille (639-5) |
|--------|-----------|-------------|-----------|-----------------|
| Anglais | `en` | `eng` | `eng` | `ine` (Indo-eur.) |
| Français | `fr` | `fra` | `fra` | `ine` |
| Allemand | `de` | `deu` | `deu` | `ine` |
| Italien | `it` | `ita` | `ita` | `ine` |
| Espagnol | `es` | `spa` | `spa` | `ine` |
| Espéranto | `eo` | `epo` | `epo` | `art` (Construite) |
| Finnois | `fi` | `fin` | `fin` | `urj` (Ouralienne) |
| Portugais | `pt` | `por` | `por` | `ine` |
| Néerlandais | `nl` | `nld` | `nld` | `ine` |
| Chinois | `zh` | `zho` | `zho`† | `sit` (Sino-tib.) |
| Japonais | `ja` | `jpn` | `jpn` | `jpx` (Japonique) |
| Russe | `ru` | `rus` | `rus` | `ine` |
| Hindi | `hi` | `hin` | `hin` | `ine` |
| Sanskrit | `sa` | `san` | `san` | `ine` |

† `zho` est un macrolangage en 639-3. Les langues individuelles sont `cmn` (mandarin),
`yue` (cantonais), `wuu` (wu), etc. Panini traite `zh` comme mandarin par défaut.

---

## 3. ISO 15924 — Codes d'écritures

### 3.1 Présentation

- **Format** : 4 lettres, première majuscule (ex. `Latn`, `Cyrl`, `Deva`).
- **Couverture** : ~200 systèmes d'écriture (vivants, historiques, non déchiffrés).
- **Autorité** : Unicode Consortium (Registration Authority).
- **Lien Unicode** : Chaque script ISO 15924 correspond à un `Script` Unicode dans l'UCD.

### 3.2 Scripts utilisés par Panini-FS

| Script ISO 15924 | Nom | Langues Panini | Détection actuelle | Unicode Property |
|-------------------|-----|----------------|--------------------|--------------------|
| `Latn` | Latin | en, fr, de, it, es, eo, fi, pt, nl | ✅ regex `[a-zA-ZÀ-ÿ…]` | `Script=Latin` |
| `Cyrl` | Cyrillique | ru | ✅ regex `[\u0400-\u04FF]` | `Script=Cyrillic` |
| `Hani` | Han (CJK) | zh | ✅ regex `[\u4E00-\u9FFF]` | `Script=Han` |
| `Hira` | Hiragana | ja | ✅ regex `[\u3040-\u309F]` | `Script=Hiragana` |
| `Kana` | Katakana | ja | ✅ regex `[\u30A0-\u30FF]` | `Script=Katakana` |
| `Deva` | Devanagari | hi, sa | ✅ regex `[\u0900-\u097F]` | `Script=Devanagari` |
| `Arab` | Arabe | (ar — tests seul.) | ✅ regex `[\u0600-\u06FF]` | `Script=Arabic` |
| `Grek` | Grec | (el — détect. seul.) | ✅ regex `[\u0370-\u03FF]` | `Script=Greek` |
| `Hebr` | Hébreu | (he — détect. seul.) | ✅ regex `[\u0590-\u05FF]` | `Script=Hebrew` |

### 3.3 Scripts non gérés mais pertinents

| Script | Code | Langues potentielles | Priorité |
|--------|------|----------------------|----------|
| `Hang` | Hangul | Coréen (`ko`) | Moyenne — CJK déjà présent |
| `Thai` | Thaï | Thaï (`th`) | Basse |
| `Beng` | Bengali | Bengali (`bn`) | Basse |
| `Geor` | Géorgien | Géorgien (`ka`) | Basse |
| `Armn` | Arménien | Arménien (`hy`) | Basse |
| `Tibt` | Tibétain | Tibétain (`bo`) | Basse — intérêt sanskrit |
| `Ethi` | Éthiopien | Amharique (`am`), Tigrinya | Basse |

### 3.4 Problème identifié : mapping 1:1 script→langue

Le code actuel fait `Deva → hi`, ignorant que le devanagari est aussi utilisé pour :
- Sanskrit (`sa`), Marathi (`mr`), Népalais (`ne`), Bodo (`brx`), Dogri (`doi`), …

De même, `Hani → zh` ignore le coréen (`ko`) et le japonais kanji.

**Solution recommandée** : Le script donne un **ensemble candidat** de langues,
pas une langue unique. La désambiguïsation doit utiliser les n-grammes ou un signal externe.

---

## 4. BCP 47 — Étiquettes de langues IETF

### 4.1 Structure (RFC 5646)

```
language[-extlang][-script][-region][-variant][-extension][-privateuse]
```

| Composant | Registre | Exemples | Obligatoire |
|-----------|----------|----------|-------------|
| `language` | ISO 639-1 ou 639-3 | `fr`, `zh`, `cmn` | ✅ Oui |
| `extlang` | ISO 639-3 (pour macrolangues) | `zh-cmn`, `zh-yue` | Non |
| `script` | ISO 15924 | `Latn`, `Hans`, `Hant` | Non (sauf ambiguïté) |
| `region` | ISO 3166-1 alpha-2 ou UN M.49 | `FR`, `CA`, `419` | Non |
| `variant` | IANA registry | `1901` (ortho. allemande), `fonipa` | Non |
| `extension` | Registré IANA | `u-ca-buddhist` (CLDR) | Non |
| `privateuse` | `x-…` | `x-panini`, `x-atom` | Non |

### 4.2 Exemples pertinents pour Panini

| Étiquette | Signification | Cas d'usage Panini |
|-----------|---------------|--------------------|
| `zh-Hans` | Chinois simplifié | Gutenberg textes PRC |
| `zh-Hant` | Chinois traditionnel | Gutenberg textes Taiwan/HK |
| `pt-BR` | Portugais brésilien | Distinction lexicale |
| `pt-PT` | Portugais européen | Distinction lexicale |
| `de-1901` | Allemand orthographe 1901 | Gutenberg textes anciens |
| `de-1996` | Allemand réforme 1996 | Gutenberg textes modernes |
| `sa-Deva` | Sanskrit en devanagari | Distinction avec ITRANS |
| `sa-Latn` | Sanskrit romanisé (IAST/ITRANS) | Gutenberg pg9000 |
| `fr-1694` | Français classique (avant 1835) | Candide, textes 18e |
| `eo-Latn` | Espéranto script latin | (implicite) |
| `en-GB` | Anglais britannique | Gutenberg UK sources |
| `en-US` | Anglais américain | Gutenberg US sources |

### 4.3 Usage actuel dans Panini

**Panini n'utilise PAS BCP 47.** Seuls les codes ISO 639-1 à 2 caractères sont utilisés.

**Conséquences** :
- Impossible de distinguer `zh-Hans` / `zh-Hant`
- Impossible de distinguer `pt-BR` / `pt-PT`
- Impossible de marquer un texte comme `sa-Latn` (Sanskrit romanisé)
- Impossible de distinguer l'orthographe allemande pré/post-réforme

### 4.4 Stratégie recommandée

**Court terme** : Rester en ISO 639-1 comme code primaire, mais **stocker le tag BCP 47
complet comme métadonnée optionnelle** dans le champ `lang_code VARCHAR(10)` de la DB
(les schémas le permettent déjà, les colonnes font VARCHAR(5) à VARCHAR(10)).

**Moyen terme** : Enrichir `LANGUAGE_PROFILES` avec un champ `bcp47_variants` listant
les variantes connues et leurs impacts sur le pipeline (orthographe, tokenisation).

---

## 5. Unicode — Normes techniques applicables

### 5.1 Unicode Standard (actuellement v16.0)

Le standard Unicode définit un répertoire de **154 998 caractères** couvrant
**168 scripts** (version 16.0, sept. 2024). Chaque caractère possède des propriétés
dans l'UCD (Unicode Character Database) :

| Propriété | Usage Panini | Exploité ? |
|-----------|-------------|------------|
| `General_Category` (Ll, Lu, Lo, Nd…) | Classification caractères | ⚠️ Indirect (regex) |
| `Script` (Latin, Cyrillic, Han…) | Détection d'écriture | ✅ Via regex ranges |
| `Block` (Basic Latin, CJK Unified…) | Ranges de caractères | ✅ Via regex ranges |
| `Bidi_Class` (L, R, AL, AN…) | Direction du texte | ❌ Non géré |
| `Canonical_Combining_Class` | Normalisation | ❌ Non explicite |
| `Decomposition_Mapping` | Normalisation NFC/NFD | ⚠️ Non vérifié |

### 5.2 UAX #15 — Normalisation Unicode (NFC, NFD, NFKC, NFKD)

Les 4 formes de normalisation :

| Forme | Nom complet | Description | Usage recommandé |
|-------|-------------|-------------|------------------|
| **NFC** | Canonical Decomposition + Composition | Forme composée canonique | ✅ **Stockage, échange** |
| **NFD** | Canonical Decomposition | Forme décomposée canonique | Traitement diacritiques |
| **NFKC** | Compatibility Decomposition + Composition | Unification compatibilité | Recherche, indexation |
| **NFKD** | Compatibility Decomposition | Décomposition totale | Analyse approfondie |

**État Panini** : ⚠️ **Aucune normalisation Unicode explicite** n'est appliquée en entrée du pipeline.

**Risques** :
- Un `é` (U+00E9, NFC) et `é` (U+0065 + U+0301, NFD) sont visuellement identiques mais
  ne matchent pas par comparaison de chaînes → un keyword `été` pourrait rater le match.
- Les textes Gutenberg mélangent potentiellement les formes.
- Les keywords indics (devanagari) sont particulièrement sensibles (voyelles dépendantes).

**Recommandation** : Appliquer `unicodedata.normalize('NFC', text)` en entrée de
`detect_language()` et `process_text()`.

### 5.3 UAX #29 — Segmentation de texte

Unicode définit des algorithmes par défaut pour :

| Frontière | Description | Impact Panini |
|-----------|-------------|---------------|
| **Grapheme Cluster** | Unité visuelle minimale | Important pour devanagari, hangul, emoji |
| **Word Boundary** | Délimitation de mots | ⚠️ Panini utilise `\b` regex (insuffisant pour CJK, thaï) |
| **Sentence Boundary** | Délimitation de phrases | Panini utilise split par ponctuation |
| **Line Break** | Coupure de ligne | Non pertinent |

**État Panini** :
- Pour le CJK, un tokenizer custom greedy est utilisé (correct).
- Pour le latin/cyrillique, `\b` regex est utilisé (correct pour ces scripts).
- Pour le devanagari, pas de tokenizer spécifique (⚠️ risque).
- Pas de gestion des Grapheme Clusters composés (ex. 👨‍👩‍👧 = 5 codepoints).

### 5.4 Unicode CLDR (Common Locale Data Repository)

**Version actuelle** : CLDR 48.1 (janvier 2026).

Le CLDR fournit pour chaque locale :
- Noms de langues localisés
- Formats de nombres, dates, monnaies
- Règles de pluriel (cardinal, ordinal)
- Règles de collation (tri alphabétique)
- Données de segmentation de mots spécifiques par locale
- Données de translittération

**Pertinence Panini** :
- Les **règles de pluriel** sont utiles pour la morphologie (stratégie de stemming).
- La **translittération** CLDR pourrait remplacer le mapping ad-hoc `sa-Deva ↔ ITRANS`.
- Les **noms de langues** localisés pourraient enrichir les `LANGUAGE_PROFILES`.

---

## 6. État actuel de Panini-FS

### 6.1 Ce que Panini fait bien ✅

| Aspect | Détail |
|--------|--------|
| **14 langues** avec profils complets | en, fr, de, it, es, eo, fi, pt, nl, zh, ja, ru, hi, sa |
| **Codes ISO 639-1 cohérents** | Utilisés partout, sans mélange 639-1/639-2 |
| **10 scripts détectés** | Latin, Cyrillique, CJK, Hiragana, Katakana, Devanagari, Arabe, Grec, Hébreu |
| **Détection multi-tier** | langdetect → trigrams custom → fallback par script |
| **34 atomes × 14 langues** | ~476 jeux de mots-clés, couverture >91% |
| **Profils typologiques riches** | word_order, morphologie, registres, marqueurs discursifs |
| **5 familles linguistiques** | Indo-européenne, ouralienne, sino-tibétaine, japonique, construite |
| **3 types d'écriture** | Alphabétique, syllabique (hiragana), logographique (CJK) |

### 6.2 Ce que Panini ne fait pas encore ⚠️

| Aspect | Détail | Norme concernée |
|--------|--------|-----------------|
| Pas de normalisation NFC en entrée | Risque de mismatch de mots-clés | UAX #15 |
| Pas de BCP 47 | Pas de variantes régionales/orthographiques | RFC 5646 |
| Mapping script→langue 1:1 | Devanagari→hindi seulement | ISO 15924 |
| Pas de codes ISO 639-3 | Impossible d'encoder grec ancien, pali, etc. | ISO 639-3 |
| Pas de gestion BiDi | Textes arabes/hébreux = détection seule | Unicode Bidi |
| Pas de Grapheme Clusters | Problèmes potentiels devanagari | UAX #29 |
| 4 langues « fantômes » | ar, sw, el, he dans les tests mais sans profils | — |

---

## 7. Analyse des écarts (Gap Analysis)

### 7.1 Écarts critiques (impact fonctionnel)

| # | Écart | Impact | Effort | Priorité |
|---|-------|--------|--------|----------|
| **G1** | Pas de normalisation NFC | Keywords en NFD ne matchent pas leur forme NFC → faux négatifs silencieux | Faible (2 lignes) | 🔴 Haute |
| **G2** | Mapping script→langue 1:1 | Sanskrit en devanagari détecté comme hindi | Moyen | 🟡 Moyenne |
| **G3** | Pas de distinction zh-Hans/zh-Hant | Caractères traditionnels potentiellement mal traités | Moyen | 🟡 Moyenne |

### 7.2 Écarts documentaires (impact connaissance)

| # | Écart | Impact | Effort | Priorité |
|---|-------|--------|--------|----------|
| **G4** | Aucune doc des langues supportées | Nouveaux agents/développeurs ne savent pas ce qui est couvert | Faible | 🔴 Haute |
| **G5** | Pas de correspondance ISO 639-2 pour Gutenberg | Métadonnées Gutenberg en 639-2 → conversion implicite | Faible | 🟡 Moyenne |
| **G6** | Pas de mention des familles 639-5 | Analyses d'universalité sans contexte phylogénétique | Faible | 🟢 Basse |

### 7.3 Écarts architecturaux (impact futur)

| # | Écart | Impact | Effort | Priorité |
|---|-------|--------|--------|----------|
| **G7** | Schéma DB VARCHAR(5) pour lang_code | Insuffisant pour BCP 47 (`zh-Hant-TW` = 10 chars) | Moyen | 🟡 Moyenne |
| **G8** | Pas de table `scripts` en DB | Relation langue-script non normalisée | Moyen | 🟢 Basse |
| **G9** | Fallback mapping mort (`pt→es`, `nl→de`) | Code confus, dead code | Faible | 🟢 Basse |
| **G10** | 4 langues test sans profil (ar, sw, el, he) | Tests qui réussissent en fallback anglais = faux positifs | Moyen | 🟡 Moyenne |

---

## 8. Recommandations

### 8.1 Actions immédiates (sprint actuel)

1. **Ajouter `unicodedata.normalize('NFC', text)` en entrée du pipeline**
   - Dans `detect_language()` de `semantic_engine.py`
   - Dans `process_text()` du moteur d'analyse
   - Coût : 2 lignes, impact : élimination risque de mismatch

2. **Ce document** sert de référence normative (G4 résolu).

### 8.2 Actions court terme (prochaines versions)

3. **Enrichir `LANGUAGE_PROFILES` avec métadonnées ISO** :
   ```python
   "fr": {
       "iso639_1": "fr",
       "iso639_2t": "fra",
       "iso639_3": "fra",
       "iso15924": ["Latn"],
       "bcp47_canonical": "fr",
       "bcp47_variants": ["fr-FR", "fr-CA", "fr-BE", "fr-1694"],
       "family_639_5": "ine",
       "unicode_scripts": ["Latin"],
       ...
   }
   ```

4. **Transformer le mapping script→langue en 1:N** :
   ```python
   SCRIPT_TO_LANGUAGES = {
       "Deva": ["hi", "sa", "mr", "ne"],  # au lieu de "hi" seul
       "Hani": ["zh", "ja"],               # au lieu de "zh" seul
       "Cyrl": ["ru", "uk", "bg", "sr"],   # au lieu de "ru" seul
   }
   ```

5. **Retirer le dead code** des fallback mappings (`pt→es`, `nl→de`).

### 8.3 Actions moyen terme (expansion linguistique)

6. **Stocker le tag BCP 47 complet** dans les tables Dolt (élargir à `VARCHAR(20)`).

7. **Ajouter le coréen** (`ko`, `Hang`) — le script Hangul est algorithmiquement décomposable
   (Jamo), ce qui s'aligne bien avec l'approche atomique de Panini.

8. **Utiliser ISO 639-3 pour les langues anciennes** rencontrées dans le corpus Gutenberg
   (grec ancien `grc`, latin `lat`/`la`, vieil anglais `ang`, etc.).

### 8.4 Actions long terme (vision)

9. **Intégrer les données CLDR** pour les règles de pluriel et de collation.

10. **Implémenter UAX #29** pour la segmentation de mots en devanagari et thaï.

11. **Produire une matrice de couverture atomique par famille linguistique (639-5)**
    pour mesurer l'universalité réelle des 34 atomes sémantiques.

---

## 9. Tables de référence

### 9.1 Couverture linguistique mondiale (contexte)

| Métrique | Valeur |
|----------|--------|
| Langues vivantes connues (Ethnologue 2025) | ~7 168 |
| Langues avec code ISO 639-1 | ~184 |
| Langues avec code ISO 639-3 | ~7 900+ |
| Scripts dans Unicode 16.0 | 168 |
| Scripts dans ISO 15924 | ~200 |
| **Langues supportées par Panini** | **14** (0.2% des langues vivantes) |
| **Scripts supportés par Panini** | **9** (5.4% des scripts Unicode) |
| **Locuteurs couverts (estimation)** | **~4.8 milliards** (~60% pop. mondiale) |

> **Note** : Bien que Panini ne couvre que 14/7168 langues (0.2%), ces 14 langues
> représentent ~60% des locuteurs natifs mondiaux. L'ajout du coréen (`ko`),
> de l'arabe (`ar`), du bengali (`bn`), et du turc (`tr`) porterait la couverture
> à ~75% des locuteurs.

### 9.2 Mapping Panini scripts → Unicode Property Values

| Regex Panini actuel | Unicode Script Property | ISO 15924 | Remarque |
|---------------------|------------------------|-----------|----------|
| `[a-zA-ZÀ-ÿ]` | `\p{Script=Latin}` | `Latn` | ⚠️ Le regex rate les extensions Latin-B/C |
| `[\u0400-\u04FF]` | `\p{Script=Cyrillic}` | `Cyrl` | ✅ Correct pour le russe |
| `[\u4E00-\u9FFF]` | `\p{Script=Han}` | `Hani` | ⚠️ Rate Extension A/B (rares mais existants) |
| `[\u3040-\u309F]` | `\p{Script=Hiragana}` | `Hira` | ✅ Correct |
| `[\u30A0-\u30FF]` | `\p{Script=Katakana}` | `Kana` | ✅ Correct |
| `[\u0900-\u097F]` | `\p{Script=Devanagari}` | `Deva` | ✅ Correct |
| `[\u0600-\u06FF]` | `\p{Script=Arabic}` | `Arab` | ⚠️ Rate Arabic Supplement/Extended |
| `[\u0370-\u03FF]` | `\p{Script=Greek}` | `Grek` | ✅ Correct pour le grec moderne |
| `[\u0590-\u05FF]` | `\p{Script=Hebrew}` | `Hebr` | ✅ Correct |

**Recommandation** : Migrer vers `\p{Script=…}` (Python `regex` module) pour une couverture
complète des blocs Unicode étendus, au lieu de ranges codés en dur.

### 9.3 Langues Gutenberg avec codes ISO 639-2

Le Project Gutenberg utilise ISO 639-2 dans ses métadonnées RDF. Table de conversion :

| Gutenberg (639-2) | Panini (639-1) | Notes |
|--------------------|----------------|-------|
| `eng` | `en` | |
| `fre` / `fra` | `fr` | Gutenberg utilise la forme B (`fre`) |
| `ger` / `deu` | `de` | Gutenberg utilise la forme B (`ger`) |
| `ita` | `it` | |
| `spa` | `es` | |
| `epo` | `eo` | |
| `fin` | `fi` | |
| `por` | `pt` | |
| `dut` / `nld` | `nl` | Gutenberg utilise la forme B (`dut`) |
| `chi` / `zho` | `zh` | Gutenberg utilise la forme B (`chi`) |
| `jpn` | `ja` | |
| `rus` | `ru` | |
| `hin` | `hi` | |
| `san` | `sa` | |
| `grc` | — | Grec ancien : pas de code 639-1, besoin 639-3 |
| `lat` | `la` | Latin : a un code 639-1 mais pas de profil Panini |

---

## Annexe A : Glossaire des normes

| Sigle | Nom complet | Organisme |
|-------|-------------|-----------|
| ISO 639 | Codes for the representation of names of languages | ISO/TC 37 |
| ISO 15924 | Codes for the representation of names of scripts | Unicode Consortium (RA) |
| ISO 3166 | Codes for the representation of names of countries | ISO/TC 46 |
| BCP 47 | Best Current Practice 47 | IETF (RFC 5646 + RFC 4647) |
| CLDR | Common Locale Data Repository | Unicode Consortium |
| UCD | Unicode Character Database | Unicode Consortium |
| UAX | Unicode Standard Annex | Unicode Consortium |
| IANA | Internet Assigned Numbers Authority | IANA (Language Subtag Registry) |
| SIL | Summer Institute of Linguistics | SIL International (RA pour 639-3) |
| LDML | Locale Data Markup Language | Unicode (UTS #35) |

## Annexe B : Références

- [ISO 639-1/2 — Library of Congress](https://www.loc.gov/standards/iso639-2/)
- [ISO 639-3 — SIL International](https://iso639-3.sil.org/)
- [ISO 15924 — Unicode](https://www.unicode.org/iso15924/)
- [BCP 47 / RFC 5646](https://tools.ietf.org/html/rfc5646)
- [IANA Language Subtag Registry](https://www.iana.org/assignments/language-subtag-registry/)
- [Unicode CLDR](https://cldr.unicode.org/)
- [UAX #15 — Normalization](https://www.unicode.org/reports/tr15/)
- [UAX #29 — Text Segmentation](https://www.unicode.org/reports/tr29/)
- [Ethnologue — Languages of the World](https://www.ethnologue.com/)
