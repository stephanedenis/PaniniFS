# 2026-02-19 — v2.6 : Atomes QUAL (BON, GRAND, VRAI, INTENSE, ANCIEN)

**Host** : hauru (Intel Xeon E5-2650, 8c/16t, 62GB RAM)
**Agent** : Copilot Claude Opus 4.6
**Commit** : à venir (post-session)

## Contexte

L'ontologie à 4 catégories (ENT, PROC, QUAL, ABS) avait une lacune :
**QUAL = 0 atomes**. Les concepts évaluatifs (BEAU, VÉRITÉ, SATISFACTION,
JUSTICE, MORAL…) s'appuyaient sur des contournements via PROC/ABS (SEEKING,
EXISTENCE, PERCEPTION). La roadmap NA-004 prévoyait v2.6 pour combler ce
trou.

Objectifs :
- ≥5 atomes QUAL primitifs, cross-linguistiquement universels
- ≥120 concepts total (était 105 en v2.5)
- Les 4 catégories ontologiques couvertes

## Décisions clés

### D1 : 5 atomes QUAL identifiés

| Atome | NSM prime | Dhātu | Dimension |
|---|---|---|---|
| **BON** | GOOD | √śubh (bon augure) | QUALITÉ: 1.0 |
| **GRAND** | BIG | √bṛh (grandir) | QUALITÉ: 0.8, ENTITÉ: 0.2 |
| **VRAI** | TRUE | √sat (être vrai) | QUALITÉ: 0.7, MODALITÉ: 0.3 |
| **INTENSE** | VERY, MUCH | √tīv (aigu) | QUALITÉ: 0.9, PROCESSUS: 0.1 |
| **ANCIEN** | BEFORE, A LONG TIME | √pur (avant) | QUALITÉ: 0.6, PROCESSUS: 0.2, ENTITÉ: 0.2 |

- **Constat** : Les 5 sont des primes NSM (Wierzbicka), cross-linguistiques,
  irréductibles, et productifs en composition.
- **Décision** : BON pour la valence (remplace SEEKING/EXISTENCE dans
  les concepts évaluatifs), GRAND pour la magnitude, VRAI pour la vérité,
  INTENSE pour le degré, ANCIEN pour la temporalité/âge.
- **Impact** : Couverture QUAL de 0 à 5 atomes, 4/4 catégories actives.

### D2 : 9 concepts existants améliorés

| Concept | Avant (v2.5) | Après (v2.6) |
|---|---|---|
| BEAU | PERCEPTION+SEEKING+CREATION | **BON**+PERCEPTION+CREATION |
| BEAUTÉ | PERCEPTION+SEEKING+INVARIANCE | **BON**+PERCEPTION+INVARIANCE |
| VÉRITÉ | COGNITION+EXISTENCE+COMMUNICATION | **VRAI**+COGNITION+COMMUNICATION |
| SATISFACTION | SEEKING+EXISTENCE | **BON**+SEEKING |
| MORAL | DESTRUCTION+EXISTENCE+COGNITION+COMM | **BON**+COGNITION+COMMUNICATION |
| JUSTICE | COGNITION+DOMINATION+EXISTENCE+SEEKING | **BON**+**VRAI**+DOMINATION |
| LÉGENDE | COMMUNICATION+COGNITION+RÉCURRENCE | **ANCIEN**+COMMUNICATION+RÉCURRENCE |
| ÉTERNITÉ | EXISTENCE+INVARIANCE | **ANCIEN**+EXISTENCE+INVARIANCE |
| EUPHORIE | PLAY+CREATION+MOUVEMENT | **INTENSE**+PLAY+CREATION |

### D3 : 15 nouveaux concepts QUAL-dépendants

SAGESSE, GLOIRE, PUISSANCE, COURAGE, CRUAUTÉ, MAGNIFICENCE, VIEILLESSE,
HÉRITAGE, SINCÉRITÉ, FIDÉLITÉ, GRANDEUR, PASSION, TRADITION, VERTU, TERREUR.

Total : 105 → **120 concepts** (+14.3%).

### D4 : Keywords ×7 langues pour chaque QUAL atom

20 mots-clés par langue (en, fr, de, it, es, eo, fi) = 700 keywords QUAL
ajoutés dans `gutenberg_multilingual_validator.py`.

## Résultats pipeline

Pipeline complet (445 paragraphes, 7 couches) en **18.3s** :

| Atome QUAL | Détections corpus | Langues |
|---|---|---|
| BON | 159 | 7/7 |
| INTENSE | 114 | 7/7 |
| GRAND | 96 | 7/7 |
| VRAI | 80 | 7/7 |
| ANCIEN | 46 | 7/7 |

Upgrades : BEAU B→A (grâce à BON).

Tous les 35 atomes sont détectés dans le corpus (34 dans 7 langues,
DUALITÉ dans 1 langue).

## Fichiers modifiés

- **`import_panlang_v2.py`** :
  - Nouveau set `ATOMS_QUALITY` (5 atomes)
  - `ATOMS` union inclut `ATOMS_QUALITY` (35 total)
  - 5 entrées dans chacun : ATOM_DIMENSIONS, ATOM_NSM, ATOM_JACKENDOFF,
    ATOM_PUSTEJOVSKY, ATOM_DHATU
  - 9 overrides v2.6 dans FORMULA_OVERRIDES_V23

- **`gutenberg_multilingual_validator.py`** :
  - 5 blocs ATOM_KEYWORDS (×7 langues, ~20 mots chacun = 700 keywords)

- **`seven_layers_engine.py`** :
  - 9 concepts mis à jour dans CONCEPT_MAPPINGS
  - 15 nouveaux concepts QUAL-dépendants
  - Total : 120 CONCEPT_MAPPINGS

## Tests effectués

1. ✅ Syntaxe Python (`py_compile`) — 3 fichiers, aucune erreur
2. ✅ 35 atomes, 5 QUAL dans ATOMS_QUALITY
3. ✅ 5/5 dicts complétés pour chaque QUAL atom
4. ✅ `compute_primary_category(['BON'])` → QUAL ✅
5. ✅ `compute_primary_category(['GRAND'])` → QUAL ✅
6. ✅ `compute_primary_category(['VRAI'])` → QUAL ✅
7. ✅ Pipeline complet : 18.3s, 445/445 paragraphes, toutes étapes ✅
8. ✅ 120 concepts total (≥120 objectif NA-004)
9. ✅ 24 concepts QUAL-dépendants
10. ✅ BEAU upgradé B→A

## Prochaines étapes

- [ ] v2.7 : Opérations structurelles + WSD (désambiguïsation lexicale)
- [ ] Enrichir les re-décompositions dans step3 pour utiliser les QUAL atoms
- [ ] Analyser la distribution QUAL par langue (biais culturels ?)
- [ ] v4.0 : Pont text media (PDF/EPUB/DOCX → engine)
