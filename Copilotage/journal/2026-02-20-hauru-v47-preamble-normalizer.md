# v4.7 : Normalisation des préambules Gutenberg & détection de citations multilingues

**Date** : 2026-02-20  
**Machine** : hauru  
**Agent** : Copilot Claude Opus 4.6  

## Contexte

Les fichiers texte du Projet Gutenberg contiennent des blocs génériques
(licence, crédits, conditions d'utilisation) qui peuvent apparaître dans une
langue différente de celle du contenu littéraire. Par exemple, *Die Verwandlung*
de Kafka (pg2229, allemand) a un en-tête et un pied de page intégralement en
anglais. Ces blocs polluaient l'analyse atomique en introduisant des mots
anglais dans des textes allemands, français, espagnols, etc.

De plus, les textes littéraires contiennent souvent des citations en langues
étrangères (latin *ad hoc*, *cogito ergo sum*, citations directes en anglais
dans un roman français) qu'il faut pouvoir identifier distinctement du corps
principal.

Enfin, un même ouvrage peut exister dans plusieurs formats (txt, html, epub)
sur Gutenberg : il faut pouvoir les réunir dans une vue unifiée pour comparer
les profils atomiques inter-formats.

## Décisions clés

### D1 : Module dédié plutôt qu'extension de l'existant
- **Constat** : `strip_gutenberg_header_footer()` existait en 2 copies (dans
  `gutenberg_multilingual_validator.py` et `text_extractor.py`) avec une logique
  purement basée sur les marqueurs `*** START/END ***`.
- **Décision** : Créer `gutenberg_preamble_normalizer.py` comme module autonome
  avec classification par zones (9 types), puis intégrer par délégation.
- **Impact** : Rétrocompatibilité totale. L'ancien `strip_gutenberg_header_footer`
  délègue au nouveau module quand disponible.

### D2 : Fingerprinting multilingue des préambules
- **Constat** : Les préambules Gutenberg existent en EN, FR, DE, ES, IT, NL, PT,
  FI, EO. Ils expriment tous le même sens (licence libre).
- **Décision** : Créer des dictionnaires de fingerprints par langue
  (`GUTENBERG_HEADER_FINGERPRINTS`, `GUTENBERG_FOOTER_FINGERPRINTS`) et un score
  combiné qui pondère la proportion × le nombre absolu de matches.
- **Impact** : Le header EN d'un texte DE est reconnu comme identique au header
  DE d'un texte FR. Chaque zone boilerplate porte `semantic_id =
  GUTENBERG_PREAMBLE_LICENCE` et `equivalent_across_languages = True`.

### D3 : Détection de citations par 4 méthodes en cascade
- **Constat** : Les citations étrangères échappent à langdetect (trop courtes).
- **Décision** : Pipeline en 4 niveaux :
  1. **Phrases latines connues** (34 locutions, conf=0.95)
  2. **Délimiteurs** (_italiques_, «guillemets», "quotes") + trigram analysis
  3. **Changement de script** (cyrillique, CJK, devanagari, grec, arabe, hébreu)
  4. **Paragraphes entiers** par trigrammes (conf > 0.5)
- **Impact** : Détecte _ad hoc_, _cogito ergo sum_, « Oh dear! I shall be late! »
  dans un texte français. Pas de faux positifs dans du texte monolingue pur.

### D4 : Re-synthèse multi-format via UnifiedWork
- **Constat** : Un même ouvrage (ex: Alice) peut avoir txt, html, epub sur Gutenberg.
- **Décision** : Dataclass `UnifiedWork` qui agrège les `EditionFormat` d'un même
  ouvrage, avec comparaison inter-formats (word count CV, cosinus atomique).
- **Impact** : Prêt pour la comparaison txt/html/epub quand les formats seront
  téléchargés.

### D5 : Détection de trigrammes adaptée aux textes courts
- **Constat** : `langdetect` est peu fiable sur < 100 mots. Les textes NL et PT
  étaient déjà mal détectés (journal D4 du 2026-02-19).
- **Décision** : `_detect_language_trigram()` — extraction de trigrammes à partir
  des mots, intersection avec des profils de référence pour 8 langues + latin.
- **Impact** : Détection correcte EN/FR/DE/ES/IT même sur 10 mots. Utilisé pour
  les citations, pas pour le document entier.

## Fichiers modifiés

| Fichier | Raison |
|---------|--------|
| `SANDBOX/dolt-concept-store/gutenberg_preamble_normalizer.py` | **Créé** (~1160 lignes). Module principal : zone classifier, citation detector, format re-synthesizer |
| `SANDBOX/dolt-concept-store/test_gutenberg_preamble.py` | **Créé** (~400 lignes). 21 tests : normalisation, citations, trigrammes, zones, intégration |
| `SANDBOX/dolt-concept-store/gutenberg_multilingual_validator.py` | **Modifié** : import conditionnel du normalizer, `strip_gutenberg_header_footer()` accepte un paramètre `lang` et délègue |

## Tests effectués

### Tests unitaires (21/21 ✅)
- `TestPreambleNormalization` (10 tests) : headers EN/FR/DE, footers, semantic_id,
  strip body only, boilerplate scoring
- `TestForeignCitationDetection` (3 tests) : latin phrases, English in French,
  no false positives
- `TestLanguageTrigramDetection` (4 tests) : EN, FR, DE, exclusion
- `TestZoneClassification` (2 tests) : title page, full coverage
- `TestIntegrationWithValidator` (2 tests) : backward compat, lang parameter

### Validation sur corpus réel
- **pg55456 (FR, Alice Bué)** : header EN (0.750), body 88.5%, 41 illustrations,
  footer EN (score élevé). ≡IDENTICAL_SENSE sur les deux blocs boilerplate.
- **pg11 (EN, Alice Carroll)** : header détecté, body 99.9%, footer détecté.
- **pg2229 (DE, Kafka Verwandlung)** : header EN (0.560), body 90.6%,
  footer EN (1.000). Les blocs EN sont correctement identifiés comme boilerplate
  même dans un texte allemand.

## Prochaines étapes

1. **Intégrer dans `gutenberg_ingest.py`** : utiliser `classify_gutenberg_zones()`
   dans le pipeline d'analyse pour exclure le boilerplate de l'analyse atomique.
2. **Intégrer dans `text_extractor.py`** : remplacer la logique de strip inline.
3. **Télécharger les formats HTML/EPUB** de Gutenberg pour tester la re-synthèse
   multi-format.
4. **Raffiner les faux positifs** : la détection par délimiteur avec conf < 0.15
   produit du bruit (mots courts EN détectés comme DE par trigram). Envisager un
   seuil adaptatif.
5. **Ajouter les trigrammes** pour les langues manquantes (zh, ja, ru, hi, sa) —
   actuellement seules les langues latines sont couvertes par le trigram detector.
