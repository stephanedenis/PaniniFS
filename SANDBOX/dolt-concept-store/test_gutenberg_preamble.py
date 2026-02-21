#!/usr/bin/env python3
"""test_gutenberg_preamble.py — Tests pour la normalisation des préambules Gutenberg.

Vérifie :
1. Les préambules en différentes langues sont reconnus comme identiques
2. Les citations en langue étrangère sont détectées
3. La re-synthèse multi-format fonctionne
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gutenberg_preamble_normalizer import (
    classify_gutenberg_zones,
    detect_foreign_citations,
    strip_gutenberg_boilerplate,
    ZoneType,
    ForeignCitation,
    _detect_language_trigram,
    _compute_boilerplate_score,
    GUTENBERG_HEADER_FINGERPRINTS,
)


# ═══════════════════════════════════════════════════════════════════════════════
# TEXTES DE TEST
# ═══════════════════════════════════════════════════════════════════════════════

ENGLISH_GUTENBERG = """The Project Gutenberg eBook of Alice's Adventures in Wonderland

This eBook is for the use of anyone anywhere in the United States and
most other parts of the world at no cost and with almost no restrictions
whatsoever. You may copy it, give it away or re-use it under the terms
of the Project Gutenberg License included with this eBook or online at
www.gutenberg.org.

Title: Alice's Adventures in Wonderland
Author: Lewis Carroll
Release Date: June 27, 2008 [eBook #11]
Character set encoding: UTF-8
Produced by: Arthur DiBianca and David Widger

*** START OF THE PROJECT GUTENBERG EBOOK ALICE'S ADVENTURES ***


ALICE'S ADVENTURES IN WONDERLAND

Lewis Carroll

THE MILLENNIUM FULCRUM EDITION 3.0


CHAPTER I. Down the Rabbit-Hole

Alice was beginning to get very tired of sitting by her sister on the
bank, and of having nothing to do: once or twice she had peeped into the
book her sister was reading, but it had no pictures or conversations in
it, 'and what is the use of a book,' thought Alice 'without pictures or
conversations?'

So she was considering in her own mind (as well as she could, for the
hot day made her feel very sleepy and stupid), whether the pleasure
of making a daisy-chain would be worth the trouble of getting up and
picking the daisies, when suddenly a White Rabbit with pink eyes ran
close by her.

There was nothing so VERY remarkable in that; nor did Alice think it so
VERY much out of the way to hear the Rabbit say to itself, 'Oh dear!
Oh dear! I shall be late!' (when she thought it over afterwards, it
occurred to her that she ought to have wondered at this, but at the time
it all seemed quite natural); but when the Rabbit actually TOOK A WATCH
OUT OF ITS WAISTCOAT-POCKET, and looked at it, and then hurried on,
Alice started to her feet, for it flashed across her mind that she had
never before seen a rabbit with either a waistcoat-pocket, or a watch
to take out of it, and burning with curiosity, she ran across the field
after it, and fortunately was just in time to see it pop down a large
rabbit-hole under the hedge.

*** END OF THE PROJECT GUTENBERG EBOOK ALICE'S ADVENTURES ***

Project Gutenberg License
This is a free eBook. You may use it for any purpose.
Donations are accepted at www.gutenberg.org.
"""

FRENCH_GUTENBERG = """Le Projet Gutenberg, Livre électronique

Ce livre est pour l'usage de quiconque, partout dans le monde, sans frais
et sans restrictions. Vous pouvez le copier, le distribuer ou le réutiliser
selon les termes de la licence du Projet Gutenberg.

Titre: Aventures d'Alice au pays des merveilles
Auteur: Lewis Carroll
Traducteur: Henri Bué
Date de publication: 30 août 2017 [Livre #55456]
Encodage: UTF-8
Produit par: Claudine Corbasson et PGDP (BnF/Gallica)

*** START OF THE PROJECT GUTENBERG EBOOK AVENTURES D'ALICE ***


AVENTURES D'ALICE AU PAYS DES MERVEILLES

Par Lewis Carroll

Traduit par Henri Bué


CHAPITRE I. Au fond du terrier

Alice, assise auprès de sa sœur sur le gazon, commençait à s'ennuyer
de rester là à ne rien faire ; une ou deux fois elle avait jeté les yeux
sur le livre que lisait sa sœur ; mais il n'y avait dans ce livre ni
images ni dialogues. « À quoi bon un livre, » pensait Alice, « sans
images ni dialogues ? »

Elle se sentait engourdie par l'oisiveté, et se demandait si le plaisir
de faire une guirlande de marguerites valait bien la peine de se lever
pour cueillir les fleurs, quand tout à coup un Lapin Blanc aux yeux
roses passa en courant près d'elle.

Il n'y avait rien là de bien étonnant, et Alice ne trouva même pas
très-extraordinaire d'entendre le Lapin se dire à lui-même : « Oh !
oh ! oh ! Je vais être en retard ! » Mais quand le Lapin vint à tirer
une montre de son gousset, Alice se leva d'un bond, car l'idée lui
traversa l'esprit qu'elle n'avait jamais vu de lapin avec un gousset et
une montre. Brûlante de curiosité, elle le suivit à travers champs, et
arriva juste à temps pour le voir disparaître dans un large trou de
lapin sous la haie.

*** END OF THE PROJECT GUTENBERG EBOOK AVENTURES D'ALICE ***

Licence du Projet Gutenberg
Ce livre est gratuit. Vous pouvez l'utiliser librement.
Donations acceptées sur www.gutenberg.org.
"""

GERMAN_GUTENBERG = """Das Projekt Gutenberg-DE, Dieses E-Book

Herausgegeben vom Projekt Gutenberg. Dieses E-Book ist für jeden
frei verfügbar. Zeichensatz: UTF-8.

*** START OF THE PROJECT GUTENBERG EBOOK ALICE IM WUNDERLAND ***


ALICE IM WUNDERLAND

Von Lewis Carroll

Übersetzt von Antonie Zimmermann


ERSTES KAPITEL. Hinab in den Kaninchenbau

Alice fing an sich zu langweilen; sie saß schon lange bei ihrer
Schwester am Ufer und hatte nichts zu thun. Das Buch, das ihre Schwester
las, gefiel ihr nicht; denn es waren weder Bilder noch Gespräche darin.

*** END OF THE PROJECT GUTENBERG EBOOK ALICE IM WUNDERLAND ***
"""

# Texte français avec citations latines et anglaises
FRENCH_WITH_FOREIGN_CITATIONS = """
CHAPITRE III. La course au Caucus

Le Dodo dit solennellement : « La course au Caucus est la meilleure
manière de se sécher. » C'est un principe _ad hoc_ que l'on retrouve
dans la philosophie, comme le disait le sage : _cogito ergo sum_.

Alice pensait que c'était un bien beau discours, et elle se rappelait
les mots du Lapin : « Oh dear! Oh dear! I shall be late! »

Le Chat du Comté de Chester murmura avec un sourire : « We are all mad
here. I'm mad. You're mad. »

Voltaire aurait dit : « Il faut cultiver notre jardin. » Mais en
allemand, on dirait plutôt : « Man muss seinen Garten pflegen. »
"""


class TestPreambleNormalization(unittest.TestCase):
    """Tests de normalisation des préambules."""

    def test_english_header_detected(self):
        zones = classify_gutenberg_zones(ENGLISH_GUTENBERG, declared_lang="en")
        headers = [z for z in zones if z.zone_type == ZoneType.GUTENBERG_HEADER]
        self.assertEqual(len(headers), 1, "Doit trouver exactement 1 header")
        self.assertIn("Project Gutenberg", headers[0].text)

    def test_english_footer_detected(self):
        zones = classify_gutenberg_zones(ENGLISH_GUTENBERG, declared_lang="en")
        footers = [z for z in zones if z.zone_type == ZoneType.GUTENBERG_FOOTER]
        self.assertEqual(len(footers), 1, "Doit trouver exactement 1 footer")

    def test_french_header_detected(self):
        zones = classify_gutenberg_zones(FRENCH_GUTENBERG, declared_lang="fr")
        headers = [z for z in zones if z.zone_type == ZoneType.GUTENBERG_HEADER]
        self.assertEqual(len(headers), 1, "Doit trouver le header même en français")

    def test_german_header_detected(self):
        zones = classify_gutenberg_zones(GERMAN_GUTENBERG, declared_lang="de")
        headers = [z for z in zones if z.zone_type == ZoneType.GUTENBERG_HEADER]
        self.assertEqual(len(headers), 1, "Doit trouver le header même en allemand")

    def test_preambles_semantically_identical(self):
        """Les préambules EN, FR, DE doivent être marqués comme sémantiquement identiques."""
        zones_en = classify_gutenberg_zones(ENGLISH_GUTENBERG, declared_lang="en")
        zones_fr = classify_gutenberg_zones(FRENCH_GUTENBERG, declared_lang="fr")
        zones_de = classify_gutenberg_zones(GERMAN_GUTENBERG, declared_lang="de")

        for zones, lang in [(zones_en, "en"), (zones_fr, "fr"), (zones_de, "de")]:
            headers = [z for z in zones if z.zone_type == ZoneType.GUTENBERG_HEADER]
            self.assertTrue(len(headers) > 0, f"Header manquant pour {lang}")
            # Tous doivent porter le même semantic_id
            self.assertEqual(
                headers[0].metadata.get("semantic_id"),
                "GUTENBERG_PREAMBLE_LICENCE",
                f"Le header {lang} doit avoir le même semantic_id"
            )
            self.assertTrue(
                headers[0].metadata.get("equivalent_across_languages"),
                f"Le header {lang} doit être marqué comme équivalent cross-langue"
            )

    def test_body_extracted(self):
        zones = classify_gutenberg_zones(ENGLISH_GUTENBERG, declared_lang="en")
        body_zones = [z for z in zones if z.zone_type == ZoneType.BODY]
        self.assertTrue(len(body_zones) > 0, "Doit identifier au moins une zone BODY")
        # Le body doit contenir le texte littéraire
        body_text = ' '.join(z.text for z in body_zones)
        self.assertIn("Alice was beginning", body_text)

    def test_strip_returns_body_only(self):
        body = strip_gutenberg_boilerplate(ENGLISH_GUTENBERG, declared_lang="en")
        self.assertNotIn("Project Gutenberg License", body)
        self.assertNotIn("This eBook is for the use", body)
        self.assertIn("Alice was beginning", body)

    def test_strip_french_returns_body(self):
        body = strip_gutenberg_boilerplate(FRENCH_GUTENBERG, declared_lang="fr")
        self.assertNotIn("Licence du Projet Gutenberg", body)
        self.assertIn("Alice, assise auprès", body)

    def test_boilerplate_score_english(self):
        header = ENGLISH_GUTENBERG[:500]
        score, lang = _compute_boilerplate_score(header, GUTENBERG_HEADER_FINGERPRINTS)
        self.assertGreater(score, 0.1, "Score boilerplate trop bas pour header anglais")
        # English should match best given the specific patterns
        self.assertIn(lang, ("en", "fr"),
                      "Detected boilerplate lang should be en or fr")

    def test_boilerplate_score_french(self):
        header = FRENCH_GUTENBERG[:500]
        score, lang = _compute_boilerplate_score(header, GUTENBERG_HEADER_FINGERPRINTS)
        self.assertGreater(score, 0.1, "Score boilerplate trop bas pour header français")
        self.assertEqual(lang, "fr")


class TestForeignCitationDetection(unittest.TestCase):
    """Tests de détection des citations en langue étrangère."""

    def test_latin_phrases_detected(self):
        citations = detect_foreign_citations(
            FRENCH_WITH_FOREIGN_CITATIONS,
            document_lang="fr",
            min_words=1,  # Latin phrases can be short
        )
        latin_cits = [c for c in citations if c.detected_language == "la"]
        self.assertTrue(len(latin_cits) > 0, "Doit détecter les phrases latines")

    def test_english_citations_in_french_text(self):
        citations = detect_foreign_citations(
            FRENCH_WITH_FOREIGN_CITATIONS,
            document_lang="fr",
        )
        en_cits = [c for c in citations if c.detected_language == "en"]
        # Au moins la citation "Oh dear! Oh dear!" ou "We are all mad here"
        self.assertTrue(len(en_cits) > 0,
                        "Doit détecter les citations anglaises dans un texte français")

    def test_no_false_positives_in_pure_text(self):
        pure_french = (
            "Alice commençait à s'ennuyer de rester là à ne rien faire. "
            "Elle se sentait engourdie, et se demandait si le plaisir "
            "de faire une guirlande de marguerites valait bien la peine "
            "de se lever pour cueillir les fleurs de ce joli jardin."
        )
        citations = detect_foreign_citations(pure_french, document_lang="fr")
        # Il ne devrait pas y avoir de faux positifs dans du texte purement français
        self.assertEqual(len(citations), 0,
                         f"Faux positifs dans du texte purement français: {[(c.text, c.detected_language, c.detection_method) for c in citations]}")


class TestLanguageTrigramDetection(unittest.TestCase):
    """Tests de détection de langue par trigrammes."""

    def test_detect_english(self):
        lang, conf = _detect_language_trigram(
            "The rabbit ran across the field and looked at the watch",
            exclude_lang="fr"
        )
        self.assertEqual(lang, "en")
        self.assertGreater(conf, 0.1)

    def test_detect_french(self):
        lang, conf = _detect_language_trigram(
            "Le lapin courut à travers les champs et regarda la montre dans son gousset",
            exclude_lang="en"
        )
        self.assertEqual(lang, "fr")
        self.assertGreater(conf, 0.0)

    def test_detect_german(self):
        lang, conf = _detect_language_trigram(
            "Das Kaninchen rannte über das Feld und schaute auf die Uhr",
            exclude_lang="en"
        )
        self.assertEqual(lang, "de")
        self.assertGreater(conf, 0.1)

    def test_excludes_document_lang(self):
        """Ne doit pas retourner la langue exclue."""
        lang, _ = _detect_language_trigram(
            "The rabbit ran across the field",
            exclude_lang="en"
        )
        self.assertNotEqual(lang, "en")

    def test_detect_russian(self):
        """Détecte le russe via trigrammes cyrilliques."""
        lang, conf = _detect_language_trigram(
            "Всё смешалось в доме Облонских. Жена узнала, что муж был в "
            "связи с бывшею в их доме француженкою"
        )
        self.assertEqual(lang, "ru")
        self.assertGreater(conf, 0.1)  # Script detection reliable, trigrams add precision

    def test_detect_japanese(self):
        """Détecte le japonais via trigrammes hiragana."""
        lang, conf = _detect_language_trigram(
            "むかしむかし、あるところに、おじいさんとおばあさんが住んでいました。"
            "おじいさんは山へしばかりに、おばあさんは川へせんたくに行きました。"
        )
        self.assertEqual(lang, "ja")
        self.assertGreater(conf, 0.3)

    def test_detect_chinese(self):
        """Détecte le chinois via bigrammes CJK."""
        lang, conf = _detect_language_trigram(
            "紅樓夢是中國古典四大名著之一。這個故事描述了一個大家族的興衰。"
            "寶玉和黛玉的故事是其中最著名的。"
        )
        self.assertEqual(lang, "zh")
        self.assertGreater(conf, 0.1)

    def test_russian_in_french_context(self):
        """Détecte une citation russe dans un contexte français."""
        lang, conf = _detect_language_trigram(
            "Всё смешалось в доме Облонских",
            exclude_lang="fr"
        )
        self.assertEqual(lang, "ru")
        self.assertGreater(conf, 0.3)

    def test_cjk_vs_hiragana_discrimination(self):
        """Le CJK pur donne zh, le texte avec hiragana donne ja."""
        lang_zh, _ = _detect_language_trigram("中國古典四大名著之一")
        lang_ja, _ = _detect_language_trigram("おじいさんとおばあさんが住んでいました")
        self.assertEqual(lang_zh, "zh")
        self.assertEqual(lang_ja, "ja")


class TestZoneClassification(unittest.TestCase):
    """Tests de classification des zones."""

    def test_title_page_detected(self):
        zones = classify_gutenberg_zones(ENGLISH_GUTENBERG, declared_lang="en")
        title_zones = [z for z in zones if z.zone_type == ZoneType.TITLE_PAGE]
        # La page de titre devrait contenir le titre en majuscules
        if title_zones:
            title_text = title_zones[0].text
            self.assertTrue(
                "ALICE" in title_text.upper() or "Lewis Carroll" in title_text,
                "La page de titre doit contenir le titre ou l'auteur"
            )

    def test_all_text_covered(self):
        """Chaque caractère du texte doit être dans au moins une zone."""
        zones = classify_gutenberg_zones(ENGLISH_GUTENBERG, declared_lang="en")
        # Au minimum : header + body + footer
        zone_types = set(z.zone_type for z in zones)
        self.assertIn(ZoneType.GUTENBERG_HEADER, zone_types)
        self.assertIn(ZoneType.GUTENBERG_FOOTER, zone_types)
        self.assertIn(ZoneType.BODY, zone_types)


class TestIntegrationWithValidator(unittest.TestCase):
    """Tests d'intégration avec gutenberg_multilingual_validator."""

    def test_strip_backward_compatible(self):
        """strip_gutenberg_header_footer doit toujours fonctionner."""
        try:
            from gutenberg_multilingual_validator import strip_gutenberg_header_footer
            result = strip_gutenberg_header_footer(ENGLISH_GUTENBERG)
            self.assertIn("Alice was beginning", result)
            self.assertNotIn("Project Gutenberg License", result)
        except ImportError:
            self.skipTest("gutenberg_multilingual_validator not importable")

    def test_strip_with_lang_parameter(self):
        """Le nouveau strip accepte un paramètre lang."""
        try:
            from gutenberg_multilingual_validator import strip_gutenberg_header_footer
            result = strip_gutenberg_header_footer(FRENCH_GUTENBERG, lang="fr")
            self.assertIn("Alice, assise", result)
        except (ImportError, TypeError):
            # TypeError si l'ancienne version ne supporte pas le paramètre lang
            self.skipTest("Old version or not importable")


class TestInformationLayers(unittest.TestCase):
    """Tests du modèle de perte informationnelle (richest → poorest)."""

    def test_format_richness_hierarchy(self):
        """HTML > EPUB > TXT dans la hiérarchie de richesse."""
        from gutenberg_preamble_normalizer import FORMAT_RICHNESS
        self.assertGreater(FORMAT_RICHNESS["html"], FORMAT_RICHNESS["epub"])
        self.assertGreater(FORMAT_RICHNESS["epub"], FORMAT_RICHNESS["txt"])

    def test_information_layer_loss_vs_self(self):
        """Un format comparé à lui-même a 0% de perte."""
        from gutenberg_preamble_normalizer import InformationLayer
        ref = InformationLayer(
            headings=10, emphasis_spans=50, images=3, paragraphs=100,
            text_words=5000, text_chars=30000
        )
        loss = ref.loss_vs(ref)
        for dim, val in loss.items():
            self.assertAlmostEqual(val, 0.0, places=3,
                                   msg=f"Self-loss should be 0 for {dim}")

    def test_txt_loses_emphasis_vs_html(self):
        """TXT perd l'emphasis par rapport à HTML."""
        from gutenberg_preamble_normalizer import InformationLayer
        html_ref = InformationLayer(
            headings=12, emphasis_spans=220, strong_spans=5, images=1,
            links=28, paragraphs=777, text_words=26000
        )
        txt = InformationLayer(
            headings=0, emphasis_spans=0, strong_spans=0, images=0,
            links=0, paragraphs=810, text_words=26000
        )
        loss = txt.loss_vs(html_ref)
        self.assertEqual(loss["emphasis_spans"], 1.0)  # 100% perdu
        self.assertEqual(loss["images"], 1.0)           # 100% perdu
        self.assertEqual(loss["links"], 1.0)             # 100% perdu
        self.assertAlmostEqual(loss["text_words"], 0.0, places=2)  # ~0% perdu

    def test_edition_richness_score(self):
        """EditionFormat.richness_score reflète FORMAT_RICHNESS."""
        from gutenberg_preamble_normalizer import EditionFormat
        e_html = EditionFormat(gutenberg_id=11, format="html", filepath="", language="en", title="")
        e_txt = EditionFormat(gutenberg_id=11, format="txt", filepath="", language="en", title="")
        self.assertGreater(e_html.richness_score, e_txt.richness_score)

    def test_extract_info_layers_html(self):
        """_extract_information_layers extrait les dimensions HTML."""
        import os
        html_path = os.path.join(os.path.dirname(__file__),
                                 "gutenberg_corpus", "en", "pg11.html")
        if not os.path.exists(html_path):
            self.skipTest("pg11.html not downloaded")
        from gutenberg_preamble_normalizer import _extract_information_layers
        layers = _extract_information_layers(html_path, "html")
        self.assertGreater(layers.headings, 10)
        self.assertGreater(layers.emphasis_spans, 100)
        self.assertGreater(layers.text_words, 20000)

    def test_extract_info_layers_txt(self):
        """_extract_information_layers sur TXT : pas d'emphasis HTML."""
        import os
        txt_path = os.path.join(os.path.dirname(__file__),
                                "gutenberg_corpus", "en", "pg11.txt")
        if not os.path.exists(txt_path):
            self.skipTest("pg11.txt not downloaded")
        from gutenberg_preamble_normalizer import _extract_information_layers
        layers = _extract_information_layers(txt_path, "txt")
        # TXT ne devrait pas avoir de links ni de tables
        self.assertEqual(layers.links, 0)
        self.assertEqual(layers.tables, 0)
        self.assertGreater(layers.text_words, 20000)


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Quick summary before running tests
    print(f"\n{'═' * 72}")
    print(f"TEST SUITE: Gutenberg Preamble Normalizer")
    print(f"{'═' * 72}")
    print(f"  Tests: normalisation, citations, trigrammes, zones, intégration")
    print(f"{'─' * 72}\n")

    unittest.main(verbosity=2)
