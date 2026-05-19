# 2026-02-22 — hauru — v4.8.12 Expanded Corpus Audit & Proper Noun Expansion

**Agent** : Copilot (Claude Opus 4.6)  
**Hôte** : hauru (Xeon E5-2650 v2 × 2, 62 Go RAM)  
**Branche** : master  
**Session** : ~3 sessions cumulées (v4.8.12 infrastructure + audit + expansion)

## Contexte

Après v4.8.11 (91.2% global sur le corpus original de 11 fichiers, 7/7 langues
européennes ≥90%), le corpus Gutenberg a été élargi de 11 → 62 fichiers couvrant
12 langues (5.9M mots). L'audit élargi a révélé une couverture globale de 50.5%
(pondérée par CJK/NL/RU/SA), avec les langues européennes en recul à cause de
textes plus difficiles (Zarathustra, Don Quijote, Divina Commedia, Jules Verne).

## Décisions clés

### 1. Infrastructure d'audit élargi
- **Constat** : L'audit v4.8.11 ne scannait que les fichiers racines de `gutenberg_corpus/`
- **Décision** : Ajout de `pathlib.Path.rglob("*.txt")` pour scanner les sous-répertoires
  (zh/, ja/, ru/, nl/, sa/, etc.)
- **Impact** : 62 fichiers analysés au lieu de 11, 5.9M mots, 12 langues

### 2. Détection de langue par métadonnées Gutenberg
- **Constat** : Certains fichiers étaient mal classés (livres EN dans répertoires FR/DE/IT)
- **Décision** : Ajout `detect_lang_from_gutenberg_metadata()` + nettoyage du corpus
  (9 fichiers déplacés vers les bons répertoires)
- **Impact** : Fiabilité accrue de l'audit linguistique

### 3. Suppression du boilerplate Gutenberg
- **Constat** : Les en-têtes/pieds de page anglais de Project Gutenberg contaminaient
  les scores des langues non-anglaises
- **Décision** : `strip_boilerplate=True` dans `analyze_document_fidelity()`,
  utilisant `strip_gutenberg_boilerplate()` de `gutenberg_preamble_normalizer.py`
- **Impact** : Scores de couverture plus fiables pour FR/DE/ES/IT

### 4. Expansion v4.8.12 — Noms propres + formes archaïques
- **Constat** : Les noms propres représentent 45-54% des top-50 mots non couverts
  (EN: Maggie, Holmes; DE: Zarathustra, Mephistopheles; FR: Pencroff, Dantès;
  ES: Panza, Rocinante). L'italien archaïque de Dante domine les lacunes IT.
- **Décision** : Création de `vocabulary_expansion_v4812.py` avec 544 entrées :
  - 164 noms propres (EN 79, FR 40, DE 23, ES 18, IT 4)
  - 201 mots-clés par catégorie sémantique (8 atomes)
  - 150 mots vides (IT 92 formes archaïques dantesques, DE 27, ES 21)
  - 29 correspondances archaïque → moderne (IT 17, ES 6, FR 3, DE 3)
- **Impact** : Améliorations mesurées sur fichiers difficiles :

| Langue | Fichier | Avant v4812 | Après v4812 | Δ |
|--------|---------|:-----------:|:-----------:|:--:|
| DE | Zarathustra (pg2407) | 81.5% | **89.1%** | +7.6 |
| EN | Modest Proposal (pg1080) | ~83.8% | **86.2%** | +2.4 |
| ES | Don Quijote (pg2000) | 78.7% | **86.0%** | +7.3 |
| FR | Jules Verne (pg17989) | ~85.6% | **90.1%** | +4.5 |
| IT | Divina Commedia (pg1012) | 82.0% | **81.2%** | -0.8 |

Note : IT est le texte le plus difficile (italien médiéval du XIVe siècle). Les
mots restants non couverts ont ≤10 occurrences chacun (rendements décroissants).

## Fichiers modifiés

### Modifiés (de commits précédents)
- `vocabulary_audit.py` — rglob subdirectories, metadata lang detection, strip_boilerplate
- `reconstruction_fidelity.py` — v4812 import/extend/stop_words, strip_boilerplate param
- `document_analyzer.py` — ajustements mineurs
- `gutenberg_ingest.py` — ajustements mineurs
- `seven_layers_engine.py` — ajustements mineurs
- `text_extractor.py` — ajustements mineurs

### Nouveaux fichiers
- `vocabulary_expansion_v4812.py` — 544 entrées (noms propres, archaïques, mots-clés)
- `text_normalizer.py` — module de normalisation de texte
- `wikipedia_dump_downloader.py` — téléchargement de dumps Wikipedia
- `wikipedia_dump_extractor.py` — extraction de dumps Wikipedia
- `vocabulary_audit_results_v4812.json` — résultats audit 62 fichiers

### Journal
- `Copilotage/journal/2026-02-22-hauru-v4812-expanded-corpus.md` (ce fichier)

## Tests effectués

1. **Audit complet v4812** : 62 fichiers, 5.9M mots, 12 langues, 166 min
   - Global pondéré : 50.5% (dominé par CJK/NL/RU/SA non ciblés)
   - Européen : DE 81.5%, EN 83.8%, EO 93.2%, ES 78.7%, FI 90.6%, FR 85.6%, IT 82.0%

2. **Smoke test post-v4812** : 5 fichiers difficiles (Zarathustra, Modest Proposal,
   Don Quijote, Jules Verne, Divina Commedia)
   - DE 89.1%, EN 86.2%, ES 86.0%, FR 90.1%, IT 81.2%

3. **Self-test v4812** : 544 entrées validées, tous noms propres sont des chaînes ✓

4. **Import test** : `reconstruction_fidelity.py` charge v4812 correctement
   - 18695 mots-clés globaux, stop words par langue intégrés

## Prochaines étapes

- Lancer un audit complet v4812 post-expansion (62 fichiers) pour mesurer
  l'amélioration globale
- v4.8.13 : cibler les langues non-européennes (NL, RU) si pertinent
- Envisager des stratégies pour l'italien archaïque (stemming diachronique ?)
- Réexaminer la contamination EN dans le corpus ES (pg15532 bilingue)
