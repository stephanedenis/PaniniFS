# v4.0–v4.1 : Pont texte multi-format ↔ moteur d'atomes

- **Date** : 2026-02-19
- **Machine** : hauru (Intel Xeon E5-2650, 62 GB RAM)
- **Agent** : GitHub Copilot (Claude Opus 4.6)
- **Référence roadmap** : NA-004, Priorité 2 (v4.0 → v4.1)

---

## Contexte

Les priorités linguistiques (v2.5 ENT, v2.6 QUAL, v2.7 WSD+struct ops) sont
terminées. Le modèle couvre désormais 35 atomes en 4 catégories, 120 concepts,
WSD POS-aware et opérateurs structurels. Il est temps de connecter ce moteur
à des documents réels : le **pont texte multi-format**.

## Décisions clés

### 1. Choix des bibliothèques d'extraction

**Constat** : requirements.txt ne contient que des dépendances MkDocs.
Les seules libs texte déjà installées étaient bs4, markdown_it, chardet.

**Décision** : Installer 4 paquets supplémentaires :
- `pdfminer.six` (v2026-01-07) — extraction PDF page par page
- `ebooklib` (v0.20) — lecture EPUB
- `python-docx` (v1.2.0) — lecture DOCX
- `langdetect` (v1.0.9) — détection de langue

**Impact** : Support 6 formats (PDF, EPUB, DOCX, HTML, Markdown, TXT) sans
dépendances lourdes.

### 2. Architecture extracteur unifié (text_extractor.py)

**Constat** : Le pipeline existant ne supporte que du texte brut pré-découpé
en paragraphes, sans notion de format d'entrée.

**Décision** : Créer `text_extractor.py` (~420 lignes) avec :
- `detect_format()` : détection par magic numbers (PDF `%PDF-`, ZIP `PK\x03\x04`
  → discrimination EPUB/DOCX par contenu) + fallback extension
- Dataclasses `ExtractionResult` et `ExtractedParagraph`
- 6 extracteurs format-spécifiques (`_extract_pdf/epub/docx/html/markdown/txt`)
- Stripping header/footer Gutenberg **case-insensitive** (bug corrigé en test)
- CLI standalone

**Impact** : Interface unifiée `extract_document(path) → ExtractionResult`
utilisable depuis n'importe quel orchestrateur.

### 3. Architecture orchestrateur (document_analyzer.py)

**Constat** : Il faut chaîner extraction → détection langue → analyse 7 couches
→ stockage, ce qui nécessite un orchestrateur dédié.

**Décision** : Créer `document_analyzer.py` (~310 lignes) avec :
- `detect_language()` : langdetect seeded (déterministe) + fallback trigrams
- `analyze_paragraph()` : syntaxe → atomes (WSD) → morpho → struct_ops → concepts
- `analyze_document()` : pipeline complet avec accumulation de stats
- `_store_document_analysis()` : table Dolt `document_analyses` (14 colonnes)
- CLI argparse avec `--lang`, `--format`, `--store`, `--verbose`, `--json`

**Impact** : Un seul appel `python document_analyzer.py mon.pdf --store`
analyse un document complet et stocke les résultats en Dolt.

### 4. Bug Gutenberg case-sensitivity

**Constat** : Les fichiers Gutenberg utilisent `*** START OF THE PROJECT
GUTENBERG EBOOK ***` en majuscules, mais le code cherchait `Project Gutenberg`
(mixed case).

**Décision** : Rendre toute la détection Gutenberg case-insensitive
(`text.upper().find(marker.upper())`).

**Impact** : Alice in Wonderland (11.txt) correctement strippée : 816 → 814
paragraphes après suppression header/footer.

## Fichiers modifiés

| Fichier | Action | Raison |
|---------|--------|--------|
| `SANDBOX/dolt-concept-store/text_extractor.py` | **Créé** (~420 lignes) | Extracteur texte unifié 6 formats |
| `SANDBOX/dolt-concept-store/document_analyzer.py` | **Créé** (~310 lignes) | Orchestrateur fichier → atomes → Dolt |
| `SANDBOX/dolt-concept-store/EXPERIMENT_REGISTRY.md` | **Modifié** | v4.0 et v4.1 marqués ✅ avec résultats |
| `Copilotage/journal/INDEX.md` | **Modifié** | Ajout entrée v4.0–v4.1 |

## Tests effectués

### text_extractor.py

| Test | Résultat |
|------|----------|
| README.md (Markdown) | ✅ 49 paragraphes, 523 mots, titre détecté |
| CONTRIBUTING.md (Markdown) | ✅ 35 paragraphes, 346 mots, titre détecté |
| index.html (HTML, page redirect) | ⚠️ 0 paragraphes (fichier vide, attendu) |
| Format detection (README/index/mkdocs) | ✅ md/html/txt correctement détectés |
| Alice 11.txt (Gutenberg TXT) | ✅ 814 para, 26521 mots, header/footer strippés |
| Compilation py_compile | ✅ Pas d'erreurs syntaxiques |

### document_analyzer.py

| Test | Résultat |
|------|----------|
| README.md --verbose | ✅ 1.05s, 25 atomes (top: COMMUNICATION 15), 18 concepts, 3 WSD |
| Alice 11.txt --verbose | ✅ 20.4s (41 para/s), 34 atomes, 119 concepts, 593 WSD, NEG=304/QUANT=378/MOD=348 |
| README.md --store | ✅ Table `document_analyses` créée, 1 row insérée, vérifiée via `dolt sql` |
| Détection de langue | ✅ README→fr, Alice→en (auto-detected) |
| Compilation py_compile | ✅ Pas d'erreurs syntaxiques |

### Métriques clés

| Métrique | README.md | Alice 11.txt |
|----------|-----------|-------------|
| Paragraphes | 49 | 814 |
| Mots | 523 | 26 521 |
| Temps analyse | 1.05s | 20.4s |
| Débit | 80 para/s | 41 para/s |
| Atomes uniques | 25 | 34 |
| Concepts uniques | 18 | 119 |
| WSD disambiguations | 3 | 593 |
| Opérateurs NEG | 4 | 304 |
| Opérateurs QUANT | 3 | 378 |
| Opérateurs MOD | 1 | 348 |

## Prochaines étapes

1. **v4.2 — Round-trip et E2** : Sérialiser les atomes extraits d'un document
   (JSON/CBOR), comparer traductions d'un même texte (FR/EN), mesurer universalité
2. **Tests PDF/EPUB/DOCX** : Trouver des fichiers de test pour valider les
   extracteurs non-TXT/MD
3. **Ajout requirements.txt** : Décider si les libs text_extractor doivent être
   dans requirements.txt (actuellement installées système uniquement)
4. **Optimisation gros documents** : Le débit baisse de 80 à 41 para/s sur
   des documents longs — investiguer si c'est le spaCy/morpho qui ralentit
