# PaniniFS — Architecture de stockage unifié Dolt

## Résultat du POC — 17 février 2026

### Vision

Dolt comme **backend de stockage unique** pour toutes les données PaniniFS,
avec isolation par branches pour 3 niveaux de visibilité.

### Architecture à 3 tiers

```
     ┌──────────────────────────────────────────────────┐
     │                   DOLT DATABASE                   │
     │                                                   │
     │  main (PUBLIC)          • 7 dhātu definitions     │
     │  ├── dhatu_definitions  • 12 format grammars      │
     │  ├── format_grammars    • semantic hash registry   │
     │  ├── public_statistics  • aggregated stats         │
     │  └── semantic_hash_reg  • clonable par tous        │
     │                                                   │
     │  confidential           • 15+ semantic mappings    │
     │  ├── semantic_mappings  • 5 analysis results       │
     │  ├── analysis_results   • 5 chunk metadata (PNG)   │
     │  ├── chunk_metadata     • 1 audio fingerprint      │
     │  ├── audio_fingerprints • 1 reconstruction manifest│
     │  ├── audio_hash_index   • deduplication results    │
     │  └── reconstruction_m   • accès restreint          │
     │                                                   │
     │  private/stephane       • 4 user files             │
     │  ├── user_files         • 3 attributions           │
     │  ├── attribution_log    • 1 analysis session       │
     │  ├── chunk_blobs        • encryption keys          │
     │  ├── encryption_keys    • jamais partagé           │
     │  └── analysis_sessions  • données personnelles     │
     └──────────────────────────────────────────────────┘
```

### Résultat du POC : isolation vérifiée

| Branche | dhātu | mappings | user_files | commits |
|---------|-------|----------|------------|---------|
| `main` (public) | 7 | **0** | **0** | 4 |
| `confidential` | 7 | 15 | **0** | 4 |
| `private/stephane` | 7 | 15 | 4 | 5 |

**Observation clé** : les données descendent (public→confidential→private)
mais ne remontent jamais automatiquement. La promotion se fait via branche
dédiée + merge contrôlé (équivalent d'un PR).

### Flux de données

```
  public (main)
    │
    │  clone / fork
    ▼
  confidential ────────── analyses, mappings, chunks
    │
    │  merge
    ▼
  private/stephane ────── fichiers perso, attributions
    │
    │  extraction stats agrégées
    ▼
  promote/stats-YYYY-MM ── branche éphémère
    │
    │  merge (PR approuvé)
    ▼
  public (main) ────────── stats publiées, jamais de données brutes
```

### Fonctionnalités démontrées

1. **Isolation par branche** : `semantic_mappings` = 0 sur public, 15 sur confidential
2. **Héritage** : `private/stephane` voit les 7 dhātu + 15 mappings + ses 4 fichiers
3. **Promotion contrôlée** : stats agrégées promues de private→public via merge
4. **SQL natif sur signatures dhātu** : `JSON_EXTRACT(dhatu_vector, '$.TRANS')`
5. **Chunk reconstruction** : 5 chunks PNG avec offsets/sizes + recette d'assemblage
6. **Audio fingerprinting** : empreinte Shazam-like stockée en SQL (1500 constellations)
7. **Déduplication cross-langue** : 5 concepts, chacun présent en 2-7 langues
8. **Provenance complète** : chaîne attribution avec licence et tier d'accès
9. **Dolt diff** : comparaison statistique entre branches (cellules ajoutées/modifiées)
10. **Historique Git-like** : `dolt log` montrant l'évolution des données

### Composants PaniniFS → Tables Dolt

| Composant Python | Tables Dolt | Tier |
|------------------|-------------|------|
| `dhatu-framework.md` (7 dhātu) | `dhatu_definitions`, `dhatu_inventory` | PUBLIC |
| `panini_fs_chunker.py` (13 formats) | `format_grammars`, `chunk_metadata`, `reconstruction_manifests` | PUBLIC/CONF |
| `panini_audio_fingerprint.py` | `audio_fingerprints`, `audio_hash_index` | CONF |
| Semantic analysis (future) | `semantic_mappings`, `analysis_results`, `deduplication_results` | CONF |
| User file management | `user_files`, `attribution_log`, `analysis_sessions` | PRIVATE |
| Security (future) | `encryption_keys`, `chunk_blobs` | PRIVATE |

### Connexion avec l'écosystème Rust

Le `Cargo.toml` définit deux crates (`panini-core` + `panini-api`) sans code Rust encore.
Dolt expose un **protocole MySQL compatible** (`dolt sql-server`), ce qui permet :

- **panini-core** : client MySQL natif en Rust (`sqlx`) pour lire/écrire les tables
- **panini-api** : serveur REST Axum exposant les données via MySQL pool
- **Web UI** : les 3 pages React existantes se connectent via l'API

### Limites identifiées

1. ~~**Pas de vrai ACL**~~ → Résolu : voir section "Modèle d'accès" ci-dessous
2. **Pas de BLOB streaming** : `chunk_blobs` avec LONGBLOB limité par la RAM Dolt
3. **GROUP_CONCAT** : non supporté par Dolt SQL, contourné dans les vues
4. **JSON escaping** : nécessite `dolt sql` via stdin (pas `-q`) pour les JSON complexes
5. **Pas de merge incrémental** : `dolt merge` est full-branch, pas par table

### Modèle d'accès : Branches + ACL natif (pas de fork)

Trois options ont été évaluées pour isoler les tiers :

#### Option A : Fork (repos séparés) ❌

```
  panini-public/     → repo Dolt indépendant (public)
  panini-confidential/ → repo Dolt indépendant
  panini-private/    → repo Dolt indépendant par user
```

**Avantages** : isolation physique totale, permissions au niveau OS/DoltHub.
**Inconvénients** :
- Les JOINs cross-tier deviennent impossibles en SQL natif
- `private/stephane` ne peut plus faire `SELECT * FROM dhatu_definitions`
  → il faut dupliquer les tables de référence dans chaque repo
- La promotion (stats agrégées → public) nécessite un ETL externe
- 3× la complexité opérationnelle (backup, migration, versioning)
- Perte de l'avantage principal de Dolt : un seul graphe de commits

**Verdict** : ❌ Le fork brise l'unicité du stockage.

#### Option B : Branches seules (POC actuel) ⚠️

```
  main                → tout le monde lit
  confidential        → tout le monde lit aussi (!)
  private/stephane    → tout le monde lit aussi (!)
```

**Avantages** : simple, JOINs cross-tier, héritage de données, `dolt diff`.
**Inconvénients** : aucune isolation réelle — quiconque a accès au repo
peut `dolt checkout private/stephane` et tout voir.

**Verdict** : ⚠️ Suffisant en mode mono-utilisateur, insuffisant en multi-user.

#### Option C : Branches + `dolt sql-server` + Branch Permissions ✅ Recommandé

```
  dolt sql-server (port 3306)
  ├── CREATE USER public_reader  → lecture seule sur main
  ├── CREATE USER analyst        → lecture/écriture sur confidential
  ├── CREATE USER stephane       → lecture/écriture sur private/stephane
  └── dolt_branch_control        → contrôle fin par branche + user
```

Dolt intègre nativement un **système de permissions par branche** via
deux tables système : `dolt_branch_control` et `dolt_branch_namespace_control`.

Configuration cible :

```sql
-- Nettoyage du défaut (qui autorise tout le monde)
DELETE FROM dolt_branch_control;

-- PUBLIC : tout le monde peut lire main, seul admin peut écrire
INSERT INTO dolt_branch_control VALUES ('%', 'main', 'admin', '%', 'admin');

-- CONFIDENTIAL : analysts peuvent lire/écrire
INSERT INTO dolt_branch_control VALUES ('%', 'confidential', 'analyst', '%', 'write');

-- PRIVATE : chaque utilisateur ne peut écrire que SA branche
INSERT INTO dolt_branch_control VALUES ('%', 'private/stephane', 'stephane', '%', 'admin');
INSERT INTO dolt_branch_control VALUES ('%', 'private/alice', 'alice', '%', 'admin');

-- PROMOTION : seul admin peut créer des branches promote/*
INSERT INTO dolt_branch_namespace_control VALUES ('%', 'promote/%', 'admin', '%');

-- Restriction : personne ne peut créer de branche private/ pour un autre
INSERT INTO dolt_branch_namespace_control VALUES ('%', 'private/%', '', '');
-- Chaque user peut créer sa propre branche private/
INSERT INTO dolt_branch_namespace_control VALUES ('%', 'private/stephane%', 'stephane', '%');
```

**Avantages** :
- ✅ Vrais ACL SQL : `stephane` ne peut PAS écrire dans `private/alice`
- ✅ JOINs cross-tier préservés (tous les users ont READ sur toutes les branches)
- ✅ Un seul repo, un seul graphe de commits, un seul `dolt diff`
- ✅ Promotion contrôlée : seul `admin` peut merge vers `main`
- ✅ Protocole MySQL standard : compatible `sqlx` (Rust), Python, Web UI
- ✅ Pattern matching sur noms de branches (`private/%`, `promote/%`)
- ✅ Pas de duplication de données entre tiers

**Point important** (de la doc Dolt) : "all users still have **read access**
to all branches. Permissions only affect **modifying** branches."

→ Pour une isolation en lecture aussi, il faut combiner avec `dolt clone --single-branch`
pour distribuer uniquement `main` aux utilisateurs publics.

**Verdict** : ✅ C'est le bon modèle — branches pour la structure, ACL pour le contrôle.

### `dolt sql-server` + Branch ACL : validé ✅

Le serveur MySQL Dolt avec permissions par branche a été implémenté et testé :

```
dolt sql-server (port 3306, démon détaché)
├── public_user  / pub_panini_2026   → lecture seule, écriture main
├── analyst      / conf_panini_2026  → écriture main + confidential
├── owner        / priv_panini_2026  → admin sur toutes les branches (%)
└── dolt_branch_control (4 règles) + dolt_branch_namespace_control (1 règle)
```

**Résultat : 14/14 tests passés** (`test_branch_acl.py`)
- Lecture cross-tier pour tous les utilisateurs ✅
- Isolation en écriture par branche ✅
- Namespace control : seul `owner` peut créer `private/*` ✅
- Scripts automatisés : `setup_dolt_acl.py` + `test_branch_acl.py`

### Topologie en cascade : distribution multi-repos ✅

#### Le besoin

Pour la distribution de PaniniFS, un modèle de type Git est souhaité :

> « Un DoltHub panini-publique duquel on a dérivé des repos confidentiels,
> et desquels on a un repo privé (local ou payant-cloud) »

#### Architecture cascade validée (20/20 tests)

```
  DoltHub (GRATUIT)            DoltLab / DoltHub Pro        Local / Hosted
  +-------------------+        +--------------------+       +-----------------+
  | panini-public     |        | panini-confidentiel|       | panini-prive    |
  |                   | clone  |                    | clone |                 |
  | main              |<------>| main               |<----->| main            |
  |  dhatu (7)        |        |  dhatu (7)         |       |  dhatu (7)      |
  |  format_grammars  |        |  format_grammars   |       |  format_grammars|
  |  public_statistics|        |  public_statistics  |       |  public_stats   |
  |                   |        |                    |       |                 |
  |                   |        | confidential        |       | confidential    |
  |                   |        |  semantic_mappings  |       |  semantic_maps  |
  |                   |        |  analysis_results   |       |  analysis_res   |
  |                   |        |  dedup_index        |       |  dedup_index    |
  |                   |        |                    |       |                 |
  |                   |        |                    |       | private/stephane |
  |                   |        |                    |       |  user_files     |
  |                   |        |                    |       |  encrypt_keys   |
  +-------------------+        +--------------------+       +-----------------+
        ^                                                         |
        +------------- upstream remote (direct sync) -------------+
```

#### Flux de données en cascade

| Direction | Opération | Contenu | Mécanisme |
|-----------|-----------|---------|-----------|
| **↓ Descendant** | clone/pull | Toutes les données ancêtres | `dolt clone` / `dolt pull` |
| **↑ Ascendant** | push main | Stats agrégées uniquement | `dolt push origin main` |
| **↑ Direct** | fetch upstream | Public → Privé directement | `dolt fetch upstream` |

#### Multi-remote (comme Git)

Le repo privé maintient **deux remotes** simultanément :
- `origin` → panini-confidential (pour les données analysées)
- `upstream` → panini-public (pour les mises à jour directes des dhātu)

```bash
# Dans panini-private :
dolt remote -v
# origin-confidential  https://doltlab.org/panini-confidential
# upstream-public      https://dolthub.com/org/panini-public

# Sync depuis public :
dolt fetch upstream-public
dolt merge upstream-public/main

# Promotion vers confidential :
dolt push origin-confidential main
```

#### Isolation par branches (prouvée)

| Repo | Branches | Tables exclusives |
|------|----------|-------------------|
| `panini-public` | `main` uniquement | dhatu, format_grammars, public_statistics |
| `panini-confidential` | `main` + `confidential` | + semantic_mappings, analysis_results, dedup_index |
| `panini-private` | `main` + `confidential` + `private/*` | + user_files, encryption_keys |

**Les branches sont LOCALES** : la branche `confidential` n'existe que dans
`panini-confidential` et `panini-private`, jamais dans `panini-public`.
Idem pour `private/*` qui n'existe que dans le repo privé.

#### Double sécurité

La topologie cascade se combine avec le `dolt sql-server` + ACL :

1. **Niveau repo** : le `dolt clone` contrôle qui reçoit quelle base de données
2. **Niveau branche** : le `dolt_branch_control` contrôle qui écrit sur quelle branche

Un utilisateur public ne peut même pas cloner le repo confidentiel.
Un analyste avec accès au repo confidentiel ne peut pas modifier les branches privées.

#### Hébergement et coûts

| Tier | Option A | Option B | Coût |
|------|----------|----------|------|
| PUBLIC | DoltHub.com | — | **Gratuit** (DBs publiques illimitées, toute taille) |
| CONFIDENTIAL | DoltLab (self-hosted) | DoltHub Pro | **Gratuit** (DoltLab) ou **$50/mois** (Pro) |
| PRIVATE | Disque local | Hosted Dolt | **Gratuit** (local) ou **$50/mois min** (Hosted) |

DoltHub offre les DBs publiques gratuites quelle que soit la taille.
DoltLab est l'équivalent GitLab pour Dolt : self-hosted, gratuit, open-source.

#### Script de test : `test_cascade_topology.py`

POC complet avec 20 tests automatisés validant :
- Création de 3 repos en cascade (public → confidentiel → privé)
- Isolation des données par tier et par branche
- Sync upstream (public → privé via fetch + merge)
- Promotion de statistiques agrégées (privé → public via main)
- Protection contre la fuite de branches
- Topologie multi-remote

### Prochaines étapes

1. ~~**`dolt sql-server` + Branch Permissions**~~ ✅ Implémenté et testé (14/14)
2. ~~**Topologie cascade multi-repos**~~ ✅ Validée (20/20)
3. **Brancher le vrai chunker** sur Dolt (PNG réel → `chunk_metadata`)
4. **Brancher le fingerprinter audio** sur Dolt (WAV réel → `audio_fingerprints`)
5. **panini-core en Rust** : client `sqlx` vers Dolt MySQL (port 3306)
6. **Web UI dashboards** : v_dhatu_distribution, v_format_coverage en temps réel
7. **DoltHub account** : créer `stephanedenis/panini-public` et publier les 7 dhātu
8. **DoltLab instance** : déployer pour le repo confidentiel (Docker self-hosted)
9. **CI/CD pipeline** : dolt push automatisé depuis les tests → DoltHub
