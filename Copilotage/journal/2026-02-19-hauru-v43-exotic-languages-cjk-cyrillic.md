# v4.3 — Support langues exotiques : CJK + Cyrillique

**Date** : 2026-02-19 (session étendue, ~4h)  
**Machine** : hauru (Intel Xeon E5-2650, 8c/16t, 62GB RAM)  
**Agent** : GitHub Copilot (Claude Opus 4.6)  
**Commit parent** : `7399698` (Gutenberg Latin corpus, 37 textes, 7 langues)

---

## Contexte

Après validation du système sur 37 textes Gutenberg en 7 langues à alphabet
latin (EN, FR, DE, ES, IT, PT, NL — commit `7399698`), l'utilisateur demande
d'étendre le système aux langues « plus exotiques » : **chinois, japonais,
russe**. Ces langues utilisent des systèmes d'écriture radicalement différents
(sinogrammes, kana, cyrillique) et ne peuvent pas être traitées par le pipeline
existant basé sur `text.split()` et la correspondance de mots-clés latins.

## Décisions clés

### 1. Architecture du tokenizer CJK

- **Constat** : Le chinois et le japonais n'ont pas d'espaces entre les mots.
  `text.split()` produit 1-2 "mots" par paragraphe chinois → quasi-aucun atome
  détecté.
- **Décision** : Implémentation d'un tokenizer greedy longest-match sans
  dépendance externe (pas de jieba/MeCab). Construit un ensemble de mots-clés
  depuis `ATOM_KEYWORDS`, scanne le texte caractère par caractère en essayant
  la correspondance la plus longue d'abord.
- **Impact** : Fonctionne pour toutes les langues CJK sans bibliothèque NLP
  externe. Performances : ~100s pour 17K "mots" chinois (三國志演義).

### 2. Extraction de radicaux kanji pour le japonais

- **Constat** : Les verbes japonais apparaissent conjugués (走って, 逃げた) mais
  les mots-clés sont en forme dictionnaire (走る, 逃げる). Le tokenizer exact ne
  les matche pas.
- **Décision** : Ajout de `_extract_kanji_stems()` qui auto-extrait le radical
  kanji de chaque forme dictionnaire japonaise (走る→走, 逃げる→逃, etc.). Ces
  radicaux sont ajoutés automatiquement lors du merge.
- **Impact** : ~16 radicaux par atome en moyenne. 走→MOUVEMENT, 逃→MOUVEMENT,
  昔→ANCIEN, etc.

### 3. Correction de la détection structurelle CJK

- **Constat** : `classify_structural_text()` classifiait les textes CJK courts
  comme "chapter_heading" car `text == text.upper()` est vrai pour les
  sinogrammes (pas de distinction majuscule/minuscule).
- **Décision** : Ajout d'un guard `has_latin` avant la classification par casse.
- **Impact** : Les paragraphes CJK courts ne sont plus ignorés.

### 4. Bogue critique : SUPPORTED_LANGS

- **Constat** : `SUPPORTED_LANGS` dans `document_analyzer.py` ne contenait que
  7 langues latines (`en, fr, de, it, es, eo, fi`). Quand `lang='zh'` était
  passé en hint, il n'était pas reconnu → fallback vers `langdetect` → détection
  "en" (à cause de l'en-tête Gutenberg anglais) → tokenizer latin utilisé pour
  le chinois → 1-3 atomes au lieu de 33.
- **Décision** : Extension de `SUPPORTED_LANGS` à 12 langues incluant
  `zh, ja, ru, pt, nl`.
- **Impact** : Résolution immédiate du problème. Chinois passe de 1-3 à 33-34
  atomes par texte. Japonais de 9-12 à 30-34. Russe de 1 à 26-34.

### 5. IDs Gutenberg russes invalides

- **Constat** : Les 3 IDs originaux (#21183 Белые ночи, #21186 Записки,
  #19681 Детство) renvoient 404 — ce sont des projets audiobook sans fichier
  texte.
- **Décision** : Remplacement par des textes russes avec fichiers texte
  disponibles : #16527 (Рачинский), #14741 (Державин), #30774 (Апостол).
- **Impact** : 3 textes russes analysables, 26-34 atomes chacun.

### 6. Troncation de la distribution d'atomes

- **Constat** : `analyze_document()` ne renvoyait que `top_atoms[:15]` dans le
  rapport, et `semantic_serializer` utilisait ces 15 atomes pour la distribution
  exportée. Résultat : les profils de langues dans la matrice ne contenaient que
  15 atomes sur 34.
- **Décision** : Ajout d'un champ `all_atoms` au rapport, et utilisation de la
  distribution complète dans le sérialiseur et la matrice.
- **Impact** : Les exports et la matrice contiennent maintenant TOUS les atomes.

## Fichiers créés

| Fichier | Lignes | Description |
|---------|--------|-------------|
| `exotic_keywords.py` | ~560 | Mots-clés CJK+cyrillique (34 atomes × zh/ja/ru), particules, tokenizer CJK, extraction radicaux kanji |

## Fichiers modifiés

| Fichier | Modification |
|---------|-------------|
| `gutenberg_multilingual_validator.py` | Import + merge des mots-clés exotiques dans ATOM_KEYWORDS (5 lignes ajoutées après le dict) |
| `seven_layers_engine.py` | Import exotic_keywords, 3 profils linguistiques (zh/ja/ru ~170 lignes), tokenization CJK dans `analyze_syntax`, `align_words_to_atoms`, `detect_structural_operators`, merge EXOTIC_NEGATION/QUANTIFIER/MODAL |
| `morpho_semantic_bridge.py` | Guard `has_latin` dans `classify_structural_text` pour CJK |
| `gutenberg_ingest.py` | 15 entrées CATALOG exotiques (zh=8, ja=4, ru=3→remplacés), suppression troncation `[:15]` des profils de langue |
| `document_analyzer.py` | Extension SUPPORTED_LANGS (7→12 langues), ajout `all_atoms`/`all_concepts` au rapport |
| `semantic_serializer.py` | Utilisation de `all_atoms` au lieu de `top_atoms` pour la distribution exportée |

## Tests effectués

### Test unitaire exotic_keywords.py
- ✅ 34 atomes × 3 langues chargés
- ✅ Détection CJK (is_cjk_char) correcte
- ✅ Tokenizer CJK produit les bons tokens
- ✅ Merge dans ATOM_KEYWORDS fonctionne
- ✅ Radicaux kanji japonais extraits (走→走, 逃→逃)

### Test d'intégration phrases courtes
- ✅ Chinois : 走→MOUVEMENT, 看→PERCEPTION, 学→COGNITION, 子→AGENT (13/32 chars)
- ✅ Japonais : 走→MOUVEMENT, 逃→MOUVEMENT, 昔→ANCIEN, ある→EXISTENCE, 山→LIEU
- ✅ Russe : дороге→LIEU, думал→COGNITION, жизни/смерти→EXISTENCE

### Corpus complet (51 textes, 3.14M mots, 10.1 min)

| Langue | Textes | Mots | Atomes uniques |
|--------|--------|------|---------------|
| de | 5 | 179,208 | 34 ✅ |
| en | 15 | 1,183,524 | 34 ✅ |
| es | 2 | 450,813 | 34 ✅ |
| fr | 10 | 725,497 | 34 ✅ |
| it | 2 | 288,172 | 34 ✅ |
| **ja** | **3** | **3,041** | **34 ✅** |
| nl | 1 | 65,250 | 1 ⚠️ |
| pt | 2 | 99,730 | 3 ⚠️ |
| **ru** | **3** | **51,545** | **34 ✅** |
| **zh** | **8** | **95,547** | **34 ✅** |

### Similarités cosinus inter-scripts

| Paire | Cosine | Qualité |
|-------|--------|---------|
| FR↔ZH | **0.904** | Excellent |
| ZH↔JA | 0.805 | Très bon |
| DE↔ZH | 0.793 | Très bon |
| EN↔ZH | 0.789 | Bon |
| FR↔JA | 0.782 | Bon |
| EN↔JA | 0.735 | Bon |
| EN↔RU | 0.727 | Bon |
| ES↔RU | 0.740 | Bon |
| ZH↔RU | 0.608 | Modéré |
| JA↔RU | 0.529 | Modéré |

### Résultat majeur

**🏆 34/34 atomes universels à travers 8 langues et 3 systèmes d'écriture = 100% d'universalité**

(excluant nl et pt qui manquent de profils linguistiques dans le moteur)

## Limitations connues

1. **nl (néerlandais) et pt (portugais)** : 1-3 atomes détectés. Ils ne sont
   pas dans `LANGUAGE_PROFILES` du moteur, donc les mots fonctionnels sont
   traités comme du contenu anglais. Nécessite l'ajout de profils linguistiques.
2. **Tokenizer CJK greedy** : pas de segmentation linguistique réelle. Dépend
   entièrement du dictionnaire de mots-clés. Les mots CJK absents du
   dictionnaire ne sont pas détectés.
3. **Conjugaison russe** : seuls les radicaux correspondant aux mots-clés sont
   détectés. Pas de stemming morphologique.
4. **奥の細道 (Bashō)** : #20683 renvoie 404 sur Gutenberg. Texte manquant.

## Prochaines étapes

1. Ajouter les profils linguistiques `nl` et `pt` dans `seven_layers_engine.py`
   (déterminants, prépositions, conjonctions, pronoms)
2. Explorer un stemmer morphologique léger pour le russe
3. Ajouter le coréen (ko) — même infrastructure CJK déjà en place
4. Investiguer pourquoi la similarité JA↔RU est relativement basse (0.529)
5. Documenter les résultats d'universalité cross-scripts dans la documentation
   principale du projet
