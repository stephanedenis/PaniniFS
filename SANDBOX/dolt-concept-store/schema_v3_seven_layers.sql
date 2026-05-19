-- Schema v3 : 7 couches d'analyse multilingue pour reconstruction textuelle
--
-- Granularite : PARAGRAPHE (pas phrase) car les langues ont des preferences
-- de longueur de phrases differentes (DE: longues, FR: courtes, FI: moyennes)
--
-- Les 7 couches :
--   1. Syntaxe          (structure, ordre des mots, dependances)
--   2. Alignement       (mot a atome cible)
--   3. Morphologie      (temps, aspect, cas, genre, nombre)
--   4. Registre/style   (formalite, archaisme, richesse)
--   5. Discours         (anaphore, connecteurs, coherence)
--   6. Prosodie         (rythme, cadence, figures)
--   7. Referents        (adaptations culturelles, domestication)
--
-- + Tables transversales : choix_traducteur, profil_langue
--
-- Compatible avec : schema_v2_universals.sql + schema_gutenberg_provenance.sql
--                   + schema_v3_reconstruction.sql (phrase-level)

-- Table 0 : Unites paragraphiques (granularite de travail)
CREATE TABLE IF NOT EXISTS paragraph_units (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    segment_id          INT NOT NULL,
    paragraph_index     INT NOT NULL,
    text_content        TEXT NOT NULL,
    sentence_count      INT NOT NULL,
    word_count          INT NOT NULL,
    char_count          INT NOT NULL,
    lang                VARCHAR(5) NOT NULL,
    alignment_group     VARCHAR(60),
    alignment_confidence FLOAT DEFAULT 0.0,
    UNIQUE KEY uq_para (segment_id, paragraph_index)
);

-- Table 1 : Analyse syntaxique (couche 1)
CREATE TABLE IF NOT EXISTS syntax_analysis (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    paragraph_id        INT NOT NULL,
    word_position       INT NOT NULL,
    word_form           VARCHAR(120) NOT NULL,
    pos_tag             VARCHAR(20),
    dep_relation        VARCHAR(30),
    head_position       INT DEFAULT -1,
    clause_id           INT DEFAULT 0,
    clause_type         VARCHAR(20) DEFAULT 'main',
    semantic_role       VARCHAR(20),
    lang                VARCHAR(5) NOT NULL,
    UNIQUE KEY uq_syn (paragraph_id, word_position)
);

-- Table 2 : Alignement mot-atome paragraphe-level (couche 2)
CREATE TABLE IF NOT EXISTS paragraph_word_atoms (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    paragraph_id        INT NOT NULL,
    word_position       INT NOT NULL,
    word_form           VARCHAR(120) NOT NULL,
    word_lemma          VARCHAR(120),
    atom_id             VARCHAR(30) NOT NULL,
    confidence          FLOAT NOT NULL,
    keyword_matched     VARCHAR(100),
    disambiguation      TEXT,
    sentence_local_idx  INT DEFAULT 0,
    UNIQUE KEY uq_pwa (paragraph_id, word_position, atom_id)
);

-- Table 3 : Traits morphologiques (couche 3)
CREATE TABLE IF NOT EXISTS morphology_features (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    paragraph_id        INT NOT NULL,
    word_position       INT NOT NULL,
    word_form           VARCHAR(120) NOT NULL,
    lemma               VARCHAR(120),
    tense               VARCHAR(30),
    aspect              VARCHAR(30),
    mood                VARCHAR(30),
    voice               VARCHAR(20),
    person              VARCHAR(5),
    number_feat         VARCHAR(10),
    gender              VARCHAR(15),
    case_feat           VARCHAR(20),
    degree              VARCHAR(15),
    lang                VARCHAR(5) NOT NULL,
    UNIQUE KEY uq_morph (paragraph_id, word_position)
);

-- Table 4 : Marqueurs de registre et style (couche 4)
CREATE TABLE IF NOT EXISTS register_markers (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    paragraph_id        INT NOT NULL,
    marker_type         VARCHAR(30) NOT NULL,
    marker_text         VARCHAR(200) NOT NULL,
    word_position_start INT,
    word_position_end   INT,
    formality_score     FLOAT DEFAULT 0.5,
    archaism_flag       BOOLEAN DEFAULT FALSE,
    literary_flag       BOOLEAN DEFAULT FALSE,
    colloquial_flag     BOOLEAN DEFAULT FALSE,
    explanation         TEXT,
    lang                VARCHAR(5) NOT NULL
);

-- Table 5 : Relations discursives (couche 5)
CREATE TABLE IF NOT EXISTS discourse_relations (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    paragraph_id        INT NOT NULL,
    relation_type       VARCHAR(30) NOT NULL,
    source_position     INT,
    target_position     INT,
    source_text         VARCHAR(200),
    target_text         VARCHAR(200),
    connector           VARCHAR(80),
    strength            FLOAT DEFAULT 0.5,
    sentence_local_idx  INT DEFAULT 0,
    lang                VARCHAR(5) NOT NULL
);

-- Table 6 : Prosodie et rythme (couche 6)
CREATE TABLE IF NOT EXISTS prosody_rhythm (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    paragraph_id        INT NOT NULL,
    sentence_local_idx  INT DEFAULT 0,
    syllable_count_est  INT,
    stress_pattern      VARCHAR(200),
    rhythm_type         VARCHAR(30),
    parallelism_group   VARCHAR(50),
    rhetorical_figure   VARCHAR(50),
    figure_text         VARCHAR(300),
    cadence_score       FLOAT DEFAULT 0.5,
    lang                VARCHAR(5) NOT NULL
);

-- Table 7 : Referents culturels (couche 7)
CREATE TABLE IF NOT EXISTS cultural_referents (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    paragraph_id        INT NOT NULL,
    referent_type       VARCHAR(30) NOT NULL,
    source_text         VARCHAR(200) NOT NULL,
    target_text         VARCHAR(200),
    original_text       VARCHAR(200),
    strategy            VARCHAR(30) NOT NULL,
    explanation         TEXT,
    cultural_distance   FLOAT DEFAULT 0.0,
    word_position_start INT,
    word_position_end   INT,
    lang                VARCHAR(5) NOT NULL
);

-- Table transversale : Choix du traducteur (explication detaillee)
CREATE TABLE IF NOT EXISTS translator_choices (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    paragraph_id        INT NOT NULL,
    edition_id          VARCHAR(50) NOT NULL,
    layer               VARCHAR(20) NOT NULL,
    choice_type         VARCHAR(40) NOT NULL,
    original_form       VARCHAR(300),
    translated_form     VARCHAR(300),
    alternative_forms   TEXT,
    explanation         TEXT NOT NULL,
    impact_on_meaning   VARCHAR(20) DEFAULT 'neutral',
    confidence          FLOAT DEFAULT 0.5,
    lang                VARCHAR(5) NOT NULL
);

-- Table transversale : Profil linguistique par langue
CREATE TABLE IF NOT EXISTS language_profiles (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    lang                VARCHAR(5) NOT NULL,
    lang_name           VARCHAR(50) NOT NULL,
    word_order          VARCHAR(10) NOT NULL,
    morphological_richness VARCHAR(10) NOT NULL,
    case_system         BOOLEAN DEFAULT FALSE,
    grammatical_gender  BOOLEAN DEFAULT FALSE,
    agglutinative       BOOLEAN DEFAULT FALSE,
    avg_sentence_length_preference FLOAT,
    subordination_tendency VARCHAR(10),
    formality_levels    VARCHAR(20),
    notes               TEXT,
    UNIQUE KEY uq_lang (lang)
);

-- Table transversale : Concepts paragraphe-level (remplacement sentence_concepts)
CREATE TABLE IF NOT EXISTS paragraph_concepts (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    paragraph_id        INT NOT NULL,
    concept_id          VARCHAR(50) NOT NULL,
    atoms_evidence      JSON,
    confidence          FLOAT NOT NULL,
    syntactic_coherence BOOLEAN DEFAULT TRUE,
    discourse_support   BOOLEAN DEFAULT FALSE,
    analysis_method     VARCHAR(30) DEFAULT 'seven_layer',
    UNIQUE KEY uq_pconcept (paragraph_id, concept_id)
);

-- Table transversale : Resume d'analyse par paragraphe
CREATE TABLE IF NOT EXISTS paragraph_analysis_summary (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    paragraph_id        INT NOT NULL,
    edition_id          VARCHAR(50) NOT NULL,
    segment_ref         VARCHAR(50) NOT NULL,
    layers_completed    INT DEFAULT 0,
    atom_count          INT DEFAULT 0,
    concept_count       INT DEFAULT 0,
    choice_count        INT DEFAULT 0,
    syntax_depth        FLOAT DEFAULT 0.0,
    morpho_complexity   FLOAT DEFAULT 0.0,
    register_score      FLOAT DEFAULT 0.5,
    discourse_density   FLOAT DEFAULT 0.0,
    prosody_score       FLOAT DEFAULT 0.5,
    cultural_adaptations INT DEFAULT 0,
    reconstruction_readiness FLOAT DEFAULT 0.0,
    UNIQUE KEY uq_psum (paragraph_id)
);

-- Vue : Alignement paragraphe inter-traductions
CREATE OR REPLACE VIEW v_paragraph_alignment AS
SELECT
    pu.alignment_group,
    ge.lang,
    ge.translator,
    pu.text_content,
    pu.word_count,
    pu.sentence_count,
    gs.segment_ref,
    gw.title_original AS work
FROM paragraph_units pu
JOIN gutenberg_segments gs ON pu.segment_id = gs.id
JOIN gutenberg_editions ge ON gs.edition_id = ge.id
JOIN gutenberg_works gw ON ge.work_id = gw.id
WHERE pu.alignment_group IS NOT NULL
ORDER BY pu.alignment_group, ge.lang;

-- Vue : Choix traducteurs compares
CREATE OR REPLACE VIEW v_translator_choices_compared AS
SELECT
    tc.layer,
    tc.choice_type,
    ge.lang,
    ge.translator,
    tc.original_form,
    tc.translated_form,
    tc.explanation,
    tc.impact_on_meaning,
    gs.segment_ref
FROM translator_choices tc
JOIN paragraph_units pu ON tc.paragraph_id = pu.id
JOIN gutenberg_segments gs ON pu.segment_id = gs.id
JOIN gutenberg_editions ge ON gs.edition_id = ge.id
ORDER BY gs.segment_ref, tc.layer, ge.lang;

-- Vue : Resume multicouche par paragraphe
CREATE OR REPLACE VIEW v_paragraph_multilayer AS
SELECT
    pas.segment_ref,
    ge.lang,
    ge.translator,
    pas.layers_completed,
    pas.atom_count,
    pas.concept_count,
    pas.choice_count,
    pas.register_score,
    pas.prosody_score,
    pas.cultural_adaptations,
    pas.reconstruction_readiness,
    pu.sentence_count,
    pu.word_count
FROM paragraph_analysis_summary pas
JOIN paragraph_units pu ON pas.paragraph_id = pu.id
JOIN gutenberg_segments gs ON pu.segment_id = gs.id
JOIN gutenberg_editions ge ON gs.edition_id = ge.id
ORDER BY pas.segment_ref, ge.lang;
