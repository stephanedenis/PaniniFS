# v4.8.7 — All-languages push: 90.1% global 🎯

- **Date** : 2026-02-21
- **Machine** : hauru (Xeon E5-2650, 62 Go RAM)
- **Agent** : Copilot Claude Opus 4.6
- **Commit précédent** : `ba45b05` (v4.8.6, 89.4%)

## Contexte

Poursuite de l'objectif 90%+ de couverture lexicale. La v4.8.6 avait atteint
89.4% avec DE comme premier non-EN à dépasser 90%. Trois langues restaient
en dessous de 90% : FI (86.8%), IT (87.5%), FR (89.0%).

## Décisions clés

### Constat → Décision → Impact

1. **FI : voikko résout les formes mais les lemmes manquent dans l'index**
   - Constat : voikko lemmatise `ilmestyi → ilmestyä`, `joutuu → joutua`, etc.
     mais ces lemmes ne sont dans aucun atome → Strategy 9 échoue
   - Décision : Ajouter 35 lemmes FI comme keywords dans les atomes appropriés
   - Impact : FI 86.8% → 87.7% (+1.0pp)

2. **IT/ES : formes verbales irrégulières (passato remoto, subjonctif)**
   - Constat : `successe`, `uscì`, `proruppe`, `vuelva`, `duerme` — le stemmer
     Snowball ne peut pas relier ces formes irrégulières à l'infinitif
   - Décision : Ajouter les formes irrégulières directement comme keywords
   - Impact : IT 87.5% → 88.2% (+0.8pp), ES 89.5% → **90.1%** (+0.6pp) ✅

3. **FR : formes élidées et verbes irréguliers**
   - Constat : `paient` (payer), `meurs` (mourir), `répandit` (répandre) —
     stems divergents entre forme conjuguée et infinitif
   - Décision : Ajouter les conjugaisons irrégulières + bases derrière élisions
   - Impact : FR 89.0% → 89.7% (+0.7pp)

4. **DE : formes passées irrégulières + composés**
   - Constat : `stampfte`, `blies`, `ward` — passé irrégulier, aucun stem match
   - Décision : Ajouter directement + composé `zauberland`
   - Impact : DE 90.1% → **91.1%** (+1.0pp) ✅

5. **EO : notation x-system et composés**
   - Constat : `pafigxis`, `cxirkauxe`, `gxojigite` — formes en x-notation
   - Décision : Ajouter les formes directes en x-notation
   - Impact : EO 92.4% → **93.2%** (+0.8pp)

## Fichiers modifiés

| Fichier | Raison |
|---------|--------|
| `vocabulary_expansion_v487.py` | **NOUVEAU** — 308 entrées (240 kw + 40 sw + 8 pn + 19 af) |
| `reconstruction_fidelity.py` | Intégration v4.8.7 (import, extend, stop words) |
| `vocabulary_audit_results_v487.json` | Résultats audit complet |
| `Copilotage/journal/INDEX.md` | Ajout entrée v4.8.7 |

## Tests effectués

- ✅ Self-test expansion : 308 entrées, 16 atomes × 7 langues
- ✅ Import module : `_HAS_EXPANSION_V487 = True`
- ✅ Top40 mots cibles : **280/280** (99.6% → 100% après ajout `zauberland`)
- ✅ Audit complet corpus : **90.1%** global pondéré

## Résultats

```
v4.8.6 → v4.8.7:
  🟢 EN: 94.8% (+0.4pp)
  🟢 EO: 93.2% (+0.8pp)
  🟢 DE: 91.1% (+1.0pp)
  🟢 ES: 90.1% (+0.6pp)  ← NOUVEAU ≥90%
  🔴 FR: 89.7% (+0.7pp)
  🔴 IT: 88.2% (+0.8pp)
  🔴 FI: 87.7% (+1.0pp)
  Global: 90.1% (+0.7pp)  ← OBJECTIF ATTEINT 🎯
```

Progression cumulée v4.8.2 → v4.8.7 : **85.1% → 90.1% (+5.0pp)**

## Prochaines étapes

- FR (89.7%) : à 0.3pp du seuil, quelques dizaines de mots suffiraient
- IT (88.2%) : plus de verbes irréguliers, participes, archaïsmes Pinocchio
- FI (87.7%) : continuer l'injection de lemmes voikko, mais rendements
  décroissants (3,253 mots uniques non couverts, freq basse ≤6)
- Considérer des améliorations algorithmiques pour les composés FI
  (voikko compound analysis) plutôt que du vocabulaire brut
