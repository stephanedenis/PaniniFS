# v4.8.8 : FR franchit 90% — 90.1%→90.5% (+0.4pp)

**Date** : 2026-02-21
**Machine** : hauru (Xeon E5-2650, 62 GB)
**Modèle** : Claude Opus 4.6 via GitHub Copilot
**Branche** : master

## Contexte

Suite à v4.8.7 qui a atteint l'objectif 90% global, cette itération cible
les 3 dernières langues européennes sous 90% : FR (89.7%), IT (88.2%), FI (87.7%).
Objectif : pousser FR au-dessus de 90% et réduire l'écart pour IT et FI.

## Décisions clés

### Constat → Décision → Impact

1. **FR à 89.7%, à 0.3pp du seuil** → Injecter 45 keywords FR couvrant noms,
   verbes et adjectifs fréquents (freq≥4) + 5 stop words élisions →
   **FR 90.1%** (+0.4pp) 🎯 5e langue ≥90%

2. **FI voikko lemmes non indexés** → Ajouter 34 lemmes finnois (saattaa,
   ennättää, ehtiä, kenttä, paha, etc.) + 15 stop words dialectaux/interjections →
   **FI 88.5%** (+0.8pp), meilleure progression

3. **IT formes apocopées et archaïques** → Ajouter 21 keywords IT + 10 stop words
   apocopés (lai, vuol, abbiam, fè) + 3 formes archaïques →
   **IT 88.8%** (+0.6pp)

4. **Diminishing returns** → 136 entrées pour +0.4pp global (vs 307→+0.7pp en v4.8.7).
   Le ratio entrées/gain augmente. Prochaines itérations devront cibler plus
   précisément les mots à haute fréquence.

## Résultats

### Couverture par langue (v4.8.7 → v4.8.8)

| Langue | v4.8.7 | v4.8.8 | Delta | Statut |
|--------|--------|--------|-------|--------|
| EN     | 94.8%  | 94.8%  | +0.0  | 🟢     |
| EO     | 93.2%  | 93.2%  | +0.0  | 🟢     |
| DE     | 91.1%  | 91.1%  | +0.0  | 🟢     |
| ES     | 90.1%  | 90.2%  | +0.1  | 🟢     |
| **FR** | 89.7%  | **90.1%** | **+0.4** | 🟢 **NOUVEAU** |
| IT     | 88.2%  | 88.8%  | +0.6  | 🔴     |
| FI     | 87.7%  | 88.5%  | +0.8  | 🔴     |

**Global : 90.1% → 90.5% (+0.4pp)**

### Langues ≥90% : 5/7 (EN, EO, DE, ES, FR)
### Langues restantes < 90% : IT (88.8%), FI (88.5%)

## Fichiers modifiés

- `vocabulary_expansion_v488.py` — **NOUVEAU** : 136 entrées
  - 100 keywords (45 FR + 34 FI + 21 IT) × 18 atomes
  - 30 stop words (15 FI + 10 IT + 5 FR)
  - 3 noms propres FR (Padoue, Badajos, Northumbrie)
  - 3 formes archaïques IT (stroppia→storpia, intiera→intera, bruttificazione)
- `reconstruction_fidelity.py` — Intégration v4.8.8 (import, extend, stop words)
- `vocabulary_audit_results_v488.json` — Résultats audit complet

## Tests effectués

- Self-test v488 : 100 kw, 30 sw, 3 pn, 3 af ✅
- Audit complet corpus : 123 500 mots de contenu, 111 755 couverts, 631.9s ✅
- 90.5% global vérifié ✅

## Statistiques cumulées v4.8.2→v4.8.8

| Version | Entrées | Delta global | Global |
|---------|---------|-------------|--------|
| v4.8.2  | base    | —           | 85.1%  |
| v4.8.3  | 771     | +2.3pp      | 87.4%  |
| v4.8.4  | 584     | +1.4pp      | 88.8%  |
| v4.8.5  | algo    | +0.2pp      | 89.0%  |
| v4.8.6  | 400     | +0.4pp      | 89.4%  |
| v4.8.7  | 307     | +0.7pp      | 90.1%  |
| v4.8.8  | 136     | +0.4pp      | 90.5%  |
| **Total** | **~2200** | **+5.4pp** | **90.5%** |

## Prochaines étapes

- v4.8.9 : Pousser IT (88.8%) et FI (88.5%) vers 90%
- Analyse des top40 mots non couverts FI et IT
- Lemmes voikko pour FI, formes irrégulières directes pour IT
- Objectif : 6/7 langues ≥90%, puis 7/7
