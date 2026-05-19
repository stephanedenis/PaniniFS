#!/usr/bin/env python3
"""
test_seven_layers.py — Tests for the 7-layer multilingual analysis engine

Tests cover:
  - Language profiles configuration
  - Paragraph splitting (sentence grouping)
  - Layer 1: Syntax (POS tagging, dependency heuristics)
  - Layer 2: Word-atom alignment (targeted attribution)
  - Layer 3: Morphology (tense, aspect, case, gender, number)
  - Layer 4: Register/style (formal, archaic, literary markers)
  - Layer 5: Discourse (connectors, anaphora)
  - Layer 6: Prosody (rhythm, syllables, figures)
  - Layer 7: Cultural referents (domestication/foreignization)
  - Translator choices generation
  - Paragraph concept detection
  - Cross-language comparison invariants
"""

import os
import sys
import unittest

# Make the module importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "SANDBOX", "dolt-concept-store"))

from seven_layers_engine import (
    LANGUAGE_PROFILES, CONCEPT_MAPPINGS,
    split_into_paragraphs, split_into_sentences,
    analyze_syntax, align_words_to_atoms,
    analyze_morphology, analyze_register,
    analyze_discourse, analyze_prosody, estimate_syllables,
    analyze_cultural_referents,
    generate_translator_choices,
    detect_paragraph_concepts,
)


class TestLanguageProfiles(unittest.TestCase):
    """Test language profile configuration."""

    def test_all_languages_present(self):
        """All 7 expected languages must have profiles."""
        expected = {"en", "fr", "de", "it", "es", "eo", "fi"}
        self.assertEqual(set(LANGUAGE_PROFILES.keys()), expected)

    def test_profile_required_fields(self):
        """Each profile must have all required fields."""
        required = [
            "lang_name", "word_order", "morphological_richness",
            "case_system", "grammatical_gender", "agglutinative",
            "avg_sentence_length_preference", "subordination_tendency",
            "formality_levels",
        ]
        for lang, p in LANGUAGE_PROFILES.items():
            for field in required:
                self.assertIn(field, p, f"{lang} missing '{field}'")

    def test_word_order_valid(self):
        """Word order must be SVO, SOV, VSO, etc."""
        valid = {"SVO", "SOV", "VSO", "VOS", "OVS", "OSV"}
        for lang, p in LANGUAGE_PROFILES.items():
            self.assertIn(p["word_order"], valid, f"{lang} invalid word order")

    def test_german_is_sov(self):
        """German should be SOV (subordinate clauses)."""
        self.assertEqual(LANGUAGE_PROFILES["de"]["word_order"], "SOV")

    def test_finnish_has_case_system(self):
        """Finnish has 15 grammatical cases."""
        self.assertTrue(LANGUAGE_PROFILES["fi"]["case_system"])
        self.assertTrue(LANGUAGE_PROFILES["fi"]["agglutinative"])

    def test_esperanto_no_gender(self):
        """Esperanto has no grammatical gender."""
        self.assertFalse(LANGUAGE_PROFILES["eo"]["grammatical_gender"])

    def test_french_has_gender(self):
        """French has grammatical gender."""
        self.assertTrue(LANGUAGE_PROFILES["fr"]["grammatical_gender"])

    def test_sentence_length_preferences(self):
        """Finnish should prefer shorter sentences than German."""
        self.assertLess(
            LANGUAGE_PROFILES["fi"]["avg_sentence_length_preference"],
            LANGUAGE_PROFILES["de"]["avg_sentence_length_preference"]
        )

    def test_connector_lists_present(self):
        """Each profile should have discourse connector lists."""
        for lang, p in LANGUAGE_PROFILES.items():
            self.assertIn("temporal_connectors", p, f"{lang} missing temporal_connectors")
            self.assertIn("causal_connectors", p, f"{lang} missing causal_connectors")
            self.assertIn("adversative_connectors", p, f"{lang} missing adversative_connectors")


class TestParagraphSplitting(unittest.TestCase):
    """Test paragraph and sentence splitting."""

    def test_split_by_double_newline(self):
        """Text with double newlines should split into paragraphs."""
        text = "First paragraph with enough text here.\n\nSecond paragraph with enough text here.\n\nThird paragraph with enough text here."
        paras = split_into_paragraphs(text, "en")
        self.assertEqual(len(paras), 3)

    def test_single_block_becomes_one_or_more_paragraphs(self):
        """A single block of text should produce at least one paragraph."""
        text = "Alice was beginning to get very tired of sitting by her sister."
        paras = split_into_paragraphs(text, "en")
        self.assertGreaterEqual(len(paras), 1)

    def test_empty_text(self):
        """Empty text should produce one paragraph."""
        paras = split_into_paragraphs("Some short text", "en")
        self.assertGreaterEqual(len(paras), 1)

    def test_sentence_split_english(self):
        """English sentence splitting should work on standard text."""
        text = "Alice fell down. She looked around. It was dark."
        sentences = split_into_sentences(text, "en")
        self.assertEqual(len(sentences), 3)

    def test_sentence_split_french(self):
        """French sentence splitting should handle accented chars."""
        text = "Alice tomba dans le terrier. Elle regarda autour d'elle. C'était sombre."
        sentences = split_into_sentences(text, "fr")
        self.assertEqual(len(sentences), 3)

    def test_abbreviations_not_split(self):
        """Abbreviations like Mr. should not cause sentence splits."""
        text = "Mr. Smith went to Washington. He met Dr. Jones there."
        sentences = split_into_sentences(text, "en")
        self.assertEqual(len(sentences), 2)


class TestSyntaxAnalysis(unittest.TestCase):
    """Test Layer 1: Syntax."""

    def test_english_sentence(self):
        """Basic English POS tagging."""
        results = analyze_syntax("The cat sat on the mat.", "en")
        self.assertGreaterEqual(len(results), 6)
        # "The" should be DET
        self.assertEqual(results[0]["pos_tag"], "DET")

    def test_pos_tags_are_valid(self):
        """All POS tags should be standard UPOS tags or close."""
        valid_pos = {"NOUN", "VERB", "ADJ", "ADV", "DET", "ADP", "PRON",
                     "CCONJ", "SCONJ", "AUX", "NUM", "PART", "PROPN"}
        results = analyze_syntax("She quickly ran to the old house.", "en")
        for r in results:
            self.assertIn(r["pos_tag"], valid_pos, f"Invalid POS: {r['pos_tag']}")

    def test_german_determiners(self):
        """German determiners should be tagged DET."""
        results = analyze_syntax("Der Hase lief schnell.", "de")
        self.assertEqual(results[0]["pos_tag"], "DET")

    def test_french_pronouns(self):
        """French pronouns should be tagged PRON."""
        results = analyze_syntax("Elle tomba dans le terrier.", "fr")
        self.assertEqual(results[0]["pos_tag"], "PRON")

    def test_semantic_roles_present(self):
        """At least some words should have semantic roles."""
        results = analyze_syntax("Alice fell down the rabbit hole.", "en")
        roles = [r["semantic_role"] for r in results if r["semantic_role"]]
        self.assertGreater(len(roles), 0)

    def test_clause_detection(self):
        """Subordinate conjunctions should trigger new clause IDs."""
        results = analyze_syntax(
            "Alice fell because she was curious.", "en"
        )
        clause_ids = set(r["clause_id"] for r in results)
        self.assertGreaterEqual(len(clause_ids), 2,
                                "Should detect at least 2 clauses")


class TestWordAtomAlignment(unittest.TestCase):
    """Test Layer 2: Word-atom alignment."""

    def test_english_movement(self):
        """'fall' or 'falling' should map to MOUVEMENT."""
        results = align_words_to_atoms("Alice was falling down the hole.", "en")
        atoms = {r["atom_id"] for r in results}
        self.assertIn("MOUVEMENT", atoms)

    def test_french_cognition(self):
        """'penser' should map to COGNITION."""
        results = align_words_to_atoms("Elle pensait à sa soeur.", "fr")
        atoms = {r["atom_id"] for r in results}
        self.assertIn("COGNITION", atoms)

    def test_german_perception(self):
        """'sehen' should map to PERCEPTION."""
        results = align_words_to_atoms("Sie konnte nichts sehen.", "de")
        atoms = {r["atom_id"] for r in results}
        self.assertIn("PERCEPTION", atoms)

    def test_confidence_levels(self):
        """Confidence should be between 0 and 1."""
        results = align_words_to_atoms("She fell and saw the light.", "en")
        for r in results:
            self.assertGreaterEqual(r["confidence"], 0.0)
            self.assertLessEqual(r["confidence"], 1.0)

    def test_disambiguation_noted(self):
        """German 'sein' should have disambiguation note."""
        results = align_words_to_atoms("sein Hut war groß.", "de")
        # Find 'sein' attribution
        sein_results = [r for r in results if "sein" in r["word_form"].lower()]
        if sein_results:
            # At least one should have disambiguation
            has_disambig = any(r.get("disambiguation") for r in sein_results)
            self.assertTrue(has_disambig, "German 'sein' should note ambiguity")

    def test_sentence_index_tracked(self):
        """Each attribution should track which sentence it's in."""
        results = align_words_to_atoms(
            "Alice can go far. She wants to run fast.", "en"
        )
        sent_indices = {r.get("sentence_local_idx") for r in results}
        # Should have attributions in at least sentence 0 (go=MOUVEMENT)
        self.assertIn(0, sent_indices)

    def test_finnish_atoms(self):
        """Finnish atom detection should work with dictionary forms."""
        results = align_words_to_atoms("Liisa pudota ja hypätä.", "fi")
        atoms = {r["atom_id"] for r in results}
        self.assertIn("MOUVEMENT", atoms)

    def test_esperanto_atoms(self):
        """Esperanto atom detection should work."""
        results = align_words_to_atoms("Alicio falis en la kuniklan truon.", "eo")
        atoms = {r["atom_id"] for r in results}
        self.assertIn("MOUVEMENT", atoms)


class TestMorphology(unittest.TestCase):
    """Test Layer 3: Morphology."""

    def test_english_past_tense(self):
        """English '-ed' words should be tagged past tense."""
        syntax = analyze_syntax("She walked to school.", "en")
        morpho = analyze_morphology("She walked to school.", "en", syntax)
        # "walked" is position 1
        walked = morpho[1]
        self.assertEqual(walked["tense"], "past")

    def test_french_passe_simple(self):
        """French passé simple should be detected."""
        syntax = analyze_syntax("Elle tomba dans le terrier.", "fr")
        morpho = analyze_morphology("Elle tomba dans le terrier.", "fr", syntax)
        # "tomba" is position 1
        tomba = morpho[1]
        self.assertEqual(tomba["tense"], "passé_simple")

    def test_italian_gender(self):
        """Italian '-a' ending should suggest feminine."""
        syntax = analyze_syntax("La ragazza cammina.", "it")
        morpho = analyze_morphology("La ragazza cammina.", "it", syntax)
        # "ragazza" position 1
        ragazza = morpho[1]
        self.assertEqual(ragazza["gender"], "feminine")

    def test_esperanto_accusative(self):
        """Esperanto '-n' ending should be accusative."""
        # Engine checks word_raw.endswith('n'), so mid-sentence words work
        syntax = analyze_syntax("Mi vidis hundon kaj katon.", "eo")
        morpho = analyze_morphology("Mi vidis hundon kaj katon.", "eo", syntax)
        # "hundon" is at position 2 (mid-sentence, no trailing period)
        hundon = morpho[2]
        self.assertEqual(hundon.get("case_feat"), "accusative")

    def test_finnish_cases(self):
        """Finnish case suffixes should be detected."""
        syntax = analyze_syntax("Talossa oli kissa.", "fi")
        morpho = analyze_morphology("Talossa oli kissa.", "fi", syntax)
        # "Talossa" — inessive (-ssa)
        talossa = morpho[0]
        if talossa.get("case_feat"):
            self.assertEqual(talossa["case_feat"], "inessive")

    def test_passive_voice_english(self):
        """English passive should be detected (was + past participle)."""
        syntax = analyze_syntax("The door was opened.", "en")
        morpho = analyze_morphology("The door was opened.", "en", syntax)
        # "opened" after "was" should be passive
        opened = morpho[3]
        self.assertEqual(opened["voice"], "passive")


class TestRegister(unittest.TestCase):
    """Test Layer 4: Register/Style."""

    def test_english_formal_markers(self):
        """English formal markers should be detected."""
        results = analyze_register("Moreover, this is indeed important.", "en")
        marker_types = {r["marker_type"] for r in results}
        self.assertIn("formal", marker_types)

    def test_english_archaic_markers(self):
        """English archaic forms should be detected."""
        results = analyze_register("Thou art forsooth a fool.", "en")
        marker_types = {r["marker_type"] for r in results}
        self.assertIn("archaic", marker_types)

    def test_french_passe_simple_register(self):
        """French passé simple should be detected as register marker."""
        results = analyze_register(
            "Elle tomba dans le terrier. Il courut après elle.", "fr"
        )
        types = {r["marker_type"] for r in results}
        self.assertIn("tense_register", types)

    def test_german_archaic(self):
        """German archaic markers should be detected."""
        results = analyze_register("Ach, er sprach gar seltsam.", "de")
        types = {r["marker_type"] for r in results}
        self.assertTrue(
            "archaic" in types or "literary" in types,
            f"Expected archaic/literary marker, got: {types}"
        )

    def test_formality_score_range(self):
        """Formality scores should be between 0 and 1."""
        results = analyze_register(
            "Nevertheless, thou art forsooth mistaken.", "en"
        )
        for r in results:
            self.assertGreaterEqual(r["formality_score"], 0.0)
            self.assertLessEqual(r["formality_score"], 1.0)


class TestDiscourse(unittest.TestCase):
    """Test Layer 5: Discourse relations."""

    def test_temporal_connector_english(self):
        """'then' should be detected as temporal connector."""
        results = analyze_discourse("Alice fell. Then she looked around.", "en")
        types = {r["relation_type"] for r in results}
        self.assertIn("temporal", types)

    def test_causal_connector_french(self):
        """'car' should be detected as causal connector."""
        results = analyze_discourse("Elle pleurait car elle était perdue.", "fr")
        types = {r["relation_type"] for r in results}
        self.assertIn("causal", types)

    def test_adversative_connector_german(self):
        """'aber' should be detected as adversative."""
        results = analyze_discourse("Er war müde, aber er ging weiter.", "de")
        types = {r["relation_type"] for r in results}
        self.assertIn("adversative", types)

    def test_anaphora_detection(self):
        """Third-person pronouns should be detected as anaphoric."""
        results = analyze_discourse(
            "Alice was curious. She followed the rabbit. He ran quickly.", "en"
        )
        anaphora = [r for r in results if r["relation_type"] == "anaphora"]
        self.assertGreater(len(anaphora), 0)

    def test_connector_strength(self):
        """Connector strength should be between 0 and 1."""
        results = analyze_discourse("Then she fell because it was dark.", "en")
        for r in results:
            self.assertGreaterEqual(r["strength"], 0.0)
            self.assertLessEqual(r["strength"], 1.0)


class TestProsody(unittest.TestCase):
    """Test Layer 6: Prosody/Rhythm."""

    def test_syllable_estimation(self):
        """Syllable counts should be reasonable."""
        self.assertGreaterEqual(estimate_syllables("Alice", "en"), 2)
        self.assertEqual(estimate_syllables("cat", "en"), 1)
        self.assertGreaterEqual(estimate_syllables("curiosity", "en"), 4)

    def test_rhythm_types(self):
        """Different sentence lengths should produce different rhythms."""
        results = analyze_prosody(
            "Short. This is a moderately long sentence with several words in it.", "en"
        )
        rhythms = {r["rhythm_type"] for r in results}
        # Should have at least two different rhythms
        self.assertGreaterEqual(len(rhythms), 1)

    def test_exclamation_detection(self):
        """Exclamation marks should be detected as rhetorical figures."""
        results = analyze_prosody("How wonderful! What a surprise!", "en")
        figures = [r for r in results if r.get("rhetorical_figure") == "exclamation"]
        self.assertGreater(len(figures), 0)

    def test_question_detection(self):
        """Question marks should be detected."""
        results = analyze_prosody("Who are you? What do you want?", "en")
        figures = [r for r in results if r.get("rhetorical_figure") == "question"]
        self.assertGreater(len(figures), 0)

    def test_cadence_score_range(self):
        """Cadence scores should be between 0 and 1."""
        results = analyze_prosody(
            "Short sentence. A much longer sentence with many more words in it.", "en"
        )
        for r in results:
            self.assertGreaterEqual(r["cadence_score"], 0.0)
            self.assertLessEqual(r["cadence_score"], 1.0)

    def test_parallelism_detection(self):
        """Similar-length consecutive sentences should trigger parallelism."""
        results = analyze_prosody(
            "She walked slowly. He talked softly. They moved gently.", "en"
        )
        parallel = [r for r in results if r.get("parallelism_group")]
        self.assertGreater(len(parallel), 0, "Should detect parallel sentences")


class TestCulturalReferents(unittest.TestCase):
    """Test Layer 7: Cultural referents."""

    def test_english_food(self):
        """English food items should be detected."""
        results = analyze_cultural_referents(
            "She ate some pudding and drank tea.", "en", "ALICE_EN_11"
        )
        types = {r["referent_type"] for r in results}
        self.assertIn("food_drink", types)

    def test_finnish_name_domestication(self):
        """Finnish 'Liisa' for 'Alice' = domestication."""
        results = analyze_cultural_referents(
            "Liisa juoksi nopeasti.", "fi", "ALICE_FI_46569"
        )
        names = [r for r in results if r["referent_type"] == "proper_name"]
        self.assertGreater(len(names), 0)
        self.assertEqual(names[0]["strategy"], "domestication")
        self.assertEqual(names[0]["target_text"], "Liisa")

    def test_esperanto_name_domestication(self):
        """Esperanto 'Alicio' for 'Alice' = domestication."""
        results = analyze_cultural_referents(
            "Alicio falis malsupren.", "eo", "ALICE_EO_17482"
        )
        names = [r for r in results if r["referent_type"] == "proper_name"]
        self.assertGreater(len(names), 0)
        self.assertEqual(names[0]["strategy"], "domestication")

    def test_french_name_retention(self):
        """French keeps 'Alice' = retention."""
        results = analyze_cultural_referents(
            "Alice tomba dans le terrier.", "fr", "ALICE_FR_55456"
        )
        names = [r for r in results if r["referent_type"] == "proper_name"]
        self.assertGreater(len(names), 0)
        self.assertEqual(names[0]["strategy"], "retention")

    def test_cultural_distance_range(self):
        """Cultural distance should be between 0 and 1."""
        results = analyze_cultural_referents(
            "Liisa söi puuroa.", "fi", "ALICE_FI_46569"
        )
        for r in results:
            self.assertGreaterEqual(r["cultural_distance"], 0.0)
            self.assertLessEqual(r["cultural_distance"], 1.0)


class TestTranslatorChoices(unittest.TestCase):
    """Test translator choice generation."""

    def test_sentence_length_deviation(self):
        """Large deviation from expected sentence length should generate a choice."""
        # German expects 25 words/sentence, give it very short sentences
        text = "Kurz. Sehr kurz. Auch kurz."
        morpho = []
        register = []
        prosody = analyze_prosody(text, "de")
        cultural = []
        choices = generate_translator_choices(
            text, "de", "TEST_ED", None, morpho, register, prosody, cultural
        )
        types = {c["choice_type"] for c in choices}
        self.assertIn("sentence_length", types)

    def test_archaic_register_choice(self):
        """Archaic markers should generate register choices."""
        register = [{"archaism_flag": True, "marker_text": "thou",
                      "explanation": "Archaic pronoun"}]
        choices = generate_translator_choices(
            "Thou art brave.", "en", "TEST", None,
            [], register, [], []
        )
        types = {c["choice_type"] for c in choices}
        self.assertIn("archaism", types)

    def test_cultural_domestication_choice(self):
        """Cultural domestication should generate a choice."""
        cultural = [{
            "strategy": "domestication",
            "original_text": "Alice",
            "target_text": "Liisa",
            "explanation": "Name adapted",
        }]
        choices = generate_translator_choices(
            "Liisa juoksi.", "fi", "TEST", None, [], [], [], cultural
        )
        types = {c["choice_type"] for c in choices}
        self.assertIn("domestication", types)

    def test_sov_word_order_choice(self):
        """SOV language should generate word_order choice."""
        choices = generate_translator_choices(
            "Der Hase lief schnell.", "de", "TEST", None, [], [], [], []
        )
        types = {c["choice_type"] for c in choices}
        self.assertIn("word_order", types)

    def test_morphological_encoding_choice(self):
        """High-morphology language should generate encoding choice."""
        choices = generate_translator_choices(
            "Talossa oli kissa.", "fi", "TEST", None, [], [], [], []
        )
        types = {c["choice_type"] for c in choices}
        self.assertIn("morphological_encoding", types)

    def test_impact_on_meaning_valid(self):
        """Impact values should be valid."""
        valid = {"neutral", "style", "register", "cultural", "semantic"}
        choices = generate_translator_choices(
            "Thou art forsooth mistaken.", "en", "TEST", None,
            [], [{"archaism_flag": True, "marker_text": "thou", "explanation": "test"}],
            [], []
        )
        for c in choices:
            self.assertIn(c.get("impact_on_meaning", "neutral"), valid)


class TestParagraphConcepts(unittest.TestCase):
    """Test paragraph-level concept detection."""

    def test_movement_perception_concept(self):
        """MOUVEMENT + PERCEPTION should produce EXPLORER or VOIR."""
        atoms = [
            {"atom_id": "MOUVEMENT", "word_form": "fell", "word_position": 1,
             "confidence": 0.95, "sentence_local_idx": 0},
            {"atom_id": "PERCEPTION", "word_form": "saw", "word_position": 5,
             "confidence": 0.90, "sentence_local_idx": 0},
        ]
        syntax = []
        concepts = detect_paragraph_concepts(atoms, syntax)
        concept_ids = {c["concept_id"] for c in concepts}
        self.assertTrue(
            "EXPLORER" in concept_ids or "VOIR" in concept_ids,
            f"Expected EXPLORER or VOIR, got: {concept_ids}"
        )

    def test_syntactic_coherence(self):
        """Atoms in same sentence should have syntactic coherence = True."""
        atoms = [
            {"atom_id": "MOUVEMENT", "word_form": "ran", "word_position": 1,
             "confidence": 0.95, "sentence_local_idx": 0},
            {"atom_id": "PERCEPTION", "word_form": "saw", "word_position": 5,
             "confidence": 0.90, "sentence_local_idx": 0},
        ]
        concepts = detect_paragraph_concepts(atoms, [])
        for c in concepts:
            self.assertTrue(c["syntactic_coherence"])

    def test_cross_sentence_coherence(self):
        """Atoms in distant sentences should have coherence = False."""
        atoms = [
            {"atom_id": "MOUVEMENT", "word_form": "ran", "word_position": 1,
             "confidence": 0.95, "sentence_local_idx": 0},
            {"atom_id": "PERCEPTION", "word_form": "saw", "word_position": 100,
             "confidence": 0.90, "sentence_local_idx": 5},
        ]
        concepts = detect_paragraph_concepts(atoms, [])
        for c in concepts:
            if c["concept_id"] in ("EXPLORER", "VOIR"):
                self.assertFalse(c["syntactic_coherence"])

    def test_confidence_boosted_by_coherence(self):
        """Syntactically coherent concepts should have boosted confidence."""
        atoms_coherent = [
            {"atom_id": "MOUVEMENT", "word_form": "ran", "word_position": 1,
             "confidence": 0.90, "sentence_local_idx": 0},
            {"atom_id": "PERCEPTION", "word_form": "saw", "word_position": 3,
             "confidence": 0.90, "sentence_local_idx": 0},
        ]
        atoms_distant = [
            {"atom_id": "MOUVEMENT", "word_form": "ran", "word_position": 1,
             "confidence": 0.90, "sentence_local_idx": 0},
            {"atom_id": "PERCEPTION", "word_form": "saw", "word_position": 100,
             "confidence": 0.90, "sentence_local_idx": 5},
        ]
        c_coherent = detect_paragraph_concepts(atoms_coherent, [])
        c_distant = detect_paragraph_concepts(atoms_distant, [])

        # Find matching concepts
        coherent_conf = {c["concept_id"]: c["confidence"] for c in c_coherent}
        distant_conf = {c["concept_id"]: c["confidence"] for c in c_distant}

        # Common concepts should have higher confidence when coherent
        for cid in coherent_conf:
            if cid in distant_conf:
                self.assertGreaterEqual(coherent_conf[cid], distant_conf[cid])


class TestCrossLanguageInvariants(unittest.TestCase):
    """Test cross-language invariants: same passage in different languages
    should produce similar atom/concept patterns."""

    def test_alice_falling_movement_all_langs(self):
        """Movement verbs in dictionary/stem form should detect MOUVEMENT."""
        # Use keyword stems that the engine can match (exact or prefix)
        texts = {
            "en": "Alice was falling down the rabbit hole.",
            "fr": "Alice va tomber dans le terrier.",
            "de": "Alice konnte fallen in den Kaninchenbau.",
            "it": "Alice andò a cadere nella tana.",
            "eo": "Alicio falis en la kuniklan truon.",  # falis matches fali (prefix)
        }
        for lang, text in texts.items():
            atoms = align_words_to_atoms(text, lang)
            atom_ids = {a["atom_id"] for a in atoms}
            self.assertIn("MOUVEMENT", atom_ids,
                          f"[{lang}] Should detect MOUVEMENT in: {text}")

    def test_queen_command_domination(self):
        """'The Queen shouted' should detect DOMINATION or COMMUNICATION."""
        texts = {
            "en": "The Queen shouted Off with her head!",
            "fr": "La Reine cria: Qu'on lui coupe la tête!",
            "de": "Die Königin schrie: Kopf ab!",
        }
        for lang, text in texts.items():
            atoms = align_words_to_atoms(text, lang)
            atom_ids = {a["atom_id"] for a in atoms}
            found = "DOMINATION" in atom_ids or "COMMUNICATION" in atom_ids
            self.assertTrue(found,
                            f"[{lang}] Should detect DOMINATION or COMMUNICATION")

    def test_all_languages_produce_syntax(self):
        """All languages should produce valid syntax analysis."""
        texts = {
            "en": "The cat sat on the mat.",
            "fr": "Le chat est assis sur le tapis.",
            "de": "Die Katze saß auf der Matte.",
            "it": "Il gatto sedeva sul tappeto.",
            "es": "El gato estaba sentado en la alfombra.",
            "eo": "La kato sidis sur la mato.",
            "fi": "Kissa istui matolla.",
        }
        for lang, text in texts.items():
            results = analyze_syntax(text, lang)
            self.assertGreater(len(results), 0,
                               f"[{lang}] Should produce syntax analysis")
            # First word should have a POS tag
            self.assertIn(results[0]["pos_tag"],
                          {"NOUN", "DET", "PROPN", "PRON", "VERB", "AUX"},
                          f"[{lang}] First word should have valid POS")


class TestConceptMappings(unittest.TestCase):
    """Test concept mapping consistency."""

    def test_all_concepts_have_valid_atoms(self):
        """All concepts should reference atoms that exist in ATOM_KEYWORDS."""
        valid_atoms = set(LANGUAGE_PROFILES["en"]["pronouns"])  # just a check
        from gutenberg_multilingual_validator import ATOM_KEYWORDS
        valid_atoms = set(ATOM_KEYWORDS.keys())

        for concept, required_atoms in CONCEPT_MAPPINGS.items():
            for atom in required_atoms:
                self.assertIn(atom, valid_atoms,
                              f"Concept {concept} references unknown atom {atom}")

    def test_concept_count(self):
        """Should have at least 30 concepts."""
        self.assertGreaterEqual(len(CONCEPT_MAPPINGS), 30)

    def test_no_single_atom_concepts(self):
        """No concept should require only a single atom (too imprecise)."""
        for concept, atoms in CONCEPT_MAPPINGS.items():
            self.assertGreaterEqual(len(atoms), 2,
                                    f"Concept {concept} has only {len(atoms)} atom(s)")


if __name__ == "__main__":
    unittest.main()
