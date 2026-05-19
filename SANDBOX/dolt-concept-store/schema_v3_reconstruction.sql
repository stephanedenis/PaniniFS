-- ═══════════════════════════════════════════════════════════════════
-- schema_v3_reconstruction.sql
-- Extension pour la reconstruction textuelle phrase-level
-- 
-- Objectif : passer du bag-of-atoms (segment ~500 mots, 19 concepts)
-- à une représentation phrase-level avec attribution mot→atome ciblée
-- (~15 mots, 2-4 concepts précis par phrase)
--
-- Tables nouvelles : 4
-- Vues nouvelles : 2
-- Compatible avec : schema_v2_universals.sql + schema_gutenberg_provenance.sql
-- ═══════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────
-- Table 1: Phrases individuelles extraites des segments
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS gutenberg_sentences (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    segment_id      INT NOT NULL,                   -- FK → gutenberg_segments
    sentence_index  INT NOT NULL,                   -- position dans le segment (0-based)
    text_content    TEXT NOT NULL,                   -- texte de la phrase
    word_count      INT NOT NULL,
    char_count      INT NOT NULL,
    lang            VARCHAR(5) NOT NULL,
    -- Alignement inter-éditions
    alignment_group VARCHAR(50),                    -- ID de groupe pour phrases alignées
    alignment_confidence FLOAT DEFAULT 0.0,         -- confiance de l'alignement (0-1)
    alignment_method VARCHAR(30) DEFAULT 'sequential', -- sequential | keyword | manual
    UNIQUE KEY uq_seg_sent (segment_id, sentence_index)
);

-- ─────────────────────────────────────────────────────────────────
-- Table 2: Attribution mot→atome ciblée
-- Chaque mot pointé vers son atome spécifique (pas le segment entier)
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS word_atom_attributions (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    sentence_id     INT NOT NULL,                   -- FK → gutenberg_sentences
    word_position   INT NOT NULL,                   -- position dans la phrase (0-based)
    word_form       VARCHAR(100) NOT NULL,           -- forme de surface ("fell", "tomba")
    word_lemma      VARCHAR(100),                    -- lemme ("fall", "tomber")
    atom_id         VARCHAR(30) NOT NULL,            -- atome attribué (MOUVEMENT, COGNITION, etc.)
    confidence      FLOAT NOT NULL,                  -- confiance de cette attribution spécifique
    keyword_matched VARCHAR(100),                    -- le keyword du dictionnaire qui a matché
    disambiguation  TEXT,                            -- note : ex "sein = être (verbe), pas son (possessif)"
    UNIQUE KEY uq_word_atom (sentence_id, word_position, atom_id)
);

-- ─────────────────────────────────────────────────────────────────
-- Table 3: Concepts détectés au niveau phrase (précis)
-- Remplace segment_decompositions pour la granularité fine
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sentence_concepts (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    sentence_id     INT NOT NULL,                   -- FK → gutenberg_sentences
    concept_id      VARCHAR(50) NOT NULL,
    atoms_evidence  JSON,                            -- {"MOUVEMENT": {"word": "fell", "pos": 2, "conf": 0.95}, ...}
    confidence      FLOAT NOT NULL,
    is_in_window    BOOLEAN DEFAULT TRUE,            -- les atomes sont-ils dans la même fenêtre syntaxique ?
    analysis_method VARCHAR(30) DEFAULT 'keyword_targeted',
    UNIQUE KEY uq_sent_concept (sentence_id, concept_id)
);

-- ─────────────────────────────────────────────────────────────────
-- Table 4: Profil stylistique par édition/traducteur
-- Métriques calculées sur les phrases pour capturer le style
-- ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS translator_style_profile (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    edition_id      VARCHAR(50) NOT NULL,            -- FK → gutenberg_editions
    segment_ref     VARCHAR(50) NOT NULL,            -- passage analysé
    -- Métriques phrase-level
    avg_sentence_length FLOAT,                       -- mots par phrase (moyenne)
    max_sentence_length INT,                         -- phrase la plus longue
    min_sentence_length INT,                         -- phrase la plus courte
    sentence_count      INT,                         -- nombre de phrases dans le segment
    -- Richesse lexicale
    type_token_ratio    FLOAT,                       -- types uniques / tokens totaux
    hapax_ratio         FLOAT,                       -- mots n'apparaissant qu'une fois / total
    -- Ponctuation et rythme
    avg_punctuation_density FLOAT,                   -- signes de ponctuation / mots
    exclamation_count   INT DEFAULT 0,
    question_count      INT DEFAULT 0,
    semicolon_count     INT DEFAULT 0,
    dash_count          INT DEFAULT 0,
    UNIQUE KEY uq_style (edition_id, segment_ref)
);

-- ─────────────────────────────────────────────────────────────────
-- Vue 1: Alignement inter-traductions phrase par phrase
-- ─────────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW v_sentence_alignment AS
SELECT 
    gs_sent.alignment_group,
    ge.lang,
    ge.translator,
    gs_sent.text_content AS sentence_text,
    gs_sent.word_count,
    gs_seg.segment_ref,
    gw.title_original AS work
FROM gutenberg_sentences gs_sent
JOIN gutenberg_segments gs_seg ON gs_sent.segment_id = gs_seg.id
JOIN gutenberg_editions ge ON gs_seg.edition_id = ge.id
JOIN gutenberg_works gw ON ge.work_id = gw.id
WHERE gs_sent.alignment_group IS NOT NULL
ORDER BY gs_sent.alignment_group, ge.lang;

-- ─────────────────────────────────────────────────────────────────
-- Vue 2: Convergence phrase-level (plus précise que segment-level)
-- ─────────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW v_sentence_convergence AS
SELECT 
    gs_sent.alignment_group,
    sc.concept_id,
    COUNT(DISTINCT ge.lang) AS langs_detected,
    COUNT(DISTINCT ge.id) AS editions_detected,
    ROUND(AVG(sc.confidence), 3) AS avg_confidence,
    GROUP_CONCAT(DISTINCT ge.lang ORDER BY ge.lang) AS langs_list
FROM sentence_concepts sc
JOIN gutenberg_sentences gs_sent ON sc.sentence_id = gs_sent.id
JOIN gutenberg_segments gs_seg ON gs_sent.segment_id = gs_seg.id
JOIN gutenberg_editions ge ON gs_seg.edition_id = ge.id
WHERE gs_sent.alignment_group IS NOT NULL
GROUP BY gs_sent.alignment_group, sc.concept_id
ORDER BY gs_sent.alignment_group, editions_detected DESC;
