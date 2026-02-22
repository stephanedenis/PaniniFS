# 2026-02-21 — Étude normes ISO/Unicode langues — hauru

> **Agent** : GitHub Copilot (Claude Opus 4.6) · hauru  
> **Session** : Méta-analyse des normes linguistiques pour Panini-FS

## Contexte

Besoin de s'assurer que Panini-FS connaît les normes internationales ISO et Unicode
relatives aux langues et écritures, comprend son propre état vis-à-vis de ces normes,
et identifie ses limitations. Travail de niveau « méta » pour que les agents futurs
disposent d'une base de connaissance normative complète.

## Décisions clés

### D1 — Document de référence centralisé

- **Constat** : Aucune documentation ne cartographiait les normes ISO 639 (1/2/3/5),
  ISO 15924, BCP 47, Unicode CLDR, UAX #15 (normalisation), UAX #29 (segmentation)
  en relation avec l'implémentation Panini.
- **Décision** : Créer `Copilotage/knowledge/LANGUAGE_STANDARDS_ISO_UNICODE.md`,
  un document exhaustif couvrant toutes les normes, l'état actuel de Panini,
  une gap analysis, et des recommandations priorisées.
- **Impact** : Les agents ont maintenant une référence unique pour toute question
  sur les langues et les normes.

### D2 — Identification de 10 écarts (Gap Analysis)

- **Constat** : Audit croisé du code vs les normes.
- **Décision** : Documenter 10 écarts classés en 3 catégories (critiques,
  documentaires, architecturaux) avec effort et priorité.
- **Impact** : Roadmap claire pour la conformité aux normes.

### D3 — Risque critique NFC identifié

- **Constat** : Aucune normalisation Unicode (NFC/NFD) n'est appliquée en entrée
  du pipeline. Un `é` en NFC et un `é` en NFD ne matchent pas par comparaison
  de chaînes → les keywords pourraient rater des matches silencieusement.
- **Décision** : Recommander `unicodedata.normalize('NFC', text)` comme action
  immédiate (2 lignes de code, impact maximal).
- **Impact** : Élimination d'une classe entière de faux négatifs potentiels.

### D4 — Panini couvre 0.2% des langues mais 60% des locuteurs

- **Constat** : 14 langues sur ~7 168 vivantes, mais ~4.8 milliards de locuteurs natifs.
- **Décision** : Documenter cette asymétrie pour contextualiser les priorités d'expansion.
- **Impact** : Vision claire pour prioriser l'ajout de langues (ko, ar, bn, tr → 75% couverture).

## Fichiers modifiés

| Fichier | Raison |
|---------|--------|
| `Copilotage/knowledge/LANGUAGE_STANDARDS_ISO_UNICODE.md` | **Créé** — Document normatif complet (9 sections, 2 annexes) |
| `Copilotage/journal/2026-02-21-hauru-normes-iso-unicode-langues.md` | **Créé** — Ce journal |
| `Copilotage/journal/INDEX.md` | **Mis à jour** — Nouvelle entrée |

## Tests effectués

- Vérification que les 14 codes ISO 639-1 utilisés par Panini sont tous valides ✅
- Vérification des correspondances ISO 639-1 ↔ 639-2/T ↔ 639-3 pour les 14 langues ✅
- Vérification que les regex de détection de script couvrent les ranges Unicode corrects ✅
- Identification de 3 regex incomplètes (Latin étendu, CJK Extension A/B, Arabic Extended) ✅
- Recherche web des versions actuelles : CLDR 48.1 (jan 2026), Unicode 16.0 (sept 2024) ✅

## Prochaines étapes

1. **Implémenter la normalisation NFC** dans `semantic_engine.py` (G1 — priorité haute)
2. **Transformer le mapping script→langue en 1:N** (G2 — priorité moyenne)
3. **Ajouter les métadonnées ISO dans `LANGUAGE_PROFILES`** (enrichissement)
4. **Retirer le dead code fallback** `pt→es`, `nl→de` (G9 — cleanup)
5. **Élargir `VARCHAR(5)` à `VARCHAR(20)`** dans les schémas Dolt pour BCP 47 (G7)
6. **Évaluer l'ajout du coréen** comme 15e langue (alignement atomique avec Hangul Jamo)
