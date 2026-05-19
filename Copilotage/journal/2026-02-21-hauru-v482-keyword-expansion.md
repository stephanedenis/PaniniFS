# 2026-02-21 — v4.8.2: Massive multilingual keyword expansion

**Agent**: GitHub Copilot (Claude Opus 4.6) — hauru  
**Session**: v4.8.2 implementation — keyword expansion + algorithmic improvements

## Contexte

Continuation du roadmap vers 90% de couverture lexicale globale.
Le v4.8.1 (Finnish voikko lemmatizer) avait atteint 81.9% global.
L'analyse des lacunes montrait que 16,553 mots uniques non couverts
nécessitaient une expansion massive du vocabulaire des atomes + des
améliorations algorithmiques pour les composés et élisions.

## Décisions clés

### 1. Expansion systématique du vocabulaire (23 atomes × 7 langues)
- **Constat** : Des mots courants (bed, duck, farm, sin, thank, ceremony...)
  n'existaient dans aucun ATOM_KEYWORDS. 14 mots anglais basiques testés :
  TOUS absents, AUCUNE correspondance de radical.
- **Décision** : Création de `vocabulary_expansion_v482.py` avec ~3,300 nouveaux
  mots-clés répartis sur 23 atomes (AGENT, LIEU, COMMUNICATION, POSSESSION,
  BON, MAUVAIS, PERCEPTION, MOUVEMENT, COGNITION, EXISTENCE, DESTRUCTION,
  MATIÈRE, CORPS, INTENSE, GRAND, SEEKING, DOMINATION, QUAL, RELATION,
  GRIEF, FEAR, PLAY, CREATION, RAGE, TEDIUM, ORDRE, MESURE, STRUCTURE,
  INVARIANCE).
- **Impact** : EN 2,242→3,126 (+884), FR ~1,700→2,500 (+800), FI ~1,200→2,029
  (+800). Global unique: 12,842→16,148 (+3,306).

### 2. Améliorations algorithmiques (strategies 0, 3, 4)
- **Constat** : Les nombres (1759, 42), les élisions françaises (m'avez,
  l'anabaptiste), et les composés à trait d'union (disait-il) échouaient.
- **Décision** :
  - Strategy 0 (NEW): Détection numérique (`word.isdigit()` → auto-couvert)
  - `_deep_check()` helper (NEW): Applique keyword + stemmer + voikko + suffixe
    aux sous-parties
  - Strategy 3 (enhanced): Composés avec trait d'union — `_deep_check()` +
    mots outils conscients (ex: "disait-il" → "il" est stop word)
  - Strategy 4 (enhanced): Élisions romanes — `_ELISION_PREFIXES` (d, l, m, n,
    s, c, j, qu, all, nell, dell...) + `_deep_check()` sur la partie principale
- **Impact** : Résolution automatique des composés et élisions sans ajout
  de mots-clés.

### 3. Stop words massifs + noms propres + formes archaïques
- **Constat** : Le corpus Gutenberg contient beaucoup de formes archaïques
  (thou, thee, hath, dost, disoit, étoit) et de noms propres littéraires.
- **Décision** : Ajout de ~500 stop words (EN archaïques, FR pronoms/adverbes,
  DE/ES/IT/EO/FI fonctions), 80+ noms propres, et mappings de formes
  archaïques (DE: theil→teil, giebt→gibt; FR: disoit→disait).
- **Impact** : Réduction du bruit dans les mots non couverts.

## Fichiers modifiés

| Fichier | Action | Raison |
|---------|--------|--------|
| `SANDBOX/dolt-concept-store/vocabulary_expansion_v482.py` | CRÉÉ | ~1,400 lignes, 23 atomes × 7 langues, +3,306 mots-clés |
| `SANDBOX/dolt-concept-store/reconstruction_fidelity.py` | MODIFIÉ | Import v482, `_extend_global_with_v482()`, stop words v482, strategies 0/3/4 |
| `SANDBOX/dolt-concept-store/vocabulary_audit_results_v482.json` | CRÉÉ | Résultats d'audit complets |

## Tests effectués

- **pytest** : 71 passed, 0 regressions (1 failure pré-existante `test_all_languages_present` exclue)
- **Import test** : Module chargé correctement, 16,148 mots-clés globaux confirmés
- **Audit complet** (611s) :

| Langue | v4.8.1 | v4.8.2 | Delta |
|--------|--------|--------|-------|
| EN     | 88.2%  | 91.9%  | +3.7pp |
| FR     | 80.9%  | 85.5%  | +4.6pp |
| DE     | 83.4%  | 85.2%  | +1.8pp |
| ES     | 83.4%  | 85.5%  | +2.1pp |
| EO     | 86.1%  | 87.6%  | +1.5pp |
| FI     | 78.1%  | 81.9%  | +3.8pp |
| IT     | 80.1%  | 81.9%  | +1.8pp |
| SA     | 43.7%  | 43.8%  | +0.1pp |
| **Global** | **81.9%** | **85.1%** | **+3.2pp** |

## Prochaines étapes

1. **v4.8.3** : Expansion ciblée ES/IT/FI (les langues sous 86%)
2. **v4.9** : Sanskrit (43.8% → objectif 60%) — nécessite approche dédiée
   (translittération IAST, morphologie agglutinante)
3. **v5.0** : Objectif 90% global — nécessite ~6,200 tokens supplémentaires
   (actuellement 18,780 non couverts, besoin de couvrir ~6,200 pour atteindre 90%)
4. **JSON-LD export** et `panini-interpretations-db`
