-- PaniniFS Unified Dolt Storage - Clean Schema (no unicode decorations)
-- All 17 tables created on main, branches fork AFTER schema commit.
-- Tier isolation = branch-level INSERT policy, not schema-level.

-- TIER 1: PUBLIC
CREATE TABLE IF NOT EXISTS dhatu_definitions (
    id VARCHAR(20) PRIMARY KEY,
    code VARCHAR(10) NOT NULL UNIQUE,
    name_fr VARCHAR(100) NOT NULL,
    name_en VARCHAR(100) NOT NULL,
    description TEXT,
    components JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dhatu_inventory (
    id VARCHAR(50) PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    symbol VARCHAR(100) NOT NULL,
    stable_id VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    lexicon_alias VARCHAR(100),
    version VARCHAR(20) DEFAULT 'v0.1',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_stable_id (stable_id)
);

CREATE TABLE IF NOT EXISTS format_grammars (
    grammar_id VARCHAR(50) PRIMARY KEY,
    format_name VARCHAR(50) NOT NULL,
    category VARCHAR(30) NOT NULL,
    magic_bytes VARBINARY(16),
    structure_spec JSON,
    version VARCHAR(20) DEFAULT 'v1',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_format (format_name),
    INDEX idx_category (category)
);

CREATE TABLE IF NOT EXISTS public_statistics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stat_type VARCHAR(50) NOT NULL,
    scope VARCHAR(100) NOT NULL,
    metrics JSON NOT NULL,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_stat_type (stat_type)
);

CREATE TABLE IF NOT EXISTS semantic_hash_registry (
    semantic_hash VARCHAR(64) PRIMARY KEY,
    dominant_dhatu VARCHAR(10) NOT NULL,
    dhatu_signature JSON NOT NULL,
    language_count INT DEFAULT 0,
    entry_count INT DEFAULT 0,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_dominant (dominant_dhatu)
);

-- TIER 2: CONFIDENTIAL
CREATE TABLE IF NOT EXISTS semantic_mappings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content_hash VARCHAR(64) NOT NULL UNIQUE,
    source_text TEXT NOT NULL,
    language VARCHAR(10) NOT NULL,
    dhatu_signature JSON NOT NULL,
    semantic_hash VARCHAR(64) NOT NULL,
    confidence FLOAT DEFAULT 1.0,
    analyzer_version VARCHAR(20),
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_semantic_hash (semantic_hash),
    INDEX idx_content_hash (content_hash),
    INDEX idx_language (language)
);

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
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_file_hash (file_hash),
    INDEX idx_dominant_dhatu (dominant_dhatu),
    INDEX idx_format (format_name)
);

CREATE TABLE IF NOT EXISTS chunk_metadata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_hash VARCHAR(64) NOT NULL,
    chunk_id INT NOT NULL,
    chunk_hash VARCHAR(64) NOT NULL,
    offset_pos BIGINT NOT NULL,
    size BIGINT NOT NULL,
    pattern_type VARCHAR(100) NOT NULL,
    grammar_id VARCHAR(50),
    dependencies JSON,
    reconstruction_recipe JSON NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_file_chunk (file_hash, chunk_id),
    INDEX idx_chunk_hash (chunk_hash),
    INDEX idx_pattern (pattern_type),
    INDEX idx_status (status)
);

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
    constellation_count INT,
    hash_pair_count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tempo (tempo_bpm),
    INDEX idx_key (detected_key)
);

CREATE TABLE IF NOT EXISTS audio_hash_index (
    hash_pair VARCHAR(32) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    pair_offset INT,
    PRIMARY KEY (hash_pair, file_hash),
    INDEX idx_file (file_hash)
);

CREATE TABLE IF NOT EXISTS deduplication_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_hash VARCHAR(64) NOT NULL,
    duplicate_hash VARCHAR(64) NOT NULL,
    similarity_score FLOAT NOT NULL,
    match_type VARCHAR(30) NOT NULL,
    dedup_method VARCHAR(50),
    delta_recipe JSON,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_source (source_hash),
    INDEX idx_duplicate (duplicate_hash),
    INDEX idx_match_type (match_type)
);

CREATE TABLE IF NOT EXISTS reconstruction_manifests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_hash VARCHAR(64) NOT NULL UNIQUE,
    file_name VARCHAR(500),
    total_chunks INT NOT NULL,
    grammar_id VARCHAR(50),
    original_size BIGINT NOT NULL,
    manifest JSON NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_grammar (grammar_id)
);

-- TIER 3: PRIVATE
CREATE TABLE IF NOT EXISTS user_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_hash VARCHAR(64) NOT NULL UNIQUE,
    file_path VARCHAR(1000) NOT NULL,
    file_name VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100),
    format_name VARCHAR(50),
    owner VARCHAR(100) NOT NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_owner (owner),
    INDEX idx_format (format_name)
);

CREATE TABLE IF NOT EXISTS attribution_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    entry_type VARCHAR(50) NOT NULL,
    entry_id INT NOT NULL,
    semantic_hash VARCHAR(64),
    source VARCHAR(500),
    author VARCHAR(100),
    license VARCHAR(100),
    attribution_text TEXT,
    access_tier VARCHAR(20) DEFAULT 'private',
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_entry (entry_type, entry_id),
    INDEX idx_access_tier (access_tier)
);

CREATE TABLE IF NOT EXISTS chunk_blobs (
    chunk_hash VARCHAR(64) PRIMARY KEY,
    raw_data LONGBLOB,
    compressed_data LONGBLOB,
    compression_ratio FLOAT,
    storage_method VARCHAR(30),
    stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS encryption_keys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    owner VARCHAR(100) NOT NULL,
    key_id VARCHAR(64) NOT NULL UNIQUE,
    algorithm VARCHAR(30) NOT NULL,
    encrypted_key BLOB,
    scope VARCHAR(50) DEFAULT 'all',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    INDEX idx_owner (owner)
);

CREATE TABLE IF NOT EXISTS analysis_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL UNIQUE,
    owner VARCHAR(100) NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'running',
    files_processed INT DEFAULT 0,
    chunks_created INT DEFAULT 0,
    dedup_found INT DEFAULT 0,
    config JSON,
    summary JSON,
    INDEX idx_owner (owner),
    INDEX idx_status (status)
);

-- VIEWS (cross-tier, available on branches that have the underlying tables populated)

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

CREATE VIEW IF NOT EXISTS v_semantic_deduplication AS
SELECT 
    semantic_hash,
    COUNT(DISTINCT language) as language_count,
    COUNT(*) as total_entries
FROM semantic_mappings
GROUP BY semantic_hash
HAVING COUNT(DISTINCT language) > 1;

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
