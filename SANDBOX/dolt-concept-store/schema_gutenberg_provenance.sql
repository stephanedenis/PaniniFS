-- =============================================================================
-- PaniniFS Gutenberg Provenance Model — Validation multilingue
-- =============================================================================
--
-- Principe PaniniFS: toute information est considérée en relation avec sa source.
-- Chaîne de provenance:
--   "édition/époque(année)/auteur" selon "traducteur/époque(année)"
--   selon "site gutenberg en date du..."
--
-- Ce schéma étend le v2 (schema_v2_universals.sql) avec les tables nécessaires
-- pour la validation empirique du modèle PanLang via les traductions Gutenberg.
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- ŒUVRES — Les œuvres originales
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS gutenberg_works (
    id              VARCHAR(50) PRIMARY KEY,       -- ex: ALICE, CANDIDE, GRIMM
    title_original  VARCHAR(500) NOT NULL,          -- Titre dans la langue originale
    author          VARCHAR(200) NOT NULL,           -- Auteur original
    author_birth    INT,                             -- Année de naissance
    author_death    INT,                             -- Année de décès
    original_lang   VARCHAR(10) NOT NULL,            -- Code ISO: en, fr, de, it, es
    original_year   INT,                             -- Année de première publication
    genre           VARCHAR(100),                    -- conte, roman, fable, philosophie
    description     TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────────────────────────────────────
-- ÉDITIONS — Chaque édition/traduction sur Gutenberg
-- Provenance: "édition/époque(année)/auteur" selon "traducteur/époque(année)"
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS gutenberg_editions (
    id              VARCHAR(80) PRIMARY KEY,        -- ex: ALICE_EN_11, ALICE_FR_55456
    work_id         VARCHAR(50) NOT NULL,            -- → gutenberg_works.id
    gutenberg_id    INT NOT NULL,                    -- Numéro ebook Gutenberg
    lang            VARCHAR(10) NOT NULL,            -- Code ISO langue de cette édition
    title           VARCHAR(500) NOT NULL,            -- Titre dans cette langue
    -- Traducteur (provenance critique)
    translator      VARCHAR(200),                    -- Nom du traducteur (NULL si original)
    translator_birth INT,                            -- Année naissance traducteur
    translator_death INT,                            -- Année décès traducteur
    translation_year INT,                            -- Année de cette traduction
    -- Édition
    edition_info    VARCHAR(500),                    -- Informations d'édition (éditeur, etc.)
    -- Source Gutenberg (provenance finale)
    gutenberg_url   VARCHAR(500) NOT NULL,           -- URL complète
    gutenberg_release_date DATE,                     -- Date de mise en ligne Gutenberg
    gutenberg_credits VARCHAR(500),                  -- Crédits Gutenberg (digitiseurs)
    gutenberg_access_date DATE NOT NULL,             -- Date d'accès (our retrieval date)
    -- Statut
    is_original     INT NOT NULL DEFAULT 0,          -- 1 si c'est l'œuvre originale
    text_retrieved  INT NOT NULL DEFAULT 0,          -- 1 si le texte a été téléchargé
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_work (work_id),
    INDEX idx_lang (lang),
    INDEX idx_gutenberg (gutenberg_id),
    FOREIGN KEY (work_id) REFERENCES gutenberg_works(id)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- SEGMENTS — Unités textuelles comparables entre traductions
-- Un segment = un passage identifiable (chapitre, paragraphe, phrase-clé)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS gutenberg_segments (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    edition_id      VARCHAR(80) NOT NULL,            -- → gutenberg_editions.id
    segment_ref     VARCHAR(100) NOT NULL,           -- Référence normalisée: "ch01_p01", "ch21_fox"
    segment_type    VARCHAR(20) NOT NULL,            -- 'chapter_opening', 'key_passage', 'dialogue', 'maxim'
    text_content    TEXT NOT NULL,                    -- Le texte brut du segment
    char_count      INT NOT NULL,
    word_count      INT NOT NULL,
    -- Localisation dans le texte
    chapter         VARCHAR(50),                     -- "Chapitre I", "Chapter 1", "Kapitel I"
    position_start  INT,                             -- Position caractère début (dans le texte complet)
    position_end    INT,                             -- Position caractère fin
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_edition_segment (edition_id, segment_ref),
    INDEX idx_ref (segment_ref),
    INDEX idx_type (segment_type),
    FOREIGN KEY (edition_id) REFERENCES gutenberg_editions(id)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- DÉCOMPOSITIONS — Analyse PanLang de chaque segment
-- Chaque décomposition est attribuée à son contexte traducteur/édition
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS segment_decompositions (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    segment_id      INT NOT NULL,                    -- → gutenberg_segments.id
    -- Concepts PanLang détectés dans ce segment
    concept_id      VARCHAR(50) NOT NULL,            -- → concepts.id (v2)
    -- Atomes PanLang activés
    atoms_detected  JSON NOT NULL,                   -- ["EMOTION","COGNITION"] — atomes identifiés
    confidence      FLOAT NOT NULL DEFAULT 0.5,      -- Confiance de la décomposition: 0.0-1.0
    -- Justification
    evidence_text   VARCHAR(1000),                   -- Extrait textuel supportant la détection
    analysis_method VARCHAR(50) NOT NULL,             -- 'keyword_match', 'semantic_field', 'manual'
    -- Provenance analytique
    analyzer        VARCHAR(50) NOT NULL DEFAULT 'gutenberg_validator_v1',
    analyzed_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_segment (segment_id),
    INDEX idx_concept (concept_id),
    INDEX idx_confidence (confidence),
    FOREIGN KEY (segment_id) REFERENCES gutenberg_segments(id)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- CONVERGENCE — Résultats de comparaison inter-traductions
-- "ce qui est commun de ce qui est spécifique"
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS translation_convergence (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    work_id         VARCHAR(50) NOT NULL,            -- → gutenberg_works.id
    segment_ref     VARCHAR(100) NOT NULL,           -- Le passage comparé
    concept_id      VARCHAR(50) NOT NULL,            -- Le concept PanLang évalué
    -- Convergence
    total_editions  INT NOT NULL,                    -- Nombre d'éditions comparées
    editions_found  INT NOT NULL,                    -- Nombre d'éditions où le concept apparaît
    convergence_ratio FLOAT NOT NULL,                -- editions_found / total_editions
    convergence_type VARCHAR(20) NOT NULL,           -- 'universal', 'majority', 'minority', 'unique'
    -- Détails par traducteur
    found_in        JSON NOT NULL,                   -- ["ALICE_FR_55456","ALICE_DE_19778"] — éditions avec
    not_found_in    JSON,                            -- ["ALICE_FI_46569"] — éditions sans
    -- Interprétation
    interpretation_notes TEXT,                       -- Notes sur les divergences
    atoms_common    JSON,                            -- Atomes communs à toutes les traductions
    atoms_variable  JSON,                            -- Atomes qui varient selon le traducteur
    computed_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_work (work_id),
    INDEX idx_segment (segment_ref),
    INDEX idx_concept (concept_id),
    INDEX idx_convergence (convergence_type),
    FOREIGN KEY (work_id) REFERENCES gutenberg_works(id)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- VUES — Analyses agrégées
-- (Created individually via pipeline step1 due to Dolt multi-statement limits)
-- ─────────────────────────────────────────────────────────────────────────────
