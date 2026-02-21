# v4.8.4 — EN base-form injection + remaining multilingual gaps

**Date** : 2026-02-21  
**Machine** : hauru (Intel Xeon E5-2650, 62 GB)  
**Agent** : GitHub Copilot (Claude Opus 4.6)  
**Commit** : (ce commit)

## Contexte

Le v4.8.3 (commit `9a75d77`) avait atteint **87.4 %** de couverture lexicale.
L'analyse des résidus a révélé une **faiblesse structurelle en anglais** : de
nombreux mots de base courants (`eye`, `drink`, `win`, `express`, `steal`,
`wife`, etc.) n'avaient jamais été assignés à aucun atome, empêchant le
stemmer Snowball (stratégie 8) de résoudre leurs formes fléchies (`eyelids`,
`drank`, `won`, `expressed`, `stole`, `wives`).

## Décisions clés

### 1. Diagnostic EN : base forms manquantes
- **Constat** : 12/13 mots fréquents EN testés échouaient. Aucune de leurs
  formes de base (`eye`, `express`, `drink`, `win`, etc.) n'était dans
  `_GLOBAL_KEYWORDS`. Le stemmer Snowball produit les bonnes racines mais ne
  trouvait aucune correspondance dans l'index pré-stemmé.
- **Décision** : Ajouter massivement les formes de base EN avec leurs variantes
  fléchies pour maximiser l'effet du stemmer.
- **Impact** : EN 93.3 % → 94.0 % (+0.7pp), et effet cascade sur les stratégies
  5-8 pour toutes les formes dérivées.

### 2. Expansion multilingue ciblée
- **IT** : +2.2pp (84.4 % → 86.6 %) — futurs (`faranno`), passati (`ebbi`,
  `piacque`), pronoms clitiques (`glielo`, `farne`), noms courants
- **DE** : +2.1pp (87.2 % → 89.4 %) — composés (`kunststücke`, `zuckerplätzchen`,
  `glaceehandschuhe`), archaïsmes (`gutmüthig`, `errieth`, `faßte`), préfixes
  (`anzureden`, `anzubieten`, `anzuklopfen`)
- **ES** : +1.5pp (87.5 % → 89.0 %) — archaïques (`sirviéron`, `conduxéron`,
  `echáron`), noms (`banquero`, `juramento`, `urbanidad`)
- **EO** : +1.4pp (90.4 % → 91.8 %) — radicaux (`kondukis`, `gxemante`,
  `subpremita`, `frakasata`), substantifs (`pencojn`, `barilo`, `marmeladujon`)
- **FI** : +1.3pp (84.9 % → 86.2 %) — verbes (`aikoi`, `tiuskasi`, `irvisti`,
  `röhki`), participes, adverbes temporels
- **FR** : +1.0pp (87.4 % → 88.4 %) — noms (`lunettes`, `gazon`, `sérail`),
  verbes (`enlever`, `pénétrer`, `conclure`)

### 3. Stop words et noms propres
- 48 stop words ajoutés (IT clitiques/archaïques, FI adverbes temporels, ES
  formes archaïques, DE particules, EN/EO interjections)
- 20 noms propres (Fernando, Alger, Palestrina, Northumbria, Lissabon, etc.)
- 13 formes archaïques → modernes (DE: `gutmüthig`→`gutmütig`, ES: `baxo`→`bajo`)

## Fichiers modifiés

| Fichier | Raison |
|---------|--------|
| `vocabulary_expansion_v484.py` | **NOUVEAU** — 584 entrées (503 kw + 48 sw + 20 pn + 13 af) |
| `reconstruction_fidelity.py` | Import v4.8.4, `_extend_global_with_v484()`, stop words |
| `vocabulary_audit_results_v484.json` | Résultats audit à 88.8 % |

## Tests effectués

| Test | Résultat |
|------|----------|
| Self-test v484 (totaux) | ✅ 584 entrées, 16 atomes, 7 langues |
| EN résolution (26 mots) | ✅ 26/26 |
| FR résolution (22 mots) | ✅ 22/22 |
| IT résolution (25 mots) | ✅ 25/25 |
| ES résolution (22 mots) | ✅ 22/22 |
| DE résolution (31 mots) | ✅ 31/31 |
| FI résolution (26 mots) | ✅ 26/26 |
| EO résolution (23 mots) | ✅ 23/23 |
| Total résolution | ✅ **175/175** |
| Audit complet (630s) | ✅ 88.8 % global |

## Résultats couverture

| Langue | v4.8.2 | v4.8.3 | v4.8.4 | Δ total |
|--------|--------|--------|--------|---------|
| **Global** | **85.1 %** | **87.4 %** | **88.8 %** | **+3.7pp** |
| EN | 91.9 % | 93.3 % | 94.0 % | +2.1pp |
| EO | 87.6 % | 90.4 % | 91.8 % | +4.2pp |
| DE | 85.2 % | 87.2 % | 89.4 % | +4.2pp |
| ES | 85.5 % | 87.5 % | 89.0 % | +3.5pp |
| FR | 85.5 % | 87.4 % | 88.4 % | +2.9pp |
| FI | 81.9 % | 84.9 % | 86.2 % | +4.3pp |
| IT | 81.9 % | 84.4 % | 86.6 % | +4.7pp |
| SA | 43.8 % | 43.9 % | 43.9 % | +0.1pp |

## Prochaines étapes

- **Objectif 90 %** : FI (86.2 %) et IT (86.6 %) sont les plus faibles
  en européen, mais progressent rapidement (+4pp chacun sur 2 versions)
- FR (88.4 %) et ES (89.0 %) approchent 90 %, une expansion supplémentaire
  devrait les y amener
- EO (91.8 %) et EN (94.0 %) sont déjà au-dessus de 90 %
- Considérer une ré-ingestion Dolt avec les keywords v4.8.4
