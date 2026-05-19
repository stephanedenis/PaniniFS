# v4.7 — Expansion vocabulaire + Base d'interprétations hiérarchique

**Date** : 2026-02-20  
**Machine** : hauru (Xeon E5-2650, 62 GB)  
**Agent** : Claude Opus 4.6, session VS Code Copilot  
**Branche** : main  

## Contexte

Après la mesure de fidélité de reconstruction (v4.6), le taux de couverture
lexicale moyen était de **44,7 %** sur le corpus Gutenberg (11 textes, 313 548
mots, 8 langues). L'objectif : étendre massivement le vocabulaire pour avancer
vers la « restitution totale », et créer une base de données hiérarchique pour
stocker l'interprétation structurée des ouvrages.

## Décisions clés

### 1. Audit profond du vocabulaire (baseline)

**Constat** : La détection automatique de langue échouait sur 4/11 textes
(eo, it, fr, sa détectés comme « en »).  
**Décision** : Créer `vocabulary_audit.py` avec un `LANG_MAP` forçant les codes
langue depuis les noms de fichiers.  
**Impact** : Résultats fiables — baseline confirmé à 44,7 %, 36 410 mots non
couverts uniques.

### 2. Expansion massive des dictionnaires (33 atomes × 8 langues)

**Constat** : Les lacunes provenaient de :
- Mots-outils manquant des listes de stop-words (~15 %)
- Vocabulaire courant non mappé aux atomes (~25 %)
- Noms propres (~15 %)

**Décision** : Créer `vocabulary_expansion_v47.py` (~1 200 lignes) avec :
- `EXTRA_STOP_WORDS` : mots-outils additionnels pour en/fr/de/es/it/eo/fi/sa
- `EXPANSION_KEYWORDS` : ~2 000+ mots-clés nouveaux couvrant mouvement, perception,
  communication, mesure, temps, taille, agents, lieux, corps, etc.
- `EXTRA_PUNCTUATION_CHARS` : caractères de ponctuation étendue à filtrer

**Impact** : Couverture lexicale globale **44,7 % → 71,0 % (+26,3 pp)**

### 3. Résultats par langue

| Langue | Avant | Après | Delta |
|--------|------:|------:|------:|
| DE     | 68,0% | 92,1% | +24,1 |
| EN     | 57,7% | 85,8% | +28,1 |
| FR     | 50,4% | 71,8% | +21,4 |
| IT     | 47,9% | 71,3% | +23,4 |
| EO     | 42,0% | 68,0% | +26,0 |
| ES     | 39,9% | 60,6% | +20,7 |
| FI     | 34,4% | 55,4% | +21,0 |
| SA     | 25,8% | 31,1% |  +5,3 |

### 4. Base d'interprétations hiérarchique

**Constat** : Les analyses 7 couches étaient éphémères (recalculées à chaque run).
Il manquait un stockage persistant avec structure documentaire.  
**Décision** : Créer `panini-interpretations-db/` (Dolt) avec 7 tables :
- `corpora` — regroupement de haut niveau
- `works` — ouvrages individuels (métadonnées)
- `structural_units` — hiérarchie auto-référencée (partie → chapitre → paragraphe)
- `atom_profiles` — vecteur de distribution sur 34 atomes par unité
- `concepts` — concepts multi-atomes détectés par unité
- `rich_layers` — JSON des 7 couches complètes (réservé)
- `fidelity_metrics` — métriques de fidélité de reconstruction

**Impact** : Structure permettant la décomposition de haut niveau des ouvrages,
socle pour le volet PaniniFS « fichier = arbre d'interprétations ».

### 5. Pipeline d'ingestion

**Constat** : La BD existait mais était vide.  
**Décision** : Créer `interpretation_ingest.py` avec :
- Détection de chapitres pour 7 langues (en/fr/de/es/it/eo/fi)
- Analyse 7 couches complète par paragraphe
- Mode batch (IDs manuels + SQL groupé) → 12× plus rapide
- Profils d'atomes agrégés par chapitre

**Impact** : Ingestion de 11 ouvrages en 15,3 minutes.

### 6. Résultats d'ingestion

| Métrique | Valeur |
|----------|-------:|
| Ouvrages | 11 |
| Unités structurelles | 7 712 |
| Paragraphes analysés | 7 588 |
| Alignements atomiques | 118 670 |
| Concepts détectés | 31 625 |
| Couverture lexicale moyenne (DB) | 67,9 % |
| Readiness moyenne (DB) | 77,5 % |
| Meilleure langue (DE) | 89,1 % lex, 83,8 % RR |

## Fichiers créés

- `SANDBOX/dolt-concept-store/vocabulary_expansion_v47.py` — ~1 200 lignes
- `SANDBOX/dolt-concept-store/vocabulary_audit.py` — ~190 lignes
- `SANDBOX/dolt-concept-store/interpretation_ingest.py` — ~490 lignes
- `SANDBOX/dolt-concept-store/panini-interpretations-db/` — Dolt DB, 7 tables

## Fichiers modifiés

- `SANDBOX/dolt-concept-store/seven_layers_engine.py` — Import + merge v4.7 expansion
- `SANDBOX/dolt-concept-store/reconstruction_fidelity.py` — Import EXTRA_STOP_WORDS,
  EXTRA_PUNCTUATION_CHARS, mise à jour de get_stop_words() et get_content_words()

## Tests effectués

1. **Audit baseline** : `python3 vocabulary_audit.py` → 44,7 % ✅
2. **Post-expansion** : `python3 vocabulary_audit.py` → 71,0 % ✅
3. **Ingestion unitaire** : Alice EN → 871 paras, 13 283 atomes ✅
4. **Ingestion complète** : 11 ouvrages → 7 588 paras, 118K atomes, 15,3 min ✅
5. **Requêtes SQL** : Vérification des agrégats par ouvrage ✅

## Prochaines étapes

1. **Pousser la couverture > 80 %** — 2e round d'expansion (ES, FI, SA en retard)
2. **Sanskrit spécifique** — Le sanskrit reste à 31,1 %, nécessite un dictionnaire
   dédié avec formes sandhī et composés
3. **Stocker les rich_layers** — La table existe mais n'est pas encore alimentée
   (JSON des 7 couches par paragraphe)
4. **API de requête** — Exposer la hiérarchie documentaire via une API (concept
   search, atom profile similarity, etc.)
5. **Prototype PaniniFS haut niveau** — Utiliser la hiérarchie pour le montage
   « fichier = arbre d'interprétations sémantiques »
