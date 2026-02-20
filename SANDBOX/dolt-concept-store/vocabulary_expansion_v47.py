#!/usr/bin/env python3
"""vocabulary_expansion_v47.py — v4.7: Massive keyword expansion for total reconstruction.

Based on deep audit of 11 Gutenberg texts (313,548 words, 8 languages):
  Baseline: 44.7% global lexical coverage, 36,410 unique uncovered words.

This expansion targets the most frequent uncovered content words across all
languages, adding them to appropriate semantic atoms.

Categories expanded:
  - MOUVEMENT: directional particles + motion verbs (up, down, out, back, ...)
  - PERCEPTION: sensory vocabulary (heard, saw, voice, eyes, bright, dark, ...)
  - COMMUNICATION: speech verbs (told, exclaimed, replied, whispered, ...)
  - MESURE: numbers/quantities (two, three, thousand, many, several, ...)
  - ANCIEN: temporal vocabulary (time, day, moment, soon, suddenly, ...)
  - GRAND: size dimension — both big AND small (little, tiny, short, ...)
  - COGNITION: mental verbs + epistemic adverbs (knew, suppose, perhaps, ...)
  - AGENT: role nouns (master, father, sir, mother, lady, servant, ...)
  - LIEU: places + directional destinations (door, window, court, side, ...)
  - CORPS: body parts extended (nose, ear, tooth, tail, wing, ...)
  - BON: positive quality (beautiful, lovely, fine, fair, wonderful, ...)
  - EXISTENCE: state verbs (began, became, remain, appear, seem, ...)
  - POSSESSION: economic + exchange (gave, took, received, bought, ...)
  - DOMINATION: authority + hierarchy (master, baron, lord, command, ...)
  - INTENSE: degree modifiers (slightly, somewhat, rather, enough, ...)
  - VRAI: certainty/truth (indeed, certainly, exactly, surely, ...)
  - RELATION: social connections (friend, enemy, husband, wife, father, ...)
  - STRUCTURE: form/shape/arrangement (round, shape, circle, line, ...)
  - RÉCURRENCE: repetition/temporal patterns (again, often, always, never, ...)
  - INVARIANCE: constancy (still, same, always, forever, eternal, ...)
  - ORDRE: sequence/ordering (next, then, finally, first, second, third, ...)
  - MATIÈRE: materials extended (paper, cloth, tea, bread, cake, ...)
  - CHOSE: object references extended (piece, sort, kind, bit, way, manner, ...)
  - SEEKING: desire/curiosity (wished, hoped, longed, eager, curious, ...)
  - CREATION: making/beginning (started, opened, prepared, wrote, built, ...)
  - DESTRUCTION: ending/damage (ended, stopped, closed, lost, fell, broke, ...)
  - PLAY: amusement (smiled, laughed, grinned, funny, ridiculous, ...)
  - FEAR: anxiety extended (worried, nervous, startled, alarmed, ...)
  - GRIEF: sadness extended (wept, cried, sobbed, mourned, suffered, ...)
  - RAGE: anger extended (furious, irritated, frustrated, indignant, ...)
  - DISGUST: repulsion extended (nasty, dirty, filthy, rotten, ...)
  - CARE: tenderness (loved, kissed, hugged, caressed, gentle, soft, ...)
  - TEDIUM: weariness (yawned, sighed, sleepy, drowsy, dull, ...)
  - DUALITÉ: opposition (opposite, both, either, neither, other, ...)

Also provides:
  - EXTRA_STOP_WORDS: additional function words per language
  - EXTRA_PUNCTUATION_CHARS: curly quotes and special chars to strip

Part of PaniniFS concept store — E2 total reconstruction target.
"""

# ═══════════════════════════════════════════════════════════════════════════════
# EXTRA PUNCTUATION for content word extraction
# ═══════════════════════════════════════════════════════════════════════════════

# Characters to strip from word boundaries (extends default set)
EXTRA_PUNCTUATION_CHARS = '.,;:!?"\'"()[]{}—–-…""''«»¡¿·•‐‑⁃›‹※†‡§¶'


# ═══════════════════════════════════════════════════════════════════════════════
# EXTRA STOP WORDS — function words missing from v4.6 stop lists
# ═══════════════════════════════════════════════════════════════════════════════

EXTRA_STOP_WORDS = {
    "en": {
        # Pronouns / reflexives
        "herself", "himself", "itself", "myself", "yourself", "themselves",
        "ourselves", "yourselves", "oneself",
        # Demonstratives / determiners
        "another", "any", "every", "either", "neither", "whether",
        "whose", "whatever", "wherever", "whenever", "whoever", "whichever",
        # Conjunctions / subordinators
        "although", "though", "because", "since", "until", "unless",
        "whereas", "whereby", "wherein", "therein", "thereof",
        "however", "therefore", "moreover", "furthermore", "nevertheless",
        "meanwhile", "nonetheless", "otherwise", "accordingly",
        # Prepositions
        "upon", "within", "among", "amongst", "besides", "despite",
        "except", "across", "along", "toward", "towards", "against",
        "throughout", "underneath", "beyond", "beside", "beneath",
        # Contracted forms
        "i'm", "i've", "i'll", "i'd", "it's", "he's", "she's",
        "we're", "they're", "we've", "they've", "we'll", "they'll",
        "don't", "didn't", "can't", "won't", "isn't", "wasn't",
        "aren't", "weren't", "hasn't", "haven't", "hadn't",
        "couldn't", "wouldn't", "shouldn't", "mustn't", "let's",
        # Misc function
        "am", "oh", "yes", "no", "well", "now", "perhaps", "maybe",
    },
    "fr": {
        # Pronouns / reflexives
        "moi", "toi", "eux", "soi",
        # Contractions (common elision forms)
        "qu'il", "qu'elle", "qu'on", "qu'un", "qu'une", "qu'ils",
        "c'est", "c'était", "c'est", "c'était",
        "d'un", "d'une", "d'autres", "d'abord",
        "j'ai", "j'avais", "j'étais", "j'en",
        "l'on", "l'un", "l'une", "l'autre",
        "n'est", "n'a", "n'avait", "n'était", "n'en",
        "s'il", "s'en", "s'est", "s'était",
        # Demonstratives / misc
        "cela", "celui", "celle", "ceux", "celles",
        "comme", "depuis", "lors", "lorsque", "dès",
        "quel", "quelle", "quels", "quelles",
        "non", "oui", "si",
        # Conjunctions
        "puisque", "quoique", "tandis",
        "cependant", "pourtant", "toutefois", "néanmoins",
    },
    "de": {
        # Demonstratives / pronouns
        "daß", "dass", "da", "so", "doch", "wohl", "ja", "nein",
        "zum", "zur", "im", "am", "vom", "beim", "ins", "ans",
        "ihn", "ihm", "ihnen", "ihr", "ihre", "ihrem", "ihren", "ihrer",
        "einer", "eines", "einem", "einen",
        "mein", "meine", "meinem", "meinen", "meiner",
        "dein", "deine", "deinem", "deinen", "deiner",
        "was", "wer", "wen", "wem", "wessen",
        "selbst", "selber",
        "nun", "gar", "eben", "gerade", "bereits", "ganz",
        "denn", "doch", "wohl", "halt", "mal", "bloß", "etwa",
        # Adverbs / conjunctions
        "dann", "deshalb", "daher", "darum", "deswegen",
        "trotzdem", "dennoch", "allerdings", "jedenfalls",
        "übrigens", "außerdem", "jedoch", "indes", "indessen",
        "sogar", "sofort", "zuerst", "zunächst", "zuletzt",
        "nämlich", "eigentlich", "tatsächlich", "schließlich",
    },
    "es": {
        # Function words
        "mas", "sino", "aunque", "porque", "cuando", "donde",
        "mientras", "además", "todavía", "aún", "también",
        "ya", "así", "tan", "pues", "luego", "entonces",
        "nunca", "siempre", "sólo", "solo", "aquel", "aquella",
        "vm", "vd",  # archaic abbreviations (vuestra merced)
        "he", "ha", "hemos", "han",  # auxiliary haber
        "fué", "fueron", "fuera", "fuese",
        "está", "están", "estaba", "estaban",
        # Pronouns
        "cual", "cuyo", "cuya", "cuanto", "quién",
        "sí", "misma", "mismo", "mismas", "mismos",
        "alguno", "alguna", "algunos", "algunas",
        "ninguno", "ninguna", "todo", "toda", "todos", "todas",
    },
    "it": {
        # Conjunctions / prepositions
        "se", "più", "perchè", "perché", "ed", "ad",
        "quando", "così", "mai", "poi", "tanto",
        "qualche", "ogni", "qualcosa", "qualcuno",
        "senza", "dopo", "prima", "durante", "verso",
        "ancora", "già", "anche", "pure", "però", "dunque",
        "eppure", "oppure", "mentre", "finché", "sebbene",
        # Pronouns
        "sè", "sua", "suo", "suoi", "sue",
        "mia", "mio", "miei", "mie",
        "tua", "tuo", "tuoi", "tue",
        "nostra", "nostro", "nostri", "nostre",
        "ella", "egli", "esso", "essa", "essi", "esse",
        "col", "coi", "dai", "agli",
        # Aux/forms
        "avea", "avrebbe", "avevo", "avevano",
        "era", "erano", "fosse", "fossero",
        "fu", "ho", "hai", "abbiamo", "avete", "hanno",
    },
    "eo": {
        # X-convention stop words (in addition to Unicode forms)
        "sxi", "gxi", "gxin", "cxar", "cxu", "cxi",
        "gxis", "aux", "ankaux", "sxin",
        # Standard stop words missed
        "ke", "per", "ja", "oni", "jen", "sin",
        "unu", "da", "tuj", "kiel", "kiam",
        "tamen", "tute", "ecx", "ho", "nun",
        "cxe", "dum", "ilin", "tiun", "eble",
        "si", "mem", "laux", "iom", "tiel",
        "ankoraux", "kvankam", "tial", "apud",
        "malgraux", "alie", "cetere", "sxajne",
        "denove", "forigi", "do",
    },
    "fi": {
        # Pronouns / demonstratives
        "hänen", "heidän", "meidän", "teidän",
        "minä", "sinä", "hän", "me", "te", "he",
        "minun", "sinun", "minua", "sinua", "häntä",
        "minulle", "sinulle", "hänelle", "meille", "teille", "heille",
        "minut", "sinut", "hänet", "meidät", "teidät", "heidät",
        # Demonstratives / adverbs
        "sitä", "siitä", "sillä", "silloin", "sitten",
        "siinä", "siihen", "sieltä", "sinne",
        "jotka", "joiden", "joita", "joissa", "jolle",
        "kuinka", "miksi", "milloin", "minne", "mistä",
        "jos", "kuin", "koska", "kunnes", "vaikka",
        "juuri", "aivan", "vielä", "enää", "eikä",
        "koskaan", "kyllä", "ehkä", "kai", "tosin",
        "siis", "kuitenkin", "silti", "taas",
    },
    "sa": {
        # Common particles missed
        "cha", "by", "the", "and", "this", "of",  # English metadata in text
        "yo", "naam", "aum", "kim", "yah",
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# EXPANSION KEYWORDS — massive vocabulary additions for each atom
# ═══════════════════════════════════════════════════════════════════════════════

EXPANSION_KEYWORDS = {

    # ─────────────────────────────────────────────────────────────────────────
    # MOUVEMENT — directional particles, motion verbs, spatial movement
    # ─────────────────────────────────────────────────────────────────────────
    "MOUVEMENT": {
        "en": [
            # Directional particles (very frequent in English)
            "down", "up", "out", "off", "away", "back", "forth", "round",
            "around", "across", "along", "through", "past", "ahead",
            # Motion verbs (not already in ATOM_KEYWORDS)
            "turn", "step", "climb", "pass", "enter", "drop", "cross",
            "throw", "bring", "carry", "put", "pull", "push", "draw",
            "rise", "lift", "stretch", "reach", "stand", "sit", "lay",
            "hang", "roll", "swing", "toss", "bend", "bow", "sink",
            "float", "drift", "lean", "spring", "land", "march", "pace",
            "stagger", "stumble", "slip", "plunge", "dart", "dash",
            "retreat", "advance", "approach", "arrive", "depart", "return",
            "emerge", "vanish", "disappear", "escape", "fled",
            "ran", "fell", "walked", "jumped", "ran", "crept",
            "trot", "crawl", "stroll", "skip", "gallop", "stride",
            "set", "place", "send", "threw", "caught", "raise",
        ],
        "fr": [
            "descendre", "monter", "sortir", "entrer", "passer", "retourner",
            "revenir", "repartir", "approcher", "reculer", "traverser",
            "franchir", "porter", "tirer", "pousser", "jeter", "lancer",
            "mettre", "poser", "prendre", "lever", "baisser", "tourner",
            "coucher", "glisser", "grimper", "sauter", "ramper", "nager",
            "voler", "fuir", "quitter", "atteindre", "arriver", "partir",
            "rentrer", "emmener", "amener", "envoyer", "rapporter",
            "conduire", "traîner", "soulever", "pencher", "renverser",
            "avancer", "reculer", "bondir", "plonger",
        ],
        "de": [
            "gehen", "kommen", "steigen", "klettern", "treten", "bringen",
            "tragen", "werfen", "setzen", "stellen", "legen", "ziehen",
            "drücken", "heben", "senken", "drehen", "schieben",
            "hinunter", "hinauf", "heraus", "herein", "herab", "empor",
            "umher", "hindurch", "vorwärts", "rückwärts", "hinweg",
            "aufstehen", "hinsetzen", "schleichen", "rennen", "kriechen",
            "fliehen", "schweben", "gleiten", "stolpern", "stürzen",
            "ankommen", "abfahren", "zurückkehren", "verschwinden",
            "sich", "fuhr", "ging", "kam", "fiel", "sprang",
            "darauf", "hin", "her", "fort", "wieder", "zurück",
        ],
        "es": [
            "bajar", "subir", "salir", "entrar", "pasar", "volver",
            "regresar", "acercarse", "alejarse", "cruzar", "llevar",
            "traer", "poner", "sacar", "tirar", "lanzar", "levantar",
            "caer", "correr", "caminar", "andar", "trepar", "nadar",
            "huir", "escapar", "llegar", "partir", "regresar",
            "avanzar", "retroceder", "deslizar", "arrastrar", "empujar",
            "arrojar", "dirigir", "conducir", "guiar", "seguir",
        ],
        "it": [
            "scendere", "salire", "uscire", "entrare", "passare", "tornare",
            "avvicinarsi", "attraversare", "portare", "tirare", "spingere",
            "gettare", "mettere", "posare", "alzare", "abbassare", "girare",
            "cadere", "correre", "camminare", "saltare", "arrampicare",
            "fuggire", "scappare", "arrivare", "partire", "avanzare",
            "indietreggiare", "strisciare", "scivolare", "precipitare",
            "condurre", "guidare", "inseguire", "raggiungere",
        ],
        "eo": [
            "iri", "veni", "kuri", "fali", "salti", "grimpi", "naĝi",
            "flugi", "rampi", "gliti", "pasi", "transiri", "eniri",
            "eliri", "supreniri", "malsupreniri", "reveni", "foriri",
            "alproksimigi", "forpeli", "porti", "tiri", "puŝi", "ĵeti",
            "meti", "levi", "turni", "sidi", "stari", "kuŝi",
            "malrapide", "rapide",
            # X-convention forms
            "nagxi", "gxis",
        ],
        "fi": [
            "mennä", "tulla", "juosta", "pudota", "hypätä", "kiivetä",
            "uida", "lentää", "ryömiä", "liukua", "kävellä", "astua",
            "nousta", "laskea", "kantaa", "vetää", "työntää", "heittää",
            "panna", "asettaa", "nostaa", "kääntää", "istua", "seisoa",
            "lähteä", "saapua", "palata", "paeta", "kadota",
            "alas", "ylös", "ulos", "sisään", "takaisin", "pois",
            "eteenpäin", "taaksepäin",
        ],
        "sa": [
            "gam", "gati", "cal", "āgam", "nirgam", "pravṛt",
            "gamana", "calana", "āgamana", "gamanam",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # PERCEPTION — sensory vocabulary
    # ─────────────────────────────────────────────────────────────────────────
    "PERCEPTION": {
        "en": [
            "heard", "saw", "watched", "noticed", "stared", "gazed",
            "glanced", "listened", "tone", "loud", "quiet", "bright",
            "dark", "light", "shadow", "color", "colour", "visible",
            "invisible", "scene", "glow", "shine", "gleam", "sparkle",
            "dim", "faint", "view", "picture", "image", "figure",
            "shape", "form",
        ],
        "fr": [
            "écouter", "apercevoir", "remarquer", "yeux", "voix",
            "son", "bruit", "lumière", "ombre", "couleur", "clair",
            "sombre", "obscur", "visible", "invisible", "scène",
            "voyez", "briller", "luire", "éclat", "reflet", "image",
            "figure", "aspect", "forme", "vue", "spectacle",
        ],
        "de": [
            "schauen", "blicken", "bemerken", "sehen", "hören",
            "Stimme", "Ton", "Laut", "Geräusch", "Licht", "Schatten",
            "Farbe", "hell", "dunkel", "sichtbar", "Bild", "Gestalt",
            "Aussehen", "Blick", "Anblick", "Augen",
            "stimme", "ton", "laut", "licht", "schatten",
            "farbe", "blick", "anblick", "augen", "bild",
        ],
        "es": [
            "mirar", "escuchar", "notar", "ojos", "voz", "sonido",
            "ruido", "luz", "sombra", "color", "claro", "oscuro",
            "visible", "invisible", "escena", "brillar", "imagen",
            "figura", "aspecto", "vista",
        ],
        "it": [
            "guardare", "ascoltare", "notare", "occhi", "voce",
            "suono", "rumore", "luce", "ombra", "colore", "chiaro",
            "scuro", "visibile", "invisibile", "scena", "brillare",
            "immagine", "figura", "aspetto", "vista", "sguardo",
        ],
        "eo": [
            "aŭdi", "auxdi", "rigardi", "rimarki", "okuloj",
            "voĉo", "vocxo", "sono", "bruo", "lumo", "ombro",
            "koloro", "hela", "malluma", "videbla", "bildo",
        ],
        "fi": [
            "kuulla", "katsoa", "huomata", "silmät", "ääni",
            "äänellä", "valo", "varjo", "väri", "kirkas", "pimeä",
            "näkyvä", "kuva", "näky", "katse",
        ],
        "sa": [
            "dṛś", "śru", "darśana", "śravaṇa", "dṛṣṭi",
            "rūpa", "śabda", "jyoti", "chāyā",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # COMMUNICATION — speech and dialogue verbs
    # ─────────────────────────────────────────────────────────────────────────
    "COMMUNICATION": {
        "en": [
            "told", "exclaimed", "spoke", "announced", "explained",
            "added", "continued", "remarked", "observed", "agreed",
            "refused", "insisted", "promised", "threatened", "begged",
            "ordered", "commanded", "suggested", "proposed", "inquired",
            "muttered", "stammered", "moaned", "screamed", "sighed",
            "sang", "read", "wrote", "letter", "message", "speech",
            "name", "sign", "signal", "conversation", "story", "tale",
            "question", "sentence", "chapter", "book", "language",
            "tongue", "mean", "meant",
        ],
        "fr": [
            "expliquer", "ajouter", "continuer", "remarquer",
            "observer", "raconter", "annoncer", "insister",
            "promettre", "menacer", "supplier", "ordonner",
            "suggérer", "proposer", "interroger", "chuchoter",
            "gémir", "hurler", "soupirer", "chanter", "lire",
            "écrire", "lettre", "message", "discours", "mot",
            "parole", "signe", "signal", "conversation", "histoire",
            "conte", "question", "phrase", "chapitre", "livre",
            "langue", "nom", "vouloir dire", "dit-il", "dit-elle",
        ],
        "de": [
            "erklären", "hinzufügen", "bemerken", "erzählen",
            "ankündigen", "flüstern", "schreien", "seufzen", "singen",
            "lesen", "schreiben", "Brief", "Nachricht", "Rede",
            "Wort", "Zeichen", "Geschichte", "Erzählung", "Frage",
            "Kapitel", "Buch", "Sprache", "Name", "Satz",
            "erklärte", "erzählte", "bemerkte", "fragte",
            "brief", "nachricht", "wort", "zeichen", "geschichte",
            "frage", "kapitel", "buch", "sprache", "name", "satz",
        ],
        "es": [
            "explicar", "agregar", "continuar", "observar",
            "prometer", "amenazar", "suplicar", "ordenar",
            "sugerir", "proponer", "preguntar", "susurrar",
            "gritar", "cantar", "leer", "escribir",
            "carta", "mensaje", "discurso", "palabra",
            "nombre", "historia", "cuento", "pregunta",
            "capítulo", "libro", "lengua", "señor", "señora",
            "dixo", "replicó", "respondió", "exclamó",
        ],
        "it": [
            "spiegare", "aggiungere", "continuare", "osservare",
            "promettere", "minacciare", "supplicare", "ordinare",
            "suggerire", "proporre", "interrogare", "sussurrare",
            "mormorare", "gridare", "cantare", "leggere", "scrivere",
            "lettera", "messaggio", "discorso", "parola",
            "nome", "storia", "racconto", "domanda",
            "capitolo", "libro", "lingua",
            "domandò", "soggiunse", "sclamò", "rispose", "esclamò",
        ],
        "eo": [
            "diri", "demandi", "respondi", "krii", "murmuri",
            "flusti", "kanti", "legi", "skribi",
            "letero", "mesaĝo", "mesagxo", "parolado", "vorto",
            "nomo", "historio", "rakonto", "demando",
            "ĉapitro", "cxapitro", "libro", "lingvo",
            "komencis", "respondis", "kriis",
        ],
        "fi": [
            "selittää", "lisätä", "jatkaa", "huomauttaa",
            "luvata", "uhata", "pyytää", "käskeä",
            "ehdottaa", "kuiskata", "huutaa", "laulaa",
            "lukea", "kirjoittaa", "kirje", "viesti",
            "puhe", "sana", "nimi", "tarina",
            "kertomus", "kysymys", "luku", "kirja", "kieli",
            "sanoi", "kysyi", "vastasi", "huusi", "arveli",
        ],
        "sa": [
            "vac", "vad", "kathā", "vacana", "nāma",
            "pustaka", "bhāṣā", "praśna",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # COGNITION — mental processes, thinking, knowing
    # ─────────────────────────────────────────────────────────────────────────
    "COGNITION": {
        "en": [
            "knew", "thought", "supposed", "expected", "decided",
            "noticed", "recognized", "forgotten", "remembered",
            "meant", "understood", "guessed", "doubted",
            "doubt", "suppose", "perhaps", "opinion",
            "certain", "sure", "aware", "sense", "wise",
            "fool", "foolish", "clever", "mad", "crazy",
            "dream", "dreamt", "secret", "mystery", "puzzle",
            "problem", "solution", "plan", "lesson", "proof",
            "explain",
        ],
        "fr": [
            "savait", "pensait", "supposer", "décider",
            "reconnaître", "oublier", "deviner", "douter",
            "doute", "opinion", "avis", "esprit",
            "sage", "fou", "folle", "intelligent", "stupide",
            "rêve", "rêver", "secret", "mystère", "énigme",
            "problème", "solution", "projet", "leçon", "preuve",
            "raison", "juger", "jugement",
        ],
        "de": [
            "wissen", "denken", "vermuten", "erwarten", "entscheiden",
            "erkennen", "vergessen", "erraten", "zweifeln",
            "Zweifel", "Meinung", "Verstand", "Geist",
            "klug", "dumm", "verrückt", "weise",
            "Traum", "Geheimnis", "Rätsel", "Problem", "Lösung",
            "Plan", "Beweis", "Grund", "Urteil",
            "traum", "geheimnis", "rätsel", "problem",
        ],
        "es": [
            "saber", "pensar", "suponer", "esperar", "decidir",
            "reconocer", "olvidar", "adivinar", "dudar",
            "opinión", "mente", "razón", "juicio",
            "sabio", "loco", "inteligente", "tonto",
            "sueño", "secreto", "misterio", "problema",
        ],
        "it": [
            "sapere", "pensare", "supporre", "aspettare", "decidere",
            "riconoscere", "dimenticare", "indovinare", "dubitare",
            "opinione", "mente", "ragione", "giudizio",
            "saggio", "pazzo", "intelligente", "sciocco",
            "sogno", "segreto", "mistero", "problema",
        ],
        "eo": [
            "scii", "pensi", "supozi", "decidi", "memori",
            "forgesi", "diveni", "dubi", "opinio", "menso",
            "saĝa", "sagxa", "freneza", "stulta",
            "sonĝo", "songxo", "sekreto", "mistero", "problemo",
        ],
        "fi": [
            "tietää", "ajatella", "olettaa", "odottaa", "päättää",
            "tunnistaa", "unohtaa", "arvata", "epäillä",
            "mielipide", "mieli", "järki", "viisas", "hullu",
            "uni", "salaisuus", "mysteeri", "ongelma",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # MESURE — numbers, quantities, measurement, counting
    # ─────────────────────────────────────────────────────────────────────────
    "MESURE": {
        "en": [
            # Numbers
            "one", "two", "three", "four", "five", "six", "seven",
            "eight", "nine", "ten", "eleven", "twelve", "twenty",
            "thirty", "forty", "fifty", "hundred", "thousand", "million",
            # Ordinals
            "second", "third", "fourth", "fifth",
            # Quantity words
            "half", "double", "twice", "pair", "dozen", "several",
            "many", "few", "number", "amount", "plenty", "total",
            "full", "empty", "some", "numerous", "various",
            "enough", "less", "more", "most", "least", "fewer",
            "multiple", "single", "only", "whole", "entire",
            # Time measures
            "hour", "minute", "year", "month", "week", "century",
            # Physical measures
            "mile", "foot", "inch", "yard", "pound", "ounce",
        ],
        "fr": [
            "deux", "trois", "quatre", "cinq", "six", "sept",
            "huit", "neuf", "dix", "onze", "douze", "vingt",
            "trente", "quarante", "cinquante", "cent", "mille", "million",
            "moitié", "double", "paire", "douzaine", "plusieurs",
            "nombre", "montant", "assez", "plein", "vide", "total",
            "nombreux", "nombreuses", "divers", "diverses",
            "heure", "minute", "année", "mois", "semaine", "siècle",
        ],
        "de": [
            "eins", "zwei", "drei", "vier", "fünf", "sechs", "sieben",
            "acht", "neun", "zehn", "elf", "zwölf", "zwanzig",
            "dreißig", "vierzig", "fünfzig", "hundert", "tausend", "Million",
            "Hälfte", "Paar", "Dutzend", "Zahl", "Menge",
            "voll", "leer", "halb",
            "Stunde", "Minute", "Jahr", "Monat", "Woche",
            "zwei", "drei", "hundert", "tausend",
            "hälfte", "paar", "dutzend", "zahl", "menge",
            "stunde", "minute", "jahr", "monat", "woche",
        ],
        "es": [
            "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete",
            "ocho", "nueve", "diez", "doce", "veinte",
            "cien", "ciento", "mil", "millón",
            "mitad", "par", "docena", "varios", "varias",
            "número", "cantidad", "bastante", "veces",
            "hora", "minuto", "año", "mes", "semana", "siglo",
        ],
        "it": [
            "uno", "due", "tre", "quattro", "cinque", "sei", "sette",
            "otto", "nove", "dieci", "dodici", "venti",
            "cento", "mille", "milione",
            "metà", "paio", "dozzina", "numero", "quantità",
            "diversi", "diverse", "vari", "varie",
            "ora", "minuto", "anno", "mese", "settimana", "secolo",
        ],
        "eo": [
            "unu", "du", "tri", "kvar", "kvin", "ses", "sep",
            "ok", "naŭ", "naux", "dek", "cent", "mil", "miliono",
            "duono", "paro", "kelkaj", "nombro", "kvanto",
            "horo", "minuto", "jaro", "monato", "semajno",
        ],
        "fi": [
            "yksi", "kaksi", "kolme", "neljä", "viisi", "kuusi",
            "seitsemän", "kahdeksan", "yhdeksän", "kymmenen",
            "sata", "tuhat", "miljoona",
            "puoli", "pari", "useita", "muutama", "lukumäärä",
            "tunti", "minuutti", "vuosi", "kuukausi", "viikko",
        ],
        "sa": [
            "eka", "dvi", "tri", "catur", "pañca", "ṣaṭ", "sapta",
            "aṣṭa", "nava", "daśa", "śata", "sahasra",
            "sarva", "aneka", "bahula", "alpa",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # ANCIEN — temporal vocabulary (time, age, past, duration)
    # ─────────────────────────────────────────────────────────────────────────
    "ANCIEN": {
        "en": [
            "time", "day", "night", "morning", "evening", "moment",
            "soon", "early", "late", "ago", "young", "new", "fresh",
            "recent", "modern", "today", "yesterday", "tomorrow",
            "suddenly", "quickly", "slowly", "finally", "immediately",
            "gradually", "eventually", "instantly", "briefly",
            "begin", "end", "last",
        ],
        "fr": [
            "temps", "jour", "nuit", "matin", "soir", "moment",
            "bientôt", "tôt", "tard", "jeune", "nouveau", "nouvelle",
            "récent", "moderne", "maintenant", "aujourd'hui",
            "soudain", "vite", "lentement", "enfin", "immédiatement",
            "brusquement", "aussitôt", "subitement",
            "début", "fin", "dernier", "dernière",
            "fois", "époque", "siècle", "ère",
        ],
        "de": [
            "Zeit", "Tag", "Nacht", "Morgen", "Abend", "Moment",
            "Augenblick", "bald", "früh", "spät", "jung", "neu",
            "plötzlich", "schnell", "langsam", "endlich",
            "sofort", "allmählich", "jetzt", "gerade",
            "zeit", "tag", "nacht", "morgen", "abend", "moment",
            "augenblick", "anfang", "ende",
        ],
        "es": [
            "tiempo", "día", "dia", "noche", "mañana", "tarde",
            "momento", "pronto", "temprano", "joven", "nuevo", "nueva",
            "ahora", "ayer", "hoy",
            "repente", "rápido", "lento", "finalmente",
            "principio", "fin", "último", "última", "época", "siglo",
        ],
        "it": [
            "tempo", "giorno", "notte", "mattina", "sera", "momento",
            "presto", "giovane", "nuovo", "nuova",
            "subito", "improvvisamente", "lentamente", "finalmente",
            "inizio", "fine", "ultimo", "ultima", "epoca",
        ],
        "eo": [
            "tempo", "tago", "nokto", "mateno", "vespero", "momento",
            "baldaŭ", "baldaux", "frue", "malfrue", "juna", "nova",
            "tuj", "subite", "lante", "fine",
            "komenco", "fino", "lasta", "epoko",
        ],
        "fi": [
            "aika", "aikaa", "päivä", "yö", "aamu", "ilta", "hetki",
            "pian", "aikainen", "myöhäinen", "nuori", "uusi",
            "äkkiä", "nopeasti", "hitaasti", "lopulta",
            "alku", "loppu", "viimeinen", "kausi",
        ],
        "sa": [
            "kāla", "divasa", "rātri", "prāta", "sāyam",
            "kṣaṇa", "yuga", "kalpa", "purātana", "nava",
            "sadaa", "anaadi",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # GRAND — SIZE dimension (both big AND small)
    # ─────────────────────────────────────────────────────────────────────────
    "GRAND": {
        "en": [
            "little", "small", "tiny", "short", "narrow", "thin",
            "slight", "minor", "low", "smaller", "smallest",
            "bigger", "larger", "taller", "wider", "longer", "deeper",
            "growing", "grew", "grow", "shrink", "expand", "stretch",
        ],
        "fr": [
            "petit", "petite", "petits", "petites", "peu",
            "court", "courte", "étroit", "mince", "bas", "basse",
            "plus grand", "plus petit", "grandir", "rétrécir",
        ],
        "de": [
            "klein", "kleine", "kleinen", "kleines", "kleiner",
            "kurz", "eng", "dünn", "niedrig", "gering",
            "größer", "kleiner", "wachsen", "schrumpfen",
        ],
        "es": [
            "pequeño", "pequeña", "poco", "poca", "corto", "corta",
            "estrecho", "delgado", "bajo", "baja",
            "más grande", "más pequeño", "crecer",
        ],
        "it": [
            "piccolo", "piccola", "poco", "poca", "corto", "corta",
            "stretto", "sottile", "basso", "bassa",
        ],
        "eo": [
            "eta", "malgranda", "mallonga", "malvasta",
            "pli granda", "pli malgranda", "kreski",
        ],
        "fi": [
            "pieni", "lyhyt", "matala", "kapea", "ohut",
            "suurempi", "pienempi", "kasvaa",
        ],
        "sa": [
            "laghu", "alpa", "kṣudra", "hrasva",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # AGENT — human roles, social identities
    # ─────────────────────────────────────────────────────────────────────────
    "AGENT": {
        "en": [
            "master", "sir", "lord", "lady", "father", "mother",
            "friend", "servant", "soldier", "doctor", "judge",
            "priest", "prophet", "hero", "villain", "stranger",
            "guest", "host", "companion", "neighbor", "neighbour",
            "husband", "wife", "daughter", "son", "brother", "sister",
            "men", "women", "children", "baby", "youth",
            "crowd", "army", "nation", "race", "family",
        ],
        "fr": [
            "monsieur", "madame", "seigneur", "dame",
            "père", "mère", "ami", "amie", "serviteur", "domestique",
            "soldat", "médecin", "juge", "prêtre", "héros",
            "étranger", "hôte", "compagnon", "voisin",
            "mari", "femme", "fille", "fils", "frère", "sœur",
            "hommes", "femmes", "enfants", "bébé", "jeunesse",
            "foule", "armée", "nation", "peuple", "famille",
            "vieille", "maître", "baron", "prince", "princesse",
        ],
        "de": [
            "Herr", "Frau", "Meister", "Vater", "Mutter",
            "Freund", "Diener", "Soldat", "Arzt", "Richter",
            "Priester", "Held", "Fremder", "Gast",
            "Mann", "Frau", "Tochter", "Sohn", "Bruder", "Schwester",
            "Männer", "Frauen", "Kinder", "Familie",
            "herr", "frau", "meister", "vater", "mutter",
            "freund", "diener", "soldat", "mann", "kind",
        ],
        "es": [
            "señor", "señora", "padre", "madre",
            "amigo", "amiga", "criado", "soldado", "médico",
            "juez", "héroe", "extranjero", "huésped",
            "esposo", "esposa", "hija", "hijo", "hermano", "hermana",
            "hombres", "mujeres", "niños", "familia", "pueblo",
        ],
        "it": [
            "signore", "signora", "padre", "madre",
            "amico", "amica", "servo", "soldato", "medico",
            "giudice", "eroe", "straniero", "ospite",
            "marito", "moglie", "figlia", "figlio", "fratello", "sorella",
            "uomini", "donne", "bambini", "famiglia", "popolo",
        ],
        "eo": [
            "sinjoro", "sinjorino", "patro", "patrino",
            "amiko", "amikino", "servanto", "soldato",
            "edzo", "edzino", "filino", "filo", "frato", "fratino",
            "viroj", "virinoj", "infanoj", "familio", "popolo",
        ],
        "fi": [
            "herra", "rouva", "isä", "äiti",
            "ystävä", "palvelija", "sotilas", "lääkäri",
            "aviomies", "vaimo", "tytär", "poika", "veli", "sisar",
            "miehet", "naiset", "lapset", "perhe", "kansa",
            "eräs",
        ],
        "sa": [
            "prabhu", "pitā", "mātā", "mitra", "sevaka",
            "vīra", "rāja", "devī", "putra", "putrī",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # LIEU — places, locations, spatial destinations
    # ─────────────────────────────────────────────────────────────────────────
    "LIEU": {
        "en": [
            "door", "window", "court", "hall", "table", "side",
            "corner", "floor", "wall", "roof", "tower", "castle",
            "palace", "church", "village", "town", "street", "path",
            "bank", "shore", "island", "mountain", "valley", "river",
            "pool", "hole", "well", "cave", "sky", "heaven",
            "bottom", "top", "edge", "end", "middle", "center",
        ],
        "fr": [
            "porte", "fenêtre", "cour", "salle", "table", "côté",
            "coin", "plancher", "sol", "mur", "toit", "tour",
            "château", "palais", "église", "village", "ville", "rue",
            "chemin", "sentier", "bord", "rivage", "île",
            "montagne", "vallée", "rivière", "fleuve",
            "mare", "trou", "puits", "grotte", "ciel",
            "fond", "sommet", "bord", "milieu", "centre",
        ],
        "de": [
            "Tür", "Fenster", "Hof", "Saal", "Tisch", "Seite",
            "Ecke", "Boden", "Wand", "Dach", "Turm", "Schloß",
            "Palast", "Kirche", "Dorf", "Stadt", "Straße", "Weg",
            "Ufer", "Insel", "Berg", "Tal", "Fluß",
            "Himmel", "Höhle", "Loch",
            "tür", "thür", "fenster", "tisch", "seite", "ecke",
            "boden", "wand", "weg", "himmel",
        ],
        "es": [
            "puerta", "ventana", "corte", "sala", "mesa", "lado",
            "esquina", "suelo", "pared", "techo",
            "castillo", "palacio", "iglesia", "pueblo", "ciudad",
            "calle", "camino", "orilla", "isla",
            "montaña", "valle", "río", "cielo", "pais",
        ],
        "it": [
            "porta", "finestra", "corte", "sala", "tavola", "lato",
            "angolo", "pavimento", "muro", "tetto",
            "castello", "palazzo", "chiesa", "villaggio", "città",
            "strada", "sentiero", "riva", "isola",
            "montagna", "valle", "fiume", "cielo",
        ],
        "eo": [
            "pordo", "fenestro", "korto", "salono", "tablo", "flanko",
            "angulo", "planko", "muro", "tegmento",
            "kastelo", "palaco", "preĝejo", "pregxejo",
            "vilaĝo", "vilagxo", "urbo", "strato", "vojo",
            "insulo", "monto", "valo", "rivero", "ĉielo", "cxielo",
        ],
        "fi": [
            "ovi", "ikkuna", "piha", "sali", "pöytä", "puoli",
            "nurkka", "lattia", "seinä", "katto",
            "linna", "palatsi", "kirkko", "kylä", "kaupunki",
            "katu", "tie", "ranta", "saari",
            "vuori", "laakso", "joki", "taivas",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # CORPS — body parts extended
    # ─────────────────────────────────────────────────────────────────────────
    "CORPS": {
        "en": [
            "nose", "ear", "ears", "tooth", "teeth", "tongue",
            "lip", "lips", "chin", "cheek", "brow", "forehead",
            "tail", "wing", "wings", "paw", "claw", "fur", "feather",
            "knee", "elbow", "wrist", "thumb", "toe", "chest",
            "throat", "stomach", "brain", "tear", "tears",
            "voice", "breath", "breathe",
        ],
        "fr": [
            "nez", "oreille", "dent", "dents", "langue", "lèvre",
            "lèvres", "menton", "joue", "front", "sourcil",
            "queue", "aile", "ailes", "patte", "griffe",
            "fourrure", "plume", "genou", "coude", "poitrine",
            "gorge", "estomac", "cerveau", "larme", "larmes",
            "souffle", "haleine", "respirer",
        ],
        "de": [
            "Nase", "Ohr", "Zahn", "Zähne", "Zunge", "Lippe",
            "Kinn", "Wange", "Stirn", "Schwanz", "Flügel", "Pfote",
            "Kralle", "Fell", "Feder", "Knie", "Brust",
            "Kehle", "Magen", "Gehirn", "Träne", "Tränen",
            "Atem", "atmen",
            "nase", "ohr", "zahn", "zunge", "schwanz", "kopf",
        ],
        "es": [
            "nariz", "oreja", "diente", "lengua", "labio",
            "barbilla", "mejilla", "frente", "cola", "ala",
            "garra", "pelo", "pluma", "rodilla", "pecho",
            "garganta", "estómago", "cerebro", "lágrima",
        ],
        "it": [
            "naso", "orecchio", "dente", "lingua", "labbro",
            "mento", "guancia", "fronte", "coda", "ala",
            "artiglio", "pelo", "piuma", "ginocchio", "petto",
            "gola", "stomaco", "cervello", "lacrima",
        ],
        "eo": [
            "nazo", "orelo", "dento", "lango", "lipo",
            "mentono", "vango", "frunto", "vosto", "flugilo",
            "ungego", "felo", "plumo", "genuo", "brusto",
            "gorĝo", "gorgxo", "stomako", "cerbo", "larmo",
        ],
        "fi": [
            "nenä", "korva", "hammas", "kieli", "huuli",
            "leuka", "poski", "otsa", "häntä", "siipi",
            "kynsi", "turkki", "höyhen", "polvi", "rinta",
            "kurkku", "vatsa", "aivot", "kyynel",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # EXISTENCE — state verbs, becoming, existing
    # ─────────────────────────────────────────────────────────────────────────
    "EXISTENCE": {
        "en": [
            "began", "became", "appear", "seem", "happen",
            "occur", "come", "gone", "been", "being",
            "alive", "dead", "awake", "asleep", "present",
            "absent", "possible", "impossible",
            "world", "nature", "creature", "spirit", "soul",
            "god", "heaven", "fate", "destiny", "chance",
        ],
        "fr": [
            "commencer", "devenir", "paraître", "sembler", "arriver",
            "survenir", "venu", "été", "étant",
            "vivant", "mort", "éveillé", "endormi", "présent",
            "absent", "possible", "impossible",
            "monde", "nature", "créature", "esprit", "âme",
            "dieu", "ciel", "destin", "sort", "hasard",
        ],
        "de": [
            "beginnen", "anfangen", "werden", "scheinen", "geschehen",
            "vorkommen", "lebendig", "tot", "wach", "schlafend",
            "anwesend", "abwesend", "möglich", "unmöglich",
            "Welt", "Natur", "Geschöpf", "Geist", "Seele",
            "Gott", "Schicksal", "Zufall",
            "welt", "natur", "gott", "geist", "seele",
        ],
        "es": [
            "comenzar", "empezar", "parecer", "suceder", "ocurrir",
            "vivo", "muerto", "presente", "ausente",
            "posible", "imposible",
            "mundo", "naturaleza", "criatura", "espíritu", "alma",
            "dios", "cielo", "destino", "suerte",
        ],
        "it": [
            "cominciare", "iniziare", "diventare", "sembrare",
            "succedere", "accadere",
            "vivo", "morto", "presente", "assente",
            "possibile", "impossibile",
            "mondo", "natura", "creatura", "spirito", "anima",
            "dio", "cielo", "destino", "sorte",
        ],
        "eo": [
            "komenci", "igxi", "igxis", "ŝajni", "sxajni",
            "okazi", "viva", "morta",
            "mondo", "naturo", "kreitaĵo", "spirito", "animo",
            "dio", "destino", "sorto",
        ],
        "fi": [
            "alkaa", "tulla", "näyttää", "tapahtua", "sattua",
            "elävä", "kuollut", "läsnä", "poissa",
            "maailma", "luonto", "olento", "henki", "sielu",
            "jumala", "kohtalo", "sattuma",
        ],
        "sa": [
            "bhū", "bhav", "asti", "jīva", "mṛta",
            "loka", "prakṛti", "ātman", "brahman",
            "deva", "daiva", "dharma",
            "bhutaatmaa", "prajaapatih",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # POSSESSION — having, giving, taking, economic exchange
    # ─────────────────────────────────────────────────────────────────────────
    "POSSESSION": {
        "en": [
            "gave", "took", "received", "brought", "sent",
            "held", "left", "paid", "cost", "worth",
            "treasure", "fortune", "wealth", "goods", "property",
            "reward", "gift", "share", "part", "piece",
        ],
        "fr": [
            "donner", "donné", "pris", "reçu", "apporté", "envoyé",
            "tenu", "laissé", "payé", "coûté",
            "trésor", "fortune", "richesse", "biens", "propriété",
            "récompense", "cadeau", "part", "morceau",
        ],
        "de": [
            "geben", "nehmen", "erhalten", "bringen", "senden",
            "halten", "lassen", "bezahlen", "kosten",
            "Schatz", "Glück", "Reichtum", "Gut", "Eigentum",
            "schatz", "glück", "reichtum", "gut",
        ],
        "es": [
            "dar", "dió", "tomar", "recibir", "enviar",
            "dejar", "pagar", "valer",
            "tesoro", "fortuna", "riqueza", "bienes", "propiedad",
        ],
        "it": [
            "dare", "prendere", "ricevere", "mandare",
            "lasciare", "pagare", "costare",
            "tesoro", "fortuna", "ricchezza", "beni", "proprietà",
        ],
        "eo": [
            "doni", "preni", "ricevi", "sendi",
            "lasi", "pagi", "kosti",
            "trezoro", "fortuno", "riĉeco", "ricxeco",
        ],
        "fi": [
            "antaa", "ottaa", "saada", "tuoda", "lähettää",
            "pitää", "jättää", "maksaa",
            "aarre", "onni", "rikkaus", "omaisuus",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # DOMINATION — authority, hierarchy, power
    # ─────────────────────────────────────────────────────────────────────────
    "DOMINATION": {
        "en": [
            "master", "baron", "lord", "duke", "prince", "emperor",
            "captain", "chief", "leader", "general", "governor",
            "subject", "slave", "servant",
            "reign", "throne", "crown", "court", "trial",
            "guilty", "innocent", "verdict", "execution",
            "duty", "right", "permission", "allow", "forbid",
        ],
        "fr": [
            "baron", "seigneur", "duc", "prince", "empereur",
            "capitaine", "chef", "général", "gouverneur",
            "sujet", "esclave", "serviteur",
            "règne", "trône", "couronne", "procès",
            "coupable", "innocent", "verdict", "exécution",
            "devoir", "droit", "permission", "permettre", "interdire",
        ],
        "de": [
            "Baron", "Fürst", "Herzog", "Prinz", "Kaiser",
            "Hauptmann", "Anführer", "General",
            "Untertan", "Sklave", "Knecht",
            "Thron", "Krone", "Gericht", "Urteil",
            "baron", "fürst", "prinz", "kaiser", "thron",
        ],
        "es": [
            "barón", "baron", "señor", "duque", "príncipe",
            "emperador", "capitán", "jefe", "general", "gobernador",
            "siervo", "esclavo",
            "trono", "corona", "tribunal",
        ],
        "it": [
            "barone", "signore", "duca", "principe", "imperatore",
            "capitano", "capo", "generale", "governatore",
            "servo", "schiavo",
            "trono", "corona", "tribunale",
            "duchessa", "marchese",
        ],
        "eo": [
            "barono", "sinjoro", "duko", "princo", "imperiestro",
            "kapitano", "estro", "generalo",
            "sklavo", "servanto",
            "trono", "krono", "tribunalo",
        ],
        "fi": [
            "herra", "paroni", "ruhtinas", "keisari",
            "kapteeni", "johtaja", "kenraali",
            "orja", "palvelija",
            "valtaistuin", "kruunu", "oikeus",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # INTENSE — degree modifiers (very, slightly, somewhat, ...)
    # ─────────────────────────────────────────────────────────────────────────
    "INTENSE": {
        "en": [
            "slightly", "somewhat", "rather", "enough", "too",
            "quite", "entirely", "completely", "absolutely",
            "remarkable", "extraordinary", "wonderful", "incredible",
            "terrible", "dreadful", "fearful", "awful",
            "curious", "strange", "odd", "peculiar", "singular",
            "serious", "important", "remarkable",
        ],
        "fr": [
            "assez", "trop", "plutôt", "vraiment", "absolument",
            "complètement", "entièrement", "tout à fait",
            "remarquable", "extraordinaire", "merveilleux",
            "incroyable", "terrible", "épouvantable",
            "curieux", "étrange", "bizarre", "singulier",
            "sérieux", "important", "considérable",
        ],
        "de": [
            "etwas", "ziemlich", "genug", "ganz", "völlig",
            "vollständig", "absolut", "durchaus",
            "merkwürdig", "außerordentlich", "wunderbar",
            "schrecklich", "furchtbar", "entsetzlich",
            "seltsam", "sonderbar", "eigenartig",
            "wichtig", "bedeutend", "bemerkenswert",
        ],
        "es": [
            "bastante", "demasiado", "completamente",
            "absolutamente", "enteramente",
            "notable", "extraordinario", "maravilloso",
            "terrible", "espantoso",
            "curioso", "extraño", "raro", "singular",
            "importante", "serio",
        ],
        "it": [
            "abbastanza", "troppo", "completamente",
            "assolutamente", "interamente",
            "notevole", "straordinario", "meraviglioso",
            "terribile", "spaventoso",
            "curioso", "strano", "bizzarro", "singolare",
            "importante", "serio", "grave",
        ],
        "eo": [
            "sufiĉe", "suficxe", "tro", "tute", "absolute",
            "rimarkinda", "eksterordinara", "mirinda",
            "terura", "timinda",
            "stranga", "kurioza", "aparta", "speciala",
            "grava", "serioza",
        ],
        "fi": [
            "tarpeeksi", "liian", "täysin", "kokonaan",
            "huomattava", "erikoinen", "ihmeellinen",
            "kauhea", "hirveä", "pelottava",
            "outo", "kummallinen", "erikoinen",
            "tärkeä", "vakava", "merkittävä",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # VRAI — truth, certainty, authenticity
    # ─────────────────────────────────────────────────────────────────────────
    "VRAI": {
        "en": [
            "indeed", "certainly", "exactly", "surely", "truly",
            "actually", "apparently", "obviously", "clearly",
            "false", "wrong", "lie", "mistake", "error",
            "fact", "evidence", "proof", "witness",
        ],
        "fr": [
            "certes", "certainement", "exactement", "sûrement",
            "vraiment", "évidemment", "apparemment", "clairement",
            "faux", "fausse", "mensonge", "erreur",
            "fait", "preuve", "témoin", "vérité",
        ],
        "de": [
            "gewiß", "gewiss", "sicherlich", "genau", "tatsächlich",
            "anscheinend", "offenbar", "offensichtlich",
            "falsch", "Lüge", "Irrtum", "Fehler",
            "Tatsache", "Beweis", "Zeuge", "Wahrheit",
            "falsch", "lüge", "fehler", "wahrheit",
        ],
        "es": [
            "ciertamente", "exactamente", "seguramente",
            "verdaderamente", "evidentemente", "aparentemente",
            "falso", "mentira", "error", "equivocación",
            "hecho", "prueba", "testigo", "verdad",
        ],
        "it": [
            "certamente", "esattamente", "sicuramente",
            "veramente", "evidentemente", "apparentemente",
            "falso", "falsa", "bugia", "errore", "sbaglio",
            "fatto", "prova", "testimone", "verità",
        ],
        "eo": [
            "certe", "ĝuste", "gxuste", "vere",
            "ŝajne", "sxajne", "evidente",
            "malvera", "mensogo", "eraro",
            "fakto", "pruvo", "atestanto",
        ],
        "fi": [
            "varmasti", "tarkasti", "todella", "selvästi",
            "ilmeisesti", "nähtävästi",
            "väärä", "valhe", "virhe", "erehdys",
            "tosiasia", "todiste", "todistaja", "totuus",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # RÉCURRENCE — repetition, temporal patterns, frequency
    # ─────────────────────────────────────────────────────────────────────────
    "RÉCURRENCE": {
        "en": [
            "always", "never", "often", "sometimes", "usually",
            "frequently", "rarely", "seldom", "occasionally",
            "every", "each", "daily", "weekly", "monthly", "yearly",
            "forever", "eternal", "continuous", "constant",
            "already", "yet", "still",
        ],
        "fr": [
            "toujours", "jamais", "souvent", "parfois",
            "habituellement", "fréquemment", "rarement",
            "chaque", "quotidien", "éternel", "continu",
            "déjà", "encore",
        ],
        "de": [
            "immer", "nie", "niemals", "oft", "manchmal",
            "gewöhnlich", "häufig", "selten", "gelegentlich",
            "jeder", "jede", "jedes", "täglich", "ewig",
            "schon", "noch",
        ],
        "es": [
            "siempre", "nunca", "jamas", "frecuentemente",
            "raramente", "cada",
            "diario", "eterno", "continuo",
        ],
        "it": [
            "sempre", "mai", "spesso", "qualche volta",
            "frequentemente", "raramente",
            "ogni", "quotidiano", "eterno", "continuo",
        ],
        "eo": [
            "ĉiam", "cxiam", "neniam", "ofte", "kelkfoje",
            "malofte", "ĉiu", "cxiu", "eterna", "daŭra", "daux",
        ],
        "fi": [
            "aina", "ei koskaan", "usein", "joskus",
            "harvoin", "jokainen", "päivittäinen",
            "ikuinen", "jatkuva",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # INVARIANCE — constancy, sameness, unchanging
    # ─────────────────────────────────────────────────────────────────────────
    "INVARIANCE": {
        "en": [
            "still", "yet", "remain", "keep", "continue",
            "ever", "forever", "eternal",
            "same", "equal", "like", "similar", "such",
        ],
        "fr": [
            "encore", "toujours", "rester", "continuer",
            "même", "pareil", "semblable", "tel", "telle",
        ],
        "de": [
            "noch", "immer noch", "bleiben", "weitermachen",
            "gleich", "ähnlich", "solch", "solche",
        ],
        "es": [
            "todavía", "aún", "seguir", "continuar",
            "igual", "similar", "semejante", "tal",
        ],
        "it": [
            "ancora", "tuttora", "rimanere", "continuare",
            "uguale", "simile", "tale",
        ],
        "eo": [
            "ankoraŭ", "ankoraux", "resti", "daŭri", "dauxri",
            "sama", "egala", "simila", "tia",
        ],
        "fi": [
            "yhä", "edelleen", "pysyä", "jatkaa",
            "sama", "yhtäläinen", "samanlainen", "sellainen",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # ORDRE — ordering, sequence, position
    # ─────────────────────────────────────────────────────────────────────────
    "ORDRE": {
        "en": [
            "then", "next", "finally", "first", "last",
            "beginning", "end", "start", "finish",
            "turn", "top", "bottom",
        ],
        "fr": [
            "ensuite", "puis", "enfin", "premier", "dernier",
            "début", "fin", "commencement", "tour",
            "haut", "bas",
        ],
        "de": [
            "dann", "danach", "schließlich", "erst", "letzt",
            "Anfang", "Ende", "Beginn",
            "oben", "unten",
            "anfang", "ende", "beginn",
        ],
        "es": [
            "entonces", "después", "finalmente", "primero", "último",
            "principio", "fin", "comienzo",
            "arriba", "abajo",
        ],
        "it": [
            "poi", "dopo", "infine", "primo", "ultimo",
            "principio", "fine", "inizio",
            "sopra", "sotto",
        ],
        "eo": [
            "poste", "fine", "unue", "laste",
            "komenco", "fino",
            "supre", "malsupre",
        ],
        "fi": [
            "sitten", "seuraavaksi", "lopulta", "ensimmäinen",
            "viimeinen", "alku", "loppu",
            "ylhäällä", "alhaalla",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # MATIÈRE — materials, substances, food
    # ─────────────────────────────────────────────────────────────────────────
    "MATIÈRE": {
        "en": [
            "paper", "cloth", "leather", "metal", "steel", "silver",
            "copper", "bronze", "tin", "lead",
            "tea", "coffee", "wine", "beer", "milk",
            "bread", "cake", "butter", "cheese", "meat",
            "fruit", "flower", "tree", "leaf", "seed", "root",
            "oil", "wax", "ink", "poison", "medicine", "drug",
        ],
        "fr": [
            "papier", "tissu", "cuir", "métal", "acier", "argent",
            "cuivre", "bronze", "plomb",
            "thé", "café", "vin", "bière", "lait",
            "pain", "gâteau", "beurre", "fromage", "viande",
            "fruit", "fleur", "arbre", "feuille", "graine", "racine",
            "huile", "cire", "encre", "poison", "remède",
        ],
        "de": [
            "Papier", "Stoff", "Leder", "Metall", "Stahl", "Silber",
            "Tee", "Kaffee", "Wein", "Bier", "Milch",
            "Brot", "Kuchen", "Butter", "Käse", "Fleisch",
            "Frucht", "Blume", "Baum", "Blatt", "Samen",
            "papier", "stoff", "tee", "wein", "brot",
            "blume", "baum", "blatt",
        ],
        "es": [
            "papel", "tela", "cuero", "metal", "acero", "plata",
            "té", "café", "vino", "cerveza", "leche",
            "pan", "pastel", "mantequilla", "queso", "carne",
            "fruta", "flor", "árbol", "hoja", "semilla",
        ],
        "it": [
            "carta", "tessuto", "cuoio", "metallo", "acciaio", "argento",
            "tè", "caffè", "vino", "birra", "latte",
            "pane", "torta", "burro", "formaggio", "carne",
            "frutto", "fiore", "albero", "foglia", "seme",
        ],
        "eo": [
            "papero", "ŝtofo", "sxtofo", "ledo", "metalo", "ŝtalo", "sxtalo",
            "teo", "kafo", "vino", "biero", "lakto",
            "pano", "kuko", "butero", "fromaĝo", "fromagxo", "viando",
            "frukto", "floro", "arbo", "folio", "semo",
        ],
        "fi": [
            "paperi", "kangas", "nahka", "metalli", "teräs",
            "tee", "kahvi", "viini", "olut", "maito",
            "leipä", "kakku", "voi", "juusto", "liha",
            "hedelmä", "kukka", "puu", "lehti", "siemen",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # CHOSE — objects, references, kinds
    # ─────────────────────────────────────────────────────────────────────────
    "CHOSE": {
        "en": [
            "sort", "kind", "type", "way", "manner", "matter",
            "fact", "case", "point", "reason", "cause",
            "idea", "plan", "answer", "truth",
            "picture", "illustration", "figure", "mark",
        ],
        "fr": [
            "sorte", "genre", "type", "façon", "manière",
            "fait", "cas", "point", "raison", "cause",
            "idée", "plan", "réponse", "vérité",
            "image", "illustration", "figure", "marque",
        ],
        "de": [
            "Sorte", "Art", "Weise", "Sache", "Fall",
            "Punkt", "Grund", "Ursache",
            "Antwort", "Bild", "Illustration", "Figur",
            "sorte", "art", "weise", "sache", "fall",
            "grund", "bild", "illustration",
        ],
        "es": [
            "clase", "tipo", "modo", "manera", "asunto",
            "hecho", "caso", "punto", "razón", "causa",
            "respuesta", "imagen", "ilustración", "figura",
        ],
        "it": [
            "sorta", "genere", "tipo", "modo", "maniera",
            "fatto", "caso", "punto", "ragione", "causa",
            "risposta", "immagine", "illustrazione", "figura",
        ],
        "eo": [
            "speco", "tipo", "maniero", "afero", "kazo",
            "punkto", "kialo", "kaŭzo", "kauzo",
            "respondo", "bildo", "ilustraĵo", "ilustrajxo",
        ],
        "fi": [
            "laji", "tyyppi", "tapa", "asia", "tapaus",
            "kohta", "syy", "aihe",
            "vastaus", "kuva", "kuvitus",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # RELATION — social/logical connections
    # ─────────────────────────────────────────────────────────────────────────
    "RELATION": {
        "en": [
            "friend", "enemy", "husband", "wife", "father",
            "mother", "brother", "sister", "family",
            "together", "apart", "alone", "with", "without",
            "cause", "effect", "result", "consequence",
        ],
        "fr": [
            "ami", "ennemi", "époux", "épouse",
            "ensemble", "séparé", "seul", "seule",
            "cause", "effet", "résultat", "conséquence",
        ],
        "de": [
            "Feind", "Ehemann", "Ehefrau",
            "zusammen", "getrennt", "allein",
            "Ursache", "Wirkung", "Ergebnis", "Folge",
            "feind", "allein",
        ],
        "es": [
            "amigo", "enemigo", "esposo", "esposa",
            "juntos", "separado", "solo", "sola",
            "causa", "efecto", "resultado", "consecuencia",
        ],
        "it": [
            "amico", "nemico", "sposo", "sposa",
            "insieme", "separato", "solo", "sola",
            "causa", "effetto", "risultato", "conseguenza",
        ],
        "eo": [
            "amiko", "malamiko", "edzo", "edzino",
            "kune", "aparte", "sola",
            "kaŭzo", "kauzo", "efiko", "rezulto", "sekvo",
        ],
        "fi": [
            "ystävä", "vihollinen", "aviomies", "vaimo",
            "yhdessä", "erillään", "yksin",
            "syy", "vaikutus", "tulos", "seuraus",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # DUALITÉ — opposition, contrasts, alternatives
    # ─────────────────────────────────────────────────────────────────────────
    "DUALITÉ": {
        "en": [
            "other", "else", "different", "change", "changed",
            "instead", "rather", "otherwise",
            "but", "however", "although", "though",
            "yes", "no", "true", "false",
        ],
        "fr": [
            "autre", "autrement", "différent", "changer",
            "au lieu de", "plutôt",
            "oui", "non", "vrai", "faux",
        ],
        "de": [
            "ander", "andere", "anderes", "anders", "sonst",
            "statt", "anstatt",
        ],
        "es": [
            "otro", "otra", "otros", "otras", "diferente",
            "cambiar", "en lugar de",
        ],
        "it": [
            "altro", "altra", "altri", "altre", "diverso",
            "cambiare", "invece",
        ],
        "eo": [
            "alia", "aliaj", "malsama", "ŝanĝi", "sxangxi",
            "anstataŭ", "anstataux",
        ],
        "fi": [
            "toinen", "muu", "erilainen", "muuttaa",
            "sen sijaan", "muuten",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # STRUCTURE — form, shape, arrangement, pattern
    # ─────────────────────────────────────────────────────────────────────────
    "STRUCTURE": {
        "en": [
            "round", "square", "straight", "circle", "line",
            "row", "column", "chain", "series", "list",
            "heap", "pile", "bunch", "crowd", "assembly",
        ],
        "fr": [
            "rond", "carré", "droit", "cercle", "ligne",
            "rang", "colonne", "chaîne", "série", "liste",
            "tas", "pile", "groupe", "foule", "assemblée",
        ],
        "de": [
            "rund", "viereckig", "gerade", "Kreis", "Linie",
            "Reihe", "Kette", "Haufen", "Menge",
            "rund", "kreis", "linie", "reihe", "kette",
        ],
        "es": [
            "redondo", "cuadrado", "recto", "círculo", "línea",
            "fila", "cadena", "serie", "lista",
            "montón", "grupo", "multitud",
        ],
        "it": [
            "rotondo", "quadrato", "dritto", "cerchio", "linea",
            "fila", "catena", "serie", "lista",
            "mucchio", "gruppo", "folla",
        ],
        "eo": [
            "ronda", "kvadrata", "rekta", "cirklo", "linio",
            "vico", "ĉeno", "cxeno", "serio", "listo",
            "amaso", "grupo", "homamaso",
        ],
        "fi": [
            "pyöreä", "neliö", "suora", "ympyrä", "viiva",
            "rivi", "ketju", "sarja", "luettelo",
            "kasa", "ryhmä", "joukko",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # BON — positive quality, beauty, pleasure
    # ─────────────────────────────────────────────────────────────────────────
    "BON": {
        "en": [
            "best", "better", "lovely", "wonderful", "splendid",
            "charming", "graceful", "elegant", "handsome",
            "comfort", "comfortable", "pleasure", "enjoy",
            "perfect", "pure", "clean", "fresh", "warm", "cool",
            "calm", "peaceful", "soft", "smooth",
        ],
        "fr": [
            "meilleur", "mieux", "charmant", "gracieux",
            "élégant", "splendide", "magnifique", "superbe",
            "confort", "plaisir", "jouir", "parfait",
            "pur", "propre", "frais", "chaud", "froid",
            "calme", "paisible", "doux", "douce",
            "hermosa",
        ],
        "de": [
            "besser", "best", "schön", "lieblich", "wunderbar",
            "herrlich", "prächtig", "hübsch",
            "Vergnügen", "Freude", "genießen",
            "perfekt", "rein", "sauber", "warm", "kühl",
            "ruhig", "friedlich", "sanft", "weich",
            "vergnügen", "freude",
        ],
        "es": [
            "mejor", "hermoso", "hermosa", "bello", "bella",
            "encantador", "elegante", "espléndido",
            "placer", "disfrutar", "perfecto",
            "puro", "limpio", "cálido", "fresco",
            "tranquilo", "suave",
        ],
        "it": [
            "migliore", "bello", "bella", "incantevole",
            "elegante", "splendido", "magnifico",
            "piacere", "godere", "perfetto",
            "puro", "pulito", "caldo", "fresco",
            "tranquillo", "morbido",
        ],
        "eo": [
            "pli bona", "bela", "ĉarma", "cxarma", "eleganta",
            "splenda", "magnifa",
            "plezuro", "ĝui", "gxui", "perfekta",
            "pura", "pura", "varma", "malvarma",
            "trankvila", "mola",
        ],
        "fi": [
            "parempi", "paras", "kaunis", "ihastuttava",
            "tyylikäs", "upea", "loistava",
            "ilo", "nauttia", "täydellinen",
            "puhdas", "siisti", "lämmin", "viileä",
            "rauhallinen", "pehmeä",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # PLAY — amusement, laughter, fun
    # ─────────────────────────────────────────────────────────────────────────
    "PLAY": {
        "en": [
            "smiled", "laughed", "grinned", "funny", "ridiculous",
            "absurd", "comical", "humorous", "witty",
            "trick", "adventure", "party", "feast", "holiday",
            "surprise", "pleasure", "entertainment",
        ],
        "fr": [
            "sourire", "rire", "amusant", "drôle", "ridicule",
            "absurde", "comique", "plaisanterie",
            "tour", "aventure", "fête", "festin", "vacances",
        ],
        "de": [
            "lächeln", "lachen", "lustig", "lächerlich",
            "absurd", "komisch", "witzig",
            "Streich", "Abenteuer", "Fest", "Feier",
            "lächeln", "lachen", "abenteuer",
        ],
        "es": [
            "sonreír", "reír", "gracioso", "ridículo",
            "absurdo", "cómico", "aventura", "fiesta",
        ],
        "it": [
            "sorridere", "ridere", "divertente", "ridicolo",
            "assurdo", "comico", "avventura", "festa",
        ],
        "eo": [
            "rideti", "ridi", "amuza", "ridinda",
            "absurda", "komika", "aventuro", "festo",
        ],
        "fi": [
            "hymyillä", "nauraa", "hauska", "naurettava",
            "absurdi", "koominen", "seikkailu", "juhla",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # FEAR — anxiety, dread, alarm
    # ─────────────────────────────────────────────────────────────────────────
    "FEAR": {
        "en": [
            "worried", "nervous", "startled", "alarmed",
            "shocked", "surprise", "uneasy", "restless",
            "danger", "dangerous", "threat", "risk",
            "brave", "courage", "bold", "dare",
        ],
        "fr": [
            "inquiet", "nerveux", "surpris", "alarmé",
            "choqué", "mal à l'aise", "agité",
            "danger", "dangereux", "menace", "risque",
            "brave", "courage", "audacieux", "oser",
        ],
        "de": [
            "besorgt", "nervös", "erschrocken", "alarmiert",
            "Gefahr", "gefährlich", "Bedrohung", "Risiko",
            "mutig", "Mut", "kühn", "wagen",
            "gefahr", "mut",
        ],
        "es": [
            "preocupado", "nervioso", "sorprendido", "alarmado",
            "peligro", "peligroso", "amenaza", "riesgo",
            "valiente", "valor", "atrevido",
        ],
        "it": [
            "preoccupato", "nervoso", "sorpreso", "allarmato",
            "pericolo", "pericoloso", "minaccia", "rischio",
            "coraggioso", "coraggio", "audace",
        ],
        "eo": [
            "maltrankvila", "nervoza", "surprizita",
            "danĝero", "dangxero", "danĝera", "dangxera",
            "minaco", "risko",
            "brava", "kuraĝo", "kuragxo", "aŭdaca", "auxdaca",
        ],
        "fi": [
            "huolestunut", "hermostunut", "hämmästynyt",
            "vaara", "vaarallinen", "uhka", "riski",
            "rohkea", "rohkeus", "uskaltaa",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # GRIEF — sadness, loss, suffering
    # ─────────────────────────────────────────────────────────────────────────
    "GRIEF": {
        "en": [
            "wept", "sobbed", "mourned", "suffered", "pain",
            "painful", "miserable", "wretched", "unhappy",
            "poor", "pity", "pitiful", "sorry", "regret",
            "unfortunate", "unlucky", "trouble", "distress",
        ],
        "fr": [
            "pleurer", "sangloter", "souffrir", "douleur",
            "douloureux", "misérable", "malheureux",
            "pauvre", "pitié", "pitoyable", "pardon", "regret",
            "infortuné", "malheur", "peine", "détresse",
        ],
        "de": [
            "weinen", "schluchzen", "leiden", "Schmerz",
            "schmerzhaft", "elend", "unglücklich",
            "arm", "Mitleid", "erbärmlich", "bedauern",
            "schmerz", "mitleid",
        ],
        "es": [
            "llorar", "sollozar", "sufrir", "dolor",
            "doloroso", "miserable", "infeliz",
            "pobre", "lástima", "lamentable", "perdón",
            "desgracia", "desgraciado", "pena",
        ],
        "it": [
            "piangere", "singhiozzare", "soffrire", "dolore",
            "doloroso", "miserabile", "infelice",
            "povero", "pietà", "pietoso", "perdono",
            "sventura", "sventurato", "pena",
        ],
        "eo": [
            "plori", "singulti", "suferi", "doloro",
            "dolora", "mizera", "malfeliĉa", "malfelicxa",
            "malriĉa", "malricxa", "kompato", "bedaŭri", "bedauxri",
        ],
        "fi": [
            "itkeä", "nyyhkyttää", "kärsiä", "kipu",
            "kivulias", "kurja", "onneton",
            "köyhä", "sääli", "säälittävä", "anteeksi",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # CREATION — making, beginning, opening
    # ─────────────────────────────────────────────────────────────────────────
    "CREATION": {
        "en": [
            "start", "started", "began", "open", "opened",
            "prepare", "prepared", "arrange", "arranged",
            "wrote", "written", "built", "born", "develop",
            "plant", "cook", "bake", "sew", "craft",
        ],
        "fr": [
            "commencer", "ouvrir", "ouvert", "préparer",
            "arranger", "écrire", "écrit", "construit",
            "planter", "cuisiner", "coudre",
        ],
        "de": [
            "starten", "anfangen", "öffnen", "vorbereiten",
            "schreiben", "geschrieben", "gebaut",
            "pflanzen", "kochen", "nähen",
        ],
        "es": [
            "empezar", "abrir", "preparar",
            "escribir", "escrito", "construido",
            "plantar", "cocinar", "coser",
        ],
        "it": [
            "iniziare", "aprire", "preparare",
            "scritto", "costruito",
            "piantare", "cucinare", "cucire",
        ],
        "eo": [
            "komenci", "malfermi", "prepari",
            "skribi", "skribita", "konstruita",
            "planti", "kuiri", "kudri",
        ],
        "fi": [
            "aloittaa", "avata", "valmistaa",
            "kirjoittaa", "kirjoitettu", "rakennettu",
            "istuttaa", "keittää", "ommella",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # DESTRUCTION — ending, closing, damaging
    # ─────────────────────────────────────────────────────────────────────────
    "DESTRUCTION": {
        "en": [
            "end", "ended", "stop", "stopped", "close", "closed",
            "shut", "finish", "finished", "dead", "death",
            "lost", "fell", "broken", "struck", "hit", "shot",
            "wound", "wounded", "injury", "injured",
            "crash", "collapse", "sink", "drown", "choke",
        ],
        "fr": [
            "terminer", "arrêter", "fermer", "fermé",
            "finir", "fini", "mourir", "mort",
            "perdu", "tombé", "brisé", "frappé",
            "blessure", "blessé", "blesser",
            "effondrer", "noyer", "étouffer",
        ],
        "de": [
            "beenden", "aufhören", "schließen", "geschlossen",
            "sterben", "Tod", "tot",
            "verloren", "gefallen", "gebrochen", "geschlagen",
            "Wunde", "verwundet", "verletzt",
            "tod", "wunde",
        ],
        "es": [
            "terminar", "parar", "cerrar",
            "morir", "muerte", "muerto",
            "perdido", "caído", "roto", "golpeado",
            "herida", "herido",
        ],
        "it": [
            "terminare", "fermare", "chiudere",
            "morire", "morte", "morto",
            "perduto", "caduto", "rotto", "colpito",
            "ferita", "ferito",
        ],
        "eo": [
            "fini", "halti", "fermi", "ĉesi", "cxesi",
            "morti", "morto", "mortinta",
            "perdita", "falinta", "rompita", "frapita",
            "vundo", "vundita",
        ],
        "fi": [
            "lopettaa", "pysäyttää", "sulkea",
            "kuolla", "kuolema", "kuollut",
            "menetetty", "pudonnut", "rikki", "lyöty",
            "haava", "haavoittunut",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # SEEKING — desire, curiosity, wanting
    # ─────────────────────────────────────────────────────────────────────────
    "SEEKING": {
        "en": [
            "wished", "hoped", "longed", "eager", "anxious",
            "look for", "hunting", "try", "tried", "attempt",
            "need", "needed", "must", "shall",
            "ready", "willing", "determined",
        ],
        "fr": [
            "souhaiter", "espérer", "désirer", "avide",
            "chercher", "essayer", "tenter", "tentative",
            "besoin", "falloir", "prêt", "disposé", "déterminé",
        ],
        "de": [
            "wünschen", "hoffen", "sehnen", "eifrig",
            "suchen", "versuchen", "Versuch",
            "brauchen", "bereit", "entschlossen",
        ],
        "es": [
            "desear", "esperar", "anhelar",
            "buscar", "intentar", "tratar",
            "necesitar", "listo", "dispuesto",
        ],
        "it": [
            "desiderare", "sperare", "bramare",
            "cercare", "tentare", "provare",
            "bisogno", "pronto", "disposto",
        ],
        "eo": [
            "deziri", "esperi", "sopiri",
            "serĉi", "sercxi", "provi", "klopodi",
            "bezoni", "preta", "decidita",
        ],
        "fi": [
            "toivoa", "haluta", "kaivata",
            "etsiä", "yrittää", "koettaa",
            "tarvita", "valmis", "päättäväinen",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # CARE — tenderness, affection, gentleness
    # ─────────────────────────────────────────────────────────────────────────
    "CARE": {
        "en": [
            "loved", "kissed", "hugged", "caressed", "soft",
            "gently", "carefully", "attention", "help", "save",
            "rescue", "sympathy", "mercy", "forgive", "pardon",
        ],
        "fr": [
            "aimé", "embrassé", "caressé", "doucement",
            "attention", "aide", "aider", "sauver",
            "secourir", "sympathie", "pitié", "grâce", "pardonner",
        ],
        "de": [
            "lieben", "küssen", "umarmen", "streicheln",
            "sanft", "vorsichtig", "Hilfe", "helfen", "retten",
            "Mitleid", "Gnade", "vergeben",
        ],
        "es": [
            "amar", "besar", "abrazar", "acariciar",
            "suavemente", "ayuda", "ayudar", "salvar",
            "simpatía", "misericordia", "perdonar",
        ],
        "it": [
            "amare", "baciare", "abbracciare", "accarezzare",
            "dolcemente", "aiuto", "aiutare", "salvare",
            "simpatia", "misericordia", "perdonare",
        ],
        "eo": [
            "ami", "kisi", "brakumi", "karesi",
            "dolĉe", "dolcxe", "helpo", "helpi", "savi",
            "kompato", "pardoni",
        ],
        "fi": [
            "rakastaa", "suudella", "halata", "hyväillä",
            "hellästi", "apu", "auttaa", "pelastaa",
            "myötätunto", "armo", "antaa anteeksi",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # TEDIUM — boredom, weariness, inactivity
    # ─────────────────────────────────────────────────────────────────────────
    "TEDIUM": {
        "en": [
            "yawned", "sighed", "wait", "waited", "waiting",
            "patience", "patient", "impatient",
            "long", "endless", "nothing",
            "silence", "silent", "quiet", "rest", "sleep",
        ],
        "fr": [
            "bâiller", "attendre", "attendu", "patience",
            "patient", "impatient",
            "long", "interminable", "rien",
            "silence", "silencieux", "repos", "dormir", "sommeil",
        ],
        "de": [
            "gähnen", "warten", "gewartet", "Geduld",
            "geduldig", "ungeduldig",
            "Stille", "still", "ruhig", "Ruhe", "schlafen", "Schlaf",
            "stille", "ruhe", "schlaf",
        ],
        "es": [
            "bostezar", "esperar", "paciencia",
            "paciente", "impaciente",
            "silencio", "silencioso", "descanso", "dormir", "sueño",
        ],
        "it": [
            "sbadigliare", "aspettare", "pazienza",
            "paziente", "impaziente",
            "silenzio", "silenzioso", "riposo", "dormire", "sonno",
        ],
        "eo": [
            "oscedi", "atendi", "pacienco",
            "pacienca", "senpacienca",
            "silento", "silenta", "ripozo", "dormi", "dormo",
        ],
        "fi": [
            "haukotella", "odottaa", "kärsivällisyys",
            "kärsivällinen", "kärsimätön",
            "hiljaisuus", "hiljainen", "lepo", "nukkua", "uni",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # DISGUST — repulsion, dirtiness
    # ─────────────────────────────────────────────────────────────────────────
    "DISGUST": {
        "en": [
            "nasty", "dirty", "filthy", "rotten", "stink",
            "stinking", "smell", "bitter", "sour", "raw",
            "rough", "crude", "coarse", "vulgar",
        ],
        "fr": [
            "sale", "crasseux", "pourri", "puant",
            "amer", "aigre", "brut", "grossier", "vulgaire",
        ],
        "de": [
            "schmutzig", "dreckig", "faul", "stinkend",
            "bitter", "sauer", "roh", "grob", "vulgär",
        ],
        "es": [
            "sucio", "asqueroso", "podrido", "apestoso",
            "amargo", "agrio", "crudo", "grosero", "vulgar",
        ],
        "it": [
            "sporco", "lurido", "marcio", "puzzolente",
            "amaro", "acido", "crudo", "rozzo", "volgare",
        ],
        "eo": [
            "malpura", "putra", "fetora",
            "amara", "acida", "kruda", "vulgara",
        ],
        "fi": [
            "likainen", "saastainen", "mätä", "haiseva",
            "kitkerä", "hapan", "raaka", "karkea",
        ],
    },

    # ─────────────────────────────────────────────────────────────────────────
    # RAGE — anger, irritation
    # ─────────────────────────────────────────────────────────────────────────
    "RAGE": {
        "en": [
            "frustrated", "irritated", "indignant", "hostile",
            "hate", "hatred", "spite", "scorn", "contempt",
            "insult", "mock", "taunt", "curse",
            "quarrel", "dispute", "argue", "argument",
        ],
        "fr": [
            "frustré", "irrité", "indigné", "hostile",
            "haine", "mépris", "dédain",
            "insulte", "moquer", "maudire",
            "querelle", "dispute", "disputer",
        ],
        "de": [
            "frustriert", "gereizt", "empört", "feindlich",
            "Hass", "Verachtung", "Spott",
            "Beleidigung", "spotten", "fluchen",
            "Streit", "streiten",
            "hass", "streit",
        ],
        "es": [
            "frustrado", "irritado", "indignado", "hostil",
            "odio", "desprecio", "insulto",
            "burlarse", "maldecir", "pelea", "disputa",
        ],
        "it": [
            "frustrato", "irritato", "indignato", "ostile",
            "odio", "disprezzo", "insulto",
            "deridere", "maledire", "lite", "disputa",
        ],
        "eo": [
            "frustrita", "incitita", "indignita",
            "malamo", "malestimo", "insulto",
            "moki", "malbeni", "kverelo", "disputo",
        ],
        "fi": [
            "turhautunut", "ärsyyntynyt", "närkästynyt",
            "viha", "halveksunta", "loukkaus",
            "pilkata", "kirota", "riita",
        ],
    },
}
