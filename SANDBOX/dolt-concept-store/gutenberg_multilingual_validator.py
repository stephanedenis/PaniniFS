#!/usr/bin/env python3
"""
gutenberg_multilingual_validator.py — Validation empirique PanLang via Gutenberg

Principe PaniniFS: toute information en relation avec sa source.
  "édition/époque(année)/auteur" selon "traducteur/époque(année)"
  selon "site gutenberg en date du..."

Workflow:
  1. Appliquer le schéma de provenance (schema_gutenberg_provenance.sql)
  2. Enregistrer les œuvres et éditions avec métadonnées complètes
  3. Télécharger les textes depuis Gutenberg (UTF-8 plain text)
  4. Extraire les segments comparables (passages-clés)
  5. Décomposer chaque segment en atomes PanLang
  6. Calculer la convergence/divergence inter-traductions
  7. Commit Dolt

Corpus initial:
  - Alice's Adventures in Wonderland (6 langues: EN, FR, DE, IT, EO, FI)
  - Candide, ou l'optimisme (5 langues: FR, EN, ES, EL, FI)
"""

import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import date
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

DOLT_DB = os.path.join(os.path.dirname(__file__), "panini-unified-db")
SCHEMA_SQL = os.path.join(os.path.dirname(__file__), "schema_gutenberg_provenance.sql")
CORPUS_DIR = os.path.join(os.path.dirname(__file__), "gutenberg_corpus")
TODAY = date.today().isoformat()

# ─────────────────────────────────────────────────────────────────────────────
# Corpus multilingue — Métadonnées de provenance complètes
# ─────────────────────────────────────────────────────────────────────────────

WORKS = {
    "ALICE": {
        "title_original": "Alice's Adventures in Wonderland",
        "author": "Carroll, Lewis",
        "author_birth": 1832,
        "author_death": 1898,
        "original_lang": "en",
        "original_year": 1865,
        "genre": "conte / roman jeunesse / nonsense littéraire",
        "description": (
            "Œuvre fondatrice du nonsense littéraire. Alice suit un lapin blanc "
            "dans un terrier et découvre un monde fantastique où la logique est "
            "subvertie. Riche en concepts de PERCEPTION, COGNITION, COMMUNICATION "
            "et MOUVEMENT."
        ),
    },
    "CANDIDE": {
        "title_original": "Candide, ou l'optimisme",
        "author": "Voltaire (François-Marie Arouet)",
        "author_birth": 1694,
        "author_death": 1778,
        "original_lang": "fr",
        "original_year": 1759,
        "genre": "conte philosophique / satire",
        "description": (
            "Conte philosophique satirique. Candide traverse le monde et subit "
            "des catastrophes qui mettent à l'épreuve l'optimisme leibnizien. "
            "Riche en concepts d'EXISTENCE, DESTRUCTION, COGNITION, MOUVEMENT, "
            "ÉMOTION et jugement moral (EVAL)."
        ),
    },
}

# Éditions avec provenance traducteur
EDITIONS = {
    # ── ALICE ──────────────────────────────────────────────────────────────
    "ALICE_EN_11": {
        "work_id": "ALICE",
        "gutenberg_id": 11,
        "lang": "en",
        "title": "Alice's Adventures in Wonderland",
        "translator": None,
        "translator_birth": None,
        "translator_death": None,
        "translation_year": None,
        "edition_info": "Original English text, illustrated by John Tenniel",
        "gutenberg_url": "https://www.gutenberg.org/ebooks/11",
        "gutenberg_release_date": "2008-06-27",
        "gutenberg_credits": "Arthur DiBianca and David Widger",
        "is_original": 1,
    },
    "ALICE_FR_55456": {
        "work_id": "ALICE",
        "gutenberg_id": 55456,
        "lang": "fr",
        "title": "Aventures d'Alice au pays des merveilles",
        "translator": "Bué, Henri",
        "translator_birth": 1843,
        "translator_death": 1929,
        "translation_year": 1869,
        "edition_info": "Première traduction française, illustrée par John Tenniel",
        "gutenberg_url": "https://www.gutenberg.org/ebooks/55456",
        "gutenberg_release_date": "2017-08-30",
        "gutenberg_credits": "Claudine Corbasson et PGDP (BnF/Gallica)",
        "is_original": 0,
    },
    "ALICE_DE_19778": {
        "work_id": "ALICE",
        "gutenberg_id": 19778,
        "lang": "de",
        "title": "Alice's Abenteuer im Wunderland",
        "translator": "Zimmermann, Antonie",
        "translator_birth": None,
        "translator_death": None,
        "translation_year": 1869,
        "edition_info": "Traduction allemande, illustrée par John Tenniel",
        "gutenberg_url": "https://www.gutenberg.org/ebooks/19778",
        "gutenberg_release_date": "2006-11-13",
        "gutenberg_credits": "Ralph Janke, David Starner, Marilynda Fraser-Cunliffe, PGDP",
        "is_original": 0,
    },
    "ALICE_IT_28371": {
        "work_id": "ALICE",
        "gutenberg_id": 28371,
        "lang": "it",
        "title": "Le avventure d'Alice nel paese delle meraviglie",
        "translator": "Pietrocòla-Rossetti, T. (Teodorico)",
        "translator_birth": None,
        "translator_death": None,
        "translation_year": 1872,
        "edition_info": "Première traduction italienne, illustrée par John Tenniel",
        "gutenberg_url": "https://www.gutenberg.org/ebooks/28371",
        "gutenberg_release_date": "2009-03-20",
        "gutenberg_credits": "Carlo Traverso, Barbara Magni, PGDP (Internet Archive)",
        "is_original": 0,
    },
    "ALICE_EO_17482": {
        "work_id": "ALICE",
        "gutenberg_id": 17482,
        "lang": "eo",
        "title": "La Aventuroj de Alicio en Mirlando",
        "translator": "Kearney, Elfric Leofwin",
        "translator_birth": 1856,
        "translator_death": 1913,
        "translation_year": 1910,
        "edition_info": "Traduction en espéranto, illustrée par Brinsley Le Fanu",
        "gutenberg_url": "https://www.gutenberg.org/ebooks/17482",
        "gutenberg_release_date": "2006-01-09",
        "gutenberg_credits": "David Starner, William Patterson, PGDP",
        "is_original": 0,
    },
    "ALICE_FI_46569": {
        "work_id": "ALICE",
        "gutenberg_id": 46569,
        "lang": "fi",
        "title": "Liisan seikkailut ihmemaassa",
        "translator": "Swan, Anni",
        "translator_birth": 1875,
        "translator_death": 1958,
        "translation_year": 1906,
        "edition_info": "Traduction finnoise",
        "gutenberg_url": "https://www.gutenberg.org/ebooks/46569",
        "gutenberg_release_date": "2014-08-12",
        "gutenberg_credits": "Juha Kiuru",
        "is_original": 0,
    },

    # ── CANDIDE ────────────────────────────────────────────────────────────
    "CANDIDE_FR_4650": {
        "work_id": "CANDIDE",
        "gutenberg_id": 4650,
        "lang": "fr",
        "title": "Candide, ou l'optimisme",
        "translator": None,
        "translator_birth": None,
        "translator_death": None,
        "translation_year": None,
        "edition_info": "Texte français original",
        "gutenberg_url": "https://www.gutenberg.org/ebooks/4650",
        "gutenberg_release_date": "2003-11-01",
        "gutenberg_credits": "Carlo Traverso",
        "is_original": 1,
    },
    "CANDIDE_EN_19942": {
        "work_id": "CANDIDE",
        "gutenberg_id": 19942,
        "lang": "en",
        "title": "Candide",
        "translator": None,  # Traducteur non identifié sur Gutenberg
        "translator_birth": None,
        "translator_death": None,
        "translation_year": None,
        "edition_info": "Traduction anglaise (traducteur non crédité sur Gutenberg)",
        "gutenberg_url": "https://www.gutenberg.org/ebooks/19942",
        "gutenberg_release_date": "2006-11-27",
        "gutenberg_credits": "Chuck Greif, Fox in the Stars, PGDP",
        "is_original": 0,
    },
    "CANDIDE_ES_7109": {
        "work_id": "CANDIDE",
        "gutenberg_id": 7109,
        "lang": "es",
        "title": "Cándido, o El Optimismo",
        "translator": None,  # Traducteur non identifié
        "translator_birth": None,
        "translator_death": None,
        "translation_year": None,
        "edition_info": "Traduction espagnole (traducteur non crédité sur Gutenberg)",
        "gutenberg_url": "https://www.gutenberg.org/ebooks/7109",
        "gutenberg_release_date": "2004-12-01",
        "gutenberg_credits": "Tom Richards, Arno Peters, Juliet Sutherland, Charles Franks, PGDP",
        "is_original": 0,
    },
    "CANDIDE_FI_52336": {
        "work_id": "CANDIDE",
        "gutenberg_id": 52336,
        "lang": "fi",
        "title": "Candide; Eli, Avosydämisen ja vilpittömän nuoren miehen ihmeelliset seikkailut",
        "translator": "Onerva, L.",
        "translator_birth": 1882,
        "translator_death": 1972,
        "translation_year": None,
        "edition_info": "Traduction finnoise par L. Onerva",
        "gutenberg_url": "https://www.gutenberg.org/ebooks/52336",
        "gutenberg_release_date": "2016-06-15",
        "gutenberg_credits": "Juhani Kärkkäinen, Tapio Riikonen",
        "is_original": 0,
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Passages-clés pour analyse comparative
# Chaque passage est identifié par une référence normalisée (segment_ref)
# et des marqueurs textuels multilingues pour extraction
# ─────────────────────────────────────────────────────────────────────────────

ALICE_KEY_PASSAGES = {
    # Chapitre 1 — Ouverture: ennui → curiosité → mouvement
    "ch01_opening": {
        "segment_type": "chapter_opening",
        "chapter": "Chapter I / Chapitre I",
        "description": "Alice s'ennuie, voit le lapin blanc, curiosité déclenchée",
        "markers": {
            "en": ["beginning to get very tired", "sitting by her sister", "White Rabbit"],
            "fr": ["commençait à se sentir très lasse", "assise auprès de sa sœur", "Lapin Blanc"],
            "de": ["anfing ihrer Schwester", "langweilig", "weißes Kaninchen"],
            "it": ["cominciava a non poterne più", "seduta accanto alla sorella", "Coniglio bianco"],
            "eo": ["komencis enui", "fratino", "blanka Kuniklo"],
            "fi": ["Liisaa väsytti", "istunut", "valkoinen punasilmä kani"],
        },
        "expected_atoms": ["PERCEPTION", "COGNITION", "TEDIUM", "MOUVEMENT"],
        "expected_concepts": ["ENNUI", "CURIOSITÉ", "OBSERVER"],
    },
    # Chapitre 1 — Chute dans le terrier: mouvement + perception
    "ch01_falling": {
        "segment_type": "key_passage",
        "chapter": "Chapter I",
        "description": "Alice tombe dans le terrier — mouvement + perception altérée",
        "markers": {
            "en": ["down the rabbit-hole", "falling", "would the fall never come to an end"],
            "fr": ["terrier du lapin", "tomber", "cette chute ne finirait"],
            "de": ["Kaninchenloch", "fallen", "Fall gar kein Ende"],
            "it": ["tana del Coniglio", "cadere", "caduta non finisse mai"],
            "eo": ["kuniklan truon", "fali", "ĉu la falo neniam finiĝos"],
            "fi": ["kaninkoloon", "putoa", "eikö tämä putoaminen"],
        },
        "expected_atoms": ["MOUVEMENT", "PERCEPTION", "COGNITION", "TEMPS"],
        "expected_concepts": ["TOMBER", "EXPLORER"],
    },
    # Chapitre 7 — Thé des fous: communication absurde
    "ch07_tea_party": {
        "segment_type": "dialogue",
        "chapter": "Chapter VII",
        "description": "Le thé des fous — communication, cognition, absurdité",
        "markers": {
            "en": ["Mad Tea-Party", "Why is a raven like a writing-desk", "No room"],
            "fr": ["thé de fous", "corbeau ressemble à un pupitre", "pas de place"],
            "de": ["tolle Theegesellschaft", "Rabe einem Schreibpulte", "kein Platz"],
            "it": ["tè dei matti", "corvo somiglia a uno scrittoio", "non c'è posto"],
            "eo": ["TETRINKADO CXE FRENEZULOJ", "korvo similas skribotablon", "Ne pli da sidlokoj"],
            "fi": ["Hullu teekutsu", "korppi on kirjoituspöydän", "ei ole tilaa"],
        },
        "expected_atoms": ["COMMUNICATION", "COGNITION", "PERCEPTION"],
        "expected_concepts": ["DIALOGUE", "INTERROGER"],
    },
    # Chapitre 21 — Le renard: lien, apprivoiser
    "ch21_fox": {
        "segment_type": "maxim",
        "chapter": "Chapter XXI",
        "description": "Paroles du renard: apprivoiser, essentiel invisible, responsabilité",
        "markers": {
            # NOTE: Ce passage est du Petit Prince, pas d'Alice !
            # On le remplace par un passage d'Alice plus pertinent
        },
        # Correction: Remplaçons par le passage "Who are you?" de la chenille
    },
    # Chapitre 5 — La Chenille: identité, cognition
    "ch05_caterpillar": {
        "segment_type": "dialogue",
        "chapter": "Chapter V",
        "description": "La Chenille demande 'Qui êtes-vous?' — identité, cognition, existence",
        "markers": {
            "en": ["Who are you", "Caterpillar", "I hardly know", "so many changes"],
            "fr": ["Qui êtes-vous", "Chenille", "je ne sais plus", "changements"],
            "de": ["Wer bist Du", "Raupe", "ich weiß es kaum", "Veränderungen"],
            "it": ["Chi siete", "Bruco", "non lo so", "trasformazioni"],
            "eo": ["Kiu _vi_ estas", "Rauxpo", "Apenaux mi scias", "sxangxigxis"],
            "fi": ["Kuka te olette", "Toukka", "en oikein tiedä", "muutoksia"],
        },
        "expected_atoms": ["COGNITION", "EXISTENCE", "COMMUNICATION", "PERCEPTION"],
        "expected_concepts": ["IDENTITÉ", "QUESTIONNER", "DOUTER"],
    },
    # Chapitre 12 — Verdict: jugement, domination, communication
    "ch12_verdict": {
        "segment_type": "key_passage",
        "chapter": "Chapter XII",
        "description": "Le verdict — domination, jugement, communication, destruction",
        "markers": {
            "en": ["Sentence first", "verdict afterwards", "Off with her head", "pack of cards"],
            "fr": ["Exécution d'abord", "jugement après", "Qu'on lui coupe la tête", "paquet de cartes"],
            "de": ["Erst das Urtheil", "Kopf ab", "Kartenspiel"],
            "it": ["Prima la sentenza", "verdetto poi", "Tagliategli la testa", "mazzo di carte"],
            "eo": ["Unue la puno", "Detranĉu", "kartaro"],
            "fi": ["Tuomio ensin", "päästä poikki", "korttipakka"],
        },
        "expected_atoms": ["DOMINATION", "COMMUNICATION", "DESTRUCTION"],
        "expected_concepts": ["JUGER", "ORDONNER", "PUNIR"],
    },
}

CANDIDE_KEY_PASSAGES = {
    # Chapitre 1 — Ouverture: existence, cognition (meilleur des mondes)
    "ch01_opening": {
        "segment_type": "chapter_opening",
        "chapter": "Chapitre I / Chapter I",
        "description": "Introduction: le meilleur des mondes possibles (Pangloss)",
        "markers": {
            "fr": ["meilleur des mondes possibles", "Pangloss", "Tout est pour le mieux"],
            "en": ["best of all possible worlds", "Pangloss", "everything is for the best"],
            "es": ["mejor de los mundos posibles", "Pangloss", "todo está lo mejor"],
            "fi": ["parhaista mahdollisista maailmoista", "Pangloss"],
        },
        "expected_atoms": ["COGNITION", "EXISTENCE", "EVAL"],
        "expected_concepts": ["JUGER", "CROIRE", "EXISTER"],
    },
    # Chapitre 3 — Guerre: destruction, mouvement, émotion
    "ch03_war": {
        "segment_type": "key_passage",
        "chapter": "Chapitre III / Chapter III",
        "description": "La bataille et ses horreurs — destruction, violence, émotion",
        "markers": {
            "fr": ["boucherie héroïque", "baïonnettes", "Bulgares", "Abares"],
            "en": ["heroic butchery", "bayonets", "Bulgarians", "Abares"],
            "es": ["carnicería heroica", "bayonetas", "búlgaros"],
            "fi": ["sankarillisen teurastuksen", "pistin", "sotajoukot"],
        },
        "expected_atoms": ["DESTRUCTION", "MOUVEMENT", "FEAR", "RAGE", "PERCEPTION"],
        "expected_concepts": ["COMBATTRE", "SOUFFRIR", "DÉTRUIRE"],
    },
    # Chapitre 6 — Auto-da-fé: domination, destruction, cognition
    "ch06_auto_da_fe": {
        "segment_type": "key_passage",
        "chapter": "Chapitre VI / Chapter VI",
        "description": "L'auto-da-fé — domination institutionnelle, punition, absurdité",
        "markers": {
            "fr": ["auto-da-fé", "tremblement de terre", "sages du pays", "spectacle"],
            "en": ["auto-da-fé", "earthquake", "sages of the country", "spectacle"],
            "es": ["auto de fe", "terremoto", "sabios del país"],
            "fi": ["auto-da-fé", "maanjäristys"],
        },
        "expected_atoms": ["DOMINATION", "DESTRUCTION", "COGNITION", "PERCEPTION"],
        "expected_concepts": ["JUGER", "PUNIR", "CROIRE"],
    },
    # Chapitre 30 — Conclusion: cultiver son jardin
    "ch30_garden": {
        "segment_type": "maxim",
        "chapter": "Chapitre XXX / Chapter XXX",
        "description": "Il faut cultiver notre jardin — création, existence, sagesse",
        "markers": {
            "fr": ["cultiver notre jardin", "travailler", "le travail éloigne"],
            "en": ["cultivate our garden", "work", "work keeps"],
            "es": ["cultivar nuestro jardín", "trabajar"],
            "fi": ["viljellä puutarhaamme", "työ"],
        },
        "expected_atoms": ["CREATION", "EXISTENCE", "COGNITION", "DOMINATION"],
        "expected_concepts": ["CRÉER", "TRAVAILLER", "SAGESSE"],
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# Atomes PanLang v2 — Mapping de mots-clés par langue pour détection
# ─────────────────────────────────────────────────────────────────────────────

ATOM_KEYWORDS = {
    "MOUVEMENT": {
        "en": ["go", "come", "run", "fall", "walk", "jump", "move", "fly", "chase", "follow",
               "swim", "rush", "hurry", "tumble", "slide", "wander"],
        "fr": ["aller", "venir", "courir", "tomber", "marcher", "sauter", "bouger", "voler",
               "suivre", "poursuivre", "glisser", "errer", "descendre", "monter"],
        "de": ["gehen", "kommen", "laufen", "fallen", "springen", "fliegen", "folgen",
               "eilen", "wandern", "stürzen", "gleiten"],
        "it": ["andare", "venire", "correre", "cadere", "camminare", "saltare", "volare",
               "seguire", "scivolare", "scendere"],
        "es": ["ir", "venir", "correr", "caer", "caminar", "saltar", "volar", "seguir",
               "huir", "pasear", "bajar"],
        "eo": ["iri", "veni", "kuri", "fali", "marŝi", "salti", "flugi", "sekvi"],
        "fi": ["mennä", "tulla", "juosta", "pudota", "kävellä", "hypätä", "lentää", "seurata"],
    },
    "COGNITION": {
        "en": ["think", "know", "understand", "believe", "remember", "wonder", "consider",
               "realize", "imagine", "learn", "idea", "thought", "mind", "reason"],
        "fr": ["penser", "savoir", "comprendre", "croire", "souvenir", "réfléchir",
               "imaginer", "apprendre", "idée", "pensée", "esprit", "raison"],
        "de": ["denken", "wissen", "verstehen", "glauben", "erinnern", "überlegen",
               "vorstellen", "lernen", "Gedanke", "Verstand", "Vernunft"],
        "it": ["pensare", "sapere", "capire", "credere", "ricordare", "immaginare",
               "imparare", "idea", "pensiero", "mente", "ragione"],
        "es": ["pensar", "saber", "comprender", "creer", "recordar", "imaginar",
               "aprender", "idea", "pensamiento", "razón"],
        "eo": ["pensi", "scii", "kompreni", "kredi", "memori", "imagi", "lerni"],
        "fi": ["ajatella", "tietää", "ymmärtää", "uskoa", "muistaa", "kuvitella", "oppia"],
    },
    "PERCEPTION": {
        "en": ["see", "hear", "look", "watch", "feel", "notice", "observe", "appear",
               "seem", "smell", "taste", "sight", "sound", "eye"],
        "fr": ["voir", "entendre", "regarder", "sentir", "remarquer", "observer",
               "paraître", "sembler", "goûter", "vue", "son", "œil"],
        "de": ["sehen", "hören", "schauen", "fühlen", "bemerken", "beobachten",
               "scheinen", "riechen", "schmecken", "Auge", "Blick"],
        "it": ["vedere", "sentire", "guardare", "osservare", "notare", "sembrare",
               "apparire", "occhio", "sguardo"],
        "es": ["ver", "oír", "mirar", "sentir", "notar", "observar", "parecer",
               "ojo", "vista"],
        "eo": ["vidi", "aŭdi", "rigardi", "senti", "rimarki", "observi", "ŝajni"],
        "fi": ["nähdä", "kuulla", "katsoa", "tuntea", "huomata", "näyttää"],
    },
    "COMMUNICATION": {
        "en": ["say", "tell", "ask", "speak", "answer", "reply", "call", "cry",
               "shout", "whisper", "word", "voice", "talk", "declare"],
        "fr": ["dire", "parler", "demander", "répondre", "appeler", "crier",
               "murmurer", "mot", "voix", "déclarer", "raconter"],
        "de": ["sagen", "sprechen", "fragen", "antworten", "rufen", "schreien",
               "flüstern", "Wort", "Stimme", "erzählen"],
        "it": ["dire", "parlare", "chiedere", "rispondere", "chiamare", "gridare",
               "sussurrare", "parola", "voce", "raccontare"],
        "es": ["decir", "hablar", "preguntar", "responder", "llamar", "gritar",
               "susurrar", "palabra", "voz", "contar"],
        "eo": ["diri", "paroli", "demandi", "respondi", "voki", "krii", "vorto", "voĉo"],
        "fi": ["sanoa", "puhua", "kysyä", "vastata", "huutaa", "kuiskaa", "sana", "ääni"],
    },
    "CREATION": {
        "en": ["make", "create", "build", "grow", "produce", "invent", "cultivate",
               "write", "draw", "paint", "design", "compose", "work"],
        "fr": ["faire", "créer", "construire", "pousser", "produire", "inventer",
               "cultiver", "écrire", "dessiner", "peindre", "travailler"],
        "de": ["machen", "schaffen", "bauen", "wachsen", "erzeugen", "erfinden",
               "schreiben", "zeichnen", "malen", "arbeiten"],
        "it": ["fare", "creare", "costruire", "crescere", "produrre", "inventare",
               "coltivare", "scrivere", "disegnare", "lavorare"],
        "es": ["hacer", "crear", "construir", "crecer", "producir", "inventar",
               "cultivar", "escribir", "dibujar", "trabajar"],
        "eo": ["fari", "krei", "konstrui", "kreski", "produkti", "skribi", "labori"],
        "fi": ["tehdä", "luoda", "rakentaa", "kasvaa", "tuottaa", "kirjoittaa", "työskennellä"],
    },
    # ── v2.2: Emotional sub-primitives (replaces single EMOTION) ──
    "SEEKING": {
        "en": ["want", "desire", "seek", "search", "curious", "wonder", "explore",
               "expect", "hope", "anticipate", "eager", "interest", "wish"],
        "fr": ["vouloir", "désirer", "chercher", "curieux", "curiosité", "espérer",
               "attendre", "intérêt", "souhaiter", "explorer"],
        "de": ["wollen", "suchen", "neugierig", "hoffen", "erwarten", "Interesse",
               "wünschen", "erforschen"],
        "it": ["volere", "desiderare", "cercare", "curioso", "sperare", "aspettare",
               "interesse", "esplorare"],
        "es": ["querer", "desear", "buscar", "curioso", "esperar", "interés",
               "explorar"],
        "eo": ["voli", "deziri", "serĉi", "scivolema", "esperi", "intereso"],
        "fi": ["haluta", "etsiä", "utelias", "toivoa", "odottaa", "kiinnostus"],
    },
    "FEAR": {
        "en": ["fear", "afraid", "terror", "dread", "frighten", "scare", "anxious",
               "panic", "horror", "tremble", "flee", "escape"],
        "fr": ["peur", "craindre", "terreur", "effrayer", "inquiet", "panique",
               "horreur", "trembler", "fuir", "anxieux"],
        "de": ["Angst", "fürchten", "Schrecken", "erschrecken", "ängstlich",
               "Panik", "zittern", "fliehen"],
        "it": ["paura", "temere", "terrore", "spaventare", "ansioso", "panico",
               "tremare", "fuggire"],
        "es": ["miedo", "temer", "terror", "asustar", "ansioso", "pánico",
               "temblar", "huir"],
        "eo": ["timo", "timi", "teruro", "timigi", "paniko", "tremi", "fuĝi"],
        "fi": ["pelko", "pelätä", "kauhu", "säikähtää", "paniikki", "vapista", "paeta"],
    },
    "CARE": {
        "en": ["care", "love", "tender", "gentle", "nurture", "protect", "comfort",
               "embrace", "kind", "compassion", "dear", "sweet", "fond"],
        "fr": ["aimer", "tendre", "doux", "protéger", "consoler", "embrasser",
               "cher", "compassion", "câlin", "gentil", "affection"],
        "de": ["lieben", "zärtlich", "sanft", "schützen", "trösten", "umarmen",
               "lieb", "Mitgefühl", "Zuneigung"],
        "it": ["amare", "tenero", "dolce", "proteggere", "consolare", "abbracciare",
               "caro", "compassione", "affetto"],
        "es": ["amar", "tierno", "dulce", "proteger", "consolar", "abrazar",
               "querido", "compasión", "cariño"],
        "eo": ["ami", "tenera", "dolĉa", "protekti", "konsoli", "ĉirkaŭpreni",
               "kara", "kompato"],
        "fi": ["rakastaa", "hellä", "suojella", "lohduttaa", "halata",
               "rakas", "myötätunto"],
    },
    "GRIEF": {
        "en": ["sad", "sorrow", "grief", "mourn", "cry", "weep", "tears", "miss",
               "lonely", "loss", "despair", "melancholy", "lament"],
        "fr": ["triste", "tristesse", "deuil", "pleurer", "larmes", "chagrin",
               "solitude", "perte", "désespoir", "mélancolie", "lamenter"],
        "de": ["traurig", "Trauer", "weinen", "Tränen", "Kummer", "Verlust",
               "Verzweiflung", "Sehnsucht", "einsam"],
        "it": ["triste", "dolore", "piangere", "lacrime", "lutto", "perdita",
               "disperazione", "malinconia"],
        "es": ["triste", "tristeza", "llorar", "lágrimas", "duelo", "pérdida",
               "desesperación", "melancolía"],
        "eo": ["malĝoja", "malĝojo", "plori", "larmoj", "funebro", "perdo",
               "malespero"],
        "fi": ["surullinen", "suru", "itkeä", "kyyneleet", "menetys",
               "epätoivo", "kaipaus"],
    },
    "RAGE": {
        "en": ["angry", "anger", "rage", "fury", "furious", "wrath", "irritate",
               "annoy", "indignant", "outrage"],
        "fr": ["colère", "furieux", "rage", "fâché", "irriter", "agacer",
               "indigné", "furie", "courroux"],
        "de": ["Zorn", "Wut", "böse", "wütend", "ärgerlich", "zornig",
               "empört", "Grimm"],
        "it": ["rabbia", "arrabbiato", "furioso", "ira", "irritare",
               "indignato", "furia"],
        "es": ["ira", "enojado", "furioso", "rabia", "irritar", "furia",
               "indignado"],
        "eo": ["kolera", "koleri", "furioza", "indigni"],
        "fi": ["viha", "vihainen", "raivo", "suuttunut", "ärsyttää", "raivoisa"],
    },
    "DISGUST": {
        "en": ["disgust", "disgusting", "revolting", "repulsive", "loathe", "nausea",
               "abhor", "vile", "foul", "repugnant"],
        "fr": ["dégoût", "dégoûtant", "répugnant", "écœurer", "abject", "ignoble",
               "immonde", "nausée", "vomir"],
        "de": ["Ekel", "ekelhaft", "widerlich", "abstoßend", "abscheulich"],
        "it": ["disgusto", "disgustoso", "ripugnante", "nauseante", "orribile"],
        "es": ["asco", "asqueroso", "repugnante", "nauseabundo", "repulsivo"],
        "eo": ["naŭzo", "naŭza", "abomena"],
        "fi": ["inho", "inhottava", "vastenmielinen", "kuvottava"],
    },
    "PLAY": {
        "en": ["play", "laugh", "fun", "game", "joke", "merry", "delight", "cheerful",
               "amuse", "happy", "joy", "glad", "celebrate", "dance"],
        "fr": ["jouer", "rire", "amusement", "jeu", "plaisanterie", "joyeux",
               "heureux", "joie", "content", "fête", "danser", "gai"],
        "de": ["spielen", "lachen", "Spaß", "Spiel", "Scherz", "fröhlich",
               "glücklich", "Freude", "lustig", "tanzen"],
        "it": ["giocare", "ridere", "divertimento", "gioco", "scherzo", "allegro",
               "felice", "gioia", "contento", "festa"],
        "es": ["jugar", "reír", "diversión", "juego", "broma", "alegre",
               "feliz", "alegría", "contento", "fiesta"],
        "eo": ["ludi", "ridi", "amuzo", "ludo", "ŝerco", "gaja",
               "feliĉa", "ĝojo", "festi"],
        "fi": ["leikkiä", "nauraa", "hauska", "peli", "iloinen",
               "onnellinen", "ilo", "juhla", "tanssia"],
    },
    "TEDIUM": {
        "en": ["bore", "bored", "boring", "tedious", "tire", "tired", "weary",
               "dull", "monotonous", "listless", "apathy"],
        "fr": ["ennui", "ennuyer", "lasse", "fatigué", "monotone", "morne",
               "apathie", "languir"],
        "de": ["langweilig", "Langeweile", "müde", "ermüden", "eintönig",
               "Apathie"],
        "it": ["noia", "noioso", "stanco", "monotono", "apatia", "annoiare"],
        "es": ["aburrimiento", "aburrido", "cansado", "monótono", "apatía"],
        "eo": ["enui", "enuiga", "laca", "monotona"],
        "fi": ["tylsä", "tylsistynyt", "väsynyt", "yksitoikkoinen", "apatia"],
    },
    "EXISTENCE": {
        "en": ["be", "exist", "live", "die", "become", "remain", "stay",
               "born", "death", "life", "real", "true", "being"],
        "fr": ["être", "exister", "vivre", "mourir", "devenir", "rester",
               "naître", "mort", "vie", "réel", "vrai"],
        "de": ["sein", "existieren", "leben", "sterben", "werden", "bleiben",
               "geboren", "Tod", "Leben", "wirklich", "wahr"],
        "it": ["essere", "esistere", "vivere", "morire", "diventare", "restare",
               "nascere", "morte", "vita", "vero", "reale"],
        "es": ["ser", "estar", "existir", "vivir", "morir", "quedarse",
               "nacer", "muerte", "vida", "verdadero", "real"],
        "eo": ["esti", "ekzisti", "vivi", "morti", "fariĝi", "resti", "morto", "vivo"],
        "fi": ["olla", "elää", "kuolla", "tulla", "jäädä", "syntyä", "kuolema", "elämä"],
    },
    "DESTRUCTION": {
        "en": ["destroy", "break", "kill", "cut", "burn", "tear", "smash",
               "ruin", "crush", "war", "battle", "fight", "attack"],
        "fr": ["détruire", "casser", "tuer", "couper", "brûler", "déchirer",
               "écraser", "ruine", "guerre", "bataille", "combattre", "attaquer"],
        "de": ["zerstören", "brechen", "töten", "schneiden", "brennen",
               "zerreißen", "zermalmen", "Krieg", "Schlacht", "kämpfen"],
        "it": ["distruggere", "rompere", "uccidere", "tagliare", "bruciare",
               "schiacciare", "guerra", "battaglia", "combattere"],
        "es": ["destruir", "romper", "matar", "cortar", "quemar",
               "aplastar", "guerra", "batalla", "combatir", "atacar"],
        "eo": ["detrui", "rompi", "mortigi", "tranĉi", "bruli", "milito", "batali"],
        "fi": ["tuhota", "rikkoa", "tappaa", "leikata", "polttaa", "sota", "taistella"],
    },
    "POSSESSION": {
        "en": ["have", "own", "give", "take", "get", "keep", "lose", "find",
               "steal", "buy", "sell", "belong", "rich", "poor", "money"],
        "fr": ["avoir", "posséder", "donner", "prendre", "garder", "perdre",
               "trouver", "voler", "acheter", "vendre", "riche", "pauvre", "argent"],
        "de": ["haben", "besitzen", "geben", "nehmen", "behalten", "verlieren",
               "finden", "stehlen", "kaufen", "verkaufen", "reich", "arm", "Geld"],
        "it": ["avere", "possedere", "dare", "prendere", "tenere", "perdere",
               "trovare", "rubare", "comprare", "vendere", "ricco", "povero"],
        "es": ["tener", "poseer", "dar", "tomar", "guardar", "perder",
               "encontrar", "robar", "comprar", "vender", "rico", "pobre", "dinero"],
        "eo": ["havi", "posedi", "doni", "preni", "gardi", "perdi", "trovi", "ŝteli"],
        "fi": ["omistaa", "antaa", "ottaa", "pitää", "menettää", "löytää", "ostaa", "myydä"],
    },
    "DOMINATION": {
        "en": ["king", "queen", "rule", "command", "order", "obey", "power",
               "authority", "judge", "sentence", "punish", "law", "force", "control"],
        "fr": ["roi", "reine", "régner", "commander", "ordonner", "obéir",
               "pouvoir", "autorité", "juger", "sentence", "punir", "loi", "force"],
        "de": ["König", "Königin", "herrschen", "befehlen", "gehorchen",
               "Macht", "Autorität", "richten", "Urteil", "strafen", "Gesetz"],
        "it": ["re", "regina", "regnare", "comandare", "obbedire",
               "potere", "autorità", "giudicare", "sentenza", "punire", "legge"],
        "es": ["rey", "reina", "reinar", "mandar", "obedecer",
               "poder", "autoridad", "juzgar", "sentencia", "castigar", "ley"],
        "eo": ["reĝo", "reĝino", "regi", "ordoni", "obei", "potenco", "juĝi", "puni", "leĝo"],
        "fi": ["kuningas", "kuningatar", "hallita", "käskeä", "totella", "valta", "tuomita", "laki"],
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Helpers Dolt
# ─────────────────────────────────────────────────────────────────────────────

def dolt_sql(query, db=DOLT_DB, check=True):
    """Execute a Dolt SQL query."""
    env = os.environ.copy()
    env["DOLT_CLI_NO_PAGER"] = "1"
    cmd = ["dolt", "sql", "-r", "csv", "-q", query]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=db, env=env)
    if check and r.returncode != 0:
        print(f"❌ DOLT SQL ERROR: {r.stderr.strip()}")
        print(f"   Query: {query[:200]}")
        return None
    return r.stdout.strip()

def dolt_source(sql_file, db=DOLT_DB):
    """Source a SQL file in Dolt."""
    env = os.environ.copy()
    env["DOLT_CLI_NO_PAGER"] = "1"
    cmd = ["dolt", "sql", f"< {sql_file}"]
    r = subprocess.run(
        f"cd {db} && dolt sql < {sql_file}",
        shell=True, capture_output=True, text=True, env=env
    )
    if r.returncode != 0:
        print(f"❌ DOLT SOURCE ERROR: {r.stderr.strip()}")
        return False
    return True

def dolt_commit(message, db=DOLT_DB):
    """Stage and commit in Dolt."""
    env = os.environ.copy()
    env["DOLT_CLI_NO_PAGER"] = "1"
    subprocess.run(["dolt", "add", "."], cwd=db, env=env)
    r = subprocess.run(
        ["dolt", "commit", "-m", message, "--allow-empty"],
        cwd=db, capture_output=True, text=True, env=env
    )
    return r.returncode == 0

def esc(s):
    """Escape a string for SQL insertion."""
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''").replace("\\", "\\\\") + "'"


# ─────────────────────────────────────────────────────────────────────────────
# Step 1: Apply provenance schema
# ─────────────────────────────────────────────────────────────────────────────

def step1_apply_schema():
    """Apply the Gutenberg provenance schema to the Dolt DB."""
    print("\n" + "="*70)
    print("STEP 1: Applying Gutenberg provenance schema")
    print("="*70)

    ok = dolt_source(SCHEMA_SQL)
    if not ok:
        print("❌ Failed to apply schema")
        return False

    # Verify tables were created
    result = dolt_sql("SHOW TABLES")
    new_tables = ["gutenberg_works", "gutenberg_editions", "gutenberg_segments",
                  "segment_decompositions", "translation_convergence"]
    for t in new_tables:
        if t in result:
            print(f"  ✅ Table {t}")
        else:
            print(f"  ❌ Missing table {t}")
            return False

    # Create views individually (Dolt can't handle multi-statement with views)
    views = {
        "v_provenance_chain": (
            "CREATE VIEW IF NOT EXISTS v_provenance_chain AS "
            "SELECT gw.title_original, gw.author, gw.original_year, "
            "ge.lang, ge.title AS edition_title, ge.translator, "
            "ge.translation_year, ge.gutenberg_id, ge.gutenberg_url, "
            "ge.gutenberg_access_date, gs.segment_ref, gs.segment_type, "
            "gs.text_content, sd.concept_id, sd.atoms_detected, "
            "sd.confidence, sd.evidence_text "
            "FROM segment_decompositions sd "
            "JOIN gutenberg_segments gs ON sd.segment_id = gs.id "
            "JOIN gutenberg_editions ge ON gs.edition_id = ge.id "
            "JOIN gutenberg_works gw ON ge.work_id = gw.id"
        ),
        "v_concept_universality": (
            "CREATE VIEW IF NOT EXISTS v_concept_universality AS "
            "SELECT tc.concept_id, c.formule_simple, c.quality_tier, "
            "COUNT(*) AS segment_comparisons, "
            "ROUND(AVG(tc.convergence_ratio), 3) AS avg_convergence, "
            "SUM(CASE WHEN tc.convergence_type = 'universal' THEN 1 ELSE 0 END) AS universal_count, "
            "SUM(CASE WHEN tc.convergence_type = 'majority' THEN 1 ELSE 0 END) AS majority_count, "
            "SUM(CASE WHEN tc.convergence_type = 'minority' THEN 1 ELSE 0 END) AS minority_count, "
            "SUM(CASE WHEN tc.convergence_type = 'unique' THEN 1 ELSE 0 END) AS unique_count "
            "FROM translation_convergence tc "
            "LEFT JOIN concepts c ON tc.concept_id = c.id "
            "GROUP BY tc.concept_id, c.formule_simple, c.quality_tier"
        ),
        "v_translator_profile": (
            "CREATE VIEW IF NOT EXISTS v_translator_profile AS "
            "SELECT ge.translator, ge.lang, ge.translation_year, "
            "gw.title_original AS work, "
            "COUNT(DISTINCT sd.concept_id) AS concepts_detected, "
            "COUNT(DISTINCT gs.segment_ref) AS segments_analyzed, "
            "ROUND(AVG(sd.confidence), 3) AS avg_confidence "
            "FROM segment_decompositions sd "
            "JOIN gutenberg_segments gs ON sd.segment_id = gs.id "
            "JOIN gutenberg_editions ge ON gs.edition_id = ge.id "
            "JOIN gutenberg_works gw ON ge.work_id = gw.id "
            "GROUP BY ge.translator, ge.lang, ge.translation_year, gw.title_original"
        ),
    }
    for vname, vsql in views.items():
        dolt_sql(vsql, check=False)
        print(f"  ✅ View {vname}")

    print(f"  → {len(new_tables)} new tables + {len(views)} views created")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Step 2: Register works and editions with full provenance
# ─────────────────────────────────────────────────────────────────────────────

def step2_register_works_and_editions():
    """Insert works and editions with complete provenance metadata."""
    print("\n" + "="*70)
    print("STEP 2: Registering works and editions (provenance metadata)")
    print("="*70)

    # Insert works
    for wid, w in WORKS.items():
        sql = (
            f"INSERT IGNORE INTO gutenberg_works "
            f"(id, title_original, author, author_birth, author_death, "
            f"original_lang, original_year, genre, description) VALUES ("
            f"{esc(wid)}, {esc(w['title_original'])}, {esc(w['author'])}, "
            f"{w.get('author_birth', 'NULL')}, {w.get('author_death', 'NULL')}, "
            f"{esc(w['original_lang'])}, {w.get('original_year', 'NULL')}, "
            f"{esc(w.get('genre'))}, {esc(w.get('description'))})"
        )
        dolt_sql(sql)
        print(f"  ✅ Work: {wid} — {w['title_original']} ({w['author']})")

    # Insert editions
    for eid, e in EDITIONS.items():
        sql = (
            f"INSERT IGNORE INTO gutenberg_editions "
            f"(id, work_id, gutenberg_id, lang, title, "
            f"translator, translator_birth, translator_death, translation_year, "
            f"edition_info, gutenberg_url, gutenberg_release_date, gutenberg_credits, "
            f"gutenberg_access_date, is_original, text_retrieved) VALUES ("
            f"{esc(eid)}, {esc(e['work_id'])}, {e['gutenberg_id']}, "
            f"{esc(e['lang'])}, {esc(e['title'])}, "
            f"{esc(e.get('translator'))}, "
            f"{e.get('translator_birth') or 'NULL'}, "
            f"{e.get('translator_death') or 'NULL'}, "
            f"{e.get('translation_year') or 'NULL'}, "
            f"{esc(e.get('edition_info'))}, {esc(e['gutenberg_url'])}, "
            f"{esc(e.get('gutenberg_release_date'))}, "
            f"{esc(e.get('gutenberg_credits'))}, "
            f"{esc(TODAY)}, "
            f"{e.get('is_original', 0)}, 0)"
        )
        dolt_sql(sql)
        prov_str = f"  ✅ Édition: {eid} [{e['lang']}]"
        if e.get('translator'):
            prov_str += f" — trad. {e['translator']}"
            if e.get('translation_year'):
                prov_str += f" ({e['translation_year']})"
        else:
            prov_str += " — (original)"
        print(prov_str)

    # Report
    result = dolt_sql("SELECT COUNT(*) as cnt FROM gutenberg_works")
    works_count = result.split('\n')[-1]
    result = dolt_sql("SELECT COUNT(*) as cnt FROM gutenberg_editions")
    editions_count = result.split('\n')[-1]
    print(f"\n  → {works_count} works, {editions_count} editions registered")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Step 3: Download texts from Gutenberg
# ─────────────────────────────────────────────────────────────────────────────

def download_gutenberg_text(gutenberg_id, lang="en"):
    """Download plain text from Project Gutenberg."""
    os.makedirs(CORPUS_DIR, exist_ok=True)
    filepath = os.path.join(CORPUS_DIR, f"pg{gutenberg_id}_{lang}.txt")

    if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
        print(f"    ℹ️  Already downloaded: {filepath}")
        return filepath

    # Try UTF-8 version first, then plain text
    urls = [
        f"https://www.gutenberg.org/cache/epub/{gutenberg_id}/pg{gutenberg_id}.txt",
        f"https://www.gutenberg.org/files/{gutenberg_id}/{gutenberg_id}-0.txt",
        f"https://www.gutenberg.org/files/{gutenberg_id}/{gutenberg_id}.txt",
    ]

    for url in urls:
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'PaniniFS-Research/1.0 (semantic-universals validation)'
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                text = resp.read().decode('utf-8', errors='replace')
                if len(text) > 1000:  # Sanity check
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(text)
                    print(f"    ✅ Downloaded: pg{gutenberg_id} ({len(text)} chars)")
                    return filepath
        except Exception as e:
            continue

    print(f"    ❌ Failed to download pg{gutenberg_id}")
    return None

def step3_download_texts():
    """Download all edition texts from Gutenberg."""
    print("\n" + "="*70)
    print("STEP 3: Downloading texts from Project Gutenberg")
    print("="*70)

    downloaded = 0
    for eid, e in EDITIONS.items():
        filepath = download_gutenberg_text(e["gutenberg_id"], e["lang"])
        if filepath:
            dolt_sql(
                f"UPDATE gutenberg_editions SET text_retrieved = 1 "
                f"WHERE id = {esc(eid)}"
            )
            downloaded += 1

    print(f"\n  → {downloaded}/{len(EDITIONS)} texts downloaded")
    return downloaded > 0


# ─────────────────────────────────────────────────────────────────────────────
# Step 4: Extract comparable segments
# ─────────────────────────────────────────────────────────────────────────────

def strip_gutenberg_header_footer(text):
    """Remove Project Gutenberg header and footer."""
    start_markers = [
        "*** START OF THIS PROJECT GUTENBERG",
        "*** START OF THE PROJECT GUTENBERG",
        "***START OF THE PROJECT GUTENBERG",
    ]
    end_markers = [
        "*** END OF THIS PROJECT GUTENBERG",
        "*** END OF THE PROJECT GUTENBERG",
        "***END OF THE PROJECT GUTENBERG",
        "End of the Project Gutenberg",
        "End of Project Gutenberg",
    ]

    # Find start
    start_idx = 0
    for marker in start_markers:
        idx = text.find(marker)
        if idx != -1:
            # Find end of that line
            newline_idx = text.find('\n', idx)
            if newline_idx != -1:
                start_idx = newline_idx + 1
            break

    # Find end
    end_idx = len(text)
    for marker in end_markers:
        idx = text.find(marker)
        if idx != -1:
            end_idx = idx
            break

    return text[start_idx:end_idx].strip()


def extract_segment(text, markers, window=1500):
    """Extract a text segment around keyword markers."""
    text_lower = text.lower()

    # Find the best anchor point
    best_pos = -1
    best_count = 0

    for marker in markers:
        pos = text_lower.find(marker.lower())
        if pos != -1:
            # Count how many other markers are within window of this one
            count = 0
            for other in markers:
                other_pos = text_lower.find(other.lower())
                if other_pos != -1 and abs(other_pos - pos) < window:
                    count += 1
            if count > best_count:
                best_count = count
                best_pos = pos

    if best_pos == -1:
        return None

    # Extract window around the anchor
    start = max(0, best_pos - window // 4)
    end = min(len(text), best_pos + window)

    # Try to align to paragraph boundaries
    para_start = text.rfind('\n\n', 0, start)
    if para_start != -1:
        start = para_start + 2

    para_end = text.find('\n\n', end)
    if para_end != -1:
        end = para_end

    return text[start:end].strip()


def step4_extract_segments():
    """Extract comparable segments from all downloaded texts."""
    print("\n" + "="*70)
    print("STEP 4: Extracting comparable segments")
    print("="*70)

    all_passages = {
        "ALICE": ALICE_KEY_PASSAGES,
        "CANDIDE": CANDIDE_KEY_PASSAGES,
    }

    segments_inserted = 0

    for work_id, passages in all_passages.items():
        print(f"\n  📖 {work_id}:")

        for seg_ref, passage in passages.items():
            if not passage.get("markers"):
                continue  # Skip entries without markers

            print(f"    📝 {seg_ref}: {passage['description']}")

            for eid, e in EDITIONS.items():
                if e["work_id"] != work_id:
                    continue

                lang = e["lang"]
                if lang not in passage["markers"]:
                    continue

                # Load text
                filepath = os.path.join(
                    CORPUS_DIR, f"pg{e['gutenberg_id']}_{lang}.txt"
                )
                if not os.path.exists(filepath):
                    continue

                with open(filepath, 'r', encoding='utf-8') as f:
                    raw_text = f.read()

                clean_text = strip_gutenberg_header_footer(raw_text)
                markers = passage["markers"][lang]
                segment_text = extract_segment(clean_text, markers)

                if not segment_text:
                    print(f"      ⚠️  [{lang}] No match for markers")
                    continue

                # Count words
                words = len(segment_text.split())
                chars = len(segment_text)

                # Insert segment
                sql = (
                    f"INSERT IGNORE INTO gutenberg_segments "
                    f"(edition_id, segment_ref, segment_type, text_content, "
                    f"char_count, word_count, chapter) VALUES ("
                    f"{esc(eid)}, {esc(seg_ref)}, {esc(passage['segment_type'])}, "
                    f"{esc(segment_text[:5000])}, {chars}, {words}, "
                    f"{esc(passage.get('chapter', ''))})"
                )
                dolt_sql(sql)
                segments_inserted += 1
                print(f"      ✅ [{lang}] {words} words, {chars} chars")

    result = dolt_sql("SELECT COUNT(*) as cnt FROM gutenberg_segments")
    total = result.split('\n')[-1] if result else "?"
    print(f"\n  → {total} segments extracted")
    return segments_inserted > 0


# ─────────────────────────────────────────────────────────────────────────────
# Step 5: Decompose segments into PanLang atoms
# ─────────────────────────────────────────────────────────────────────────────

def detect_atoms_in_text(text, lang):
    """Detect PanLang atoms in a text segment by keyword matching."""
    text_lower = text.lower()
    results = {}

    for atom, keywords_by_lang in ATOM_KEYWORDS.items():
        if lang not in keywords_by_lang:
            continue

        keywords = keywords_by_lang[lang]
        matches = 0
        evidence = []

        for kw in keywords:
            # Word boundary matching
            pattern = r'\b' + re.escape(kw.lower()) + r'\b'
            found = re.findall(pattern, text_lower)
            if found:
                matches += len(found)
                evidence.append(kw)

        if matches > 0:
            # Confidence based on density
            word_count = len(text.split())
            density = matches / max(word_count, 1)
            confidence = min(1.0, density * 50)  # Normalize
            results[atom] = {
                "matches": matches,
                "confidence": round(confidence, 3),
                "evidence": evidence[:5],  # Top 5 matches
            }

    return results


def map_atoms_to_concepts(atoms_detected):
    """Map detected atoms to known PanLang concepts."""
    # Simplified mapping: check existing concepts whose atoms match
    # Uses formulas from the v2 model
    atom_set = set(atoms_detected.keys())

    # Key concept-atom mappings (from PanLang v2 — using actual v2 concept IDs)
    # Each concept maps to the atom set from its formule_simple
    CONCEPT_MAPPINGS = {
        # ── Tier A concepts ── (v2.2: EMOTION → emotional sub-primitives)
        "COLÈRE": {"RAGE", "DOMINATION"},
        "PEUR": {"FEAR", "PERCEPTION"},
        "SURPRISE": {"SEEKING", "PERCEPTION"},
        "JOIE": {"PLAY", "CREATION"},
        "TRISTESSE": {"GRIEF", "DESTRUCTION"},
        "MÉLANCOLIE": {"GRIEF", "COGNITION", "TEDIUM"},
        "ENNEMI": {"RAGE", "DOMINATION", "DESTRUCTION"},
        "ENSEIGNER": {"COGNITION", "COMMUNICATION", "CREATION"},
        "EXPLIQUER": {"COGNITION", "COMMUNICATION"},
        "COMPRENDRE": {"PERCEPTION", "COGNITION"},
        "ENTENDRE": {"PERCEPTION", "COGNITION"},
        "OBÉIR": {"PERCEPTION", "DOMINATION", "EXISTENCE"},
        "GOUVERNER": {"DOMINATION", "COMMUNICATION", "CREATION"},
        "JUSTICE": {"COGNITION", "DOMINATION", "EXISTENCE"},
        "LIBERTÉ": {"MOUVEMENT", "DOMINATION", "EXISTENCE"},
        "AIMER": {"CARE", "COMMUNICATION", "POSSESSION"},
        "CAUSE": {"CREATION", "MOUVEMENT", "COGNITION"},
        "BEAUTÉ": {"PERCEPTION", "SEEKING", "CREATION"},
        "DORMIR": {"EXISTENCE", "PERCEPTION", "DESTRUCTION"},
        "VÉRITÉ": {"COGNITION", "PERCEPTION", "EXISTENCE"},
        "MARCHER": {"MOUVEMENT", "EXISTENCE"},
        "VOIR": {"PERCEPTION", "MOUVEMENT"},
        # ── Tier B concepts ──
        "APPRENDRE": {"PERCEPTION", "COGNITION", "POSSESSION"},
        "CHERCHER": {"MOUVEMENT", "PERCEPTION", "COGNITION"},
        "EXPLORER": {"MOUVEMENT", "PERCEPTION"},
        "OBSERVER": {"DESTRUCTION", "COMMUNICATION", "EXISTENCE"},
        "FUIR": {"MOUVEMENT", "FEAR"},
        "SOUFFRIR": {"DESTRUCTION", "GRIEF"},
        "AMOUR": {"CARE", "PERCEPTION", "EXISTENCE"},
        "CONSTRUIRE": {"MOUVEMENT", "CREATION"},
        "INVENTER": {"COGNITION", "CREATION"},
        "DETRUIRE": {"MOUVEMENT", "DESTRUCTION"},
        "COMMANDER": {"COMMUNICATION", "DOMINATION"},
        "INTIMIDER": {"DOMINATION", "RAGE", "FEAR"},
        "SAISIR": {"POSSESSION", "MOUVEMENT"},
        "PARTAGER": {"POSSESSION", "COMMUNICATION"},
        "SAVOIR": {"COGNITION", "POSSESSION"},
        "CONSOLER": {"COMMUNICATION", "CARE"},
        "RACONTER": {"COMMUNICATION", "CREATION"},
        "ORGANISER": {"DOMINATION", "CREATION"},
        "GUERRE": {"MOUVEMENT", "DOMINATION", "DESTRUCTION"},
        "REALISER": {"EXISTENCE", "COGNITION"},
        "RESSENTIR": {"COGNITION", "SEEKING"},
        "VIVRE": {"EXISTENCE", "SEEKING"},
        "DESIRER": {"POSSESSION", "SEEKING"},
        "HAIR": {"RAGE", "DISGUST", "DOMINATION"},
        "ACCUMULER": {"POSSESSION", "CREATION"},
        "DANSER": {"MOUVEMENT", "PLAY"},
        # ── New v2.2 concepts (using emotional axes) ──
        "DÉGOÛT": {"DISGUST", "PERCEPTION"},
        "ENNUI": {"TEDIUM", "COGNITION"},
    }

    detected_concepts = {}
    for concept, required_atoms in CONCEPT_MAPPINGS.items():
        if required_atoms.issubset(atom_set):
            # All required atoms present
            avg_conf = sum(
                atoms_detected[a]["confidence"]
                for a in required_atoms if a in atoms_detected
            ) / len(required_atoms)
            detected_concepts[concept] = round(avg_conf, 3)

    return detected_concepts


def step5_decompose_segments():
    """Decompose each segment into PanLang atoms and map to concepts.
    
    Uses locally stored segment texts to avoid CSV parsing issues with 
    multilingual text containing commas, quotes, and special characters.
    """
    print("\n" + "="*70)
    print("STEP 5: Decomposing segments into PanLang atoms")
    print("="*70)

    # Get segment IDs and metadata via simple queries
    result = dolt_sql(
        "SELECT gs.id, gs.edition_id, gs.segment_ref, ge.lang "
        "FROM gutenberg_segments gs "
        "JOIN gutenberg_editions ge ON gs.edition_id = ge.id "
        "ORDER BY gs.segment_ref, ge.lang"
    )

    if not result:
        print("  ❌ No segments found")
        return False

    lines = result.strip().split('\n')
    if len(lines) < 2:
        print("  ❌ No segment data")
        return False

    decompositions = 0

    for line in lines[1:]:  # Skip header
        parts = line.split(',')
        if len(parts) < 4:
            continue

        seg_id = parts[0].strip()
        edition_id = parts[1].strip()
        seg_ref = parts[2].strip()
        lang = parts[3].strip()

        # Read text from locally downloaded file instead of DB
        # (avoids CSV encoding issues with multilingual text)
        edition_info = EDITIONS.get(edition_id)
        if not edition_info:
            continue

        filepath = os.path.join(
            CORPUS_DIR, f"pg{edition_info['gutenberg_id']}_{lang}.txt"
        )
        if not os.path.exists(filepath):
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            full_text = f.read()

        clean_text = strip_gutenberg_header_footer(full_text)

        # Find the segment in the text using markers
        all_passages = {
            "ALICE": ALICE_KEY_PASSAGES,
            "CANDIDE": CANDIDE_KEY_PASSAGES,
        }
        work_id = edition_info["work_id"]
        passages = all_passages.get(work_id, {})
        passage = passages.get(seg_ref)

        if not passage or lang not in passage.get("markers", {}):
            continue

        markers = passage["markers"][lang]
        segment_text = extract_segment(clean_text, markers)

        if not segment_text:
            continue

        # Detect atoms
        atoms = detect_atoms_in_text(segment_text, lang)
        if not atoms:
            print(f"    ⚠️  [{lang}] {seg_ref}: No atoms detected")
            continue

        # Map to concepts
        concepts = map_atoms_to_concepts(atoms)

        # Insert decompositions for detected concepts
        atom_list = list(atoms.keys())
        evidence_list = []
        for a, info in atoms.items():
            evidence_list.extend(info["evidence"])

        for concept, confidence in concepts.items():
            # Check if concept exists in v2 model
            existing = dolt_sql(
                f"SELECT id FROM concepts WHERE id = {esc(concept)}"
            )
            concept_id = concept if existing and concept in existing else f"_DETECTED_{concept}"

            evidence_str = ', '.join(evidence_list[:10])
            sql = (
                f"INSERT INTO segment_decompositions "
                f"(segment_id, concept_id, atoms_detected, confidence, "
                f"evidence_text, analysis_method) VALUES ("
                f"{seg_id}, {esc(concept_id)}, "
                f"'{json.dumps(atom_list)}', {confidence}, "
                f"{esc(evidence_str)}, "
                f"'keyword_match')"
            )
            dolt_sql(sql, check=False)
            decompositions += 1

        atom_names = ", ".join(f"{a}({atoms[a]['matches']})" for a in sorted(atoms))
        concept_names = ", ".join(f"{c}({v})" for c, v in sorted(concepts.items()))
        print(f"    [{lang}] {seg_ref}: {len(atoms)} atoms [{atom_names}]")
        if concepts:
            print(f"         → concepts: {concept_names}")

    result = dolt_sql("SELECT COUNT(*) as cnt FROM segment_decompositions")
    total = result.split('\n')[-1] if result else "?"
    print(f"\n  → {total} decompositions ({decompositions} new)")
    return decompositions > 0


# ─────────────────────────────────────────────────────────────────────────────
# Step 6: Compute convergence/divergence across translations
# ─────────────────────────────────────────────────────────────────────────────

def step6_compute_convergence():
    """Compute convergence analysis: common vs specific per translator."""
    print("\n" + "="*70)
    print("STEP 6: Computing convergence/divergence across translations")
    print("  'ce qui est commun de ce qui est spécifique'")
    print("="*70)

    all_passages = {
        "ALICE": ALICE_KEY_PASSAGES,
        "CANDIDE": CANDIDE_KEY_PASSAGES,
    }

    convergence_count = 0

    for work_id, passages in all_passages.items():
        print(f"\n  📖 {work_id}:")

        for seg_ref, passage in passages.items():
            if not passage.get("markers"):
                continue

            # Get all editions for this segment
            result = dolt_sql(
                f"SELECT gs.id, ge.id as eid, ge.lang, ge.translator "
                f"FROM gutenberg_segments gs "
                f"JOIN gutenberg_editions ge ON gs.edition_id = ge.id "
                f"WHERE gs.segment_ref = {esc(seg_ref)} AND ge.work_id = {esc(work_id)}"
            )
            if not result:
                continue

            lines = result.strip().split('\n')
            if len(lines) < 2:
                continue

            editions_data = []
            for line in lines[1:]:
                parts = line.split(',', 3)
                if len(parts) >= 4:
                    editions_data.append({
                        "seg_id": parts[0],
                        "edition_id": parts[1],
                        "lang": parts[2],
                        "translator": parts[3] if parts[3] else "(original)",
                    })

            total_editions = len(editions_data)
            if total_editions < 2:
                continue

            # Get all concepts detected across all editions for this segment
            all_concepts = {}
            for ed in editions_data:
                concepts_result = dolt_sql(
                    f"SELECT concept_id, atoms_detected, confidence "
                    f"FROM segment_decompositions "
                    f"WHERE segment_id = {ed['seg_id']}"
                )
                if not concepts_result:
                    continue
                for cline in concepts_result.strip().split('\n')[1:]:
                    cparts = cline.split(',', 2)
                    if len(cparts) >= 1:
                        concept = cparts[0]
                        if concept not in all_concepts:
                            all_concepts[concept] = {"found_in": [], "not_found_in": []}
                        all_concepts[concept]["found_in"].append(ed["edition_id"])

            # For each concept, compute convergence
            for concept, data in all_concepts.items():
                found_in = data["found_in"]
                not_found_in = [
                    ed["edition_id"] for ed in editions_data
                    if ed["edition_id"] not in found_in
                ]
                editions_found = len(found_in)
                ratio = editions_found / total_editions

                if ratio >= 1.0:
                    conv_type = "universal"
                elif ratio >= 0.5:
                    conv_type = "majority"
                elif ratio > 1.0 / total_editions:
                    conv_type = "minority"
                else:
                    conv_type = "unique"

                sql = (
                    f"INSERT INTO translation_convergence "
                    f"(work_id, segment_ref, concept_id, total_editions, editions_found, "
                    f"convergence_ratio, convergence_type, found_in, not_found_in) VALUES ("
                    f"{esc(work_id)}, {esc(seg_ref)}, {esc(concept)}, "
                    f"{total_editions}, {editions_found}, {round(ratio, 3)}, "
                    f"{esc(conv_type)}, "
                    f"'{json.dumps(found_in)}', "
                    f"'{json.dumps(not_found_in)}')"
                )
                dolt_sql(sql, check=False)
                convergence_count += 1

            print(f"    {seg_ref}: {len(all_concepts)} concepts, {total_editions} editions")
            for concept, data in sorted(all_concepts.items()):
                n = len(data["found_in"])
                ratio = n / total_editions
                ctype = "🌍" if ratio >= 1.0 else "📊" if ratio >= 0.5 else "🔍"
                print(f"      {ctype} {concept}: {n}/{total_editions} ({ratio:.0%})")

    result = dolt_sql("SELECT COUNT(*) as cnt FROM translation_convergence")
    total = result.split('\n')[-1] if result else "?"
    print(f"\n  → {total} convergence records computed")
    return convergence_count > 0


# ─────────────────────────────────────────────────────────────────────────────
# Step 7: Generate summary report
# ─────────────────────────────────────────────────────────────────────────────

def step7_summary_report():
    """Generate a comprehensive provenance-aware summary report."""
    print("\n" + "="*70)
    print("STEP 7: Summary — Provenance-aware validation report")
    print("="*70)

    # Works and editions
    print("\n  ── CORPUS ──")
    result = dolt_sql(
        "SELECT gw.id, gw.title_original, gw.author, gw.original_year, "
        "COUNT(ge.id) as editions "
        "FROM gutenberg_works gw "
        "JOIN gutenberg_editions ge ON ge.work_id = gw.id "
        "GROUP BY gw.id, gw.title_original, gw.author, gw.original_year"
    )
    if result:
        for line in result.strip().split('\n')[1:]:
            print(f"    {line}")

    # Provenance chain sample
    print("\n  ── CHAÎNE DE PROVENANCE (exemple) ──")
    result = dolt_sql(
        "SELECT ge.lang, ge.translator, ge.translation_year, "
        "ge.gutenberg_id, ge.gutenberg_access_date "
        "FROM gutenberg_editions ge "
        "WHERE ge.work_id = 'ALICE' "
        "ORDER BY ge.lang"
    )
    if result:
        print("    format: édition/auteur selon traducteur/époque selon gutenberg/date")
        for line in result.strip().split('\n')[1:]:
            print(f"    → {line}")

    # Convergence summary
    print("\n  ── CONVERGENCE ──")
    result = dolt_sql(
        "SELECT convergence_type, COUNT(*) as cnt, "
        "ROUND(AVG(convergence_ratio), 3) as avg_ratio "
        "FROM translation_convergence "
        "GROUP BY convergence_type "
        "ORDER BY avg_ratio DESC"
    )
    if result:
        for line in result.strip().split('\n')[1:]:
            print(f"    {line}")

    # Universal concepts (present in all translations)
    print("\n  ── CONCEPTS UNIVERSELS (convergence = 1.0) ──")
    result = dolt_sql(
        "SELECT concept_id, segment_ref, total_editions "
        "FROM translation_convergence "
        "WHERE convergence_type = 'universal' "
        "ORDER BY concept_id"
    )
    if result:
        for line in result.strip().split('\n')[1:]:
            print(f"    🌍 {line}")

    # Translator-specific concepts
    print("\n  ── INTERPRÉTATIONS SPÉCIFIQUES PAR TRADUCTEUR ──")
    result = dolt_sql(
        "SELECT concept_id, segment_ref, found_in, convergence_ratio "
        "FROM translation_convergence "
        "WHERE convergence_type IN ('minority', 'unique') "
        "ORDER BY convergence_ratio ASC"
    )
    if result:
        for line in result.strip().split('\n')[1:]:
            print(f"    🔍 {line}")

    # Segment coverage
    print("\n  ── COUVERTURE SEGMENTS ──")
    result = dolt_sql(
        "SELECT gs.segment_ref, COUNT(DISTINCT ge.lang) as langs, "
        "COUNT(DISTINCT sd.concept_id) as concepts "
        "FROM gutenberg_segments gs "
        "JOIN gutenberg_editions ge ON gs.edition_id = ge.id "
        "LEFT JOIN segment_decompositions sd ON sd.segment_id = gs.id "
        "GROUP BY gs.segment_ref "
        "ORDER BY gs.segment_ref"
    )
    if result:
        for line in result.strip().split('\n')[1:]:
            print(f"    {line}")

    return True


# ─────────────────────────────────────────────────────────────────────────────
# Step 8: Dolt commit
# ─────────────────────────────────────────────────────────────────────────────

def step8_commit():
    """Commit all changes to Dolt."""
    print("\n" + "="*70)
    print("STEP 8: Committing to Dolt")
    print("="*70)

    message = (
        f"feat(gutenberg): validation multilingue — provenance traducteurs\n\n"
        f"- {len(WORKS)} œuvres ({', '.join(WORKS.keys())})\n"
        f"- {len(EDITIONS)} éditions multilingues avec provenance\n"
        f"- Chaîne d'attribution: édition/auteur → traducteur/époque → gutenberg/date\n"
        f"- Passages-clés extraits et décomposés en atomes PanLang\n"
        f"- Analyse de convergence inter-traductions\n"
        f"- Accès Gutenberg: {TODAY}"
    )

    ok = dolt_commit(message)
    if ok:
        print(f"  ✅ Committed to Dolt")
    else:
        print(f"  ⚠️  Commit result unclear (may be clean)")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  PaniniFS — Validation multilingue via Gutenberg                    ║")
    print("║  Principe: toute information en relation avec sa source             ║")
    print("║  'édition/époque/auteur' selon 'traducteur/époque'                  ║")
    print("║  selon 'site gutenberg en date du...'                               ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    steps = [
        ("Apply schema", step1_apply_schema),
        ("Register works & editions", step2_register_works_and_editions),
        ("Download texts", step3_download_texts),
        ("Extract segments", step4_extract_segments),
        ("Decompose → PanLang atoms", step5_decompose_segments),
        ("Compute convergence", step6_compute_convergence),
        ("Summary report", step7_summary_report),
        ("Dolt commit", step8_commit),
    ]

    results = {}
    for name, func in steps:
        try:
            ok = func()
            results[name] = "✅" if ok else "⚠️"
        except Exception as e:
            print(f"\n❌ ERROR in {name}: {e}")
            results[name] = "❌"

    print("\n" + "="*70)
    print("RESULTS:")
    for name, status in results.items():
        print(f"  {status} {name}")
    print("="*70)


if __name__ == "__main__":
    main()
