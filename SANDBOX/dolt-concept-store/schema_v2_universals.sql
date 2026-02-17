-- =============================================================================
-- PaniniFS Semantic Primitives v2.2 — Architecture 3 couches + axes émotionnels
-- =============================================================================
--
-- Fondé sur la revue interdisciplinaire (UNIVERSAUX_INTERDISCIPLINAIRES_*.md)
-- qui identifie 7 dimensions irréductibles à travers 10 domaines scientifiques.
--
-- v2.2: L'atome unique EMOTION (√hṛd) est remplacé par 8 sous-primitifs
-- émotionnels en 4 axes neurophysiologiques (Panksepp/Ekman/Plutchik/Damasio).
-- Voir PROPOSITION_SOUS_PRIMITIFS_EMOTIONNELS.md pour la justification.
--
-- Architecture: 3 couches + sous-couche émotionnelle
--   Couche 1:  Méta-catégories ontologiques (DOLCE/BFO/SUMO)
--   Couche 2:  Opérations structurelles (catégories/logique/computation)
--   Couche 3a: Prédicats sémantiques (9 dhātu — EMOTION retiré)
--   Couche 3b: Extensions non-verbales (espace, temps, évaluation, taxonomie)
--   Couche 3c: Axes émotionnels (4 axes × 2 pôles = 8 sous-primitifs)
--
-- Total: 4 + 5 + 9 + 4 + 8 = 30 primitifs
-- Stockage: branches Dolt tiered (public/confidential/private)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- COUCHE 1 — Méta-catégories ontologiques
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS ontological_categories (
    id          VARCHAR(10) PRIMARY KEY,      -- ENT, PROC, QUAL, ABS
    name_fr     VARCHAR(100) NOT NULL,
    name_en     VARCHAR(100) NOT NULL,
    name_sa     VARCHAR(100),                 -- Sanskrit si applicable
    description TEXT NOT NULL,
    dolce_equiv VARCHAR(50),                  -- Endurant, Perdurant, Quality, Abstract
    bfo_equiv   VARCHAR(50),                  -- Continuant, Occurrent, Dep.Continuant, Gen.Dep.
    sumo_equiv  VARCHAR(50),                  -- Object, Process, Attribute, Abstract
    examples    JSON,                         -- ["personne","arbre","lieu"]
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────────────────────────────────────
-- COUCHE 2 — Opérations structurelles
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS structural_operations (
    id          VARCHAR(10) PRIMARY KEY,      -- COMP, ID, NEG, QUANT, MOD
    name_fr     VARCHAR(100) NOT NULL,
    name_en     VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    category_theory_equiv VARCHAR(100),       -- composition, identity, initial, limit, subobject
    logic_equiv           VARCHAR(100),       -- conjunction, tautology, negation, quantifier, modality
    computation_equiv     VARCHAR(100),       -- S combinator, I combinator, bottom, recursion, maybe
    nsm_equiv             VARCHAR(100),       -- SAME, NOT, ONE/ALL/SOME, CAN/MAYBE
    arity       INT NOT NULL DEFAULT 2,       -- Nombre d'arguments
    signature   VARCHAR(200),                 -- Ex: "(concept, concept) -> concept"
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────────────────────────────────────
-- COUCHE 3a — Prédicats sémantiques (dhātu) — 9 predicats (EMOTION retiré)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS semantic_predicates (
    id          VARCHAR(20) PRIMARY KEY,      -- MOUVEMENT, COGNITION, etc.
    code        VARCHAR(10) NOT NULL UNIQUE,  -- MOV, COG, PER, COM, CRE, EMO, EXI, DES, POS, VOL
    name_fr     VARCHAR(100) NOT NULL,
    name_en     VARCHAR(100) NOT NULL,
    dhatu_sa    VARCHAR(50),                  -- Racine sanskrit: √gam, √jñā, etc.
    description TEXT NOT NULL,
    ontological_category VARCHAR(10) NOT NULL DEFAULT 'PROC',  -- Tous sont PROC
    nsm_mapping JSON,                        -- ["MOVE","DO"] mapping vers NSM primes
    jackendoff_mapping VARCHAR(50),           -- GO, BE, STAY, CAUSE, LET, AFFECT
    levin_classes JSON,                       -- Classes de Levin correspondantes
    pustejovsky_quale VARCHAR(20),            -- FORMAL, CONSTITUTIVE, TELIC, AGENTIVE
    vendler_aspect VARCHAR(20),              -- state, activity, accomplishment, achievement
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ontological_category) REFERENCES ontological_categories(id)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- COUCHE 3bis — Extensions non-verbales
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS nonverbal_extensions (
    id          VARCHAR(20) PRIMARY KEY,      -- ESPACE, TEMPS, EVAL, TAXO
    name_fr     VARCHAR(100) NOT NULL,
    name_en     VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    ontological_category VARCHAR(10) NOT NULL, -- Variée: ABS, QUAL, etc.
    nsm_mapping JSON,                         -- Mapping NSM
    dimension   VARCHAR(30) NOT NULL,         -- SITUATION, QUALITE, RELATION
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ontological_category) REFERENCES ontological_categories(id)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- COUCHE 3c — Axes émotionnels (Panksepp/Ekman/Plutchik/Damasio) [v2.2]
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS emotional_axes (
    id              VARCHAR(20) PRIMARY KEY,      -- SEEKING, FEAR, CARE, GRIEF, RAGE, DISGUST, PLAY, TEDIUM
    code            VARCHAR(10) NOT NULL UNIQUE,  -- SEK, FEA, CAR, GRI, RAG, DIS, PLA, TED
    axis_name_fr    VARCHAR(100) NOT NULL,        -- APPÉTENCE, LIEN, ASSERTION, JOUISSANCE
    axis_name_en    VARCHAR(100) NOT NULL,        -- APPETENCE, BOND, ASSERTION, ENJOYMENT
    polarity        VARCHAR(10) NOT NULL,         -- '+' ou '-'
    name_fr         VARCHAR(100) NOT NULL,
    name_en         VARCHAR(100) NOT NULL,
    dhatu_sa        VARCHAR(50),                  -- Racine sanskrit: √iṣ, √bhī, etc.
    description     TEXT NOT NULL,
    neural_circuit  VARCHAR(200),                 -- Circuit neuronal principal
    neurotransmitters VARCHAR(200),               -- Neurotransmetteurs clés
    panksepp_system VARCHAR(30),                  -- Système Panksepp correspondant
    ekman_emotion   VARCHAR(50),                  -- Émotion Ekman correspondante (si applicable)
    plutchik_emotion VARCHAR(50),                 -- Émotion Plutchik correspondante (si applicable)
    nsm_mapping     JSON,                         -- Mapping vers NSM primes
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────────────────────────────────────
-- CONCEPTS — Les concepts PanLang (nettoyés et importés)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS concepts (
    id              VARCHAR(50) PRIMARY KEY,       -- COLÈRE, EXPLORER, etc.
    name_fr         VARCHAR(200) NOT NULL,
    formule_simple  VARCHAR(500) NOT NULL,          -- "EMOTION + DOMINATION"
    formule_typed   JSON,                           -- Formule typée v2
    -- Décomposition en atomes
    atoms           JSON NOT NULL,                  -- ["EMOTION","DOMINATION"]
    atom_count      INT NOT NULL,
    complexity      INT NOT NULL DEFAULT 1,
    -- Qualité
    validity_score  FLOAT,                          -- 0.0 - 1.0
    quality_tier    CHAR(1) NOT NULL DEFAULT 'C',   -- A, B, C
    -- Classification ontologique
    primary_category VARCHAR(10),                   -- ENT, PROC, QUAL, ABS
    dimensions_covered JSON,                        -- ["PROCESSUS","QUALITÉ"]
    -- Provenance
    source          VARCHAR(200),
    formule_format  VARCHAR(20) NOT NULL,            -- 'dict' ou 'plain'
    scientifically_validated INT DEFAULT 0,          -- 0/1
    -- Références croisées
    nsm_coverage    JSON,                           -- Quels NSM primes ce concept touche
    pustejovsky_qualia JSON,                        -- Quels qualia sont impliqués
    -- Timestamps
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_quality (quality_tier),
    INDEX idx_complexity (complexity),
    INDEX idx_category (primary_category),
    INDEX idx_validity (validity_score),
    FOREIGN KEY (primary_category) REFERENCES ontological_categories(id)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- COMPOSITIONS — Règles de composition typées
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS composition_rules (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    concept_id      VARCHAR(50) NOT NULL,
    position        INT NOT NULL,                    -- Ordre dans la formule
    atom_id         VARCHAR(20) NOT NULL,             -- Réf vers semantic_predicates ou nonverbal_ext
    atom_layer      VARCHAR(10) NOT NULL,             -- 'predicate', 'extension', or 'emotional'
    role            VARCHAR(30),                      -- Rôle dans la composition: CAUSE, AGENT, THEME
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_concept (concept_id),
    INDEX idx_atom (atom_id),
    FOREIGN KEY (concept_id) REFERENCES concepts(id)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- DIMENSION COVERAGE — Couverture des 7 dimensions irréductibles
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS dimension_coverage (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    concept_id      VARCHAR(50) NOT NULL,
    dimension       VARCHAR(20) NOT NULL,             -- ENTITE, PROCESSUS, QUALITE, RELATION, STRUCTURE, SITUATION, MODALITE
    coverage_score  FLOAT NOT NULL,                   -- 0.0 - 1.0
    covered_by      JSON,                             -- Quels atomes couvrent cette dimension
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_concept_dim (concept_id, dimension),
    INDEX idx_dimension (dimension),
    FOREIGN KEY (concept_id) REFERENCES concepts(id)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- VALIDATION SCIENTIFIQUE — Résultats de comparaison avec la littérature
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS scientific_validation (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    concept_id      VARCHAR(50) NOT NULL,
    framework       VARCHAR(50) NOT NULL,             -- NSM, Jackendoff, Pustejovsky, Lakoff, Greimas
    validation_type VARCHAR(30) NOT NULL,             -- 'coverage', 'alignment', 'divergence'
    score           FLOAT,
    details         JSON,
    reference       VARCHAR(500),                     -- Citation bibliographique
    validated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_concept (concept_id),
    INDEX idx_framework (framework),
    FOREIGN KEY (concept_id) REFERENCES concepts(id)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- QUALITY AUDIT LOG — Historique de l'audit qualité
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS quality_audit (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    concept_id      VARCHAR(50),                      -- NULL si audit global
    issue_type      VARCHAR(50) NOT NULL,             -- 'duplicate', 'tautology', 'low_validity', 'absurd_formula', 'metadata_pollution'
    severity        VARCHAR(10) NOT NULL,             -- 'critical', 'warning', 'info'
    description     TEXT NOT NULL,
    resolution      VARCHAR(30),                      -- 'excluded', 'fixed', 'accepted', 'pending'
    detected_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_issue (issue_type),
    INDEX idx_severity (severity)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- VUES
-- ─────────────────────────────────────────────────────────────────────────────

-- Vue: Distribution des atomes dans les concepts
CREATE VIEW IF NOT EXISTS v_atom_distribution AS
SELECT 
    j.atom,
    COUNT(*) as usage_count,
    GROUP_CONCAT(c.id ORDER BY c.id SEPARATOR ', ') as concepts
FROM concepts c
JOIN JSON_TABLE(c.atoms, '$[*]' COLUMNS (atom VARCHAR(20) PATH '$')) j
GROUP BY j.atom
ORDER BY usage_count DESC;

-- Vue: Concepts par tier de qualité
CREATE VIEW IF NOT EXISTS v_quality_summary AS
SELECT 
    quality_tier,
    COUNT(*) as concept_count,
    ROUND(AVG(validity_score), 3) as avg_validity,
    ROUND(AVG(atom_count), 1) as avg_atoms,
    ROUND(AVG(complexity), 1) as avg_complexity
FROM concepts
GROUP BY quality_tier
ORDER BY quality_tier;

-- Vue: Couverture dimensionnelle globale
CREATE VIEW IF NOT EXISTS v_dimension_gap_analysis AS
SELECT 
    dimension,
    COUNT(*) as concepts_covering,
    ROUND(AVG(coverage_score), 3) as avg_coverage,
    ROUND(SUM(coverage_score) / (SELECT COUNT(*) FROM concepts), 3) as global_coverage
FROM dimension_coverage
WHERE coverage_score > 0
GROUP BY dimension
ORDER BY global_coverage DESC;

-- Vue: Concepts problématiques (audit)
CREATE VIEW IF NOT EXISTS v_problematic_concepts AS
SELECT 
    c.id,
    c.formule_simple,
    c.validity_score,
    c.quality_tier,
    COUNT(qa.id) as issue_count,
    GROUP_CONCAT(qa.issue_type SEPARATOR ', ') as issues
FROM concepts c
LEFT JOIN quality_audit qa ON c.id = qa.concept_id
WHERE c.quality_tier = 'C' OR c.validity_score < 0.3
GROUP BY c.id, c.formule_simple, c.validity_score, c.quality_tier
ORDER BY c.validity_score ASC;
