# v4.4 — Support Indic : Hindi et Sanskrit (पाणिनि)

**Date** : 2026-02-20  
**Machine** : hauru (Xeon E5-2650, 62 Go RAM)  
**Agent** : GitHub Copilot (Claude Opus 4.6)  
**Version** : v4.4

---

## Contexte

« Et Panini qui est indien, l'a-t-on oublié ? » — Le projet PaniniFS tire
son nom de Pāṇini (पाणिनि, ~IVe siècle av. J.-C.), le grammairien indien
dont l'Aṣṭādhyāyī constitue le premier système formel de l'histoire de la
linguistique. Ironie : après 12 langues et 4 écritures, aucune langue indienne
n'était supportée.

Cette session corrige cet oubli symbolique en ajoutant Hindi (hi) et
Sanskrit (sa), portant le système à **14 langues, 5 écritures**.

## Décisions clés

### 1. Corpus Gutenberg quasi inexistant pour les langues indiennes
- **Constat** : 0 texte hindi, 1 seul texte sanskrit (pg9000 — Vishnu Sahasranaamam)
- **Décision** : Ajouter les mots-clés quand même (pour usage futur avec d'autres
  sources) et tester sur pg9000 malgré sa brièveté (~1458 mots)
- **Impact** : Hindi non testable sur Gutenberg ; Sanskrit testable via pg9000 uniquement

### 2. Sanskrit en double encodage : Devanagari + ITRANS
- **Constat** : pg9000 est en translittération ITRANS (ASCII), pas en Devanagari
- **Décision** : Inclure LES DEUX scripts dans les mots-clés Sanskrit —
  885 mots-clés au total (Devanagari pour textes futurs + ITRANS pour pg9000)
- **Impact** : Sanskrit a la densité de mots-clés la plus élevée (885 vs 545 pour l'anglais)

### 3. Devanagari : pas de tokeniseur spécial nécessaire
- **Constat** : Contrairement au CJK, le devanagari utilise des espaces entre les mots.
  Pas de casse (majuscule/minuscule). Le guard `has_latin` existant gère déjà
  correctement les textes devanagari (aucun caractère ASCII alpha).
- **Décision** : Pas de `is_devanagari_char()` ni de tokeniseur spécial —
  le tokeniseur whitespace standard suffit
- **Impact** : Intégration légère, même pattern que nl/pt (supplementary_keywords)

### 4. Résultat : 31/34 atomes dans pg9000
- **Constat** : 31/34 atomes détectés par substring, 30/34 via le pipeline complet
- **Manquants** : DISGUST, TEDIUM, DUALITÉ — cohérent car pg9000 est un hymne
  dévotionnel (liste de 1000 noms/épithètes de Vishnu), pas un récit narratif
- **Décision** : Accepter ce résultat comme excellent pour un texte aussi spécialisé

### 5. Inclusion des dhātu (racines verbales sanscrites)
- **Constat** : Les dhātu sont la base du système verbal sanskrit (10 gaṇa).
  Le codebase avait déjà des références dhātu dans `wikipedia_corpus_loader.py`
- **Décision** : Inclure les dhātu dans les mots-clés (ex: गम् gam, दृश् dRsh,
  भू bhuu) aux côtés des formes conjuguées
- **Impact** : Meilleure couverture des textes grammaticaux et philosophiques

## Fichiers modifiés

| Fichier | Action | Raison |
|---------|--------|--------|
| `indic_keywords.py` | **CRÉÉ** | 34 atomes × 2 langues (hi Devanagari + sa Devanagari/ITRANS), 538+885 mots-clés, LANGUAGE_PROFILES, NEG/QUANT/MOD |
| `gutenberg_multilingual_validator.py` | Modifié | Ajout merge indic_keywords (bloc v4.4) |
| `seven_layers_engine.py` | Modifié | Import HAS_INDIC, merge LANGUAGE_PROFILES + NEG/QUANT/MOD |
| `document_analyzer.py` | Modifié | Ajout 'hi', 'sa' à SUPPORTED_LANGS (14 langues) |
| `gutenberg_ingest.py` | Modifié | Ajout pg9000 au CATALOG (Sanskrit ITRANS) |
| `gutenberg_corpus/pg9000_sa.txt` | Téléchargé | Vishnu Sahasranaamam (ITRANS, ~14.8 Ko) |

## Tests effectués

### Vérification du merge
```
hi: 34/34 atoms, 538 keywords  ✅
sa: 34/34 atoms, 885 keywords  ✅
Total: 14 langues
```

### Analyse pg9000 (pipeline complet)
```
Language: sa
Atoms detected: 30 unique, 375 total detections
Top atoms: INTENSE(55), AGENT(37), EXISTENCE(35), ORDRE(24), BON(23)
Concepts: 9 unique, 12 total
WSD disambiguations: 56
Analysis time: 1.8s
```

### Couverture universelle
```
14 langues × 34/34 atomes = 100% couverture
5 écritures : Latin, CJK, Cyrillique, Devanagari, ITRANS
```

## Bilan des langues

| # | Langue | Code | Écriture | Mots-clés | Corpus Gutenberg |
|---|--------|------|----------|-----------|------------------|
| 1 | Anglais | en | Latin | 545 | 15 textes |
| 2 | Français | fr | Latin | 503 | 10 textes |
| 3 | Allemand | de | Latin | 443 | 5 textes |
| 4 | Espagnol | es | Latin | 432 | 2 textes |
| 5 | Italien | it | Latin | 430 | 2 textes |
| 6 | Espéranto | eo | Latin | 391 | (kw only) |
| 7 | Finnois | fi | Latin | 392 | (kw only) |
| 8 | Chinois | zh | CJK | 576 | 8 textes |
| 9 | Japonais | ja | CJK | 630 | 4 textes |
| 10 | Russe | ru | Cyrillique | 442 | 3 textes |
| 11 | Néerlandais | nl | Latin | 593 | 1 texte |
| 12 | Portugais | pt | Latin | 594 | 2 textes |
| 13 | **Hindi** | **hi** | **Devanagari** | **538** | **0 textes** |
| 14 | **Sanskrit** | **sa** | **Devanagari/ITRANS** | **885** | **1 texte** |

## Prochaines étapes

- [ ] Chercher des corpus hindi/sanskrit hors Gutenberg (Wikisource, DCS, GRETIL)
- [ ] Relier les dhātu du module `indic_keywords.py` au `simulate_dhatu_analysis()`
  existant dans `wikipedia_corpus_loader.py`
- [ ] Explorer l'ajout du bengali (bn) et du tamoul (ta) — autres langues majeures
  de l'Inde
- [ ] Ajouter un tokeniseur Devanagari qui gère le sandhi (jonction inter-mots
  en sanskrit classique)
- [ ] Ingestion massive via `gutenberg_ingest.py` avec le CATALOG mis à jour
