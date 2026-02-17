-- =============================================================================
-- PaniniFS Unified Dolt Storage — Tiered Architecture
-- =============================================================================
--
-- Architecture: 3 tiers via branches Dolt
--
--   main/public       → Données ouvertes (dhātu, lexicon, grammaires, stats)
--   confidential      → Données restreintes (analyses, mappings corpus, chunks)
--   private/{user}    → Données privées (fichiers perso, attributions sensibles)
--
-- Principe: Dolt branches = isolation + fusion contrôlée
--   - public peut être cloné par quiconque (dolt clone)
--   - confidential merge FROM public, jamais vers
--   - private merge FROM confidential, jamais vers
--
-- Flow: public → confidential → private  (données de référence descendent)
--       private → confidential → public  (contributions remontent via PR)
--
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- TIER 1: PUBLIC — Données ouvertes, clonables, réutilisables
-- ─────────────────────────────────────────────────────────────────────────────

-- T1.1: Les 7 dhātu informationnels (référence immuable)
CREATE TABLE IF NOT EXISTS dhatu_definitions (
    id VARCHAR(20) PRIMARY KEY,
    code VARCHAR(10) NOT NULL UNIQUE,
    name_fr VARCHAR(100) NOT NULL,
    name_en VARCHAR(100) NOT NULL,
    description TEXT,
    components JSON,                -- Ex: ["canal", "source", "cible"]
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- T1.2: Inventaire primitives conceptuelles (lexicon PaniniFS)
CREATE TABLE IF NOT EXISTS dhatu_inventory (
    id VARCHAR(50) PRIMARY KEY,
    category VARCHAR(50) NOT NULL,  -- AGENT, ACTION, PATIENT, REL, MODALITY, ASPECT
    symbol VARCHAR(100) NOT NULL,
    stable_id VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    lexicon_alias VARCHAR(100),
    version VARCHAR(20) DEFAULT 'v0.1',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_stable_id (stable_id)
);

-- T1.3: Grammaires de format binaire (pour le chunker sémantique)
CREATE TABLE IF NOT EXISTS format_grammars (
    grammar_id VARCHAR(50) PRIMARY KEY,    -- 'png_v1', 'mp4_v1', 'jpeg_v1'
    format_name VARCHAR(50) NOT NULL,      -- 'PNG', 'MP4', 'JPEG'
    category VARCHAR(30) NOT NULL,         -- 'image', 'video', 'audio', 'document'
    magic_bytes VARBINARY(16),             -- Magic number bytes
    structure_spec JSON,                   -- Spec de parsing: chunks, markers, boxes
    version VARCHAR(20) DEFAULT 'v1',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_format (format_name),
    INDEX idx_category (category)
);

-- T1.4: Statistiques agrégées (pas de données brutes → public safe)
CREATE TABLE IF NOT EXISTS public_statistics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stat_type VARCHAR(50) NOT NULL,        -- 'dhatu_distribution', 'format_coverage', etc.
    scope VARCHAR(100) NOT NULL,           -- 'global', 'language:fr', 'format:png'
    metrics JSON NOT NULL,                 -- {"total": 5035, "avg_comm": 0.25, ...}
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_stat_type (stat_type)
);

-- T1.5: Semantic hash registry (hashes publics, pas les textes sources)
CREATE TABLE IF NOT EXISTS semantic_hash_registry (
    semantic_hash VARCHAR(64) PRIMARY KEY,
    dominant_dhatu VARCHAR(10) NOT NULL,
    dhatu_signature JSON NOT NULL,         -- Signature quantifiée
    language_count INT DEFAULT 0,
    entry_count INT DEFAULT 0,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_dominant (dominant_dhatu)
);


-- ─────────────────────────────────────────────────────────────────────────────
-- TIER 2: CONFIDENTIAL — Données analysées, accès restreint
-- ─────────────────────────────────────────────────────────────────────────────

-- T2.1: Mappings sémantiques complets (textes sources inclus)
CREATE TABLE IF NOT EXISTS semantic_mappings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content_hash VARCHAR(64) NOT NULL UNIQUE,
    source_text TEXT NOT NULL,
    language VARCHAR(10) NOT NULL,
    dhatu_signature JSON NOT NULL,
    semantic_hash VARCHAR(64) NOT NULL,
    confidence FLOAT DEFAULT 1.0,          -- Score de confiance de l'analyseur
    analyzer_version VARCHAR(20),
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_semantic_hash (semantic_hash),
    INDEX idx_content_hash (content_hash),
    INDEX idx_language (language)
);

-- T2.2: Résultats d'analyse par fichier
CREATE TABLE IF NOT EXISTS analysis_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_path VARCHAR(500) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    file_size BIGINT,
    format_name VARCHAR(50),
    grammar_id VARCHAR(50),
    dhatu_vector JSON NOT NULL,
    dominant_dhatu VARCHAR(20),
    analysis_version VARCHAR(20) NOT NULL,
    metadata JSON,                         -- {lines, tokens, patterns, ...}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_file_hash (file_hash),
    INDEX idx_dominant_dhatu (dominant_dhatu),
    INDEX idx_format (format_name),
    FOREIGN KEY (grammar_id) REFERENCES format_grammars(grammar_id)
);

-- T2.3: Chunks sémantiques (métadonnées, pas les blobs)
CREATE TABLE IF NOT EXISTS chunk_metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_hash VARCHAR(64) NOT NULL,        -- Fichier source
    chunk_id INT NOT NULL,                 -- Index séquentiel dans le fichier
    chunk_hash VARCHAR(64) NOT NULL,       -- SHA-256 du chunk
    offset BIGINT NOT NULL,
    size BIGINT NOT NULL,
    pattern_type VARCHAR(100) NOT NULL,    -- 'PNG_IHDR', 'ISOBMFF_MDAT_KEYFRAMES'
    grammar_id VARCHAR(50),
    dependencies JSON,                     -- [chunk_id, ...] pour reconstruction
    reconstruction_recipe JSON NOT NULL,   -- Recette complète de reconstruction
    status VARCHAR(20) DEFAULT 'pending',  -- pending, compressed, verified
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_file_chunk (file_hash, chunk_id),
    INDEX idx_chunk_hash (chunk_hash),
    INDEX idx_pattern (pattern_type),
    INDEX idx_status (status)
);

-- T2.4: Index de similarité audio (empreintes Shazam-like)
CREATE TABLE IF NOT EXISTS audio_fingerprints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_hash VARCHAR(64) NOT NULL UNIQUE,
    duration_ms INT NOT NULL,
    sample_rate INT NOT NULL,
    channels INT NOT NULL,
    spectral_centroid FLOAT,
    zero_crossing_rate FLOAT,
    tempo_bpm FLOAT,
    detected_key VARCHAR(10),
    constellation_count INT,               -- Nombre de points constellation
    hash_pair_count INT,                   -- Nombre de paires hashées
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tempo (tempo_bpm),
    INDEX idx_key (detected_key)
);

-- T2.5: Index inversé audio (pour recherche O(1))
CREATE TABLE IF NOT EXISTS audio_hash_index (
    hash_pair VARCHAR(32) NOT NULL,        -- MD5 tronqué de la paire anchor-target
    file_hash VARCHAR(64) NOT NULL,
    pair_offset INT,                       -- Position dans la séquence
    PRIMARY KEY (hash_pair, file_hash),
    INDEX idx_file (file_hash),
    FOREIGN KEY (file_hash) REFERENCES audio_fingerprints(file_hash)
);

-- T2.6: Résultats de déduplication (quels fichiers sont des doublons)
CREATE TABLE IF NOT EXISTS deduplication_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_hash VARCHAR(64) NOT NULL,
    duplicate_hash VARCHAR(64) NOT NULL,
    similarity_score FLOAT NOT NULL,       -- 0.0-1.0
    match_type VARCHAR(30) NOT NULL,       -- 'exact', 'semantic', 'audio_similar'
    dedup_method VARCHAR(50),              -- 'sha256', 'dhatu_signature', 'shazam'
    delta_recipe JSON,                     -- Comment reconstruire duplicate depuis source
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_source (source_hash),
    INDEX idx_duplicate (duplicate_hash),
    INDEX idx_match_type (match_type)
);

-- T2.7: Manifests de reconstruction (groupes de chunks → fichier)
CREATE TABLE IF NOT EXISTS reconstruction_manifests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_hash VARCHAR(64) NOT NULL UNIQUE,
    file_name VARCHAR(500),
    total_chunks INT NOT NULL,
    grammar_id VARCHAR(50),
    original_size BIGINT NOT NULL,
    manifest JSON NOT NULL,                -- Liste ordonnée des chunk_ids + offsets
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_grammar (grammar_id)
);


-- ─────────────────────────────────────────────────────────────────────────────
-- TIER 3: PRIVATE — Données utilisateur, jamais partagées sans consentement
-- ─────────────────────────────────────────────────────────────────────────────

-- T3.1: Fichiers sources enregistrés (métadonnées seulement, pas de blobs)
CREATE TABLE IF NOT EXISTS user_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_hash VARCHAR(64) NOT NULL UNIQUE,
    file_path VARCHAR(1000) NOT NULL,      -- Chemin original sur la machine user
    file_name VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100),
    format_name VARCHAR(50),
    owner VARCHAR(100) NOT NULL,           -- Utilisateur propriétaire
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_owner (owner),
    INDEX idx_format (format_name)
);

-- T3.2: Log d'attribution et provenance complet
CREATE TABLE IF NOT EXISTS attribution_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    entry_type VARCHAR(50) NOT NULL,       -- 'semantic_mapping', 'analysis', 'chunk', 'file'
    entry_id INT NOT NULL,
    semantic_hash VARCHAR(64),
    source VARCHAR(500),                   -- URL, file path, etc.
    author VARCHAR(100),
    license VARCHAR(100),
    attribution_text TEXT,
    access_tier VARCHAR(20) DEFAULT 'private',  -- 'public', 'confidential', 'private'
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_entry (entry_type, entry_id),
    INDEX idx_access_tier (access_tier)
);

-- T3.3: Blobs de chunks (stockage binaire des données compressées)
CREATE TABLE IF NOT EXISTS chunk_blobs (
    chunk_hash VARCHAR(64) PRIMARY KEY,
    raw_data LONGBLOB,                     -- Données brutes du chunk
    compressed_data LONGBLOB,              -- Données après compression sémantique
    compression_ratio FLOAT,
    storage_method VARCHAR(30),            -- 'raw', 'zstd', 'semantic', 'delta'
    stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- T3.4: Clés de chiffrement par utilisateur (pour chunks privés)
CREATE TABLE IF NOT EXISTS encryption_keys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    owner VARCHAR(100) NOT NULL,
    key_id VARCHAR(64) NOT NULL UNIQUE,    -- Identifiant public de la clé
    algorithm VARCHAR(30) NOT NULL,        -- 'AES-256-GCM', 'ChaCha20-Poly1305'
    encrypted_key BLOB,                    -- Clé chiffrée par master password
    scope VARCHAR(50) DEFAULT 'all',       -- 'all', 'media', 'documents'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    INDEX idx_owner (owner)
);

-- T3.5: Sessions d'analyse (historique des jobs de l'utilisateur)
CREATE TABLE IF NOT EXISTS analysis_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL UNIQUE,
    owner VARCHAR(100) NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'running',  -- running, completed, failed
    files_processed INT DEFAULT 0,
    chunks_created INT DEFAULT 0,
    dedup_found INT DEFAULT 0,
    config JSON,                           -- Configuration de la session
    summary JSON,                          -- Résumé post-session
    INDEX idx_owner (owner),
    INDEX idx_status (status)
);


-- ─────────────────────────────────────────────────────────────────────────────
-- CROSS-TIER VIEWS
-- ─────────────────────────────────────────────────────────────────────────────

-- Vue: Distribution dhātu agrégée (safe pour public)
CREATE VIEW IF NOT EXISTS v_dhatu_distribution AS
SELECT 
    dominant_dhatu,
    COUNT(*) as file_count,
    ROUND(AVG(JSON_UNQUOTE(JSON_EXTRACT(dhatu_vector, '$.COMM'))), 3) as avg_comm,
    ROUND(AVG(JSON_UNQUOTE(JSON_EXTRACT(dhatu_vector, '$.ITER'))), 3) as avg_iter,
    ROUND(AVG(JSON_UNQUOTE(JSON_EXTRACT(dhatu_vector, '$.TRANS'))), 3) as avg_trans,
    ROUND(AVG(JSON_UNQUOTE(JSON_EXTRACT(dhatu_vector, '$.DECIDE'))), 3) as avg_decide,
    ROUND(AVG(JSON_UNQUOTE(JSON_EXTRACT(dhatu_vector, '$.LOCATE'))), 3) as avg_locate,
    ROUND(AVG(JSON_UNQUOTE(JSON_EXTRACT(dhatu_vector, '$.GROUP'))), 3) as avg_group,
    ROUND(AVG(JSON_UNQUOTE(JSON_EXTRACT(dhatu_vector, '$.SEQ'))), 3) as avg_seq
FROM analysis_results
GROUP BY dominant_dhatu;

-- Vue: Déduplication sémantique cross-langue
CREATE VIEW IF NOT EXISTS v_semantic_deduplication AS
SELECT 
    semantic_hash,
    COUNT(DISTINCT language) as language_count,
    COUNT(*) as total_entries,
    GROUP_CONCAT(DISTINCT language) as languages,
    GROUP_CONCAT(source_text SEPARATOR ' | ') as texts
FROM semantic_mappings
GROUP BY semantic_hash
HAVING COUNT(DISTINCT language) > 1;

-- Vue: Couverture de formats analysés
CREATE VIEW IF NOT EXISTS v_format_coverage AS
SELECT
    format_name,
    COUNT(*) as file_count,
    SUM(file_size) as total_bytes,
    COUNT(DISTINCT dominant_dhatu) as dhatu_diversity,
    AVG(JSON_UNQUOTE(JSON_EXTRACT(dhatu_vector, '$.TRANS'))) as avg_transform
FROM analysis_results
WHERE format_name IS NOT NULL
GROUP BY format_name;

-- Vue: Efficacité de compression par format
CREATE VIEW IF NOT EXISTS v_compression_efficiency AS
SELECT
    fg.format_name,
    fg.category,
    COUNT(cm.id) as total_chunks,
    AVG(cm.size) as avg_chunk_size,
    COUNT(DISTINCT cm.pattern_type) as pattern_diversity,
    SUM(CASE WHEN cm.status = 'compressed' THEN 1 ELSE 0 END) as compressed_count,
    SUM(CASE WHEN cm.status = 'verified' THEN 1 ELSE 0 END) as verified_count
FROM chunk_metadata cm
JOIN format_grammars fg ON cm.grammar_id = fg.grammar_id
GROUP BY fg.format_name, fg.category;

-- Vue: Sommaire de session (pour dashboard utilisateur)
CREATE VIEW IF NOT EXISTS v_session_summary AS
SELECT
    s.session_id,
    s.owner,
    s.status,
    s.files_processed,
    s.chunks_created,
    s.dedup_found,
    TIMESTAMPDIFF(SECOND, s.started_at, COALESCE(s.completed_at, CURRENT_TIMESTAMP)) as duration_seconds,
    s.started_at,
    s.completed_at
FROM analysis_sessions s;

-- Vue: Audio similarity clusters
CREATE VIEW IF NOT EXISTS v_audio_clusters AS
SELECT
    dr.source_hash,
    af.duration_ms,
    af.tempo_bpm,
    af.detected_key,
    COUNT(*) as cluster_size,
    AVG(dr.similarity_score) as avg_similarity
FROM deduplication_results dr
JOIN audio_fingerprints af ON dr.source_hash = af.file_hash
WHERE dr.match_type = 'audio_similar'
GROUP BY dr.source_hash, af.duration_ms, af.tempo_bpm, af.detected_key
HAVING cluster_size > 1;
