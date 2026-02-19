#!/usr/bin/env python3
"""
seven_layers_engine.py — Moteur d'analyse multilingue à 7 couches

Objectif : Pour chaque paragraphe de chaque édition, analyser les 7 couches
linguistiques et expliquer les choix d'interprétation du traducteur.

Couches :
  1. Syntaxe          — ordre des mots, clauses, rôles sémantiques
  2. Alignement       — mot→atome ciblé (réutilise ATOM_KEYWORDS)
  3. Morphologie      — temps, aspect, genre, cas, nombre
  4. Registre/style   — formalité, archaïsme, richesse lexicale
  5. Discours         — anaphore, connecteurs, cohérence
  6. Prosodie         — rythme, cadence, parallélisme, figures
  7. Référents        — adaptations culturelles, domestication/étrangéisation

Entrée :  corpus Gutenberg (2 œuvres, 10 éditions, 6+4 langues, 46 segments)
Sortie :  tables Dolt remplies + choix traducteur documentés

Granularité : PARAGRAPHE (pas phrase) car les langues ont des préférences

Dépendance : morpho_semantic_bridge.py (pont morphologie ↔ sémantique)
de longueur de phrases différentes.

Usage :
  cd SANDBOX/dolt-concept-store
  python3 seven_layers_engine.py
"""

import json
import math
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

DOLT_DB = os.path.join(os.path.dirname(__file__), "panini-unified-db")
CORPUS_DIR = os.path.join(os.path.dirname(__file__), "gutenberg_corpus")
SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "schema_v3_seven_layers.sql")
TODAY = date.today().isoformat()

# Import from existing modules
sys.path.insert(0, os.path.dirname(__file__))
from gutenberg_multilingual_validator import (
    ATOM_KEYWORDS, EDITIONS, WORKS,
    ALICE_KEY_PASSAGES, CANDIDE_KEY_PASSAGES,
    strip_gutenberg_header_footer, extract_segment
)

# Same concept mappings as v3-alpha (for paragraph_concepts)
# v2.3: synchronized with FORMULA_OVERRIDES_V23 from import_panlang_v2.py
# Only concepts with ≥2 atoms and all non-ABS atoms are included
# (ABS atoms like MESURE, STRUCTURE, etc. are not detected in literary corpora)
CONCEPT_MAPPINGS = {
    # ── Emotional/affective concepts ─────────────────────────────────────
    "COLÈRE": {"RAGE", "DOMINATION"},
    "PEUR": {"FEAR", "PERCEPTION"},
    "SURPRISE": {"SEEKING", "PERCEPTION"},
    "JOIE": {"PLAY", "CREATION"},
    "TRISTESSE": {"GRIEF", "DESTRUCTION"},
    "MÉLANCOLIE": {"GRIEF", "COGNITION", "TEDIUM"},
    "DÉGOÛT": {"DISGUST", "PERCEPTION"},
    "ENNUI": {"TEDIUM", "COGNITION"},           # = ENNUI (same as v2.2)
    "NOSTALGIE": {"GRIEF", "COGNITION", "POSSESSION"},
    "EUPHORIE": {"PLAY", "CREATION", "MOUVEMENT"},
    "AFFECTION": {"CARE", "POSSESSION"},
    "EMOTION": {"SEEKING", "CARE"},

    # ── Perception/cognition concepts ────────────────────────────────────
    "COMPRENDRE": {"COGNITION", "PERCEPTION", "EXISTENCE"},   # understanding = cognition about perceived reality
    "ENTENDRE": {"PERCEPTION", "COMMUNICATION"}, # v2.3: was PERCEPTION+COGNITION
    "VOIR": {"PERCEPTION", "EXISTENCE"},  # seeing = perceiving what exists
    "SENTIR": {"PERCEPTION", "COGNITION"},  # sensing = perceiving + processing mentally
    "OBSERVER": {"PERCEPTION", "COGNITION", "CARE"},  # observing = attentive cognition
    "TOUCHER": {"PERCEPTION", "MOUVEMENT", "EXISTENCE"},  # touching = physical contact perception
    "BEAU": {"PERCEPTION", "SEEKING", "CREATION"},  # v2.3 override
    # BEAUTÉ has INVARIANCE (ABS) — not detectable in literary corpus

    # ── Movement/action concepts ─────────────────────────────────────────
    "CHERCHER": {"MOUVEMENT", "SEEKING", "COGNITION"},  # searching = seeking + thinking + moving
    "EXPLORER": {"MOUVEMENT", "PERCEPTION"},
    "FUIR": {"MOUVEMENT", "FEAR"},
    "MARCHER": {"MOUVEMENT", "EXISTENCE"},
    "DANSER": {"MOUVEMENT", "PLAY"},
    # DEMEURER = same atoms as MARCHER (MOUVEMENT+EXISTENCE) — merged

    # ── Social/communication concepts ────────────────────────────────────
    "AIMER": {"CARE", "COMMUNICATION", "POSSESSION"},
    "AMOUR": {"CARE", "PERCEPTION", "EXISTENCE"},
    "CONSOLER": {"COMMUNICATION", "CARE"},
    "RACONTER": {"COMMUNICATION", "CREATION"},
    "COMMANDER": {"COMMUNICATION", "DOMINATION"},
    "EXPLIQUER": {"COGNITION", "COMMUNICATION"},
    "PARTAGER": {"POSSESSION", "COMMUNICATION"},
    "AMI": {"CARE", "COMMUNICATION", "PERCEPTION"},
    "PAIX": {"COMMUNICATION", "CARE", "CREATION"},
    "ENSEIGNER": {"COGNITION", "COMMUNICATION", "CREATION"},
    "GOUVERNER": {"DOMINATION", "COMMUNICATION", "CREATION"},

    # ── Creation/knowledge concepts ──────────────────────────────────────
    "CONSTRUIRE": {"MOUVEMENT", "CREATION"},
    "INVENTER": {"COGNITION", "CREATION", "SEEKING"},  # v2.3: +SEEKING
    "IMAGINER": {"COGNITION", "CREATION"},
    "SAVOIR": {"COGNITION", "POSSESSION"},
    "APPRENDRE": {"PERCEPTION", "COGNITION", "POSSESSION"},
    "ACCUMULER": {"POSSESSION", "CREATION"},
    "ART": {"CREATION", "COMMUNICATION", "PLAY"},
    "COOPÉRER": {"COMMUNICATION", "CREATION", "POSSESSION"},
    "REALISER": {"EXISTENCE", "COGNITION"},

    # ── Conflict/dominance concepts ──────────────────────────────────────
    "GUERRE": {"MOUVEMENT", "DOMINATION", "DESTRUCTION"},
    "LIBERTÉ": {"MOUVEMENT", "DOMINATION", "EXISTENCE"},
    "SOUFFRIR": {"DESTRUCTION", "GRIEF", "EXISTENCE"},  # suffering = enduring destruction
    "HAIR": {"DISGUST", "DESTRUCTION", "DOMINATION"},
    "ENNEMI": {"RAGE", "DOMINATION", "DESTRUCTION"},
    "INTIMIDER": {"DOMINATION", "FEAR"},
    "OBÉIR": {"PERCEPTION", "DOMINATION", "EXISTENCE"},
    "DETRUIRE": {"MOUVEMENT", "DESTRUCTION"},

    # ── Existence/desire concepts ────────────────────────────────────────
    "CAUSE": {"CREATION", "MOUVEMENT", "COGNITION"},
    "VÉRITÉ": {"COGNITION", "EXISTENCE", "COMMUNICATION"},  # truth = known reality communicated
    "SATISFACTION": {"SEEKING", "EXISTENCE"},
    "DESIRER": {"POSSESSION", "SEEKING"},
    "RESSENTIR": {"COGNITION", "SEEKING"},
    "VIVRE": {"EXISTENCE", "SEEKING", "CARE"},  # living = existing + seeking + caring
    "SAISIR": {"POSSESSION", "MOUVEMENT"},
    "ILLUSION": {"MOUVEMENT", "CREATION", "EXISTENCE"},

    # ── Entity/nature concepts ───────────────────────────────────────────
    "DORMIR": {"EXISTENCE", "PERCEPTION", "DESTRUCTION"},
    "MANGER": {"DESTRUCTION", "EXISTENCE", "POSSESSION"},
    "PARENT": {"CREATION", "CARE", "EXISTENCE"},  # parent = creator who nurtures
    "POISSON": {"DESTRUCTION", "POSSESSION", "CREATION"},
    "LUNE": {"DESTRUCTION", "MOUVEMENT", "POSSESSION"},
    "SOLEIL": {"COMMUNICATION", "POSSESSION", "EXISTENCE"},
    "FEU": {"MOUVEMENT", "DESTRUCTION", "CREATION"},  # fire = transformative energy
    "ANIMAL": {"EXISTENCE", "MOUVEMENT", "SEEKING"},  # animal = existing moving seeking being
    "SE_SOUVENIR": {"MOUVEMENT", "POSSESSION", "EXISTENCE"},

    # ── Complex/multi-atom concepts ──────────────────────────────────────
    "BUT": {"MOUVEMENT", "EXISTENCE", "POSSESSION", "DOMINATION"},
    "JUSTICE": {"COGNITION", "DOMINATION", "EXISTENCE", "SEEKING"},
    "ARCHITECTURE": {"MOUVEMENT", "EXISTENCE", "DESTRUCTION", "POSSESSION"},
    "COMMUNAUTÉ": {"EXISTENCE", "COMMUNICATION", "CREATION", "POSSESSION"},
    "FAMILLE": {"EXISTENCE", "CARE", "POSSESSION", "CREATION"},
    "INSTRUMENT": {"EXISTENCE", "MOUVEMENT", "DESTRUCTION", "CREATION"},
    "RACINE": {"EXISTENCE", "CREATION", "POSSESSION"},  # root = origin that persists
    "MORAL": {"DESTRUCTION", "EXISTENCE", "COGNITION", "COMMUNICATION"},
    "NATION": {"DESTRUCTION", "EXISTENCE", "MOUVEMENT", "COMMUNICATION"},
}


# ═══════════════════════════════════════════════════════════════════════════════
# LANGUAGE PROFILES — Paramétrage par langue
# ═══════════════════════════════════════════════════════════════════════════════

LANGUAGE_PROFILES = {
    "en": {
        "lang_name": "English",
        "word_order": "SVO",
        "morphological_richness": "low",
        "case_system": False,
        "grammatical_gender": False,
        "agglutinative": False,
        "avg_sentence_length_preference": 18.0,
        "subordination_tendency": "medium",
        "formality_levels": "2-tier",
        "notes": "Analytical language; word order carries syntactic information. "
                 "No grammatical gender, minimal inflection.",
        # POS heuristics
        "determiners": {"the", "a", "an", "this", "that", "these", "those", "my",
                        "your", "his", "her", "its", "our", "their", "some", "any",
                        "no", "every", "each", "all"},
        "prepositions": {"in", "on", "at", "to", "for", "with", "from", "by",
                         "of", "about", "into", "through", "during", "before",
                         "after", "above", "below", "between", "under", "over",
                         "down", "up", "out", "off", "away"},
        "conjunctions": {"and", "but", "or", "nor", "so", "yet", "for",
                         "because", "although", "while", "if", "when", "then",
                         "however", "therefore", "moreover", "nevertheless",
                         "unless", "since", "whereas", "though"},
        "pronouns": {"i", "me", "my", "mine", "you", "your", "yours",
                     "he", "him", "his", "she", "her", "hers", "it", "its",
                     "we", "us", "our", "ours", "they", "them", "their", "theirs",
                     "who", "whom", "whose", "which", "that", "what",
                     "myself", "yourself", "himself", "herself", "itself",
                     "ourselves", "themselves", "nothing", "something", "everything"},
        "auxiliaries": {"be", "is", "am", "are", "was", "were", "been", "being",
                        "have", "has", "had", "having", "do", "does", "did",
                        "will", "would", "shall", "should", "may", "might",
                        "can", "could", "must"},
        "negations": {"not", "no", "never", "neither", "nor", "none", "nobody",
                      "nothing", "nowhere"},
        # Tense markers
        "past_markers": {"ed", "was", "were", "had", "did"},
        "present_markers": {"is", "am", "are", "do", "does"},
        "future_markers": {"will", "shall", "going"},
        # Register markers
        "formal_markers": {"henceforth", "whereas", "notwithstanding", "hereby",
                           "therein", "thereof", "pursuant", "aforementioned",
                           "indeed", "moreover", "furthermore", "nevertheless"},
        "archaic_markers": {"thou", "thee", "thy", "thine", "hath", "doth",
                            "dost", "art", "wilt", "shalt", "nay", "aye",
                            "ere", "hither", "thither", "whence", "hence",
                            "wherefore", "perchance", "methinks", "forsooth",
                            "prithee", "anon"},
        "literary_markers": {"alas", "behold", "thus", "lo", "verily",
                             "exceedingly", "forthwith"},
        # Discourse connectors
        "temporal_connectors": {"then", "after", "before", "when", "while",
                                "during", "until", "since", "meanwhile",
                                "afterwards", "suddenly", "immediately",
                                "presently", "soon", "at last", "finally"},
        "causal_connectors": {"because", "since", "therefore", "thus", "hence",
                              "consequently", "so", "accordingly"},
        "adversative_connectors": {"but", "however", "yet", "although",
                                   "nevertheless", "despite", "though",
                                   "whereas", "still"},
        "additive_connectors": {"and", "also", "moreover", "furthermore",
                                "besides", "too", "as well"},
        # Cultural markers
        "measurement_system": "imperial",
        "cultural_food": {"porridge", "pudding", "tea", "biscuit", "cake", "pie",
                          "jam", "butter", "bread", "mustard", "pepper"},
    },
    "fr": {
        "lang_name": "French",
        "word_order": "SVO",
        "morphological_richness": "medium",
        "case_system": False,
        "grammatical_gender": True,
        "agglutinative": False,
        "avg_sentence_length_preference": 15.0,
        "subordination_tendency": "high",
        "formality_levels": "2-tier",
        "notes": "Grammatical gender (M/F), passé simple vs passé composé as "
                 "register marker. Subordination-heavy in literary style.",
        "determiners": {"le", "la", "les", "un", "une", "des", "du", "de",
                        "ce", "cet", "cette", "ces", "mon", "ma", "mes",
                        "ton", "ta", "tes", "son", "sa", "ses", "notre",
                        "nos", "votre", "vos", "leur", "leurs"},
        "prepositions": {"à", "de", "en", "dans", "sur", "pour", "par",
                         "avec", "sans", "sous", "entre", "vers", "chez",
                         "contre", "depuis", "devant", "derrière", "après",
                         "avant", "pendant", "durant"},
        "conjunctions": {"et", "mais", "ou", "ni", "car", "donc", "or",
                         "puis", "ensuite", "cependant", "pourtant",
                         "néanmoins", "toutefois", "quoique", "bien que",
                         "puisque", "parce que", "tandis que", "alors que",
                         "comme", "si", "quand", "lorsque"},
        "pronouns": {"je", "me", "moi", "tu", "te", "toi", "il", "elle",
                     "lui", "le", "la", "nous", "vous", "ils", "elles",
                     "les", "leur", "on", "se", "soi", "en", "y",
                     "qui", "que", "quoi", "dont", "où",
                     "rien", "quelque chose", "tout"},
        "auxiliaries": {"être", "est", "suis", "es", "sommes", "êtes", "sont",
                        "était", "étais", "étaient", "fut", "fus", "furent",
                        "avoir", "ai", "as", "a", "avons", "avez", "ont",
                        "avait", "avais", "avaient", "eut", "eus", "eurent"},
        "negations": {"ne", "pas", "jamais", "rien", "personne", "aucun",
                      "nulle", "point", "guère", "plus"},
        "past_markers": {"passé simple", "imparfait"},
        "present_markers": {"présent"},
        "future_markers": {"futur"},
        "formal_markers": {"cependant", "néanmoins", "toutefois", "par conséquent",
                           "en outre", "de surcroît", "nonobstant",
                           "ci-dessus", "susdit"},
        "archaic_markers": {"point", "guère", "oncques", "naguère", "céans",
                            "moult", "icelui", "icelle", "es", "ès",
                            "dont acte", "sied", "fors"},
        "literary_markers": {"hélas", "certes", "voici", "voilà", "or",
                             "sus", "dame", "diantre", "parbleu"},
        "temporal_connectors": {"puis", "ensuite", "alors", "après", "avant",
                                "pendant", "quand", "lorsque", "tandis que",
                                "depuis", "aussitôt", "soudain", "enfin",
                                "bientôt", "tout à coup"},
        "causal_connectors": {"car", "parce que", "puisque", "donc",
                              "par conséquent", "ainsi", "c'est pourquoi"},
        "adversative_connectors": {"mais", "cependant", "pourtant", "néanmoins",
                                   "toutefois", "bien que", "quoique",
                                   "malgré", "or"},
        "additive_connectors": {"et", "aussi", "de plus", "en outre",
                                "également", "de même"},
        "measurement_system": "metric",
        "cultural_food": {"soupe", "pain", "vin", "fromage", "beurre",
                          "café", "chocolat", "confiture", "galette"},
    },
    "de": {
        "lang_name": "German",
        "word_order": "SOV",
        "morphological_richness": "high",
        "case_system": True,
        "grammatical_gender": True,
        "agglutinative": False,
        "avg_sentence_length_preference": 25.0,
        "subordination_tendency": "very_high",
        "formality_levels": "2-tier",
        "notes": "V2 in main clauses, SOV in subordinates. 4-case system "
                 "(NOM/ACC/DAT/GEN). Compound nouns. Long sentences typical "
                 "in 19th-century literary style.",
        "determiners": {"der", "die", "das", "den", "dem", "des",
                        "ein", "eine", "einen", "einem", "einer", "eines",
                        "dieser", "diese", "dieses", "jener", "jene",
                        "mein", "dein", "sein", "ihr", "unser", "euer"},
        "prepositions": {"in", "an", "auf", "für", "mit", "von", "zu",
                         "nach", "bei", "um", "über", "unter", "zwischen",
                         "vor", "hinter", "neben", "aus", "durch", "gegen",
                         "ohne", "seit", "während"},
        "conjunctions": {"und", "aber", "oder", "denn", "sondern",
                         "weil", "dass", "ob", "wenn", "als", "während",
                         "obwohl", "obgleich", "nachdem", "bevor", "bis",
                         "damit", "indem", "seitdem", "sodass", "jedoch",
                         "dennoch", "trotzdem", "deshalb", "daher"},
        "pronouns": {"ich", "mich", "mir", "du", "dich", "dir", "er",
                     "ihn", "ihm", "sie", "es", "wir", "uns", "ihr",
                     "euch", "ihnen", "man", "sich", "wer", "was",
                     "welcher", "welche", "welches"},
        "auxiliaries": {"sein", "ist", "bin", "bist", "sind", "seid",
                        "war", "waren", "haben", "hat", "habe", "hast",
                        "hatte", "hatten", "werden", "wird", "wirst",
                        "wurde", "wurden"},
        "negations": {"nicht", "kein", "keine", "keinen", "keinem",
                      "keiner", "niemals", "nie", "nirgends", "nichts",
                      "niemand", "weder"},
        "past_markers": {"Präteritum"},
        "present_markers": {"Präsens"},
        "future_markers": {"Futur"},
        "formal_markers": {"indes", "indessen", "gleichwohl", "nichtsdestoweniger",
                           "ferner", "überdies", "desgleichen"},
        "archaic_markers": {"allhier", "dergestalt", "alsbald", "allda",
                            "sintemal", "derohalben", "gar", "sehr",
                            "ward", "warb", "sprach"},
        "literary_markers": {"ach", "wehe", "siehe", "fürwahr", "traun",
                             "wahrlich", "wohlan"},
        "temporal_connectors": {"dann", "danach", "nachher", "vorher",
                                "während", "als", "nachdem", "bevor",
                                "seitdem", "plötzlich", "sofort",
                                "endlich", "schließlich", "bald"},
        "causal_connectors": {"weil", "da", "denn", "deshalb", "daher",
                              "darum", "folglich", "also", "somit"},
        "adversative_connectors": {"aber", "jedoch", "dennoch", "trotzdem",
                                   "obwohl", "obgleich", "hingegen",
                                   "dagegen", "allerdings"},
        "additive_connectors": {"und", "auch", "außerdem", "ferner",
                                "überdies", "zudem", "ebenfalls"},
        "measurement_system": "metric",
        "cultural_food": {"Brot", "Wurst", "Käse", "Bier", "Kuchen",
                          "Kartoffel", "Suppe"},
    },
    "it": {
        "lang_name": "Italian",
        "word_order": "SVO",
        "morphological_richness": "high",
        "case_system": False,
        "grammatical_gender": True,
        "agglutinative": False,
        "avg_sentence_length_preference": 22.0,
        "subordination_tendency": "high",
        "formality_levels": "3-tier",
        "notes": "Rich verb morphology (passato remoto vs passato prossimo = "
                 "literary/spoken split). Flexible word order for emphasis.",
        "determiners": {"il", "lo", "la", "i", "gli", "le", "un", "uno",
                        "una", "del", "dello", "della", "dei", "degli",
                        "delle", "questo", "questa", "quello", "quella",
                        "mio", "mia", "tuo", "tua", "suo", "sua"},
        "prepositions": {"di", "a", "da", "in", "con", "su", "per",
                         "tra", "fra", "dopo", "prima", "durante",
                         "senza", "contro", "verso", "sotto", "sopra"},
        "conjunctions": {"e", "ma", "o", "né", "però", "dunque",
                         "perché", "che", "se", "quando", "mentre",
                         "sebbene", "benché", "affinché", "poiché",
                         "siccome", "tuttavia", "eppure", "anzi"},
        "pronouns": {"io", "mi", "me", "tu", "ti", "te", "lui", "lei",
                     "lo", "la", "gli", "le", "noi", "ci", "voi",
                     "vi", "loro", "essi", "esse", "si",
                     "chi", "che", "quale", "cui"},
        "auxiliaries": {"essere", "è", "sono", "era", "erano", "fu",
                        "furono", "avere", "ha", "ho", "hai", "hanno",
                        "aveva", "avevano", "ebbe", "ebbero"},
        "negations": {"non", "no", "mai", "niente", "nulla", "nessuno",
                      "né", "neanche", "nemmeno", "neppure"},
        "formal_markers": {"pertanto", "altresì", "ciononostante",
                           "nondimeno", "invero"},
        "archaic_markers": {"pur", "ove", "colà", "quivi", "cotesto",
                            "egli", "ella", "esso", "dessa", "cosiffatto"},
        "literary_markers": {"ahimè", "ohimè", "ecco", "orsù", "invero"},
        "temporal_connectors": {"poi", "dopo", "prima", "quando", "mentre",
                                "intanto", "frattanto", "all'improvviso",
                                "subito", "finalmente", "infine", "allora"},
        "causal_connectors": {"perché", "poiché", "siccome", "dunque",
                              "quindi", "pertanto", "perciò"},
        "adversative_connectors": {"ma", "però", "tuttavia", "eppure",
                                   "sebbene", "benché", "nonostante",
                                   "malgrado", "anzi"},
        "additive_connectors": {"e", "anche", "inoltre", "pure", "altresì",
                                "nonché"},
        "measurement_system": "metric",
        "cultural_food": {"pane", "vino", "formaggio", "pasta", "olio",
                          "minestra", "polenta"},
    },
    "es": {
        "lang_name": "Spanish",
        "word_order": "SVO",
        "morphological_richness": "high",
        "case_system": False,
        "grammatical_gender": True,
        "agglutinative": False,
        "avg_sentence_length_preference": 20.0,
        "subordination_tendency": "high",
        "formality_levels": "3-tier",
        "notes": "ser/estar distinction. Subjunctive mood highly productive. "
                 "Flexible word order for emphasis.",
        "determiners": {"el", "la", "los", "las", "un", "una", "unos", "unas",
                        "este", "esta", "estos", "estas", "ese", "esa",
                        "aquel", "aquella", "mi", "tu", "su", "nuestro"},
        "prepositions": {"a", "de", "en", "con", "por", "para", "sin",
                         "sobre", "entre", "hasta", "desde", "hacia",
                         "contra", "durante", "tras", "bajo", "ante"},
        "conjunctions": {"y", "pero", "o", "ni", "sino", "pues",
                         "porque", "que", "si", "cuando", "mientras",
                         "aunque", "como", "ya que", "puesto que",
                         "sin embargo", "no obstante"},
        "pronouns": {"yo", "me", "mí", "tú", "te", "ti", "él", "ella",
                     "lo", "la", "le", "nos", "nosotros", "vosotros",
                     "ellos", "ellas", "los", "las", "les", "se",
                     "quien", "que", "cual"},
        "auxiliaries": {"ser", "es", "soy", "eres", "somos", "son",
                        "era", "fue", "fueron", "estar", "está", "estoy",
                        "haber", "ha", "he", "has", "han", "había", "hubo"},
        "negations": {"no", "nunca", "jamás", "nada", "nadie", "ninguno",
                      "ni", "tampoco"},
        "formal_markers": {"empero", "no obstante", "asimismo", "por ende"},
        "archaic_markers": {"vos", "vuesa merced", "antaño", "otrora",
                            "aqueste", "do", "maguer"},
        "literary_markers": {"ay", "he aquí", "ved"},
        "temporal_connectors": {"luego", "después", "antes", "cuando",
                                "mientras", "entonces", "de repente",
                                "enseguida", "finalmente", "al fin"},
        "causal_connectors": {"porque", "ya que", "puesto que", "pues",
                              "por lo tanto", "por consiguiente", "así"},
        "adversative_connectors": {"pero", "sin embargo", "no obstante",
                                   "aunque", "a pesar de", "sino"},
        "additive_connectors": {"y", "también", "además", "asimismo",
                                "igualmente"},
        "measurement_system": "metric",
        "cultural_food": {"pan", "vino", "aceite", "jamón", "queso",
                          "tortilla", "sopa"},
    },
    "eo": {
        "lang_name": "Esperanto",
        "word_order": "SVO",
        "morphological_richness": "medium",
        "case_system": True,
        "grammatical_gender": False,
        "agglutinative": True,
        "avg_sentence_length_preference": 22.0,
        "subordination_tendency": "medium",
        "formality_levels": "1-tier",
        "notes": "Planned language with regular morphology. Accusative case (-n). "
                 "Agglutinative derivation (mal-, -ino, -ejo, etc.).",
        "determiners": {"la"},
        "prepositions": {"en", "sur", "al", "de", "kun", "por", "el",
                         "pri", "tra", "ĉe", "antaŭ", "post", "sub",
                         "super", "inter", "ekster", "kontraŭ", "sen"},
        "conjunctions": {"kaj", "sed", "aŭ", "nek", "ĉar", "do",
                         "tamen", "kvankam", "dum", "se", "kiam",
                         "ke", "por ke"},
        "pronouns": {"mi", "vi", "li", "ŝi", "ĝi", "ni", "ili", "oni",
                     "si", "kiu", "kio", "tiu", "tio", "ĉiu", "ĉio",
                     "neniu", "nenio"},
        "auxiliaries": {"estas", "estis", "estos", "estus", "estu"},
        "negations": {"ne", "neniam", "nenie", "neniel", "nenio",
                      "neniu", "nek"},
        "formal_markers": set(),
        "archaic_markers": set(),
        "literary_markers": {"ho", "ve", "jen"},
        "temporal_connectors": {"tiam", "poste", "antaŭe", "kiam", "dum",
                                "subite", "tuj", "fine", "baldaŭ"},
        "causal_connectors": {"ĉar", "do", "tial", "sekve", "pro tio"},
        "adversative_connectors": {"sed", "tamen", "kvankam", "malgraŭ",
                                   "spite"},
        "additive_connectors": {"kaj", "ankaŭ", "krome", "cetere", "plie"},
        "measurement_system": "metric",
        "cultural_food": set(),
    },
    "fi": {
        "lang_name": "Finnish",
        "word_order": "SVO",
        "morphological_richness": "very_high",
        "case_system": True,
        "grammatical_gender": False,
        "agglutinative": True,
        "avg_sentence_length_preference": 14.0,
        "subordination_tendency": "low",
        "formality_levels": "2-tier",
        "notes": "15 grammatical cases. Agglutinative with extensive suffixing. "
                 "No grammatical gender, no articles. Short sentences preferred.",
        "determiners": set(),
        "prepositions": set(),
        "conjunctions": {"ja", "mutta", "tai", "vai", "sillä", "koska",
                         "kun", "jos", "vaikka", "että", "jotta",
                         "kuitenkin", "silti", "siis", "nimittäin"},
        "pronouns": {"minä", "sinä", "hän", "me", "te", "he",
                     "se", "tämä", "tuo", "nämä", "nuo", "ne",
                     "joka", "mikä", "kuka", "mitä", "kukaan",
                     "mikään", "jokin", "joku"},
        "auxiliaries": {"olla", "on", "oli", "ovat", "olivat"},
        "negations": {"ei", "en", "et", "emme", "ette", "eivät",
                      "koskaan", "ei koskaan", "ei mitään", "ei kukaan"},
        "formal_markers": set(),
        "archaic_markers": {"ken", "tahi", "vaan", "lieneekö"},
        "literary_markers": {"voi", "kas"},
        "temporal_connectors": {"sitten", "sen jälkeen", "ennen", "kun",
                                "samalla", "yhtäkkiä", "heti", "vihdoin",
                                "lopulta", "pian"},
        "causal_connectors": {"koska", "sillä", "siksi", "sen vuoksi",
                              "niinpä", "siis"},
        "adversative_connectors": {"mutta", "kuitenkin", "silti", "vaikka",
                                   "siitä huolimatta"},
        "additive_connectors": {"ja", "myös", "lisäksi", "samoin",
                                "niin ikään"},
        "measurement_system": "metric",
        "cultural_food": {"leipä", "puuro", "kalakukko", "piirakka",
                          "kahvi", "voi"},
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# DOLT HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def dolt_sql(query, check=True):
    """Execute Dolt SQL, return CSV stdout."""
    env = os.environ.copy()
    env["DOLT_CLI_NO_PAGER"] = "1"
    r = subprocess.run(
        ["dolt", "sql", "-r", "csv", "-q", query],
        capture_output=True, text=True, cwd=DOLT_DB, env=env
    )
    if check and r.returncode != 0:
        print(f"  ⚠️  SQL error: {r.stderr.strip()[:300]}")
        return None
    return r.stdout.strip()


def dolt_commit(message):
    """Stage all + commit."""
    env = os.environ.copy()
    env["DOLT_CLI_NO_PAGER"] = "1"
    subprocess.run(["dolt", "add", "."], capture_output=True, text=True, cwd=DOLT_DB, env=env)
    r = subprocess.run(
        ["dolt", "commit", "-m", message, "--allow-empty"],
        capture_output=True, text=True, cwd=DOLT_DB, env=env
    )
    return r.returncode == 0


def esc(val):
    """Escape for SQL."""
    if val is None:
        return "NULL"
    return "'" + str(val).replace("'", "''").replace("\\", "\\\\") + "'"


def get_text_by_id(table, row_id, text_col="text_content"):
    """Get text content from a table by ID, avoiding CSV parsing issues."""
    result = dolt_sql(
        f"SELECT CHAR_LENGTH({text_col}), {text_col} FROM {table} WHERE id = {row_id}"
    )
    if not result:
        return ""
    lines = result.strip().split('\n')
    if len(lines) < 2:
        return ""
    full_data = '\n'.join(lines[1:])
    try:
        first_comma = full_data.index(',')
        return full_data[first_comma + 1:]
    except ValueError:
        return full_data


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 0: APPLY SCHEMA
# ═══════════════════════════════════════════════════════════════════════════════

def step0_apply_schema():
    """Apply schema_v3_seven_layers.sql to Dolt."""
    print("\n" + "=" * 70)
    print("STEP 0: Apply 7-layer schema")
    print("=" * 70)

    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        schema_text = f.read()

    # Extract SQL statements (skip comment-only blocks)
    statements = []
    for stmt in schema_text.split(';'):
        lines = [l for l in stmt.strip().split('\n')
                 if l.strip() and not l.strip().startswith('--')]
        clean = '\n'.join(lines).strip()
        if clean and ('CREATE' in clean.upper() or 'INSERT' in clean.upper()
                      or 'VIEW' in clean.upper()):
            statements.append(clean)

    for stmt in statements:
        keyword = ' '.join(stmt.split()[:4])
        dolt_sql(stmt, check=False)
        print(f"  ✅ {keyword}...")

    # Verify key tables
    tables = dolt_sql("SHOW TABLES") or ""
    expected = [
        "paragraph_units", "syntax_analysis", "paragraph_word_atoms",
        "morphology_features", "register_markers", "discourse_relations",
        "prosody_rhythm", "cultural_referents", "translator_choices",
        "language_profiles", "paragraph_concepts", "paragraph_analysis_summary"
    ]
    ok_count = 0
    for t in expected:
        if t in tables:
            print(f"  ✅ {t}")
            ok_count += 1
        else:
            print(f"  ❌ {t}")

    print(f"\n  → {ok_count}/{len(expected)} tables created")
    return ok_count == len(expected)


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1: INSERT LANGUAGE PROFILES
# ═══════════════════════════════════════════════════════════════════════════════

def step1_language_profiles():
    """Insert language profile configurations into Dolt."""
    print("\n" + "=" * 70)
    print("STEP 1: Language profiles (paramétrage multilingue)")
    print("=" * 70)

    count = 0
    for lang, p in LANGUAGE_PROFILES.items():
        sql = (
            f"INSERT IGNORE INTO language_profiles "
            f"(lang, lang_name, word_order, morphological_richness, "
            f"case_system, grammatical_gender, agglutinative, "
            f"avg_sentence_length_preference, subordination_tendency, "
            f"formality_levels, notes) VALUES ("
            f"{esc(lang)}, {esc(p['lang_name'])}, {esc(p['word_order'])}, "
            f"{esc(p['morphological_richness'])}, "
            f"{1 if p['case_system'] else 0}, "
            f"{1 if p['grammatical_gender'] else 0}, "
            f"{1 if p['agglutinative'] else 0}, "
            f"{p['avg_sentence_length_preference']}, "
            f"{esc(p['subordination_tendency'])}, "
            f"{esc(p['formality_levels'])}, {esc(p['notes'])})"
        )
        dolt_sql(sql, check=False)
        count += 1
        print(f"  ✅ {lang} ({p['lang_name']}): {p['word_order']}, "
              f"morph={p['morphological_richness']}, "
              f"case={p['case_system']}, gender={p['grammatical_gender']}, "
              f"avg_sent={p['avg_sentence_length_preference']}")

    print(f"\n  → {count} language profiles inserted")
    return count > 0


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2: SPLIT SEGMENTS INTO PARAGRAPHS
# ═══════════════════════════════════════════════════════════════════════════════

def split_into_paragraphs(text, lang):
    """Split text into paragraphs. A paragraph is separated by blank lines
    or double newlines. If no paragraph breaks, treat whole text as one paragraph."""
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Split on double newlines (paragraph boundaries)
    raw_paras = re.split(r'\n\s*\n', text)

    paragraphs = []
    for p in raw_paras:
        p = re.sub(r'\s+', ' ', p).strip()
        if p and len(p) > 10:
            paragraphs.append(p)

    # If no paragraph breaks found, split by sentence groups
    # Each group = ~3-5 sentences (approximate paragraph)
    if len(paragraphs) <= 1 and len(text) > 200:
        sentences = split_into_sentences(text, lang)
        # Group sentences into paragraphs of ~3-5 sentences
        profile = LANGUAGE_PROFILES.get(lang, LANGUAGE_PROFILES["en"])
        target_words = int(profile["avg_sentence_length_preference"] * 4)
        current_para = []
        current_words = 0
        for s in sentences:
            wc = len(s.split())
            current_para.append(s)
            current_words += wc
            if current_words >= target_words and len(current_para) >= 2:
                paragraphs.append(' '.join(current_para))
                current_para = []
                current_words = 0
        if current_para:
            paragraphs.append(' '.join(current_para))

    return paragraphs if paragraphs else [text.strip()]


def split_into_sentences(text, lang):
    """Rule-based sentence splitter (reuse from v3-alpha)."""
    text = re.sub(r'\s+', ' ', text).strip()
    abbreviations = {
        "en": r"(?:Mr|Mrs|Ms|Dr|St|Jr|Sr|vs|etc|Vol|Ch|Fig|No|pp)",
        "fr": r"(?:Mr|Mme|Mlle|Dr|St|etc|vol|ch|fig|pp|av|J\.-C)",
        "de": r"(?:Hr|Fr|Dr|St|Nr|Bd|Kap|usw|bzw|vgl|sog)",
        "it": r"(?:Sig|Dott|Prof|ecc|vol|cap|fig|pag)",
        "es": r"(?:Sr|Sra|Dr|Ud|Uds|etc|vol|cap|fig)",
        "eo": r"(?:S-ro|S-ino|D-ro|k\.t\.p)",
        "fi": r"(?:hr|rva|tri|prof|esim|jne|ks|mm)",
    }
    abbr = abbreviations.get(lang, abbreviations["en"])
    parts = re.split(r'([.!?]+(?:\s+|$))', text)
    sentences = []
    buffer = ""
    for part in parts:
        buffer += part
        if re.search(r'[.!?]\s*$', buffer):
            if re.search(abbr + r'\.\s*$', buffer):
                continue
            sentence = buffer.strip()
            if sentence and len(sentence) > 5:
                sentences.append(sentence)
            buffer = ""
    if buffer.strip() and len(buffer.strip()) > 5:
        sentences.append(buffer.strip())
    return sentences


def step2_split_into_paragraphs():
    """Split all segments into paragraphs and store in Dolt."""
    print("\n" + "=" * 70)
    print("STEP 2: Split segments into paragraphs")
    print("=" * 70)

    all_passages = {}
    all_passages.update({k: ("ALICE", v) for k, v in ALICE_KEY_PASSAGES.items()})
    all_passages.update({k: ("CANDIDE", v) for k, v in CANDIDE_KEY_PASSAGES.items()})

    total_paragraphs = 0

    for seg_ref, (work_id, passage) in sorted(all_passages.items()):
        if not passage.get("markers"):
            continue

        for eid, e in EDITIONS.items():
            if e["work_id"] != work_id:
                continue
            lang = e["lang"]
            if lang not in passage.get("markers", {}):
                continue

            # Get segment_id
            seg_result = dolt_sql(
                f"SELECT id FROM gutenberg_segments "
                f"WHERE edition_id = {esc(eid)} AND segment_ref = {esc(seg_ref)}"
            )
            if not seg_result:
                continue
            lines = seg_result.strip().split('\n')
            if len(lines) < 2:
                continue
            segment_id = int(lines[1].strip())

            # Load corpus text
            filepath = os.path.join(CORPUS_DIR, f"pg{e['gutenberg_id']}_{lang}.txt")
            if not os.path.exists(filepath):
                continue

            with open(filepath, 'r', encoding='utf-8') as f:
                full_text = f.read()

            clean_text = strip_gutenberg_header_footer(full_text)
            markers = passage["markers"][lang]
            segment_text = extract_segment(clean_text, markers)

            if not segment_text:
                continue

            # Split into paragraphs
            paragraphs = split_into_paragraphs(segment_text, lang)

            for idx, para_text in enumerate(paragraphs):
                sentences = split_into_sentences(para_text, lang)
                word_count = len(para_text.split())
                char_count = len(para_text)
                sent_count = len(sentences)
                alignment_group = f"{seg_ref}_p{idx:03d}"

                sql = (
                    f"INSERT IGNORE INTO paragraph_units "
                    f"(segment_id, paragraph_index, text_content, sentence_count, "
                    f"word_count, char_count, lang, alignment_group, "
                    f"alignment_confidence) VALUES ("
                    f"{segment_id}, {idx}, {esc(para_text[:4000])}, {sent_count}, "
                    f"{word_count}, {char_count}, {esc(lang)}, "
                    f"{esc(alignment_group)}, 0.5)"
                )
                dolt_sql(sql, check=False)
                total_paragraphs += 1

            print(f"  ✅ [{lang}] {seg_ref}: {len(paragraphs)} para "
                  f"({sum(len(p.split()) for p in paragraphs)} mots)")

    print(f"\n  → {total_paragraphs} paragraph_units inserted")
    return total_paragraphs > 0


# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 1: SYNTAX ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_syntax(text, lang):
    """Rule-based syntactic analysis: POS tagging + dependency approximation.
    
    No NLP library — uses language-specific closed-class word lists +
    positional heuristics for open-class words.
    """
    profile = LANGUAGE_PROFILES.get(lang, LANGUAGE_PROFILES["en"])
    words = text.split()
    analysis = []
    
    determiners = profile.get("determiners", set())
    prepositions = profile.get("prepositions", set())
    conjunctions = profile.get("conjunctions", set())
    pronouns = profile.get("pronouns", set())
    auxiliaries = profile.get("auxiliaries", set())
    negations = profile.get("negations", set())

    # Sentence boundary detection for clause_id
    clause_id = 0
    sentence_idx = 0

    for i, word_raw in enumerate(words):
        word_clean = word_raw.lower().strip('.,;:!?"\'"()[]{}—–-…""''«»')
        
        # POS tagging via closed-class lists
        if word_clean in determiners:
            pos = "DET"
            dep = "det"
        elif word_clean in prepositions:
            pos = "ADP"
            dep = "case"
        elif word_clean in conjunctions:
            pos = "CCONJ" if word_clean in {"and", "et", "und", "e", "y", "kaj", "ja",
                                              "but", "mais", "aber", "ma", "pero", "sed", "mutta",
                                              "or", "ou", "oder", "o", "aŭ", "tai"} else "SCONJ"
            dep = "cc" if pos == "CCONJ" else "mark"
            if pos == "SCONJ":
                clause_id += 1
        elif word_clean in pronouns:
            pos = "PRON"
            dep = "nsubj" if i == 0 or (i > 0 and words[i-1].lower().strip('.,;:!?') in conjunctions) else "obj"
        elif word_clean in auxiliaries:
            pos = "AUX"
            dep = "aux"
        elif word_clean in negations:
            pos = "PART"
            dep = "advmod"
        elif re.match(r'^\d+$', word_clean):
            pos = "NUM"
            dep = "nummod"
        elif word_clean.endswith(('ly', 'ment', 'lich', 'mente')) and len(word_clean) > 4:
            pos = "ADV"
            dep = "advmod"
        elif word_clean.endswith(('tion', 'ness', 'ment', 'ity', 'ung', 'keit',
                                   'heit', 'zione', 'ción', 'ado')):
            pos = "NOUN"
            dep = "obj"
        elif word_clean.endswith(('ous', 'ful', 'less', 'able', 'ible', 'eux',
                                   'ive', 'al', 'isch', 'lich', 'oso', 'osa')):
            pos = "ADJ"
            dep = "amod"
        elif word_clean[0:1].isupper() and i > 0:
            pos = "PROPN"
            dep = "nsubj" if i < 3 else "flat"
        else:
            # Heuristic: verbs tend to follow subjects
            # Look for atom keywords to help
            is_verb = False
            for atom, kw_by_lang in ATOM_KEYWORDS.items():
                if lang in kw_by_lang:
                    for kw in kw_by_lang[lang]:
                        if word_clean == kw.lower() or (len(kw) >= 4 and 
                            word_clean.startswith(kw.lower()[:max(4, len(kw)-2)])):
                            if atom in {"MOUVEMENT", "COMMUNICATION", "CREATION",
                                        "DESTRUCTION", "PERCEPTION", "COGNITION"}:
                                is_verb = True
                            break
                    if is_verb:
                        break

            if is_verb:
                pos = "VERB"
                dep = "root" if not any(a["pos_tag"] == "VERB" for a in analysis) else "conj"
            else:
                pos = "NOUN"
                dep = "nsubj" if i < 2 else "obj"

        # Detect sentence boundaries for clause tracking
        if re.search(r'[.!?]$', word_raw):
            sentence_idx += 1
            clause_id = sentence_idx

        # Semantic role heuristic
        semantic_role = None
        if dep == "nsubj":
            semantic_role = "AGENT"
        elif dep == "obj":
            semantic_role = "PATIENT"
        elif dep in ("obl", "case") and pos == "ADP":
            semantic_role = None
        elif dep == "advmod":
            semantic_role = "MANNER"

        # Head position heuristic (simplified)
        head_pos = -1
        if dep in ("det", "amod", "nummod"):
            # Head is typically the next noun
            for j in range(i + 1, min(i + 5, len(words))):
                head_pos = j
                break
        elif dep in ("nsubj", "obj"):
            # Head is typically the verb
            for a in analysis:
                if a["pos_tag"] in ("VERB", "AUX"):
                    head_pos = a["word_position"]
                    break

        analysis.append({
            "word_position": i,
            "word_form": word_raw,
            "pos_tag": pos,
            "dep_relation": dep,
            "head_position": head_pos,
            "clause_id": clause_id,
            "clause_type": "main" if clause_id == 0 else "subordinate",
            "semantic_role": semantic_role,
        })

    return analysis


# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 2: WORD-ATOM ALIGNMENT (paragraph level)
# ═══════════════════════════════════════════════════════════════════════════════

def align_words_to_atoms(text, lang):
    """Attribute each word to its atom(s). Reuses ATOM_KEYWORDS with
    paragraph-level context for disambiguation.
    
    Cascade de résolution (v3 — couverture 100%) :
      0. Classification structurelle (titres, TOC, illustrations)
      1. Match direct/prefix dans ATOM_KEYWORDS (original)
      1b. EO X-notation normalization (gx→ĝ, sx→ŝ, etc.)
      2. Lemmatisation → ATOM_KEYWORDS (irréguliers + suffixes)
      3. Racines étymologiques (latines, germaniques)
      4. Inférence inter-langues (langues parentes)
      5. Compound word splitting (Finnish agglutination)
    """
    # Import conditionnel pour ne pas casser si le module est absent
    try:
        from morpho_semantic_bridge import (
            resolve_word_full, classify_structural_text, normalize_eo_x_notation
        )
        has_bridge = True
    except ImportError:
        try:
            from morpho_semantic_bridge import resolve_word_full
            has_bridge = True
        except ImportError:
            has_bridge = False

    # --- Pass 0: Structural text classification ---
    if has_bridge:
        structural = classify_structural_text(text, lang)
        if structural:
            return structural  # Structural text fully classified

    # Normalize EO X-notation for keyword matching
    text_for_matching = text
    if lang == "eo" and has_bridge:
        text_for_matching = normalize_eo_x_notation(text)

    words = text_for_matching.split()
    original_words = text.split()  # Keep originals for word_form
    attributions = []
    sentences = split_into_sentences(text_for_matching, lang)
    matched_positions = set()  # Track positions already matched
    
    # Map word positions to sentence index
    word_to_sent = {}
    offset = 0
    for si, sent in enumerate(sentences):
        sent_words = sent.split()
        for j in range(len(sent_words)):
            word_to_sent[offset + j] = si
        offset += len(sent_words)

    # --- Pass 1: Original match (direct + prefix) ---
    for word_pos, word_raw in enumerate(words):
        word_lower = word_raw.lower().strip('.,;:!?"\'"()[]{}—–-…""''«»')
        if len(word_lower) < 2:
            continue

        for atom, keywords_by_lang in ATOM_KEYWORDS.items():
            if lang not in keywords_by_lang:
                continue

            for kw in keywords_by_lang[lang]:
                kw_lower = kw.lower()
                if word_lower == kw_lower or (
                    len(kw_lower) >= 4 and word_lower.startswith(
                        kw_lower[:max(4, len(kw_lower) - 2)]
                    )
                ):
                    if word_lower == kw_lower:
                        confidence = 0.95
                    elif word_lower.startswith(kw_lower):
                        confidence = 0.80
                    else:
                        confidence = 0.60

                    # Disambiguation notes for known ambiguities
                    disambiguation = None
                    if lang == "de" and word_lower in ("sein", "seine", "seinem", "seinen"):
                        disambiguation = "sein = possessif OU être (auxiliaire); contexte requis"
                    elif lang == "fr" and word_lower == "être":
                        disambiguation = "être = EXISTENCE (verbe copule); fréquent, bruit possible"
                    elif lang == "en" and word_lower == "be":
                        disambiguation = "be = EXISTENCE (copula); very frequent, possible noise"

                    orig_form = original_words[word_pos] if word_pos < len(original_words) else word_raw
                    attributions.append({
                        "word_position": word_pos,
                        "word_form": orig_form,
                        "word_lemma": kw,
                        "atom_id": atom,
                        "confidence": confidence,
                        "keyword_matched": kw,
                        "disambiguation": disambiguation,
                        "sentence_local_idx": word_to_sent.get(word_pos, 0),
                    })
                    matched_positions.add(word_pos)
                    break

    # --- Pass 2: Morpho-semantic bridge (lemmatisation + racines + inter-langues) ---
    if has_bridge:
        for word_pos, word_raw in enumerate(words):
            if word_pos in matched_positions:
                continue  # Déjà résolu en pass 1

            word_lower = word_raw.lower().strip('.,;:!?"\'"()[]{}—–-…""''«»')
            if len(word_lower) < 3:  # Seuil plus strict pour le bridge
                continue

            bridge_results = resolve_word_full(word_lower, lang, ATOM_KEYWORDS)
            for r in bridge_results:
                if r["confidence"] >= 0.45:  # Seuil minimum
                    orig_form = original_words[word_pos] if word_pos < len(original_words) else word_raw
                    attributions.append({
                        "word_position": word_pos,
                        "word_form": orig_form,
                        "word_lemma": r["lemma"],
                        "atom_id": r["atom_id"],
                        "confidence": r["confidence"],
                        "keyword_matched": r["lemma"],
                        "disambiguation": r["disambiguation"],
                        "sentence_local_idx": word_to_sent.get(word_pos, 0),
                    })
                    matched_positions.add(word_pos)
                    break  # Best match only per word

    # --- Pass 3: Finnish compound word splitting ---
    if lang == "fi" and has_bridge:
        for word_pos, word_raw in enumerate(words):
            if word_pos in matched_positions:
                continue
            word_lower = word_raw.lower().strip('.,;:!?"\'"()[]{}—–-…""''«»')
            if len(word_lower) < 8:  # Compounds are long
                continue
            # Try splitting at various positions
            for split_pos in range(4, len(word_lower) - 3):
                part2 = word_lower[split_pos:]
                bridge_results = resolve_word_full(part2, lang, ATOM_KEYWORDS)
                for r in bridge_results:
                    if r["confidence"] >= 0.50:
                        orig_form = original_words[word_pos] if word_pos < len(original_words) else word_raw
                        attributions.append({
                            "word_position": word_pos,
                            "word_form": orig_form,
                            "word_lemma": r["lemma"],
                            "atom_id": r["atom_id"],
                            "confidence": round(r["confidence"] * 0.85, 3),
                            "keyword_matched": r["lemma"],
                            "disambiguation": f"FI compound split: {word_lower} → ...+{part2} → {r['lemma']}",
                            "sentence_local_idx": word_to_sent.get(word_pos, 0),
                        })
                        matched_positions.add(word_pos)
                        break
                if word_pos in matched_positions:
                    break

    return attributions


# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 3: MORPHOLOGY
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_morphology(text, lang, syntax_results):
    """Rule-based morphological analysis. Uses suffix patterns and
    language-specific rules to approximate tense, aspect, mood, etc."""
    profile = LANGUAGE_PROFILES.get(lang, LANGUAGE_PROFILES["en"])
    words = text.split()
    morpho = []

    for i, word_raw in enumerate(words):
        word = word_raw.lower().strip('.,;:!?"\'"()[]{}—–-…""''«»')
        syn = syntax_results[i] if i < len(syntax_results) else {}
        pos = syn.get("pos_tag", "NOUN")

        tense = None
        aspect = None
        mood = "indicative"
        voice = "active"
        person = None
        number = "sing"
        gender = None
        case_feat = None
        degree = None
        lemma = word

        if pos in ("VERB", "AUX"):
            # English tense detection
            if lang == "en":
                if word.endswith("ed"):
                    tense = "past"
                    aspect = "perfective"
                    lemma = word[:-2] if len(word) > 4 else word[:-1]
                elif word.endswith("ing"):
                    tense = "present"
                    aspect = "progressive"
                    lemma = word[:-3]
                elif word.endswith("s") and not word.endswith("ss"):
                    tense = "present"
                    person = "3"
                    lemma = word[:-1]
                else:
                    tense = "present"
            # French tense detection
            elif lang == "fr":
                if word.endswith(("a", "èrent", "it", "ut")):
                    tense = "passé_simple"
                    aspect = "perfective"
                elif word.endswith(("ait", "aient", "ais")):
                    tense = "imparfait"
                    aspect = "imperfective"
                elif word.endswith(("é", "ée", "és", "ées")):
                    tense = "participe_passé"
                    aspect = "perfective"
                elif word.endswith(("ant",)):
                    tense = "participe_présent"
                    aspect = "progressive"
                elif word.endswith(("ra", "ront", "ras", "rai")):
                    tense = "futur"
                elif word.endswith(("rait", "raient", "rais")):
                    tense = "conditionnel"
                    mood = "conditional"
                else:
                    tense = "présent"
            # German tense detection
            elif lang == "de":
                if word.endswith(("te", "ten", "test", "tet")):
                    tense = "Präteritum"
                    aspect = "perfective"
                elif word.endswith(("t", "st", "en", "e")):
                    tense = "Präsens"
                else:
                    tense = "Präsens"
            # Italian
            elif lang == "it":
                if word.endswith(("ò", "arono", "ì", "irono")):
                    tense = "passato_remoto"
                    aspect = "perfective"
                elif word.endswith(("va", "vano", "vi")):
                    tense = "imperfetto"
                    aspect = "imperfective"
                else:
                    tense = "presente"
            # Spanish
            elif lang == "es":
                if word.endswith(("ó", "aron", "ieron")):
                    tense = "pretérito"
                    aspect = "perfective"
                elif word.endswith(("ba", "ban", "aba", "aban")):
                    tense = "imperfecto"
                    aspect = "imperfective"
                else:
                    tense = "presente"
            # Esperanto
            elif lang == "eo":
                if word.endswith("is"):
                    tense = "past"
                elif word.endswith("as"):
                    tense = "present"
                elif word.endswith("os"):
                    tense = "future"
                elif word.endswith("us"):
                    mood = "conditional"
                elif word.endswith("u"):
                    mood = "imperative"
            # Finnish
            elif lang == "fi":
                if word.endswith(("i", "isi")):
                    tense = "past"
                else:
                    tense = "present"

        # Gender detection (FR, DE, IT, ES)
        if profile.get("grammatical_gender"):
            if lang == "fr":
                if word.endswith(("ée", "euse", "ière", "ive", "elle", "enne", "ette")):
                    gender = "feminine"
                elif word.endswith(("eur", "ier", "er", "ien", "if")):
                    gender = "masculine"
            elif lang == "de":
                if word.endswith(("ung", "heit", "keit", "schaft", "tion", "ie")):
                    gender = "feminine"
                elif word.endswith(("ling", "ismus", "er")):
                    gender = "masculine"
                elif word.endswith(("chen", "lein", "ment", "um")):
                    gender = "neuter"
            elif lang == "it":
                if word.endswith("a"):
                    gender = "feminine"
                elif word.endswith("o"):
                    gender = "masculine"
            elif lang == "es":
                if word.endswith("a"):
                    gender = "feminine"
                elif word.endswith("o"):
                    gender = "masculine"

        # Number detection
        if lang in ("en",):
            if word.endswith("s") and not word.endswith("ss") and pos == "NOUN":
                number = "plur"
        elif lang in ("fr", "it", "es"):
            if word.endswith("s") or word.endswith("i"):
                number = "plur"
        elif lang == "de":
            if word.endswith(("en", "er", "e")) and pos == "NOUN":
                number = "plur"

        # Case detection (DE, EO, FI)
        if profile.get("case_system"):
            if lang == "eo":
                if word_raw.endswith("n"):
                    case_feat = "accusative"
                else:
                    case_feat = "nominative"
            elif lang == "fi":
                if word.endswith(("ssa", "ssä")):
                    case_feat = "inessive"
                elif word.endswith(("sta", "stä")):
                    case_feat = "elative"
                elif word.endswith(("lle",)):
                    case_feat = "allative"
                elif word.endswith(("lta", "ltä")):
                    case_feat = "ablative"
                elif word.endswith(("lla", "llä")):
                    case_feat = "adessive"
                elif word.endswith(("n",)) and pos == "NOUN":
                    case_feat = "genitive"
                elif word.endswith(("a", "ä")) and pos == "NOUN":
                    case_feat = "partitive"
                else:
                    case_feat = "nominative"

        # Degree (adjectives)
        if pos == "ADJ":
            if lang == "en":
                if word.endswith("er"):
                    degree = "comparative"
                elif word.endswith("est"):
                    degree = "superlative"
                else:
                    degree = "positive"
            elif lang == "de":
                if word.endswith("er"):
                    degree = "comparative"
                elif word.endswith("sten"):
                    degree = "superlative"
            elif lang == "fr":
                degree = "positive"

        # Passive voice detection
        if lang == "en" and i > 0:
            prev = words[i-1].lower().strip('.,;:!?')
            if prev in ("was", "were", "been", "being") and word.endswith("ed"):
                voice = "passive"
        elif lang == "fr" and i > 0:
            prev = words[i-1].lower().strip('.,;:!?')
            if prev in ("est", "sont", "fut", "furent", "été") and word.endswith(("é", "ée", "és", "ées")):
                voice = "passive"

        morpho.append({
            "word_position": i,
            "word_form": word_raw,
            "lemma": lemma,
            "tense": tense,
            "aspect": aspect,
            "mood": mood,
            "voice": voice,
            "person": person,
            "number_feat": number,
            "gender": gender,
            "case_feat": case_feat,
            "degree": degree,
        })

    return morpho


# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 4: REGISTER & STYLE
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_register(text, lang):
    """Detect register and style markers in the paragraph."""
    profile = LANGUAGE_PROFILES.get(lang, LANGUAGE_PROFILES["en"])
    words = text.lower().split()
    markers = []

    formal_set = profile.get("formal_markers", set())
    archaic_set = profile.get("archaic_markers", set())
    literary_set = profile.get("literary_markers", set())

    for i, word_raw in enumerate(words):
        word = word_raw.strip('.,;:!?"\'"()[]{}—–-…""''«»')

        if word in formal_set:
            markers.append({
                "marker_type": "formal",
                "marker_text": word,
                "word_position_start": i,
                "word_position_end": i,
                "formality_score": 0.8,
                "archaism_flag": False,
                "literary_flag": False,
                "colloquial_flag": False,
                "explanation": f"Formal register marker in {profile['lang_name']}",
            })
        elif word in archaic_set:
            markers.append({
                "marker_type": "archaic",
                "marker_text": word,
                "word_position_start": i,
                "word_position_end": i,
                "formality_score": 0.9,
                "archaism_flag": True,
                "literary_flag": True,
                "colloquial_flag": False,
                "explanation": f"Archaic form: '{word}' marks pre-modern or literary register",
            })
        elif word in literary_set:
            markers.append({
                "marker_type": "literary",
                "marker_text": word,
                "word_position_start": i,
                "word_position_end": i,
                "formality_score": 0.7,
                "archaism_flag": False,
                "literary_flag": True,
                "colloquial_flag": False,
                "explanation": f"Literary interjection or marker in {profile['lang_name']}",
            })

    # Check for passé simple (FR) — strong register marker
    if lang == "fr":
        passe_simple_count = 0
        for w in words:
            w_clean = w.strip('.,;:!?"\'"()[]{}—–-')
            if re.search(r'(a|èrent|it|ut|ûmes|ûtes|urent)$', w_clean) and len(w_clean) > 3:
                passe_simple_count += 1
        if passe_simple_count >= 2:
            markers.append({
                "marker_type": "tense_register",
                "marker_text": f"passé simple ×{passe_simple_count}",
                "word_position_start": None,
                "word_position_end": None,
                "formality_score": 0.85,
                "archaism_flag": True,
                "literary_flag": True,
                "colloquial_flag": False,
                "explanation": "Passé simple usage indicates literary/formal register "
                               "(vs passé composé in spoken/modern French)",
            })

    # Check for passato remoto (IT) — same literary marker
    if lang == "it":
        passato_count = 0
        for w in words:
            w_clean = w.strip('.,;:!?"\'"()[]{}—–-')
            if re.search(r'(ò|arono|ì|irono)$', w_clean) and len(w_clean) > 3:
                passato_count += 1
        if passato_count >= 2:
            markers.append({
                "marker_type": "tense_register",
                "marker_text": f"passato remoto ×{passato_count}",
                "word_position_start": None,
                "word_position_end": None,
                "formality_score": 0.8,
                "archaism_flag": False,
                "literary_flag": True,
                "colloquial_flag": False,
                "explanation": "Passato remoto usage indicates literary register "
                               "(vs passato prossimo in spoken Italian)",
            })

    return markers


# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 5: DISCOURSE RELATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_discourse(text, lang):
    """Detect discourse relations: connectors, anaphora, co-reference."""
    profile = LANGUAGE_PROFILES.get(lang, LANGUAGE_PROFILES["en"])
    words = text.split()
    relations = []
    sentences = split_into_sentences(text, lang)

    # Connector detection
    temporal = profile.get("temporal_connectors", set())
    causal = profile.get("causal_connectors", set())
    adversative = profile.get("adversative_connectors", set())
    additive = profile.get("additive_connectors", set())

    for i, word_raw in enumerate(words):
        word = word_raw.lower().strip('.,;:!?"\'"()[]{}—–-…""''«»')

        rel_type = None
        if word in temporal:
            rel_type = "temporal"
        elif word in causal:
            rel_type = "causal"
        elif word in adversative:
            rel_type = "adversative"
        elif word in additive and i > 0:
            rel_type = "additive"

        if rel_type:
            # Determine sentence context
            sent_idx = 0
            offset = 0
            for si, sent in enumerate(sentences):
                sent_words = sent.split()
                if offset + len(sent_words) > i:
                    sent_idx = si
                    break
                offset += len(sent_words)

            relations.append({
                "relation_type": rel_type,
                "source_position": i,
                "target_position": None,
                "source_text": word_raw,
                "target_text": None,
                "connector": word,
                "strength": 0.7 if rel_type in ("temporal", "causal") else 0.5,
                "sentence_local_idx": sent_idx,
            })

    # Anaphora detection (pronouns referring back)
    pronouns_set = profile.get("pronouns", set())
    for i, word_raw in enumerate(words):
        word = word_raw.lower().strip('.,;:!?"\'"()[]{}—–-…""''«»')
        if word in pronouns_set and i > 3:
            # Check if this is a 3rd person pronoun (anaphoric)
            third_person = {
                "en": {"he", "she", "it", "they", "him", "her", "them", "his", "its", "their"},
                "fr": {"il", "elle", "ils", "elles", "lui", "leur", "le", "la", "les"},
                "de": {"er", "sie", "es", "ihm", "ihn", "ihr", "ihnen", "sein", "ihre"},
                "it": {"egli", "ella", "esso", "essa", "essi", "esse", "lui", "lei", "loro"},
                "es": {"él", "ella", "ellos", "ellas", "lo", "la", "los", "las", "le", "les"},
                "eo": {"li", "ŝi", "ĝi", "ili"},
                "fi": {"hän", "he", "se", "ne"},
            }
            if word in third_person.get(lang, set()):
                relations.append({
                    "relation_type": "anaphora",
                    "source_position": i,
                    "target_position": None,
                    "source_text": word_raw,
                    "target_text": None,
                    "connector": None,
                    "strength": 0.6,
                    "sentence_local_idx": 0,
                })

    return relations


# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 6: PROSODY & RHYTHM
# ═══════════════════════════════════════════════════════════════════════════════

def estimate_syllables(word, lang):
    """Rough syllable count estimation per language."""
    word = word.lower().strip('.,;:!?"\'"()[]{}—–-…""''«»')
    if not word:
        return 0
    
    if lang in ("en",):
        # English: count vowel clusters
        vowels = re.findall(r'[aeiouy]+', word)
        count = len(vowels)
        if word.endswith('e') and count > 1:
            count -= 1
        return max(1, count)
    elif lang in ("fr",):
        # French: count vowel groups, silent e
        vowels = re.findall(r'[aeiouyéèêëàâîïôùûü]+', word)
        count = len(vowels)
        if word.endswith('e') and count > 1:
            count -= 1
        if word.endswith('es') and count > 1:
            count -= 1
        return max(1, count)
    elif lang in ("de",):
        vowels = re.findall(r'[aeiouyäöü]+', word)
        return max(1, len(vowels))
    elif lang in ("it", "es"):
        vowels = re.findall(r'[aeiouàèéìíòóùú]+', word)
        return max(1, len(vowels))
    elif lang == "eo":
        vowels = re.findall(r'[aeiou]+', word)
        return max(1, len(vowels))
    elif lang == "fi":
        vowels = re.findall(r'[aeiouyäö]+', word)
        return max(1, len(vowels))
    else:
        return max(1, len(re.findall(r'[aeiouy]+', word)))


def analyze_prosody(text, lang):
    """Analyze rhythm, cadence, parallelism, and rhetorical figures."""
    sentences = split_into_sentences(text, lang)
    results = []

    sentence_lengths = []
    for si, sent in enumerate(sentences):
        words_in_sent = sent.split()
        syllable_count = sum(estimate_syllables(w, lang) for w in words_in_sent)
        word_count = len(words_in_sent)
        sentence_lengths.append(word_count)

        # Rhythm type heuristic
        if word_count <= 8:
            rhythm = "staccato"
        elif word_count <= 15:
            rhythm = "moderate"
        elif word_count <= 25:
            rhythm = "flowing"
        else:
            rhythm = "periodic"

        # Detect rhetorical figures
        figure = None
        figure_text = None

        # Repetition (anaphora — same word at start)
        if si > 0 and len(sentences) > si:
            prev_start = sentences[si-1].split()[0].lower() if sentences[si-1].split() else ""
            curr_start = words_in_sent[0].lower() if words_in_sent else ""
            if prev_start == curr_start and len(prev_start) > 2:
                figure = "anaphora"
                figure_text = f"Repeated start: '{curr_start}'"

        # Exclamation/question (rhetorical)
        if sent.endswith('!'):
            figure = figure or "exclamation"
            figure_text = figure_text or f"Emphatic: {sent[:50]}"
        elif sent.endswith('?'):
            figure = figure or "question"
            figure_text = figure_text or f"Interrogative: {sent[:50]}"

        # Ellipsis
        if '...' in sent or '…' in sent:
            figure = figure or "ellipsis"
            figure_text = figure_text or f"Suspension: {sent[:50]}"

        # Cadence score (variation in sentence length = more dynamic)
        cadence = 0.5

        results.append({
            "sentence_local_idx": si,
            "syllable_count_est": syllable_count,
            "stress_pattern": None,
            "rhythm_type": rhythm,
            "parallelism_group": None,
            "rhetorical_figure": figure,
            "figure_text": figure_text,
            "cadence_score": cadence,
        })

    # Compute cadence based on length variation
    if len(sentence_lengths) > 1:
        mean_len = sum(sentence_lengths) / len(sentence_lengths)
        variance = sum((l - mean_len) ** 2 for l in sentence_lengths) / len(sentence_lengths)
        std_dev = math.sqrt(variance)
        # Normalize: high variation = dynamic cadence
        cadence_score = min(1.0, std_dev / max(mean_len, 1))
        for r in results:
            r["cadence_score"] = round(cadence_score, 3)

    # Detect parallelism (similar length sentences in sequence)
    for i in range(1, len(sentence_lengths)):
        if abs(sentence_lengths[i] - sentence_lengths[i-1]) <= 3:
            group = f"parallel_{i-1}_{i}"
            results[i-1]["parallelism_group"] = group
            results[i]["parallelism_group"] = group

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# LAYER 7: CULTURAL REFERENTS
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_cultural_referents(text, lang, edition_info):
    """Detect cultural adaptations and translation strategies."""
    profile = LANGUAGE_PROFILES.get(lang, LANGUAGE_PROFILES["en"])
    words_lower = text.lower()
    referents = []

    # Food/drink cultural markers
    cultural_food = profile.get("cultural_food", set())
    for food in cultural_food:
        if food.lower() in words_lower:
            pos = words_lower.find(food.lower())
            word_pos_start = len(words_lower[:pos].split()) - 1

            referents.append({
                "referent_type": "food_drink",
                "source_text": food,
                "target_text": food,
                "original_text": None,
                "strategy": "retention",
                "explanation": f"Cultural food item '{food}' retained in {profile['lang_name']} translation",
                "cultural_distance": 0.1,
                "word_position_start": max(0, word_pos_start),
                "word_position_end": max(0, word_pos_start),
            })

    # Measurement system
    if profile.get("measurement_system") == "imperial":
        for unit in ["mile", "miles", "foot", "feet", "inch", "inches",
                     "yard", "yards", "pound", "pounds", "ounce"]:
            if unit in words_lower:
                referents.append({
                    "referent_type": "measurement",
                    "source_text": unit,
                    "target_text": unit,
                    "original_text": unit,
                    "strategy": "retention",
                    "explanation": f"Imperial measurement '{unit}' — source language uses same system",
                    "cultural_distance": 0.0,
                    "word_position_start": None,
                    "word_position_end": None,
                })
    else:
        # Check if imperial units were converted or kept
        for unit in ["mile", "mille", "Meile", "miglio", "milla"]:
            if unit.lower() in words_lower:
                referents.append({
                    "referent_type": "measurement",
                    "source_text": unit,
                    "target_text": unit,
                    "original_text": None,
                    "strategy": "foreignization",
                    "explanation": f"Kept non-metric unit '{unit}' from source (foreignization)",
                    "cultural_distance": 0.3,
                    "word_position_start": None,
                    "word_position_end": None,
                })

    # Proper names — check if adapted or kept
    alice_names = {
        "en": "Alice", "fr": "Alice", "de": "Alice", "it": "Alice",
        "eo": "Alicio", "fi": "Liisa",
    }
    if lang in alice_names:
        name = alice_names[lang]
        original = "Alice"
        if name.lower() in words_lower:
            strategy = "retention" if name == original else "domestication"
            dist = 0.0 if name == original else 0.5
            referents.append({
                "referent_type": "proper_name",
                "source_text": original,
                "target_text": name,
                "original_text": original,
                "strategy": strategy,
                "explanation": (f"'{original}' → '{name}': "
                                + ("name kept" if strategy == "retention"
                                   else f"name adapted to {profile['lang_name']} phonology")),
                "cultural_distance": dist,
                "word_position_start": None,
                "word_position_end": None,
            })

    return referents


# ═══════════════════════════════════════════════════════════════════════════════
# TRANSLATOR CHOICE EXPLANATION
# ═══════════════════════════════════════════════════════════════════════════════

def generate_translator_choices(para_text, lang, edition_id, original_text,
                                 morpho_results, register_results,
                                 prosody_results, cultural_results):
    """Generate explanations for translator interpretation choices."""
    profile = LANGUAGE_PROFILES.get(lang, LANGUAGE_PROFILES["en"])
    choices = []

    # Choice 1: Sentence length preference
    sentences = split_into_sentences(para_text, lang)
    avg_len = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
    expected = profile["avg_sentence_length_preference"]
    deviation = abs(avg_len - expected)

    if deviation > 5:
        choices.append({
            "layer": "prosody",
            "choice_type": "sentence_length",
            "original_form": f"avg {expected:.0f} words/sentence expected for {profile['lang_name']}",
            "translated_form": f"avg {avg_len:.0f} words/sentence actual",
            "alternative_forms": None,
            "explanation": (f"Translator deviates from typical {profile['lang_name']} "
                            f"sentence length ({expected:.0f}) with avg {avg_len:.0f} words. "
                            f"{'Longer sentences suggest formal/literary style.' if avg_len > expected else 'Shorter sentences suggest modern/accessible style.'}"),
            "impact_on_meaning": "style",
            "confidence": 0.7,
        })

    # Choice 2: Register markers
    for rm in register_results:
        if rm.get("archaism_flag"):
            choices.append({
                "layer": "register",
                "choice_type": "archaism",
                "original_form": None,
                "translated_form": rm["marker_text"],
                "alternative_forms": None,
                "explanation": rm.get("explanation", "Archaic form used"),
                "impact_on_meaning": "style",
                "confidence": 0.8,
            })

    # Choice 3: Tense selection (FR passé simple, IT passato remoto)
    for rm in register_results:
        if rm.get("marker_type") == "tense_register":
            choices.append({
                "layer": "morphology",
                "choice_type": "tense_selection",
                "original_form": None,
                "translated_form": rm["marker_text"],
                "alternative_forms": "passé composé (FR) / passato prossimo (IT)",
                "explanation": rm.get("explanation", "Literary tense selected"),
                "impact_on_meaning": "register",
                "confidence": 0.85,
            })

    # Choice 4: Cultural adaptations
    for cr in cultural_results:
        if cr.get("strategy") in ("domestication", "foreignization"):
            choices.append({
                "layer": "cultural",
                "choice_type": cr["strategy"],
                "original_form": cr.get("original_text"),
                "translated_form": cr.get("target_text"),
                "alternative_forms": None,
                "explanation": cr.get("explanation", "Cultural adaptation"),
                "impact_on_meaning": "cultural",
                "confidence": 0.75,
            })

    # Choice 5: Word order deviation (for SOV languages)
    if profile["word_order"] != "SVO":
        choices.append({
            "layer": "syntax",
            "choice_type": "word_order",
            "original_form": f"SVO (source typically)",
            "translated_form": f"{profile['word_order']} ({profile['lang_name']})",
            "alternative_forms": None,
            "explanation": (f"{profile['lang_name']} uses {profile['word_order']} word order, "
                            f"requiring structural reorganization of clauses."),
            "impact_on_meaning": "neutral",
            "confidence": 0.9,
        })

    # Choice 6: Morphological richness compensation
    if profile["morphological_richness"] in ("high", "very_high"):
        choices.append({
            "layer": "morphology",
            "choice_type": "morphological_encoding",
            "original_form": None,
            "translated_form": f"rich morphology ({profile['morphological_richness']})",
            "alternative_forms": None,
            "explanation": (f"{profile['lang_name']} encodes grammatical information "
                            f"(case, gender, number, tense) within word forms, "
                            f"allowing more flexible word order and fewer function words."),
            "impact_on_meaning": "neutral",
            "confidence": 0.85,
        })

    return choices


# ═══════════════════════════════════════════════════════════════════════════════
# PARAGRAPH CONCEPT DETECTION
# ═══════════════════════════════════════════════════════════════════════════════

def detect_paragraph_concepts(atom_results, syntax_results):
    """Detect concepts from paragraph-level atom attributions,
    using syntactic coherence for disambiguation."""
    # Build atom set with per-sentence distribution
    atoms_by_sentence = defaultdict(set)
    atom_evidence = {}

    for attr in atom_results:
        atom = attr["atom_id"]
        sent_idx = attr.get("sentence_local_idx", 0)
        atoms_by_sentence[sent_idx].add(atom)
        if atom not in atom_evidence:
            atom_evidence[atom] = {
                "word": attr["word_form"],
                "pos": attr["word_position"],
                "conf": attr["confidence"],
                "sent": sent_idx,
            }

    all_atoms = set(atom_evidence.keys())
    concepts = []

    for concept, required_atoms in CONCEPT_MAPPINGS.items():
        if not required_atoms.issubset(all_atoms):
            continue

        # Check syntactic coherence: are the required atoms in the same
        # sentence (or adjacent sentences)?
        atom_sentences = {atom_evidence[a]["sent"] for a in required_atoms}
        syntactic_coherence = max(atom_sentences) - min(atom_sentences) <= 1

        # Check discourse support: are there discourse connectors linking?
        discourse_support = False

        evidence = {}
        total_conf = 0
        for a in required_atoms:
            info = atom_evidence[a]
            evidence[a] = {"word": info["word"], "pos": info["pos"], "conf": info["conf"]}
            total_conf += info["conf"]

        avg_conf = total_conf / len(required_atoms)

        # Boost confidence if syntactically coherent
        if syntactic_coherence:
            avg_conf = min(1.0, avg_conf * 1.1)

        concepts.append({
            "concept_id": concept,
            "atoms_evidence": evidence,
            "confidence": round(avg_conf, 3),
            "syntactic_coherence": syntactic_coherence,
            "discourse_support": discourse_support,
        })

    return concepts


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN PIPELINE: Process all paragraphs through 7 layers
# ═══════════════════════════════════════════════════════════════════════════════

def step3_process_all_paragraphs():
    """Process every paragraph through all 7 layers + translator choices."""
    print("\n" + "=" * 70)
    print("STEP 3: Process all paragraphs through 7 layers")
    print("=" * 70)

    # Get all paragraph IDs and metadata
    result = dolt_sql(
        "SELECT pu.id, pu.lang, pu.paragraph_index, pu.word_count, "
        "pu.alignment_group, gs.segment_ref, gs.edition_id "
        "FROM paragraph_units pu "
        "JOIN gutenberg_segments gs ON pu.segment_id = gs.id "
        "ORDER BY gs.segment_ref, pu.lang, pu.paragraph_index"
    )

    if not result:
        print("  ❌ No paragraphs found")
        return False

    lines = result.strip().split('\n')
    total = len(lines) - 1
    print(f"  → {total} paragraphs to process")

    stats = {
        "syntax": 0, "atoms": 0, "morpho": 0, "register": 0,
        "discourse": 0, "prosody": 0, "cultural": 0, "choices": 0,
        "concepts": 0,
    }

    for line_idx, line in enumerate(lines[1:], 1):
        parts = line.split(',')
        if len(parts) < 7:
            continue

        para_id = int(parts[0].strip())
        lang = parts[1].strip()
        para_idx = parts[2].strip()
        word_count = int(parts[3].strip())
        alignment_group = parts[4].strip()
        seg_ref = parts[5].strip()
        edition_id = parts[6].strip()

        # Get text
        para_text = get_text_by_id("paragraph_units", para_id)
        if not para_text or len(para_text) < 10:
            continue

        if line_idx % 20 == 1 or line_idx == 1:
            print(f"\n  [{lang}] {seg_ref} p{para_idx} ({word_count} mots)...")

        # ── LAYER 1: Syntax ──
        syntax_results = analyze_syntax(para_text, lang)
        for sr in syntax_results:
            dolt_sql(
                f"INSERT IGNORE INTO syntax_analysis "
                f"(paragraph_id, word_position, word_form, pos_tag, dep_relation, "
                f"head_position, clause_id, clause_type, semantic_role, lang) VALUES ("
                f"{para_id}, {sr['word_position']}, {esc(sr['word_form'][:120])}, "
                f"{esc(sr['pos_tag'])}, {esc(sr['dep_relation'])}, {sr['head_position']}, "
                f"{sr['clause_id']}, {esc(sr['clause_type'])}, "
                f"{esc(sr['semantic_role'])}, {esc(lang)})",
                check=False
            )
            stats["syntax"] += 1

        # ── LAYER 2: Word→atom alignment ──
        atom_results = align_words_to_atoms(para_text, lang)
        for ar in atom_results:
            dolt_sql(
                f"INSERT IGNORE INTO paragraph_word_atoms "
                f"(paragraph_id, word_position, word_form, word_lemma, atom_id, "
                f"confidence, keyword_matched, disambiguation, sentence_local_idx) VALUES ("
                f"{para_id}, {ar['word_position']}, {esc(ar['word_form'][:120])}, "
                f"{esc(ar['word_lemma'])}, {esc(ar['atom_id'])}, {ar['confidence']}, "
                f"{esc(ar['keyword_matched'])}, {esc(ar.get('disambiguation'))}, "
                f"{ar.get('sentence_local_idx', 0)})",
                check=False
            )
            stats["atoms"] += 1

        # ── LAYER 3: Morphology ──
        morpho_results = analyze_morphology(para_text, lang, syntax_results)
        for mr in morpho_results:
            dolt_sql(
                f"INSERT IGNORE INTO morphology_features "
                f"(paragraph_id, word_position, word_form, lemma, tense, aspect, "
                f"mood, voice, person, number_feat, gender, case_feat, degree, lang) VALUES ("
                f"{para_id}, {mr['word_position']}, {esc(mr['word_form'][:120])}, "
                f"{esc(mr.get('lemma'))}, {esc(mr.get('tense'))}, {esc(mr.get('aspect'))}, "
                f"{esc(mr.get('mood'))}, {esc(mr.get('voice'))}, {esc(mr.get('person'))}, "
                f"{esc(mr.get('number_feat'))}, {esc(mr.get('gender'))}, "
                f"{esc(mr.get('case_feat'))}, {esc(mr.get('degree'))}, {esc(lang)})",
                check=False
            )
            stats["morpho"] += 1

        # ── LAYER 4: Register & style ──
        register_results = analyze_register(para_text, lang)
        for rr in register_results:
            dolt_sql(
                f"INSERT IGNORE INTO register_markers "
                f"(paragraph_id, marker_type, marker_text, word_position_start, "
                f"word_position_end, formality_score, archaism_flag, literary_flag, "
                f"colloquial_flag, explanation, lang) VALUES ("
                f"{para_id}, {esc(rr['marker_type'])}, {esc(rr['marker_text'][:200])}, "
                f"{rr['word_position_start'] if rr['word_position_start'] is not None else 'NULL'}, "
                f"{rr['word_position_end'] if rr['word_position_end'] is not None else 'NULL'}, "
                f"{rr['formality_score']}, {1 if rr['archaism_flag'] else 0}, "
                f"{1 if rr['literary_flag'] else 0}, {1 if rr['colloquial_flag'] else 0}, "
                f"{esc(rr.get('explanation', '')[:500])}, {esc(lang)})",
                check=False
            )
            stats["register"] += 1

        # ── LAYER 5: Discourse ──
        discourse_results = analyze_discourse(para_text, lang)
        for dr in discourse_results:
            dolt_sql(
                f"INSERT IGNORE INTO discourse_relations "
                f"(paragraph_id, relation_type, source_position, target_position, "
                f"source_text, target_text, connector, strength, sentence_local_idx, lang) VALUES ("
                f"{para_id}, {esc(dr['relation_type'])}, "
                f"{dr['source_position'] if dr['source_position'] is not None else 'NULL'}, "
                f"{dr['target_position'] if dr['target_position'] is not None else 'NULL'}, "
                f"{esc(dr.get('source_text', '')[:200])}, "
                f"{esc(dr.get('target_text'))}, {esc(dr.get('connector'))}, "
                f"{dr['strength']}, {dr.get('sentence_local_idx', 0)}, {esc(lang)})",
                check=False
            )
            stats["discourse"] += 1

        # ── LAYER 6: Prosody ──
        prosody_results = analyze_prosody(para_text, lang)
        for pr in prosody_results:
            dolt_sql(
                f"INSERT IGNORE INTO prosody_rhythm "
                f"(paragraph_id, sentence_local_idx, syllable_count_est, stress_pattern, "
                f"rhythm_type, parallelism_group, rhetorical_figure, figure_text, "
                f"cadence_score, lang) VALUES ("
                f"{para_id}, {pr['sentence_local_idx']}, {pr['syllable_count_est']}, "
                f"{esc(pr.get('stress_pattern'))}, {esc(pr['rhythm_type'])}, "
                f"{esc(pr.get('parallelism_group'))}, {esc(pr.get('rhetorical_figure'))}, "
                f"{esc(pr.get('figure_text', '')[:300] if pr.get('figure_text') else None)}, "
                f"{pr['cadence_score']}, {esc(lang)})",
                check=False
            )
            stats["prosody"] += 1

        # ── LAYER 7: Cultural referents ──
        cultural_results = analyze_cultural_referents(para_text, lang, edition_id)
        for cr in cultural_results:
            dolt_sql(
                f"INSERT IGNORE INTO cultural_referents "
                f"(paragraph_id, referent_type, source_text, target_text, "
                f"original_text, strategy, explanation, cultural_distance, "
                f"word_position_start, word_position_end, lang) VALUES ("
                f"{para_id}, {esc(cr['referent_type'])}, {esc(cr['source_text'][:200])}, "
                f"{esc(cr.get('target_text', '')[:200])}, "
                f"{esc(cr.get('original_text'))}, {esc(cr['strategy'])}, "
                f"{esc(cr.get('explanation', '')[:500])}, {cr['cultural_distance']}, "
                f"{cr['word_position_start'] if cr.get('word_position_start') is not None else 'NULL'}, "
                f"{cr['word_position_end'] if cr.get('word_position_end') is not None else 'NULL'}, "
                f"{esc(lang)})",
                check=False
            )
            stats["cultural"] += 1

        # ── Paragraph concepts ──
        concepts = detect_paragraph_concepts(atom_results, syntax_results)
        for c in concepts:
            dolt_sql(
                f"INSERT IGNORE INTO paragraph_concepts "
                f"(paragraph_id, concept_id, atoms_evidence, confidence, "
                f"syntactic_coherence, discourse_support, analysis_method) VALUES ("
                f"{para_id}, {esc(c['concept_id'])}, "
                f"'{json.dumps(c['atoms_evidence'])}', {c['confidence']}, "
                f"{1 if c['syntactic_coherence'] else 0}, "
                f"{1 if c['discourse_support'] else 0}, 'seven_layer')",
                check=False
            )
            stats["concepts"] += 1

        # ── Translator choices ──
        original_text = None  # Would need cross-referencing original edition
        choices = generate_translator_choices(
            para_text, lang, edition_id, original_text,
            morpho_results, register_results, prosody_results, cultural_results
        )
        for ch in choices:
            dolt_sql(
                f"INSERT IGNORE INTO translator_choices "
                f"(paragraph_id, edition_id, layer, choice_type, "
                f"original_form, translated_form, alternative_forms, "
                f"explanation, impact_on_meaning, confidence, lang) VALUES ("
                f"{para_id}, {esc(edition_id)}, {esc(ch['layer'])}, "
                f"{esc(ch['choice_type'])}, {esc(ch.get('original_form'))}, "
                f"{esc(ch.get('translated_form'))}, {esc(ch.get('alternative_forms'))}, "
                f"{esc(ch['explanation'][:1000])}, {esc(ch.get('impact_on_meaning', 'neutral'))}, "
                f"{ch['confidence']}, {esc(lang)})",
                check=False
            )
            stats["choices"] += 1

        # ── Analysis summary ──
        layers_done = 7
        register_avg = (sum(r.get("formality_score", 0.5) for r in register_results) /
                        max(len(register_results), 1)) if register_results else 0.5
        prosody_avg = (sum(p.get("cadence_score", 0.5) for p in prosody_results) /
                       max(len(prosody_results), 1)) if prosody_results else 0.5
        syntax_depth = max((s.get("clause_id", 0) for s in syntax_results), default=0)
        morpho_feats = sum(1 for m in morpho_results
                           if any(m.get(f) for f in ("tense", "gender", "case_feat")))
        morpho_complexity = morpho_feats / max(len(morpho_results), 1)

        readiness = min(1.0, (
            (0.15 if stats["syntax"] > 0 else 0) +
            (0.15 if stats["atoms"] > 0 else 0) +
            (0.15 if stats["morpho"] > 0 else 0) +
            (0.1 if stats["register"] > 0 else 0) +
            (0.15 if stats["discourse"] > 0 else 0) +
            (0.15 if stats["prosody"] > 0 else 0) +
            (0.15 if stats["cultural"] > 0 else 0)
        ))

        dolt_sql(
            f"INSERT IGNORE INTO paragraph_analysis_summary "
            f"(paragraph_id, edition_id, segment_ref, layers_completed, "
            f"atom_count, concept_count, choice_count, syntax_depth, "
            f"morpho_complexity, register_score, discourse_density, "
            f"prosody_score, cultural_adaptations, reconstruction_readiness) VALUES ("
            f"{para_id}, {esc(edition_id)}, {esc(seg_ref)}, {layers_done}, "
            f"{len(atom_results)}, {len(concepts)}, {len(choices)}, "
            f"{syntax_depth}, {morpho_complexity:.3f}, {register_avg:.3f}, "
            f"{len(discourse_results) / max(word_count, 1):.4f}, "
            f"{prosody_avg:.3f}, {len(cultural_results)}, {readiness:.3f})",
            check=False
        )

    # Final statistics
    print("\n  ── RESULTS ──")
    for layer, count in stats.items():
        print(f"    {layer}: {count} entries")
    print(f"    Total paragraphs processed: {total}")

    return True


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4: COMPARATIVE REPORT
# ═══════════════════════════════════════════════════════════════════════════════

def step4_comparative_report():
    """Generate a comparative report across languages and translators."""
    print("\n" + "=" * 70)
    print("STEP 4: Comparative multilingual report")
    print("=" * 70)

    # 1. Summary by language
    print("\n  ── Summary by language ──")
    result = dolt_sql(
        "SELECT pu.lang, COUNT(*) as paras, SUM(pu.word_count) as total_words, "
        "AVG(pu.sentence_count) as avg_sents "
        "FROM paragraph_units pu GROUP BY pu.lang ORDER BY pu.lang"
    )
    if result:
        for line in result.strip().split('\n')[1:]:
            parts = line.split(',')
            if len(parts) >= 4:
                lang = parts[0].strip()
                paras = parts[1].strip()
                words = parts[2].strip()
                avg_s = parts[3].strip()
                profile = LANGUAGE_PROFILES.get(lang, {})
                expected = profile.get("avg_sentence_length_preference", "?")
                print(f"    {lang}: {paras} paragraphs, {words} words, "
                      f"avg {avg_s} sents/para (expected sent_len: {expected})")

    # 2. Atom distribution
    print("\n  ── Atom distribution ──")
    result = dolt_sql(
        "SELECT pwa.atom_id, COUNT(*) as detections, "
        "COUNT(DISTINCT pu.lang) as langs "
        "FROM paragraph_word_atoms pwa "
        "JOIN paragraph_units pu ON pwa.paragraph_id = pu.id "
        "GROUP BY pwa.atom_id ORDER BY detections DESC"
    )
    if result:
        for line in result.strip().split('\n')[1:]:
            parts = line.split(',')
            if len(parts) >= 3:
                print(f"    {parts[0].strip()}: {parts[1].strip()} detections "
                      f"across {parts[2].strip()} languages")

    # 3. Concept convergence
    print("\n  ── Concept convergence (paragraphe-level) ──")
    result = dolt_sql(
        "SELECT pc.concept_id, COUNT(*) as detections, "
        "COUNT(DISTINCT pu.lang) as langs, "
        "ROUND(AVG(pc.confidence), 3) as avg_conf, "
        "SUM(pc.syntactic_coherence) as coherent "
        "FROM paragraph_concepts pc "
        "JOIN paragraph_units pu ON pc.paragraph_id = pu.id "
        "GROUP BY pc.concept_id "
        "HAVING langs >= 3 "
        "ORDER BY langs DESC, detections DESC "
        "LIMIT 15"
    )
    if result:
        for line in result.strip().split('\n')[1:]:
            parts = line.split(',')
            if len(parts) >= 5:
                print(f"    {parts[0].strip()}: {parts[2].strip()} langs, "
                      f"{parts[1].strip()} detections, conf={parts[3].strip()}, "
                      f"coherent={parts[4].strip()}")

    # 4. Translator choices summary
    print("\n  ── Translator choices ──")
    result = dolt_sql(
        "SELECT tc.layer, tc.choice_type, COUNT(*) as choices "
        "FROM translator_choices tc "
        "GROUP BY tc.layer, tc.choice_type "
        "ORDER BY choices DESC"
    )
    if result:
        for line in result.strip().split('\n')[1:]:
            parts = line.split(',')
            if len(parts) >= 3:
                print(f"    {parts[0].strip()}/{parts[1].strip()}: "
                      f"{parts[2].strip()} documented choices")

    # 5. Register analysis
    print("\n  ── Register markers ──")
    result = dolt_sql(
        "SELECT rm.lang, rm.marker_type, COUNT(*) as markers "
        "FROM register_markers rm "
        "GROUP BY rm.lang, rm.marker_type "
        "ORDER BY rm.lang, markers DESC"
    )
    if result:
        for line in result.strip().split('\n')[1:]:
            parts = line.split(',')
            if len(parts) >= 3:
                print(f"    [{parts[0].strip()}] {parts[1].strip()}: "
                      f"{parts[2].strip()} markers")

    # 6. Cultural referents
    print("\n  ── Cultural referents ──")
    result = dolt_sql(
        "SELECT cr.lang, cr.strategy, cr.referent_type, COUNT(*) as refs "
        "FROM cultural_referents cr "
        "GROUP BY cr.lang, cr.strategy, cr.referent_type "
        "ORDER BY cr.lang, refs DESC"
    )
    if result:
        for line in result.strip().split('\n')[1:]:
            parts = line.split(',')
            if len(parts) >= 4:
                print(f"    [{parts[0].strip()}] {parts[1].strip()} ({parts[2].strip()}): "
                      f"{parts[3].strip()}")

    # 7. Reconstruction readiness
    print("\n  ── Reconstruction readiness (by language) ──")
    result = dolt_sql(
        "SELECT pu.lang, "
        "ROUND(AVG(pas.reconstruction_readiness), 3) as avg_readiness, "
        "ROUND(AVG(pas.morpho_complexity), 3) as avg_morpho, "
        "ROUND(AVG(pas.register_score), 3) as avg_register "
        "FROM paragraph_analysis_summary pas "
        "JOIN paragraph_units pu ON pas.paragraph_id = pu.id "
        "GROUP BY pu.lang ORDER BY pu.lang"
    )
    if result:
        for line in result.strip().split('\n')[1:]:
            parts = line.split(',')
            if len(parts) >= 4:
                print(f"    {parts[0].strip()}: readiness={parts[1].strip()}, "
                      f"morpho={parts[2].strip()}, register={parts[3].strip()}")

    return True


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 5: DOLT COMMIT
# ═══════════════════════════════════════════════════════════════════════════════

def step5_commit():
    """Commit all 7-layer data to Dolt."""
    print("\n" + "=" * 70)
    print("STEP 5: Dolt commit")
    print("=" * 70)

    message = (
        f"feat(v3): 7-layer multilingual analysis engine\n\n"
        f"- Schema: 12 tables + 3 views for paragraph-level analysis\n"
        f"- Layer 1: Syntax (POS, dependencies, clauses, semantic roles)\n"
        f"- Layer 2: Word-atom alignment (targeted, paragraph-level)\n"
        f"- Layer 3: Morphology (tense, aspect, mood, case, gender)\n"
        f"- Layer 4: Register/style (formal, archaic, literary markers)\n"
        f"- Layer 5: Discourse (connectors, anaphora, coherence)\n"
        f"- Layer 6: Prosody (rhythm, cadence, parallelism, figures)\n"
        f"- Layer 7: Cultural referents (domestication, foreignization)\n"
        f"- Translator choices: documented interpretation decisions\n"
        f"- Language profiles: 7 languages parameterized\n"
        f"- Paragraph-level concepts with syntactic coherence check\n"
        f"- Corpus: all segments x all editions"
    )

    ok = dolt_commit(message)
    if ok:
        print(f"  ✅ Committed to Dolt")
    else:
        print(f"  ⚠️  Commit result unclear (may be empty)")
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  PaniniFS — Seven-Layer Multilingual Analysis Engine (v3)           ║")
    print("║  Paragraph-level · 7 couches · Choix traducteur documentés         ║")
    print("║  L'équivalence parfaite est impossible — on explique les choix     ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    steps = [
        ("Apply 7-layer schema",        step0_apply_schema),
        ("Language profiles",           step1_language_profiles),
        ("Split into paragraphs",       step2_split_into_paragraphs),
        ("Process 7 layers",            step3_process_all_paragraphs),
        ("Comparative report",          step4_comparative_report),
        ("Dolt commit",                 step5_commit),
    ]

    results = {}
    for name, func in steps:
        try:
            ok = func()
            results[name] = "✅" if ok else "⚠️"
        except Exception as e:
            print(f"\n❌ ERROR in {name}: {e}")
            import traceback
            traceback.print_exc()
            results[name] = "❌"

    print("\n" + "=" * 70)
    print("FINAL RESULTS:")
    for name, status in results.items():
        print(f"  {status} {name}")
    print("=" * 70)


if __name__ == "__main__":
    main()
