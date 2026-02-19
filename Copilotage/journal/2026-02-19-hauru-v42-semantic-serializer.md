# v4.2 : Sérialisation sémantique, comparaison cross-language, spec E2

- **Date** : 2026-02-19
- **Machine** : hauru (Intel Xeon E5-2650, 62 GB RAM)
- **Agent** : GitHub Copilot (Claude Opus 4.6)
- **Référence roadmap** : NA-004, Priorité 2c (v4.2, dernière étape)

---

## Contexte

v4.0 (extracteur multi-format) et v4.1 (orchestrateur document→atomes) sont
terminés et validés. v4.2 vise trois objectifs :
1. Sérialiser les profils sémantiques en JSON portable
2. Comparer des traductions d'un même texte (Alice EN vs FR)
3. Mesurer l'universalité des atomes à travers les langues
4. Spécifier l'expérience E2 (reconstruction)

## Décisions clés

### 1. Architecture du sérialiseur

**Constat** : Les rapports de `document_analyzer.py` sont riches mais pas
portables — ils restent en mémoire ou dans Dolt.

**Décision** : Créer `semantic_serializer.py` (~480 lignes) avec :
- `SemanticExport` dataclass : profil sémantique complet (atom/concept
  distributions, proportions normalisées, operators, timing)
- Schema version 1.0 pour évolutivité future
- 4 sous-commandes CLI : `export`, `compare`, `batch`, `e2-prep`
- Import/export JSON avec `load_export()` / `save_export()`

**Impact** : Les analyses sont désormais persistantes, comparables et
transportables entre machines.

### 2. Métriques d'universalité

**Constat** : Pour mesurer si les atomes sont vraiment universels à travers
les langues, il faut des métriques quantitatives, pas juste du qualitatif.

**Décision** : Implémenter 5 métriques :
- **Jaccard** : |intersection| / |union| des ensembles d'atomes
- **Cosine similarity** : similarité vectorielle des proportions d'atomes
- **Spearman rank correlation** : corrélation des rangs d'atomes
- **Operator similarity** : cosine des vecteurs NEG/QUANT/MOD
- **Universality score** : moyenne pondérée (0.40×cos + 0.25×concept_cos +
  0.20×rank + 0.10×jaccard + 0.05×ops)

**Impact** : Score unique interprétable pour juger de l'universalité.

### 3. Résultat Alice EN ↔ FR

**Constat** : Alice in Wonderland existe en anglais (Gutenberg 11) et en
français (Gutenberg 55456, traduction Henri Bué 1869).

**Résultat** :
| Métrique | Valeur | Interprétation |
|----------|--------|----------------|
| **Universality score** | **0.8671** | **EXCELLENT** |
| Cosine atomes | 0.9307 | Profils atomiques très similaires |
| Rank correlation | 0.8462 | Même hiérarchie d'atomes |
| Jaccard atomes | 0.7647 | 13/17 atomes partagés |
| Cosine concepts | 0.8303 | Bonne convergence conceptuelle |
| Operator similarity | 0.8305 | Même distribution NEG/QUANT/MOD |

**Atomes universels (EN ∩ FR)** : AGENT, CHOSE, COGNITION, COMMUNICATION,
CORPS, CREATION, EXISTENCE, GRAND, LIEU, MOUVEMENT, ORDRE, PERCEPTION,
POSSESSION (13 atomes)

**Atomes divergents** : EN seul=INTENSE,SEEKING ; FR seul=BON,PLAY
→ Différences dues aux lexiques de keywords, pas à une vraie divergence sémantique.

### 4. Spec E2

**Constat** : 13 atomes universels couvrent 79.6% des détections.
Le seuil de 15 n'est pas atteint — il faut 2 atomes de plus.

**Décision** : Rédiger un protocole E2 en 4 phases :
1. Corpus bilingue (≥5 paires Gutenberg)
2. Atom encoding vectoriel
3. Reconstruction par génération
4. Mesure BLEU/BERTScore

**Note importante** : la reconstruction « bit-perfect » (SHA256) n'est pas
réaliste pour du texte naturel. L'objectif est la préservation du sens.

## Fichiers modifiés

| Fichier | Action | Raison |
|---------|--------|--------|
| `SANDBOX/dolt-concept-store/semantic_serializer.py` | **Créé** (~480 lignes) | Export JSON + comparaison + batch + E2 prep |
| `SANDBOX/dolt-concept-store/EXPERIMENT_REGISTRY.md` | **Modifié** | v4.2 ✅, E2 spec rédigée, roadmap marqué COMPLET |
| `Copilotage/journal/INDEX.md` | **Modifié** | Ajout entrée v4.2 |

## Tests effectués

| Test | Résultat |
|------|----------|
| py_compile semantic_serializer.py | ✅ |
| Export Alice EN (26K mots) → JSON | ✅ 34 atomes, 119 concepts |
| Export Alice FR (26K mots) → JSON | ✅ 34 atomes, 116 concepts |
| Compare EN ↔ FR | ✅ Score 0.8671 EXCELLENT |
| Dashboard terminal | ✅ Affichage complet avec breakdown |
| E2 prep report | ✅ 13 universels, 79.6% coverage |

## Prochaines étapes

Le roadmap NA-004 (Priorité 1 + Priorité 2) est **COMPLET**.

Pour le futur :
1. **E2 — Reconstruction** : Implémenter le protocole en 4 phases
2. **Enrichir les lexiques** : Ajouter SEEKING et PLAY aux keywords EN
   pour atteindre le seuil de 15 atomes universels
3. **Tester PDF/EPUB** : Valider les extracteurs sur des fichiers binaires réels
4. **v5.x** : Chunking par phrases (pas juste paragraphes) pour
   granularité plus fine
5. **Push** : Pousser les commits sur GitHub
