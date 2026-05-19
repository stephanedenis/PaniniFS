# 2026-02-18 — v2.4 : Activation des atomes ABS dans le corpus littéraire

> **Agent** : Claude Opus 4.6 · **Host** : hauru · **Session** : Phase 36

## Contexte

Suite à la Phase 35 (révision des concepts, 76/104 activés), 29 concepts
restaient non-activés. Le diagnostic a révélé une **hypothèse fausse** :
le commentaire dans le code affirmait que les atomes ABS (MESURE, STRUCTURE,
RELATION, RÉCURRENCE, INVARIANCE, ORDRE) « ne sont pas détectés dans les
corpus littéraires ». C'était **faux**.

## Décisions clés

### 1. Découverte : les ABS sont massivement détectés dans le corpus

- **Constat** : Les keywords ABS incluent des mots littéraires courants :
  "encore"→RÉCURRENCE, "même"→INVARIANCE, "entre"→RELATION, "forme"→STRUCTURE,
  "avant/après"→ORDRE, "taille"→MESURE. En vérifiant `paragraph_word_atoms` :
  ORDRE=148, MESURE=63, STRUCTURE=28, INVARIANCE=21, RELATION=17, RÉCURRENCE=14.
- **Décision** : Supprimer l'exclusion ABS et ajouter tous les concepts
  ABS-dépendants à CONCEPT_MAPPINGS.
- **Impact** : +17 concepts activés d'un coup.

### 2. MÉLANCOLIE : fix formule Dolt (TEDIUM ≠ DESTRUCTION)

- **Constat** : CONCEPT_MAPPINGS avait {GRIEF, COGNITION, TEDIUM} mais Dolt
  avait GRIEF+COGNITION+DESTRUCTION (héritage de EMOTION_REMAP sans override).
- **Décision** : Ajout de MÉLANCOLIE dans FORMULA_OVERRIDES_V23 →
  GRIEF+COGNITION+TEDIUM. Total overrides : 28.
- **Impact** : Cohérence CM↔Dolt. MÉLANCOLIE reste non-activée car
  GRIEF+TEDIUM ne co-occurrent jamais dans Alice/Candide (normal).

### 3. Alignement COMPRENDRE et OBSERVER sur Dolt

- **Constat** : COMPRENDRE avait {COGNITION, PERCEPTION, EXISTENCE} en CM
  mais {COGNITION, PERCEPTION, STRUCTURE} dans l'override Dolt. Même chose
  pour OBSERVER ({CARE} vs {EXISTENCE}).
- **Décision** : Alignement CM→Dolt (source de vérité).
- **Impact** : 0 mismatches CM↔overrides.

## Résultats

| Métrique | Avant (v2.3) | Après (v2.4) | Δ |
|---|---|---|---|
| Concepts activés | 76/104 | **92/104** | **+21%** |
| CONCEPT_MAPPINGS | 78 | **95** | +17 |
| Overrides | 27 | **28** | +1 |
| Tests | 162/162 ✅ | 162/162 ✅ | = |
| Doublons formule (Dolt) | 0 | 0 | = |
| Doublons atom-set (CM) | 0 | 0 | = |
| Mismatches CM↔overrides | 2 | **0** | -2 |

### Nouveaux concepts activés (17 ABS-dépendants)
- DISTANCE=30, GOÛTER=27, LIEU=18, DURÉE=16, TEMPS=15, BEAUTÉ=14,
  PHILOSOPHIE=13, ÉTERNITÉ=12, RÉCIT=11, MUR=7, LITTÉRATURE=6,
  LÉGENDE=5, MUSIQUE=4, ORGANISER=4, PROXIMITÉ=4, GROUPE=2, INQUIÉTUDE=2

### 12 concepts encore non-activés
- 9 single-atom (par conception : COGNITION, COMMUNICATION, etc.)
- MÉLANCOLIE (GRIEF+TEDIUM jamais co-présents — corpus trop léger)
- DEMEURER (fusionné avec MARCHER — par conception)
- HAIR (DISGUST=0 dans corpus), DÉGOÛT (idem)

## Fichiers modifiés

| Fichier | Raison |
|---|---|
| `seven_layers_engine.py` | +17 concepts ABS dans CONCEPT_MAPPINGS (95 total), alignement COMPRENDRE/OBSERVER, commentaire ABS corrigé |
| `import_panlang_v2.py` | +1 override MÉLANCOLIE (28 total), version commit message v2.4 |

## Tests effectués

- `pytest test_seven_layers.py test_morpho_semantic_bridge.py` : 162/162 ✅
- `import_panlang_v2.py` : 104 concepts importés, 0 doublons formule
- `seven_layers_engine.py` (pipeline complet) : 6/6 étapes ✅
- Dolt : 92 concepts activés dans paragraph_concepts
- ABS détections : ORDRE=148, MESURE=63, STRUCTURE=28, INVARIANCE=21,
  RELATION=17, RÉCURRENCE=14 (total 291 détections ABS)

## Prochaines étapes

1. **Corpus expansion** : Ajouter textes philosophiques (Descartes, Kant,
   Pascal) pour activer MÉLANCOLIE (TEDIUM+GRIEF) et valider les C-tier
2. **DISGUST improvement** : Enrichir ATOM_KEYWORDS[DISGUST] avec des
   synonymes littéraires plus courants pour activer HAIR/DÉGOÛT
3. **C-tier validity** : Les 9 concepts C-tier ont validity_score <0.3 —
   calculer une validité proxy basée sur les détections
4. **Taux d'activation objectif** : 92/104 = 88.5% → cible 95% avec
   l'expansion corpus
