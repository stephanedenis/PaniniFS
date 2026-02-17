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

1. **Pas de vrai ACL** : l'isolation repose sur les branches, pas sur des permissions SQL
2. **Pas de BLOB streaming** : `chunk_blobs` avec LONGBLOB limité par la RAM Dolt
3. **GROUP_CONCAT** : non supporté par Dolt SQL, contourné dans les vues
4. **JSON escaping** : nécessite `dolt sql` via stdin (pas `-q`) pour les JSON complexes
5. **Pas de merge incrémental** : `dolt merge` est full-branch, pas par table

### Prochaines étapes

1. **Brancher le vrai chunker** sur Dolt (PNG réel → `chunk_metadata`)
2. **Brancher le fingerprinter audio** sur Dolt (WAV réel → `audio_fingerprints`)
3. **`dolt sql-server`** : démarrer le serveur MySQL pour les clients Rust
4. **panini-core en Rust** : client `sqlx` vers Dolt MySQL
5. **Web UI dashboards** : v_dhatu_distribution, v_format_coverage en temps réel
6. **`dolt clone`** : distribution du tier public à d'autres nœuds
