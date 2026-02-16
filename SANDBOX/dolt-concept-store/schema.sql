-- Schema SQL pour le concept store PaniniFS sur Dolt
-- Architecture: séparation des responsabilités entre Rust (analyse) et Dolt (stockage versionné)
-- Dolt permet le versioning Git-like : branches, commits, diffs, merge

-- Table 1: Définition des 7 dhātu informationnels
-- Les dhātu sont les atomes conceptuels universels de PaniniFS
CREATE TABLE IF NOT EXISTS dhatu_definitions (
    id VARCHAR(20) PRIMARY KEY,
    code VARCHAR(10) NOT NULL UNIQUE,
    name_fr VARCHAR(100) NOT NULL,
    name_en VARCHAR(100) NOT NULL,
    description TEXT,
    components TEXT,  -- Format JSON: composants du dhātu (ex: COMM → ["canal", "source", "cible"])
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: Inventaire dhātu v0.1 - primitives conceptuelles
-- Basé sur docs/en/research/dhatu-inventory-v0-1.md
CREATE TABLE IF NOT EXISTS dhatu_inventory (
    id VARCHAR(50) PRIMARY KEY,
    category VARCHAR(50) NOT NULL,  -- AGENT, ACTION, PATIENT, etc.
    symbol VARCHAR(100) NOT NULL,
    stable_id VARCHAR(100) NOT NULL,  -- ID stable du concept (ex: concept:book, action:hunt)
    description TEXT,
    lexicon_alias VARCHAR(100),  -- Alias lexical fréquent
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 3: Mappings sémantiques - déduplication cross-langue
-- Un même concept dans différentes langues partage le même semantic_hash
CREATE TABLE IF NOT EXISTS semantic_mappings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content_hash VARCHAR(64) NOT NULL,  -- SHA256 du texte original
    source_text TEXT NOT NULL,
    language VARCHAR(10) NOT NULL,  -- fr, en, es, etc.
    dhatu_signature JSON NOT NULL,  -- Signature conceptuelle: {"COMM": 0.8, "TRANS": 0.2}
    semantic_hash VARCHAR(64) NOT NULL,  -- Hash du concept (identique pour "Hello" et "Bonjour")
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_semantic_hash (semantic_hash),
    INDEX idx_content_hash (content_hash),
    INDEX idx_language (language)
);

-- Table 4: Résultats d'analyse par fichier
-- Le core Rust analyse les fichiers, Dolt stocke les résultats
CREATE TABLE IF NOT EXISTS analysis_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_path VARCHAR(500) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,  -- Hash du contenu du fichier
    dhatu_vector JSON NOT NULL,  -- Scores des 7 dhātu: {"COMM": 0.3, "ITER": 0.1, "TRANS": 0.4, ...}
    dominant_dhatu VARCHAR(20),  -- Dhātu dominant dans ce fichier
    analysis_version VARCHAR(20) NOT NULL,  -- Version de l'analyseur Rust
    metadata JSON,  -- Métadonnées additionnelles (taille, lignes, tokens, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_file_path (file_path),
    INDEX idx_file_hash (file_hash),
    INDEX idx_dominant_dhatu (dominant_dhatu)
);

-- Table 5: Log d'attribution et provenance
-- Traçabilité complète: qui, quand, d'où provient chaque entrée
CREATE TABLE IF NOT EXISTS attribution_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    entry_type VARCHAR(50) NOT NULL,  -- 'semantic_mapping', 'analysis_result', etc.
    entry_id INT NOT NULL,  -- ID de l'entrée concernée
    semantic_hash VARCHAR(64),  -- Optionnel: hash sémantique pour dédup
    source VARCHAR(200),  -- Source du contenu (URL, file path, etc.)
    author VARCHAR(100),  -- Auteur ou système
    license VARCHAR(100),  -- Licence du contenu
    attribution_text TEXT,  -- Texte d'attribution complet
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_entry (entry_type, entry_id),
    INDEX idx_semantic_hash (semantic_hash)
);

-- Vues pour faciliter les requêtes

-- Vue: statistiques des dhātu par analyse
CREATE VIEW IF NOT EXISTS dhatu_statistics AS
SELECT 
    dominant_dhatu,
    COUNT(*) as file_count,
    AVG(JSON_UNQUOTE(JSON_EXTRACT(dhatu_vector, '$.COMM'))) as avg_comm,
    AVG(JSON_UNQUOTE(JSON_EXTRACT(dhatu_vector, '$.ITER'))) as avg_iter,
    AVG(JSON_UNQUOTE(JSON_EXTRACT(dhatu_vector, '$.TRANS'))) as avg_trans,
    AVG(JSON_UNQUOTE(JSON_EXTRACT(dhatu_vector, '$.DECIDE'))) as avg_decide,
    AVG(JSON_UNQUOTE(JSON_EXTRACT(dhatu_vector, '$.LOCATE'))) as avg_locate,
    AVG(JSON_UNQUOTE(JSON_EXTRACT(dhatu_vector, '$.GROUP'))) as avg_group,
    AVG(JSON_UNQUOTE(JSON_EXTRACT(dhatu_vector, '$.SEQ'))) as avg_seq
FROM analysis_results
GROUP BY dominant_dhatu;

-- Vue: déduplication sémantique cross-langue
CREATE VIEW IF NOT EXISTS semantic_deduplication AS
SELECT 
    semantic_hash,
    COUNT(DISTINCT language) as language_count,
    COUNT(*) as total_entries,
    GROUP_CONCAT(DISTINCT language) as languages,
    GROUP_CONCAT(source_text SEPARATOR ' | ') as texts
FROM semantic_mappings
GROUP BY semantic_hash
HAVING COUNT(DISTINCT language) > 1;
