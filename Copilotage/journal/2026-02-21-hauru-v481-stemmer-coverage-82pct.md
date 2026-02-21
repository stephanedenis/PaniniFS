# v4.8.1 Round 7 — Post-stemmer multi-language expansion 80.3% → 81.8%

**Date** : 2026-02-21  
**Machine** : hauru (Intel Xeon E5-2650, 8c/16t, 62GB)  
**Agent** : GitHub Copilot (Claude Opus 4.6)  
**Commit** : (à venir)

## Contexte

Suite du commit `fa1da1a` (v4.8.1 stemmer + voikko). Audit post-stemmer montrait
80.3% weighted. Ce round cible les mots irréguliers que les stemmers ne captent
pas (EN: said≠say, DE: befand≠finden).

## Décisions clés

### 1. Round 7 expansion ciblée multi-langue
- **Constat** : Audit 80.3% montrait que les formes verbales irrégulières (EN
  past tense, DE Ablaut, FR subjonctif) ne sont pas résolues par Snowball.
- **Décision** : Ajout dans `vocabulary_expansion_v48.py` : ~200 stop words
  (verbes irréguliers EN, modaux DE subjunctif, contractions FR/IT, particules
  FI/ES), ~200 keywords (verbes irréguliers, noms communs, adjectifs), ~10 noms
  propres.
- **Impact** : 80.3% → 81.8% (+1.5pp).

## Fichiers modifiés

| Fichier | Raison |
|---------|--------|
| `vocabulary_expansion_v48.py` | Round 7 : STOP_WORDS_V48_R7, EXPANSION_KEYWORDS_V48_R7, PROPER_NOUN_AGENTS_R7 |
| `vocabulary_audit_v481_r7.json` | Résultats audit final (81.8%) |

## Tests effectués

### Audit v4.8.1 Round 7 — Résultats

| Langue | v4.8 (R6) | v4.8.1 (R7+stemmer) | Δ |
|--------|-----------|---------------------|---|
| EN | 84.9% | 88.2% | **+3.3pp** |
| EO | 81.4% | 86.1% | **+4.7pp** |
| DE | 83.2% | 83.4% | +0.2pp |
| ES | 74.3% | 83.4% | **+9.1pp** |
| FI | 65.8% | 78.1% | **+12.3pp** |
| FR | 80.6% | 80.8% | +0.2pp |
| IT | 78.9% | 80.1% | +1.2pp |
| SA | 43.9% | 43.7% | -0.2pp |
| **Global weighted** | **77.4%** | **81.8%** | **+4.4pp** |

- 279,495 mots, 128,612 content, 105,192 couverts
- 16,716 mots uniques non couverts (vs 19,599 en v4.8)
- Temps d'analyse : 630s

## Prochaines étapes

1. **Re-ingestion interpretations-db** avec keywords v4.8.1
2. **v4.9 target 85%** — Lemmatiseurs FR/IT (spaCy/simplemma)
3. **Objectif 90%** — NLP sophistiqué (POS-tagging + lemmatisation)
