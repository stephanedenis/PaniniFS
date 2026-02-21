# v4.8.9 : IT 89.6%, FI 89.2% — dernière ligne droite vers 90%

**Date** : 2026-02-21
**Machine** : hauru (Xeon E5-2650, 62 GB)
**Modèle** : Claude Opus 4.6 via GitHub Copilot
**Branche** : master

## Contexte

Suite à v4.8.8 (FR franchit 90%), cette itération cible les 2 dernières langues
européennes sous 90% : IT (88.8%) et FI (88.5%). Objectif : les rapprocher le
plus possible du seuil de 90%.

## Décisions clés

1. **FI 88.5%, besoin +1.5pp** → Injection de 35 lemmes voikko (naida, kulua,
   yltyä, eteinen, lammikko, pääkaupunki, etc.) + 10 stop words → **FI 89.2%**
   (+0.7pp), à 0.8pp du seuil

2. **IT 88.8%, besoin +1.2pp** → 40 keywords (errante, inghiottire, pergamena,
   pesciolino, vaneggiare, etc.) + 12 stop words (apocopés/élisions) + 7 formes
   archaïques (côre→cuore, gittato→gettato, etc.) → **IT 89.6%** (+0.8pp),
   à 0.4pp du seuil

3. **Noms propres** → 5 FI (Saksa, Morcar, Mercian, Ludvig, Propontiksen) +
   5 IT (Carroll, Tenniel, Macmillan, Pietrocòla-Rossetti, Ruotolo) → élimination
   des faux négatifs littéraires

## Résultats

| Langue | v4.8.8 | v4.8.9 | Delta | Statut |
|--------|--------|--------|-------|--------|
| EN     | 94.8%  | 94.8%  | +0.0  | 🟢     |
| EO     | 93.2%  | 93.2%  | +0.0  | 🟢     |
| DE     | 91.1%  | 91.1%  | +0.0  | 🟢     |
| ES     | 90.2%  | 90.2%  | +0.1  | 🟢     |
| FR     | 90.1%  | 90.1%  | +0.0  | 🟢     |
| **IT** | 88.8%  | **89.6%** | **+0.8** | 🔴 (→90% imminent) |
| **FI** | 88.5%  | **89.2%** | **+0.7** | 🔴 (→90% en vue) |

**Global : 90.5% → 90.8% (+0.3pp)**

## Fichiers modifiés

- `vocabulary_expansion_v489.py` — **NOUVEAU** : 113 entrées
  - 74 keywords (35 FI + 39 IT) × 15 atomes
  - 22 stop words (10 FI + 12 IT)
  - 10 noms propres (5 FI + 5 IT)
  - 7 formes archaïques IT
- `reconstruction_fidelity.py` — Intégration v4.8.9
- `vocabulary_audit_results_v489.json` — Résultats audit

## Tests effectués

- Self-test v489 : 74 kw, 22 sw, 10 pn, 7 af ✅
- Import integration : `_HAS_EXPANSION_V489 = True` ✅
- Audit complet : 123 450 mots contenu, 112 043 couverts, 628.9s ✅

## Prochaines étapes

- v4.8.10 : Push final IT (+0.4pp) et FI (+0.8pp) au-dessus de 90%
- IT : top mots non couverts freq≥2, formes verbales irrégulières
- FI : lemmes voikko des prochains top40, composés non décomposés
- Objectif : 7/7 langues européennes ≥90%
