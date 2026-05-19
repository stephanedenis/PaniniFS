# 2026-02-22 — v4.8.13 : Règles diachroniques (sūtra vs koṣa)

**Agent** : Copilot (Claude Opus 4.6) sur hauru  
**Branche** : `master`

## Contexte

Après v4.8.12 (expansion brute-force du vocabulaire, 544 entrées manuelles),
l'utilisateur a posé une question clé :

> « Est-ce que connaître l'histoire des langues permettrait de combler les gaps
> en essayant de deviner l'origine du locuteur (lieu/époque) et faisant des
> ponts entre des règles apparentées ? »

Réponse : OUI. Au lieu d'ajouter des mots un par un (koṣa = dictionnaire),
encoder des **règles de changement phonétique/orthographique** (sūtra = règles
génératives) — l'approche de Pāṇini lui-même.

## Décisions clés

### 1. Règles diachroniques plutôt que listes — `diachronic_rules.py`

**Constat** : ~200 entrées manuelles d'archaïsmes dans v482→v4812 ne couvrent
qu'une fraction des formes. Une seule règle couvre des dizaines de mots.

**Décision** : Créer `diachronic_rules.py` avec 3 niveaux :
- `DIACHRONIC_RULES` (94 mappings spécifiques par langue/époque)
- `GENERATIVE_RULES` (23 règles regex productives)
- `COGNATE_CORRESPONDENCES` (43 règles de correspondance entre langues)

**Impact** : ~160 règles remplacent potentiellement des centaines d'entrées
manuelles et couvrent des mots jamais vus dans le corpus.

### 2. Intégration comme Stratégies 10-11 dans `_is_covered_enhanced()`

**Constat** : Le pipeline a déjà 10 stratégies (0-9). Les règles diachroniques
sont un nouveau type de résolution, pas un remplacement.

**Décision** :
- **Stratégie 10** : `diachronic_modernize()` — applique les règles de
  changement sonore pour l'époque détectée du document
- **Stratégie 11** : `cognate_bridge()` — essaie les cognates dans les langues
  sœurs via des correspondances suffixales systématiques

### 3. Détection d'époque automatique au niveau document

**Constat** : `text_normalizer.py` a déjà `detect_epoch()` mais il est isolé.

**Décision** : Utiliser `detect_epoch_lightweight()` (version rapide) au début
de `analyze_document_fidelity()`, stocker dans `_DOC_EPOCH` (variable module),
vider le cache de couverture entre documents.

### 4. Normalisation diacritiques (ï→i)

**Constat** : Dante utilise des trémas pour marquer les diérèses métriques :
`fïata`, `coscïenza`, `Danïel`. Ces ne matchent pas les mots modernes.

**Décision** : Ajouter un strip de diacritiques (ï→i, ë→e, ü→u, ö→o) en
pré-traitement dans `_is_covered_enhanced()`.

## Fichiers modifiés

| Fichier | Action | Raison |
|---------|--------|--------|
| `diachronic_rules.py` | **CRÉÉ** | Module central : 94 règles spécifiques + 23 regex + 43 cognates, 5 langues, self-test 24/24 |
| `reconstruction_fidelity.py` | Modifié | Import diachronic_rules, `_DOC_EPOCH`, Strategies 10-11, epoch auto-detect, diaeresis strip |

## Tests effectués

### Self-test diachronic_rules.py
- 24/24 tests passent (IT 10/10, DE 5/5, FR 4/4, ES 5/5)
- Détection d'époque : 4/4 langues (letterario, pre_1901, classique, antiguo)

### Smoke test coverage (5 langues, textes les plus difficiles)

| Langue | Texte | v4.8.12 | v4.8.13 | Delta |
|--------|-------|---------|---------|-------|
| IT | Divina Commedia (1307) | 81.2% | **81.9%** | +0.7pp |
| DE | Also sprach Zarathustra (1883) | 89.1% | **89.8%** | +0.7pp |
| FR | Voyage centre de la Terre (1864) | 90.1% | **90.3%** | +0.2pp |
| ES | Don Quijote (1605) | 86.0% | **86.1%** | +0.1pp |
| EN | A Modest Proposal (1729) | 86.2% | **86.2%** | +0.0pp |

### Coverage moyenne corpus complet (62 fichiers)
- DE : **90.1%** (4 fichiers, croise 90% !)
- EN : 86.5% (22 fichiers)
- FR : 84.5% (6 fichiers, tiré vers le bas par textes très archaïques)
- IT : 81.9% (1 fichier = Dante, le plus dur du corpus)
- ES : 68.4% (2 fichiers, dont 1 à 50.7% probablement problématique)

## Analyse

### Pourquoi les gains sont modestes (+0.1 à +0.7pp) ?

1. **45-54% des mots non couverts sont des noms propres** — les règles
   diachroniques ne les touchent pas
2. **Les stemmers Snowball (Stratégie 8) capturent déjà beaucoup** — le stemmer
   normalise déjà `hörte→hör`, `freiwillige→freiwillig`
3. **Les archaic_forms manuels (v482→v4812) couvrent les cas les plus fréquents**

### Pourquoi c'est quand même important ?

1. **Génératif** : couvre des mots jamais vus dans le corpus
2. **Infrastructure** : la détection d'époque connectée au pipeline est une
   fondation pour de futures améliorations
3. **Cognate bridge** : permet de résoudre des mots entre langues apparentées
4. **Pāṇinien** : ~160 règles au lieu de ~200 entrées manuelles

## Prochaines étapes

1. **Enrichir les règles ES** — Don Quijote a beaucoup de formes archaïques
   f→h systématique pas encore couvertes (f- initial devant voyelle)
2. **Investiguer ES pg à 50.7%** — probablement un problème de détection de
   langue ou de boilerplate
3. **Ajouter des règles FR classique** — les textes de Molière/Voltaire utilisent
   systématiquement -oit/-oient
4. **Connecter `detect_epoch()` complet** (text_normalizer.py) au lieu de la
   version légère — plus de marqueurs, plus de confiance
5. **Considérer un module de noms propres universels** — NER ou gazetteer pour
   les 45-54% de mots non couverts qui sont des noms propres
