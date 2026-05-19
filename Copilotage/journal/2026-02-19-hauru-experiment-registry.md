# 📓 Journal — 2026-02-19 : Registre des expérimentations + audit documentation

**Host** : hauru
**Agent** : GitHub Copilot (Claude Opus 4.6)
**Session** : v2.4b (convention vX.Y remplace l'ancien « Phase N »)

---

## Contexte

Suite de la session du 18 février (ajout de 7 atomes ABS, journal obligatoire,
pre-commit hook, reconstitution de 10 journaux). Le moteur `seven_layers_engine.py`
tourne depuis 08:44 (PID 668992) avec le nouveau `step4b_corpus_quality_upgrade()`.

L'utilisateur demande :
1. Documenter tout le processus en détail avec références au journal
2. Ne pas committer tant que le process tourne (v2.4b en cours)
3. Vérifier s'il existe une bonne documentation de toutes les phases/expérimentations

## Décisions clés

### 1. Audit : 3 systèmes de numérotation « Phase » non reliés

- **Constat** : Le mot « Phase » est massivement surchargé dans l'écosystème.
  Trois systèmes indépendants coexistent sans document les reliant :
  - **Système A** (Panini-FS) : Phases 1→10.8.3 du Spec Kit Rust (août 2025)
  - **Système B** (Panini) : Phases P1→P4 de migration repo (sept 2025)
  - **Système C** (SANDBOX) : « Phase 17, 35, 36 » = compteur de sessions agent
- **Décision** : Déprécier la numérotation « Phase N ». Adopter les **versions
  sémantiques** (v2.3, v2.4, etc.) comme référence canonique et les **identifiants
  d'expérience** (E1, E2, ...) pour les hypothèses formelles.
- **Impact** : Clarté, traçabilité, fin de la confusion.

### 2. Trou noir « Phases 18–34 »

- **Constat** : Le journal v2.4 mentionne « Phase 36 » et « Phase 35 ».
  Le document de revue interdisciplinaire mentionne « Phase 17 ».
  Les phases 18 à 34 n'existent nulle part.
- **Décision** : Ces « phases » étaient vraisemblablement un compteur cumulé
  de sessions agent sur l'ensemble de l'écosystème (pas spécifique au concept
  store). Les sessions 18-34 ont eu lieu sur d'autres repos sans documentation.
  Ce trou est documenté mais non comblable rétrospectivement.
- **Impact** : Le registre note explicitement cette lacune.

### 3. Création du registre central `EXPERIMENT_REGISTRY.md`

- **Constat** : Aucun document ne centralise l'historique des versions, des
  expériences formelles (E1, E2) et des sessions, avec les commits et journaux
  associés.
- **Décision** : Créer `SANDBOX/dolt-concept-store/EXPERIMENT_REGISTRY.md`
  contenant :
  - Les 2 expériences formelles (E1 validée, E2 planifiée)
  - L'historique complet des versions v0.1 → v2.4b
  - La chronologie consolidée 2020–2026
  - Les liens vers chaque journal et chaque commit
  - Les lacunes documentaires connues
  - La convention de nommage adoptée
- **Impact** : Premier document de référence unique pour tout le processus
  expérimental.

### 4. E1 — Validité réévaluée

- **Constat** : L'expérience E1 (FORMAT-SEMANTIC UNIVERSALITY) est déclarée
  « HYPOTHESIS SUPPORTED » avec 99.95% fidélité. Mais l'analyse détaillée
  du code (session 2026-02-18) révèle que :
  - Phase 3 mesure le temps de lecture, pas la décomposition sémantique
  - Phase 4 calcule un ratio structurel, pas une reconstruction effective
  - Le corpus est auto-généré (5.6 KB)
- **Décision** : Documenter ces limites dans le registre. Planifier E2
  (reconstruction bit-perfect sur fichiers réels) comme prochaine expérience.
- **Impact** : Honnêteté scientifique. E1 reste valide pour ce qu'elle
  prouve (détection format + hashing) mais les claims sont recalibrées.

### 5. Process v2.4b en cours — pas de commit

- **Constat** : `seven_layers_engine.py` tourne depuis 08:44 (PID 668992).
  Le step4b fait des UPDATEs dans la base Dolt. Committer pendant l'exécution
  risquerait de créer un état incohérent.
- **Décision** : Tous les fichiers créés/modifiés aujourd'hui restent staged
  mais non commités. Le commit sera fait après la fin du process et la
  vérification des résultats step4b.
- **Impact** : Intégrité des données Dolt préservée.

### 6. Résultats intermédiaires step4b (observés pendant l'exécution)

- **Constat** : Pendant que le process tourne, les tiers de qualité ont évolué.
  Distribution Dolt observée à ~10:30 :

  | Tier | Avant (v2.4) | Pendant step4b | Δ |
  |------|-------------|----------------|---|
  | A    | 49          | **78**         | +29 |
  | B    | 46          | **25**         | -21 |
  | C    | 9           | **2**          | -7 |

  29 concepts upgradés par preuve empirique (détections corpus ≥20→A, ≥5→B).
  Les 2 C restants : PROXIMITÉ (4 détections), DÉGOÛT (1 détection).
  Les 2 B sans détection (DEMEURER, HAIR) : termes absents du corpus Alice/Candide.

### 7. Étude LLVM — Verdict : ❌ Non pertinent pour PaniniFS

- **Constat** : LLVM est une infrastructure de compilation (représentation de code
  exécutable). PaniniFS fait de la transformation de données (décomposition/
  reconstruction de formats binaires). Le mismatch est fondamental.
- **Analyse détaillée** :
  - **LLVM IR** : conçu pour SSA/registres/contrôle de flux ≠ atomes sémantiques/chunks/ontologie
  - **LLVM JIT** : les hot paths PaniniFS sont I/O-bound (lecture DB, décompression)
    pas compute-bound → JIT n'accélérerait rien. Latence JIT (5-50ms) = budget FUSE entier.
  - **Passes custom** : complexité astronomique pour bénéfice nul (optimisation
    algorithmique en Rust est plus efficace)
  - **Rust interop** : `rustc` compile déjà via LLVM → les optimisations sont déjà là
    (LTO, PGO, auto-vectorisation). Ajouter `inkwell` = double LLVM, 200MB de dépendance.
- **Alternatives recommandées** :
  - ✅ **WASM plugins** (Wasmtime/Extism) pour les parsers de format extensibles
  - ✅ **`winnow`/`nom`** pour le parsing binaire performant
  - ✅ **`binrw`/`deku`** pour les structures binaires déclaratives
  - ✅ **`aho-corasick`** pour le multi-pattern matching sémantique
  - ✅ **Cargo LTO+PGO** pour les optimisations LLVM *via rustc*
  - 🟡 **Tree-sitter** pour l'analyse sémantique de fichiers texte/code
  - ❌ Cranelift — même problème que LLVM (pas besoin de JIT)
- **Impact** : L'étude clarifie la stack Rust cible. Documentée dans le registre.

### 8. Stratégie WASM unifiée : serveur + browser + visualisation

- **Constat** : L'utilisateur fait remarquer que WASM ne sert pas seulement
  côté serveur (plugins format) mais ouvre 3 surfaces avec le même code Rust :
  1. **PaniniFS-Web** — version navigateur de la décomposition (démo sans serveur)
  2. **Graphes de concepts** — visualisation interactive des 104 concepts, formules,
     co-occurrences (le moteur sémantique en WASM + D3.js/Cytoscape.js pour le rendu)
  3. **Docs dynamiques** — composants WASM intégrés dans MkDocs via `extra_javascript`
     pour des exemples interactifs dans la documentation
- **Décision** : Adopter WASM comme **stratégie de convergence**, pas juste comme
  format de plugin. L'architecture cible : `panini-core` (Rust) compilé vers 3 targets
  (`x86_64-linux`, `wasm32-wasi`, `wasm32-unknown-unknown`). Même code partout.
- **Code existant** : `web-ui/src/pages/AtomExplorer.tsx` (React, appels API REST)
  pourrait évoluer vers un explorer alimenté par WASM local au lieu d'un serveur.
- **Impact** : Pas de réécriture JavaScript du moteur sémantique. Le Rust compilé
  en WASM sert le browser directement. Documenté dans le registre §NA-002.

## Fichiers modifiés / créés

| Fichier | Action | Raison |
|---------|--------|--------|
| `SANDBOX/dolt-concept-store/EXPERIMENT_REGISTRY.md` | **Créé** | Registre central des expérimentations |
| `Copilotage/journal/2026-02-19-hauru-experiment-registry.md` | **Créé** | Ce journal |
| `Copilotage/journal/INDEX.md` | Mis à jour | Nouvelle entrée |

### Rappel : fichiers non commités de la session 2026-02-18

- `import_panlang_v2.py` — 7 atomes ABS, compute_primary_category() refondu
- `gutenberg_multilingual_validator.py` — +608 keywords ABS
- `seven_layers_engine.py` — CONCEPT_MAPPINGS 78→95, step4b ajouté
- `AGENT_CONVENTION.md` — Règle journal obligatoire
- `.github/copilot-instructions.md` — Instructions Copilot (4 règles)
- `scripts/hooks/pre-commit` — Hook bloquant
- `Copilotage/elargissement-horizon-mathematiques-physique.md` — RFC math/physique
- 11 fichiers journal (1 session + 10 reconstitués)

## Tests effectués

- ✅ Process seven_layers_engine.py vérifié en cours (PID 668992, uptime 1h30+)
- ✅ Audit des 3 systèmes de numérotation Phase complété
- ✅ Registre croisé avec git log (494 commits dans Panini-FS)
- ✅ Vérification liens journal↔commit dans le registre

### 9. Audit panoramique des 14 repos — Inventaire des idées manquantes

- **Constat** : L'EXPERIMENT_REGISTRY.md ne couvre que le Concept Store Dolt
  (v0.1→v2.4b, E1, E2, NA-001/NA-002). L'écosystème compte **14 repos GitHub**
  avec ~200 fichiers Markdown, ~150 scripts Python, et des dizaines de concepts
  dispersés. Un audit systématique révèle **~130 idées** dont seulement **15 (12%)**
  étaient formellement documentées dans le registre.
- **Méthode** : Exploration récursive de chaque repo (structure, README, TODO/FIXME,
  git log, fichiers .py/.md/.yml/.toml/.json). 3 sous-agents parallèles : Panini main,
  Panini-FS, 12 repos satellites.
- **Découvertes majeures non inventoriées** :
  1. **LLM2Symbolic** (Panini-Research) — Pont neuro-symbolique mapping attention
     heads LLM → dhātu. 18 fichiers, ~40% avancé, roadmap Q1-Q2 2026. ABSENT de tout registre.
  2. **Universal IP Engine** (Panini-Research) — Provenance, licensing, attribution,
     audit, signatures digitales. 183 fichiers, 73 tests, ~15,950 lignes. COMPLET mais invisible.
  3. **PanLang 147 concepts** (Panini-Research) — 61 primitifs NSM + 51 molécules +
     35 composés. Greimas, dhātu mappings, interfaces web. 97 fichiers. Non référencé.
  4. **Chunker sémantique** (Panini-FS `src/`) — 957 lignes, 13 grammaires, v0.2.2.
     Code fonctionnel non mentionné dans aucun registre.
  5. **Audio fingerprinting** (Panini-FS `src/`) — 482 lignes, constellation map,
     Shazam-like. v0.3.0. Fonctionnel et invisible.
  6. **Web UI Phase 7** (Panini-FS `web-ui/`) — 3 pages React (DeduplicationDashboard,
     AtomExplorer, FileUploadAnalysis) sans backend. Phase 8 FUSE planifiée.
  7. **~70 fichiers Python vides** (Panini-FS `Copilotage/`, racine) — Plan fantôme
     d'automatisation jamais implémenté.
  8. **28 workflows GitHub Actions désactivés** — CI/CD ambitieux désormais dormant.
  9. **7 repos coquilles vides** à archiver (AttributionRegistry, AutonomousMissions,
     CloudOrchestrator, DatasetsIngestion, PublicationEngine, SemanticCore, UltraReactive).
  10. **Pensine-Web v0.0.22** — Produit fonctionnel (Logseq replacement) absent du roadmap FS.
- **Décision** : Créer `Copilotage/IDEAS_INVENTORY.md` — inventaire complet de
  toutes les idées, classées par domaine (12 sections), maturité (7 niveaux), et
  présence/absence dans le roadmap. 130 items au total.
- **Impact** : Le roadmap peut maintenant être rebâti sur une base factuelle.
  L'inventaire montre que seulement 15% du travail est formellement suivi.

### 10. Nouvelles directions : inférence symbolique parallèle, réseaux bayésiens, modèles probabilistes

- **Constat** : Le pipeline actuel (7 couches, import_panlang_v2) est purement
  déterministe : dictionnaires de keywords → mapping mot→atome. Pas de propagation
  d'inférence, pas de quantification de l'incertitude, pas de résolution probabiliste
  de la polysémie.
- **Décision** : Ajouter 3 axes de recherche complémentaires (#131-133 dans l'inventaire) :
  1. **Moteur d'inférence symbolique massivement parallèle** — Rete/Datalog compilé sur
     le graphe de 104+ concepts, chaînage avant/arrière, résolution de contraintes,
     détection de contradictions. GPU/WASM parallèle.
  2. **Réseaux bayésiens sur les dhātu** — DAG causal appris sur les co-occurrences
     du corpus Gutenberg (445 paragraphes × 7 langues). P(atome|contexte) pour
     remplacer l'heuristique de polysémie.
  3. **Modèles probabilistes** — LDA/ETM sur séquences d'atomes (thèmes émergents),
     CRF pour dépendances contextuelles, modèles de mélange par langue/registre/époque,
     quantification de la confiance de chaque attribution.
- **Synergie** : les 3 axes convergent vers le remplacement des mappings déterministes
  manuels par un système appris+probabiliste, tout en gardant la transparence
  symbolique (explicabilité = avantage vs pure deep learning).
- **Impact** : Documenté dans EXPERIMENT_REGISTRY.md §NA-003 et IDEAS_INVENTORY.md #131-133.

### 11. Analyse de convergence — Cartographie des connexions entre 133 idées

- **Constat** : L'inventaire de 133 idées n'est pas une liste plate. Le graphe de
  dépendances révèle 5 hubs gravitationnels, 3 chemins critiques, 6 synergies
  cachées entre repos, 4 contradictions à résoudre, et 5 liens manquants évidents.
- **Décision** : Ajouter une section §13 « Analyse de convergence » à l'inventaire
  avec les résultats complets de l'étude.
- **Découvertes clés** :
  1. **MÉGA-HUB : les dhātu** — 9+ connexions, centre gravitationnel absolu, mais
     le nombre de primitifs est instable (7, 9, 10, 23, 30, 61 selon les sources).
     C'est la contradiction #1 bloquante.
  2. **Raisonneur hybride** — Les 3 axes NA-003 (symbolique/bayésien/probabiliste)
     forment une architecture empilée naturelle : le symbolique donne la rigueur,
     le bayésien la probabilité, le probabiliste l'humilité, le déterministe
     (existant) la transparence. Chaque niveau enrichit le précédent.
  3. **Knowledge OS** — Pensine-Web × FUSE3 × OntoWave + raisonneur hybride
     forment une boucle complète jamais architecturée en tant que produit unique.
  4. **Pont neuro-géométrique** — LLM2Symbolic × Géométrie 9D = théorie falsifiable
     des internaux LLM. Résultat publiable.
  5. **Thèse unificatrice** articulée sur 4 piliers (universalité, compositionnalité,
     calculabilité, gouvernance) — tous partiellement validés mais aucun à 100%.
- **Impact** : Le roadmap peut désormais être construit non pas comme une liste
  de tâches mais comme un graphe de convergence avec chemins critiques.

## Fichiers modifiés

| Fichier | Action | Raison |
|---------|--------|--------|
| `SANDBOX/dolt-concept-store/EXPERIMENT_REGISTRY.md` | **Créé** | Registre central des expérimentations |
| `Copilotage/IDEAS_INVENTORY.md` | **Créé** | Inventaire complet 130 idées, 14 repos audités |
| `Copilotage/journal/2026-02-19-hauru-experiment-registry.md` | **Créé** | Ce journal |
| `Copilotage/journal/INDEX.md` | Mis à jour | Nouvelle entrée |

### Rappel : fichiers non commités de la session 2026-02-18

- `import_panlang_v2.py` — 7 atomes ABS, compute_primary_category() refondu
- `gutenberg_multilingual_validator.py` — +608 keywords ABS
- `seven_layers_engine.py` — CONCEPT_MAPPINGS 78→95, step4b ajouté
- `AGENT_CONVENTION.md` — Règle journal obligatoire
- `.github/copilot-instructions.md` — Instructions Copilot (4 règles)
- `scripts/hooks/pre-commit` — Hook bloquant
- `Copilotage/elargissement-horizon-mathematiques-physique.md` — RFC math/physique
- 11 fichiers journal (1 session + 10 reconstitués)

## Tests effectués

- ✅ Process seven_layers_engine.py vérifié en cours (PID 668992, uptime 2h30+)
- ✅ Audit des 3 systèmes de numérotation Phase complété
- ✅ Registre croisé avec git log (494 commits dans Panini-FS)
- ✅ Vérification liens journal↔commit dans le registre
- ✅ Audit 14 repos : 51,898 fichiers dans Research, ~300 dans FS, 7 coquilles vides identifiées
- ✅ Inventaire croisé avec EXPERIMENT_REGISTRY.md : 115 idées manquantes identifiées
- ✅ **v2.4b TERMINÉ** — PID 668992 terminé normalement
- ✅ **Vérification Dolt finale** — table `concepts` (pas `semantic_universals`)
- ✅ **Métriques finales confirmées** — A=78, B=25, C=2 (105 concepts, score moyen 0.673)

## §12 — Vérification état final v2.4b (Dolt)

### Constat
Le process `seven_layers_engine.py` (PID 668992, lancé ~08:44) a **terminé normalement**.
La requête initiale sur la table `semantic_universals` a échoué ("table not found") —
la table correcte est `concepts`.

### Résultats finaux v2.4b

| Métrique | Valeur |
|----------|--------|
| **HEAD Dolt** | `hdc7787s` |
| **Tables + vues** | 42 |
| **Concepts total** | 105 |
| **Tier A** | 78 (74.3%) — score moyen 0.747 |
| **Tier B** | 25 (23.8%) — score moyen 0.480 |
| **Tier C** | 2 (1.9%) — score moyen 0.190 |
| **Score global moyen** | 0.673 |
| **Score min / max** | 0.163 / 0.950 |
| **Catégories** | PROC=81, ABS=13, QUAL=9, ENT=2 |

### Décision
- v2.4b marqué **✅ TERMINÉ** dans EXPERIMENT_REGISTRY.md
- Résultats intermédiaires = résultats finaux (A=78 stable)
- Prêt pour commit consolidé

### Impact
- Le pipeline v0.1 → v2.4b est entièrement complété
- Prochaine étape technique : v3 (7 couches) est déjà commité
- Le commit consolidé peut maintenant inclure toute la session 18+19

## Prochaines étapes

1. ~~Attendre la fin de v2.4b~~ ✅ FAIT
2. ~~Vérifier les résultats step4b~~ ✅ FAIT — A=78, B=25, C=2
3. **Mettre à jour le README.md** du concept store avec v2.3, v2.4, v2.4b
4. ~~Commit consolidé~~ ✅ FAIT — `8691188` (16 fichiers, +2229 lignes)
5. ~~Rebâtir le roadmap~~ ✅ FAIT — NA-004 priorisé (linguistique → médias)
6. **Archiver les 7 repos coquilles vides** (après récolte des specs utiles)
7. ~~Prioriser les idées impactantes~~ ✅ FAIT — v2.5→v2.7 (linguistique) puis v4.0→v4.2 (médias texte)

## §13 — Priorisation du roadmap (NA-004) : Linguistique → Médias texte

### Constat — Audit code du 2026-02-19

Audit complet du code linguistique et des extracteurs de médias texte.

**Côté linguistique** (fonctionnel mais incomplet) :
- 24 atomes dans 2 catégories seulement (PROC=17, ABS=7)
- **ENT = 0 atomes, QUAL = 0 atomes** — 2 catégories vides sur 4
- 95 concepts, 1831 keywords, 7 langues
- 22/25 mappings Jackendoff à `None`
- Pas de désambiguïsation sémantique (WSD)
- 5 opérations structurelles (COMP, ID, NEG, QUANT, MOD) en docstring mais pas en code

**Côté médias texte** (quasi inexistant) :
- PDF : magic number + split grossier sur `obj`/`endobj`, pas d'extraction de texte
- EPUB, DOCX, ODT, LaTeX : rien du tout
- Le chunker `semantic_chunker.py` est un parser binaire, pas textuel
- Aucune lib d'extraction (PyPDF2, pdfminer, ebooklib) dans requirements.txt
- **Le pont entre le chunker binaire et le moteur d'atomes n'existe pas**

### Décision — Direction donnée par l'humain

> « La priorité va d'abord aller sur les modèles linguistiques,
> puis médias supportant les textes (PDF, EPUB, ...) »

### Plan d'exécution (NA-004)

**Priorité 1 — Modèle linguistique** :
- v2.5 : Atomes ENT (5-8 primitifs entités : SUBSTANCE, OBJET, LIEU…)
- v2.6 : Atomes QUAL (5-8 primitifs qualités : TAILLE, COULEUR, INTENSITÉ…)
- v2.7 : Opérations structurelles + WSD basique + Jackendoff complet
- Critère : 4 catégories couvertes, ≥120 concepts, WSD sur les 10 mots les plus ambigus

**Priorité 2 — Médias texte** :
- v4.0 : `text_extractor.py` — extracteur unifié PDF/EPUB/HTML/MD/TXT
- v4.1 : `document_analyzer.py` — pont extracteur↔seven_layers_engine + détection langue
- v4.2 : Round-trip et préparation E2 avec documents réels
- Critère : `python document_analyzer.py mon.pdf` → atomes + stockage Dolt

### Impact
- NA-004 ajouté au registre d'expérimentations
- Ordre d'exécution clairement défini
- v2.5 (atomes ENT) = prochaine étape immédiate

### Fichiers modifiés
| Fichier | Action | Raison |
|---------|--------|--------|
| `SANDBOX/dolt-concept-store/EXPERIMENT_REGISTRY.md` | Mis à jour | NA-004 ajouté (~180 lignes) |
| `Copilotage/journal/2026-02-19-hauru-experiment-registry.md` | Mis à jour | §13 ajouté |

---

## §14 — Implémentation v2.5 : Atomes ENT (CHOSE, AGENT, CORPS, LIEU, MATIÈRE)

**Horodatage** : 2026-02-19 ~22:00 UTC
**Session** : Continuation directe après priorisation NA-004

### Constat
- L'ontologie PaniniFS avait 24 atomes couvrant 3/4 catégories : PROC (9+8), ABS (7), mais ENT = 0 et QUAL = 0
- Aucun atome ne pouvait capturer les noms concrets (personnes, lieux, objets, substances)
- Les CONCEPT_MAPPINGS utilisaient EXISTENCE comme proxy pour les entités

### Recherche théorique
Sous-agent de recherche mobilisé, croisant 6 cadres théoriques :
- **NSM** (Wierzbicka) : SOMETHING, SOMEONE, BODY, PART, WHERE/PLACE
- **Jackendoff** : THING, PLACE comme primitifs ontologiques
- **Pustejovsky** : Qualia FORMAL (identité) vs CONSTITUTIVE (matière)
- **BFO/DOLCE** : Distinction endurant/perdurant
- **Spelke** : Core knowledge — objets bornés, agents, lieux, substances
- **Dhātu** : √dhṛ (porter/soutenir), √jan (naître/produire), √tan (étendre), √vas (habiter), √bhū (devenir/matière)

### 5 atomes choisis

| Atome | NSM | Jackendoff | Pustejovsky | Dhātu | Dim. dominante |
|-------|-----|------------|-------------|-------|----------------|
| CHOSE | SOMETHING | THING | FORMAL | √dhṛ | ENTITÉ: 1.0 |
| AGENT | SOMEONE | — | FORMAL | √jan | ENTITÉ: 0.6 |
| CORPS | BODY | — | CONSTITUTIVE | √tan | ENTITÉ: 0.7 |
| LIEU | WHERE/PLACE | PLACE | FORMAL | √vas | ENTITÉ: 0.6 |
| MATIÈRE | PART | — | CONSTITUTIVE | √bhū | ENTITÉ: 0.7 |

**Candidats rejetés** : ANIMAL (=AGENT+CORPS+MOUVEMENT), EAU/FEU (instances de MATIÈRE), OBJET (redondant avec CHOSE), ÂME (non testable empiriquement), ARTEFACT (=CHOSE+CREATION)

### Modifications effectuées

**1. `import_panlang_v2.py`** — 6 sections modifiées :
- `ATOMS_ENTITY` set créé (5 atomes)
- `ATOMS` union mise à jour
- `ATOM_DIMENSIONS` : 5 entrées avec vecteurs dimensionnels
- `ATOM_NSM` : 5 entrées avec primes NSM
- `ATOM_JACKENDOFF` : 5 entrées (CHOSE→THING, LIEU→PLACE, autres→None)
- `ATOM_PUSTEJOVSKY` : 5 entrées (FORMAL/CONSTITUTIVE)
- `ATOM_DHATU` : 5 entrées avec racines sanskrites

**2. `gutenberg_multilingual_validator.py`** — ATOM_KEYWORDS :
- 5 blocs ENT ajoutés (CHOSE, AGENT, CORPS, LIEU, MATIÈRE)
- Chaque bloc × 7 langues (EN, FR, DE, IT, ES, EO, FI)
- ~100 mots-clés par atome ENT

**3. `seven_layers_engine.py`** — CONCEPT_MAPPINGS :
- 18 concepts re-décomposés avec atomes ENT (ANIMAL, FEU, PARENT, AMI, MANGER, DORMIR, MUR, LIEU, INSTRUMENT, NATION, FAMILLE, COMMUNAUTÉ, ARCHITECTURE, SOLEIL, LUNE, ENNEMI, GUERRE, RACINE)
- 10 nouveaux concepts ajoutés (NOURRITURE, VÊTEMENT, ARME, FOYER, TOMBE, VOYAGE, PEUPLE, CORPS_CONCEPT, NATURE, MAISON)
- Total : 95 → 105 concepts

### Validation
```
v2.5 VALIDATION COMPLETE ✅
  30 atoms (29 + EMOTION legacy)
  5 ENT atoms: CHOSE, AGENT, CORPS, LIEU, MATIÈRE
  105 concept mappings (29 use ENT atoms)
  All 7 languages covered in keyword dicts
  All atoms in CONCEPT_MAPPINGS are defined in ATOMS
  compute_primary_category: all ENT atoms → ENT
```

### Fichiers modifiés
| Fichier | Action | Raison |
|---------|--------|--------|
| `SANDBOX/dolt-concept-store/import_panlang_v2.py` | Modifié | +ATOMS_ENTITY, 6 dictionnaires |
| `SANDBOX/dolt-concept-store/gutenberg_multilingual_validator.py` | Modifié | +5 blocs keywords ENT ×7 langues |
| `SANDBOX/dolt-concept-store/seven_layers_engine.py` | Modifié | 18 re-décompositions + 10 nouveaux concepts |

### Prochaines étapes
- [ ] Re-run pipeline complet sur corpus Gutenberg (10 textes ×7 langues)
- [ ] Vérifier distribution des tiers (A/B/C) avec ENT
- [ ] v2.6 : Atomes QUAL (candidats : BON, GRAND, VRAI, BEAU, VIEUX)
