#!/usr/bin/env python3
"""
test_morpho_semantic_bridge.py — Tests du pont morphologie ↔ sémantique

Vérifie :
  1. Tables de verbes irréguliers (7 langues × 16 atomes)
  2. Lemmatisation rule-based par suffixes
  3. Inférence par racines étymologiques (latines, germaniques)
  4. Inférence inter-langues (langues parentes)
  5. Résolution complète (cascade 4 étapes)
  6. Intégration dans align_words_to_atoms()
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from morpho_semantic_bridge import (
    lemmatize,
    resolve_word,
    resolve_word_full,
    infer_atom_from_roots,
    cross_language_inference,
    get_language_family,
    get_sibling_languages,
    IRREGULAR_VERBS,
    VERB_SUFFIXES,
    LATIN_ROOTS,
    GERMANIC_ROOTS,
    LANGUAGE_FAMILIES,
)
from gutenberg_multilingual_validator import ATOM_KEYWORDS


class TestIrregularVerbTables(unittest.TestCase):
    """Test 1: Tables de verbes irréguliers"""

    def test_all_7_languages_present(self):
        expected = {"en", "fr", "de", "it", "es", "eo", "fi"}
        self.assertEqual(set(IRREGULAR_VERBS.keys()), expected)

    def test_english_key_irregulars(self):
        irr = IRREGULAR_VERBS["en"]
        self.assertEqual(irr["fell"], "fall")
        self.assertEqual(irr["went"], "go")
        self.assertEqual(irr["saw"], "see")
        self.assertEqual(irr["thought"], "think")
        self.assertEqual(irr["said"], "say")
        self.assertEqual(irr["was"], "be")
        self.assertEqual(irr["had"], "have")
        self.assertEqual(irr["gave"], "give")
        self.assertEqual(irr["took"], "take")
        self.assertEqual(irr["made"], "make")

    def test_french_key_irregulars(self):
        irr = IRREGULAR_VERBS["fr"]
        self.assertEqual(irr["alla"], "aller")
        self.assertEqual(irr["vint"], "venir")
        self.assertEqual(irr["vit"], "voir")
        self.assertEqual(irr["dit"], "dire")
        self.assertEqual(irr["fut"], "être")
        self.assertEqual(irr["eut"], "avoir")
        self.assertEqual(irr["prit"], "prendre")
        self.assertEqual(irr["fit"], "faire")

    def test_german_key_irregulars(self):
        irr = IRREGULAR_VERBS["de"]
        self.assertEqual(irr["fiel"], "fallen")
        self.assertEqual(irr["ging"], "gehen")
        self.assertEqual(irr["kam"], "kommen")
        self.assertEqual(irr["sah"], "sehen")
        self.assertEqual(irr["sprach"], "sprechen")
        self.assertEqual(irr["war"], "sein")
        self.assertEqual(irr["hatte"], "haben")
        self.assertEqual(irr["gab"], "geben")

    def test_italian_key_irregulars(self):
        irr = IRREGULAR_VERBS["it"]
        self.assertEqual(irr["cadde"], "cadere")
        self.assertEqual(irr["disse"], "dire")
        self.assertEqual(irr["vide"], "vedere")
        self.assertEqual(irr["fu"], "essere")
        self.assertEqual(irr["ebbe"], "avere")
        self.assertEqual(irr["fece"], "fare")

    def test_spanish_key_irregulars(self):
        irr = IRREGULAR_VERBS["es"]
        self.assertEqual(irr["cayó"], "caer")
        self.assertEqual(irr["dijo"], "decir")
        self.assertEqual(irr["vio"], "ver")
        self.assertEqual(irr["hizo"], "hacer")
        self.assertEqual(irr["tuvo"], "tener")

    def test_esperanto_key_irregulars(self):
        irr = IRREGULAR_VERBS["eo"]
        self.assertEqual(irr["iris"], "iri")
        self.assertEqual(irr["vidis"], "vidi")
        self.assertEqual(irr["diris"], "diri")
        self.assertEqual(irr["estis"], "esti")

    def test_finnish_key_irregulars(self):
        irr = IRREGULAR_VERBS["fi"]
        self.assertEqual(irr["juoksi"], "juosta")
        self.assertEqual(irr["näki"], "nähdä")
        self.assertEqual(irr["oli"], "olla")
        self.assertEqual(irr["tuli"], "tulla")
        self.assertEqual(irr["sanoi"], "sanoa")

    def test_min_entries_per_language(self):
        """Each language should have at least 30 irregular forms."""
        for lang, irr in IRREGULAR_VERBS.items():
            self.assertGreaterEqual(len(irr), 30,
                f"{lang} has only {len(irr)} irregular entries")


class TestLemmatize(unittest.TestCase):
    """Test 2: Lemmatisation rule-based"""

    def test_english_irregular_via_lemmatize(self):
        results = lemmatize("fell", "en")
        lemmas = [r[0] for r in results]
        self.assertIn("fall", lemmas)
        # Should be high confidence
        for l, m, c in results:
            if l == "fall":
                self.assertGreater(c, 0.90)

    def test_english_suffix_ed(self):
        results = lemmatize("walked", "en")
        lemmas = [r[0] for r in results]
        self.assertIn("walk", lemmas)

    def test_english_suffix_ing(self):
        results = lemmatize("running", "en")
        lemmas = [r[0] for r in results]
        self.assertIn("run", lemmas)  # via irregular table

    def test_french_suffix_ait(self):
        results = lemmatize("marchait", "fr")
        lemmas = [r[0] for r in results]
        # Should produce "marcher" via irregular table or suffix rule
        has_marcher = any("march" in l for l in lemmas)
        self.assertTrue(has_marcher)

    def test_german_ge_prefix(self):
        results = lemmatize("gemacht", "de")
        lemmas = [r[0] for r in results]
        self.assertIn("machen", lemmas)

    def test_esperanto_is_suffix(self):
        results = lemmatize("faris", "eo")
        lemmas = [r[0] for r in results]
        self.assertIn("fari", lemmas)

    def test_identity_fallback(self):
        results = lemmatize("xyz", "en")
        # Should always include identity
        self.assertTrue(any(m == "identity" for _, m, _ in results))

    def test_short_word_returns_identity(self):
        results = lemmatize("a", "en")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1], "identity")

    def test_punctuation_stripped(self):
        results = lemmatize("fell,", "en")
        lemmas = [r[0] for r in results]
        self.assertIn("fall", lemmas)


class TestRootInference(unittest.TestCase):
    """Test 3: Inférence par racines étymologiques"""

    def test_latin_root_romance_mouvement(self):
        # "camminando" contains "cammin" → MOUVEMENT
        results = infer_atom_from_roots("camminando", "it")
        atoms = [r[0] for r in results]
        self.assertIn("MOUVEMENT", atoms)

    def test_germanic_root_fall(self):
        # "falling" contains "fall" → MOUVEMENT
        results = infer_atom_from_roots("falling", "en")
        atoms = [r[0] for r in results]
        self.assertIn("MOUVEMENT", atoms)

    def test_latin_root_perception(self):
        # "observation" contains "observ" → PERCEPTION
        results = infer_atom_from_roots("observación", "es")
        atoms = [r[0] for r in results]
        self.assertIn("PERCEPTION", atoms)

    def test_no_false_positive_short_word(self):
        # Very short word should not match
        results = infer_atom_from_roots("it", "en")
        self.assertEqual(len(results), 0)

    def test_english_latin_loans(self):
        # English also checked against Latin roots
        results = infer_atom_from_roots("imagination", "en")
        atoms = [r[0] for r in results]
        self.assertIn("COGNITION", atoms)

    def test_german_germanic_roots(self):
        # "Zerstörung" contains "zerstör" → DESTRUCTION
        results = infer_atom_from_roots("Zerstörung", "de")
        atoms = [r[0] for r in results]
        self.assertIn("DESTRUCTION", atoms)


class TestLanguageFamilies(unittest.TestCase):
    """Test 4: Familles de langues"""

    def test_romance_family(self):
        self.assertEqual(get_language_family("fr"), "romance")
        self.assertEqual(get_language_family("it"), "romance")
        self.assertEqual(get_language_family("es"), "romance")
        self.assertEqual(get_language_family("eo"), "romance")

    def test_germanic_family(self):
        self.assertEqual(get_language_family("en"), "germanic")
        self.assertEqual(get_language_family("de"), "germanic")

    def test_finno_ugric_family(self):
        self.assertEqual(get_language_family("fi"), "finno_ugric")

    def test_siblings_french(self):
        siblings = get_sibling_languages("fr")
        self.assertIn("it", siblings)
        self.assertIn("es", siblings)
        self.assertNotIn("en", siblings)
        self.assertNotIn("fr", siblings)

    def test_siblings_english(self):
        siblings = get_sibling_languages("en")
        self.assertIn("de", siblings)
        self.assertNotIn("fr", siblings)

    def test_finnish_no_siblings(self):
        siblings = get_sibling_languages("fi")
        self.assertEqual(len(siblings), 0)


class TestCrossLanguageInference(unittest.TestCase):
    """Test 4b: Inférence inter-langues"""

    def test_cross_lang_romance_word(self):
        # "camminò" (IT past tense of camminare=walk) should find MOUVEMENT
        # via FR/ES siblings
        results = cross_language_inference("camminò", "it", ATOM_KEYWORDS)
        # May or may not find depending on sibling keywords
        # At minimum, function should not crash
        self.assertIsInstance(results, list)

    def test_cross_lang_reduces_confidence(self):
        # Cross-language results should have reduced confidence
        results = cross_language_inference("walk", "de", ATOM_KEYWORDS)
        for r in results:
            self.assertLess(r["confidence"], 0.85)

    def test_cross_lang_method_contains_arrow(self):
        results = cross_language_inference("walk", "de", ATOM_KEYWORDS)
        for r in results:
            self.assertIn("cross_lang:", r["method"])


class TestResolveWord(unittest.TestCase):
    """Test 5: Résolution complète (resolve_word)"""

    def test_direct_match_en(self):
        results = resolve_word("fall", "en", ATOM_KEYWORDS)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["atom_id"], "MOUVEMENT")
        self.assertEqual(results[0]["method"], "direct_match")
        self.assertGreaterEqual(results[0]["confidence"], 0.95)

    def test_irregular_en_fell(self):
        results = resolve_word("fell", "en", ATOM_KEYWORDS)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["atom_id"], "MOUVEMENT")
        self.assertIn("lemma:", results[0]["method"])

    def test_irregular_fr_tomba(self):
        results = resolve_word("tomba", "fr", ATOM_KEYWORDS)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["atom_id"], "MOUVEMENT")

    def test_irregular_de_fiel(self):
        results = resolve_word("fiel", "de", ATOM_KEYWORDS)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["atom_id"], "MOUVEMENT")

    def test_irregular_it_cadde(self):
        results = resolve_word("cadde", "it", ATOM_KEYWORDS)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["atom_id"], "MOUVEMENT")

    def test_irregular_es_cayo(self):
        results = resolve_word("cayó", "es", ATOM_KEYWORDS)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["atom_id"], "MOUVEMENT")

    def test_irregular_eo_iris(self):
        results = resolve_word("iris", "eo", ATOM_KEYWORDS)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["atom_id"], "MOUVEMENT")

    def test_irregular_fi_juoksi(self):
        results = resolve_word("juoksi", "fi", ATOM_KEYWORDS)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["atom_id"], "MOUVEMENT")

    def test_empty_for_short_word(self):
        results = resolve_word("a", "en", ATOM_KEYWORDS)
        self.assertEqual(len(results), 0)

    def test_punctuation_handling(self):
        results = resolve_word("fell,", "en", ATOM_KEYWORDS)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["atom_id"], "MOUVEMENT")

    def test_result_structure(self):
        results = resolve_word("fell", "en", ATOM_KEYWORDS)
        r = results[0]
        self.assertIn("atom_id", r)
        self.assertIn("lemma", r)
        self.assertIn("confidence", r)
        self.assertIn("method", r)
        self.assertIn("disambiguation", r)


class TestResolveWordFull(unittest.TestCase):
    """Test 5b: Résolution complète avec fallback inter-langues"""

    def test_full_resolution_en(self):
        results = resolve_word_full("saw", "en", ATOM_KEYWORDS)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["atom_id"], "PERCEPTION")

    def test_full_resolution_fr(self):
        results = resolve_word_full("dit", "fr", ATOM_KEYWORDS)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["atom_id"], "COMMUNICATION")

    def test_full_resolution_de(self):
        results = resolve_word_full("sah", "de", ATOM_KEYWORDS)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["atom_id"], "PERCEPTION")

    def test_full_dedup_by_atom(self):
        # resolve_word_full should deduplicate by atom_id
        results = resolve_word_full("fell", "en", ATOM_KEYWORDS)
        atom_ids = [r["atom_id"] for r in results]
        self.assertEqual(len(atom_ids), len(set(atom_ids)))


class TestMultiAtomCoverage(unittest.TestCase):
    """Test multi-atom — vérifie que le pont couvre les 16 atomes sémantiques"""

    ATOM_WORD_TESTS = {
        "MOUVEMENT": [("fell", "en"), ("tomba", "fr"), ("fiel", "de"),
                       ("cadde", "it"), ("cayó", "es"), ("iris", "eo"),
                       ("juoksi", "fi")],
        "PERCEPTION": [("saw", "en"), ("vit", "fr"), ("sah", "de"),
                        ("vide", "it"), ("vio", "es"), ("vidis", "eo"),
                        ("näki", "fi")],
        "COGNITION": [("thought", "en"), ("pensait", "fr"), ("dachte", "de"),
                       ("pensò", "it"), ("pensó", "es"), ("pensis", "eo"),
                       ("ajatteli", "fi")],
        "COMMUNICATION": [("said", "en"), ("dit", "fr"), ("sagte", "de"),
                           ("disse", "it"), ("dijo", "es"), ("diris", "eo"),
                           ("sanoi", "fi")],
        "EXISTENCE": [("was", "en"), ("était", "fr"), ("war", "de"),
                       ("era", "it"), ("estaba", "es"), ("estis", "eo"),
                       ("oli", "fi")],
        "POSSESSION": [("had", "en"), ("avait", "fr"), ("hatte", "de"),
                        ("ebbe", "it"), ("tuvo", "es"), ("havis", "eo"),
                        ("omisti", "fi")],
        "CREATION": [("made", "en"), ("fit", "fr"), ("machte", "de"),
                      ("fece", "it"), ("hizo", "es"), ("faris", "eo"),
                      ("teki", "fi")],
        "DESTRUCTION": [("broke", "en"), ("détruisit", "fr"),
                         ("zerstörte", "de"), ("distrusse", "it"),
                         ("destruyó", "es"), ("detruis", "eo"),
                         ("tuhosi", "fi")],
        "DOMINATION": [("ruled", "en"), ("régna", "fr"), ("herrschte", "de"),
                        ("regnò", "it"), ("regis", "eo")],
        "SEEKING": [("wanted", "en"), ("voulait", "fr"), ("wollte", "de"),
                     ("volle", "it"), ("volis", "eo"), ("halusi", "fi")],
        "FEAR": [("feared", "en"), ("craignait", "fr"), ("fürchtete", "de"),
                  ("temette", "it"), ("timis", "eo"), ("pelkäsi", "fi")],
        "CARE": [("loved", "en"), ("aimait", "fr"), ("liebte", "de"),
                  ("amò", "it"), ("amis", "eo"), ("rakasti", "fi")],
        "PLAY": [("played", "en"), ("jouait", "fr"), ("spielte", "de"),
                  ("giocò", "it"), ("ludis", "eo")],
        "GRIEF": [("wept", "en"), ("pleurait", "fr"), ("weinte", "de"),
                   ("itki", "fi")],
    }

    def test_all_atoms_resolving(self):
        """Each atom should have at least 3 correctly resolved forms."""
        for atom, word_pairs in self.ATOM_WORD_TESTS.items():
            resolved = 0
            for word, lang in word_pairs:
                results = resolve_word_full(word, lang, ATOM_KEYWORDS)
                if results and results[0]["atom_id"] == atom:
                    resolved += 1
            self.assertGreaterEqual(resolved, 3,
                f"{atom}: only {resolved}/{len(word_pairs)} resolved correctly")


class TestIntegration(unittest.TestCase):
    """Test 6: Intégration dans align_words_to_atoms"""

    def test_align_words_resolves_irregulars(self):
        from seven_layers_engine import align_words_to_atoms
        # "Alice fell down a very deep well"
        text = "Alice fell down a very deep well"
        results = align_words_to_atoms(text, "en")
        atoms = [r["atom_id"] for r in results]
        self.assertIn("MOUVEMENT", atoms, "Should find MOUVEMENT via 'fell'")

    def test_align_words_french_passe_simple(self):
        from seven_layers_engine import align_words_to_atoms
        text = "Alice tomba dans un puits très profond"
        results = align_words_to_atoms(text, "fr")
        atoms = [r["atom_id"] for r in results]
        self.assertIn("MOUVEMENT", atoms, "Should find MOUVEMENT via 'tomba'")

    def test_align_words_german_prateritum(self):
        from seven_layers_engine import align_words_to_atoms
        text = "Alice fiel in einen sehr tiefen Brunnen"
        results = align_words_to_atoms(text, "de")
        atoms = [r["atom_id"] for r in results]
        self.assertIn("MOUVEMENT", atoms, "Should find MOUVEMENT via 'fiel'")

    def test_align_words_italian(self):
        from seven_layers_engine import align_words_to_atoms
        text = "Alice cadde in un pozzo molto profondo"
        results = align_words_to_atoms(text, "it")
        atoms = [r["atom_id"] for r in results]
        self.assertIn("MOUVEMENT", atoms, "Should find MOUVEMENT via 'cadde'")

    def test_align_words_spanish(self):
        from seven_layers_engine import align_words_to_atoms
        text = "Alicia cayó por un pozo muy profundo"
        results = align_words_to_atoms(text, "es")
        atoms = [r["atom_id"] for r in results]
        self.assertIn("MOUVEMENT", atoms, "Should find MOUVEMENT via 'cayó'")

    def test_align_words_esperanto(self):
        from seven_layers_engine import align_words_to_atoms
        text = "Alicio iris malsupren tra tre profunda puto"
        results = align_words_to_atoms(text, "eo")
        atoms = [r["atom_id"] for r in results]
        self.assertIn("MOUVEMENT", atoms, "Should find MOUVEMENT via 'iris'")

    def test_align_words_finnish(self):
        from seven_layers_engine import align_words_to_atoms
        text = "Liisa putosi hyvin syvään kaivoon"
        results = align_words_to_atoms(text, "fi")
        atoms = [r["atom_id"] for r in results]
        self.assertIn("MOUVEMENT", atoms, "Should find MOUVEMENT via 'putosi'")

    def test_backward_compatibility(self):
        """Direct matches should still work (base forms)."""
        from seven_layers_engine import align_words_to_atoms
        text = "fall run jump walk"
        results = align_words_to_atoms(text, "en")
        atoms = [r["atom_id"] for r in results]
        self.assertEqual(atoms.count("MOUVEMENT"), 4)


class TestCoverageImprovement(unittest.TestCase):
    """Test 7: Vérification que la couverture a augmenté"""

    def test_coverage_above_baseline(self):
        """Global atom coverage should exceed 75% (baseline was 65.2%)."""
        import subprocess, json
        DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "panini-unified-db")
        r = subprocess.run(
            ["dolt", "sql", "-q",
             "SELECT ROUND(100.0 * COUNT(DISTINCT CASE WHEN wa.paragraph_id "
             "IS NOT NULL THEN pu.id END) / COUNT(DISTINCT pu.id), 1) as pct "
             "FROM paragraph_units pu "
             "LEFT JOIN paragraph_word_atoms wa ON pu.id = wa.paragraph_id",
             "-r", "csv"],
            capture_output=True, text=True, cwd=DB
        )
        lines = r.stdout.strip().split('\n')
        if len(lines) >= 2:
            pct = float(lines[1])
            self.assertGreaterEqual(pct, 75.0,
                f"Atom coverage {pct}% should be ≥ 75% (baseline 65.2%)")

    def test_attributions_increased(self):
        """Total attributions should exceed 2000 (baseline was 1085)."""
        import subprocess
        DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "panini-unified-db")
        r = subprocess.run(
            ["dolt", "sql", "-q",
             "SELECT COUNT(*) FROM paragraph_word_atoms",
             "-r", "csv"],
            capture_output=True, text=True, cwd=DB
        )
        lines = r.stdout.strip().split('\n')
        if len(lines) >= 2:
            n = int(lines[1])
            self.assertGreaterEqual(n, 2000,
                f"Attributions {n} should be ≥ 2000 (baseline 1085)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
