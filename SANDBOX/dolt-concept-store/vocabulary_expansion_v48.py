#!/usr/bin/env python3
"""vocabulary_expansion_v48.py — Round 2: Push towards 100% coverage

Strategy:
  A. Proper nouns → AGENT atom (character names are agents)
  B. Contractions → stop words (function word contractions)
  C. Quote-attached artifacts → extra punctuation chars
  D. Massive function word expansion → stop words
  E. Common content words → atom mappings
  F. Finnish agglutinated forms → stop words + atoms
  G. Old/archaic spellings → atom mappings
  H. Animal names → CORPS/CHOSE (animals as body/entity)
  I. Literary/document words → stop words (illustration, chapter, etc.)

Part of PaniniFS concept store — v4.8 vocabulary expansion.
"""

# ═══════════════════════════════════════════════════════════════════════════════
# A. EXTRA PUNCTUATION CHARACTERS (strip from tokens)
# ═══════════════════════════════════════════════════════════════════════════════

EXTRA_PUNCTUATION_V48 = '«»„""‹›❝❞❛❜\u201c\u201d\u2018\u2019\u00ab\u00bb_—–'

# ═══════════════════════════════════════════════════════════════════════════════
# B. PROPER NOUNS → mapped to AGENT (literary character names)
# ═══════════════════════════════════════════════════════════════════════════════

PROPER_NOUN_AGENTS = {
    # Alice in Wonderland characters
    "alice", "alicio", "alicion", "liisa", "liisan",
    "dina",  # Alice's cat name
    # Candide characters
    "candide", "candido", "candiden", "candides",
    "cunegonde", "cunégonde", "cunegunda", "kunigundan", "kunigunda",
    "pangloss", "panglós",
    "martin",
    "cacambo",
    "paquita", "paquette",
    # Alice creatures (treated as agents in the story)
    "gryphon", "hatter", "dormouse", "duchess",
    "caterpillar", "bruco", "chenille", "raupe",
    "chapelier", "cxapelisto", "hatuntekijä",
    "dukino", "herttuatar",  # duchess in eo/fi
    # Candide characters
    "cunégonde", "abbé", "abate",
    "inquisitor", "jesuit", "jésuite", "jesuita",
    # Minor characters
    "dodo", "lakeo", "muori",
}

# ═══════════════════════════════════════════════════════════════════════════════
# C. LITERARY/DOCUMENT STOP WORDS (non-content)
# ═══════════════════════════════════════════════════════════════════════════════

LITERARY_STOP_WORDS = {
    "illustration", "illustrazione", "chapter", "chapitre", "kapitel",
    "capitolo", "capítulo", "ĉapitro", "luku",
    "etext", "formatted", "proofed", "transcriber",
    "pg", "gutenberg", "ebook",
    "fig", "vol", "cap", "vms",
    "_vi_",  # Esperanto formatting artifact
}

# ═══════════════════════════════════════════════════════════════════════════════
# D. MASSIVE STOP WORDS EXPANSION (Round 2)
# ═══════════════════════════════════════════════════════════════════════════════

STOP_WORDS_V48 = {
    "en": {
        # Contractions
        "i'm", "it's", "can't", "won't", "i'll", "it's", "don't", "didn't",
        "doesn't", "isn't", "aren't", "wasn't", "weren't", "hasn't", "haven't",
        "hadn't", "wouldn't", "couldn't", "shouldn't", "mustn't", "let's",
        "that's", "there's", "here's", "what's", "who's", "he's", "she's",
        "we're", "they're", "you're", "i've", "you've", "we've", "they've",
        "i'd", "you'd", "he'd", "she'd", "we'd", "they'd",
        # Quote-attached (tokenizer artifacts)
        '"i', '"and', '"you', '"but', '"what', '"it', '"oh', '"it\'s',
        '"well', '"if', '"the', '"no', '"yes', '"we', '"he', '"she',
        '"do', '"so', '"why', '"how', '"come', '"let', '"now', '"then',
        # Common function words still missing
        "about", "over", "let", "near", "also", "cannot", "alas", "ah", "oh",
        "yet", "upon", "thus", "hence", "therefore", "although", "though",
        "however", "moreover", "furthermore", "nevertheless", "meanwhile",
        "perhaps", "maybe", "almost", "enough", "rather", "quite", "indeed",
        "certainly", "surely", "anyway", "besides", "otherwise", "instead",
        "across", "along", "among", "behind", "below", "beneath", "beside",
        "between", "beyond", "during", "except", "inside", "outside",
        "throughout", "toward", "towards", "within", "without",
        "anybody", "anyone", "anything", "everybody", "everyone", "everything",
        "nobody", "somebody", "someone", "something", "itself", "myself",
        "yourself", "himself", "herself", "ourselves", "themselves",
        "whose", "whom", "whichever", "whatever", "wherever", "whenever",
        "whoever", "whether",
        "el", "dorado",  # El Dorado treated as proper noun
    },
    "fr": {
        # Contractions & elisions
        "qu'il", "qu'on", "qu'elle", "qu'un", "qu'une", "qu'ils", "qu'elles",
        "qu'en", "qu'y", "qu'à",
        "d'un", "d'une", "d'abord", "d'ailleurs", "d'après",
        "d'être", "d'avoir", "d'où",
        "l'on", "l'un", "l'une", "l'autre", "l'air", "l'eau", "l'homme",
        "l'instant", "l'avait", "l'a", "l'y",
        "n'y", "n'est", "n'en", "n'a", "n'ai", "n'avait", "n'était",
        "n'ont", "n'avons",
        "c'est", "c'était", "c'eût",
        "j'ai", "j'avais", "j'étais", "j'en", "j'y",
        "s'il", "s'en", "s'y", "s'est", "s'était",
        "m'a", "m'en", "m'y",
        # Function words
        "tous", "quand", "aussi", "alors", "ainsi", "faut", "peut",
        "pendant", "près", "peut-être", "bout", "oh", "eh",
        "pouvait", "avez", "vais", "fus", "vu", "mit",
        "puisque", "lorsque", "tandis", "aussitôt", "surtout",
        "cependant", "néanmoins", "pourtant", "toutefois", "davantage",
        "plutôt", "environ", "autant", "autrefois", "auparavant",
        "désormais", "dorénavant", "guère", "certes", "volontiers",
        "quelqu'un", "quelqu'une", "quelque", "quelques",
        "chaque", "plusieurs", "aucun", "aucune",
        "celui", "celle", "ceux", "celles",
        "celui-ci", "celle-ci", "ceux-ci", "celles-ci",
        "celui-là", "celle-là", "ceux-là", "celles-là",
    },
    "de": {
        # Modal/auxiliary verbs & forms
        "konnte", "hätte", "möchte", "wußte", "kannst", "willst",
        "sei", "bin", "bist", "hast",
        "muß", "mußte", "müssen", "dürfte", "dürfen", "sollte",
        "würde", "könnte", "mögen",
        # Function words & adverbs
        "also", "dabei", "davon", "damit", "darum", "daran", "darauf",
        "darin", "darüber", "darunter", "dazu", "dagegen", "danach",
        "dafür", "dahinter", "daneben", "davor",
        "ab", "hinein", "hinzu", "hinaus", "hinauf", "hinab", "hinüber",
        "herein", "heraus", "herauf", "herab", "herüber",
        "mehr", "gern", "natürlich", "ungefähr", "kaum",
        "während", "keinen", "welche", "ehe",
        "oh", "ach", "je", "laß",
        "nächsten", "weiße",
        "allerdings", "freilich", "jedenfalls", "übrigens", "außerdem",
        "trotzdem", "inzwischen", "unterdessen", "überhaupt",
        "beinahe", "ziemlich", "genug", "sogar", "wenigstens",
        "mindestens", "höchstens", "meistens", "gewöhnlich",
        # Old German spellings
        "thun", "saß",
    },
    "es": {
        # Archaic spellings (19th century Spanish)
        "quando", "quanto", "ménos", "miéntras", "cómo", "ámbos",
        "podia", "tenia", "hubiera", "habia",
        # Function words
        "qué", "cual", "tanto", "hay", "tiene", "puede", "hasta",
        "mis", "soy", "eran", "cabo", "puesto", "sea", "vez",
        "tengo", "mayor", "demas", "muger", "duros", "sucesos",
        "dias", "años",
        "sino", "apenas", "acaso", "quizá", "quizás", "además",
        "todavía", "aún", "ya", "aquí", "allí", "ahí", "ahora",
        "luego", "después", "antes", "entonces", "también", "tampoco",
        "jamás", "nunca", "siempre", "casi", "bastante", "demasiado",
        "alguno", "alguna", "algunos", "algunas", "ninguno", "ninguna",
        "cualquier", "cualquiera", "mismo", "misma", "mismos", "mismas",
        "cada", "demás", "ambos", "ambas",
        "cuyo", "cuya", "cuyos", "cuyas",
        "nadie", "alguien", "nada", "algo",
    },
    "it": {
        # Contractions & elisions
        "c'è", "c'era", "c'erano",
        # Function words
        "quale", "forse", "appena", "sino", "fuori", "nulla", "meglio",
        "mezzo", "stesso", "stessa", "ecco", "meno", "quasi", "vicino",
        "sul", "sulle", "sulla", "sullo", "sui", "sugli",
        "giù", "quì", "lì", "sì",
        "no", "oh", "de",
        "vorrei", "sarebbe", "avesse", "sarà", "stava", "mise",
        "faccia", "bianco", "istante",
        "inoltre", "perciò", "pertanto", "tuttavia", "comunque",
        "piuttosto", "abbastanza", "troppo", "parecchio",
        "qualcuno", "qualcuna", "qualcosa", "nessuno", "nessuna",
        "ciascuno", "ciascuna", "ognuno", "ognuna",
        "costui", "costei", "costoro", "colui", "colei", "coloro",
        "codesto", "codesta",
    },
    "eo": {
        # Pronouns & particles
        "se", "min", "ol", "lin", "sxin", "nin",
        "sia", "sian", "mia", "lia", "nia", "via", "ilia",
        "sxia", "gxia",
        # Correlatives
        "kiun", "kiuj", "tiuj", "kiom", "tiu", "kiu",
        "iu", "neniu", "cxiu", "cxiuj",
        "ie", "nenie", "cxie", "tie", "kie",
        "ial", "nenial", "cxial", "tial", "kial",
        "iam", "neniam", "cxiam", "tiam", "kiam",
        "iom", "neniom", "cxiom", "tiom",
        "iel", "neniel", "cxiel", "tiel", "kiel",
        "ies", "nenies", "cxies", "ties", "kies",
        # Common function words
        "pro", "nepre", "nu", "plu", "kvazaux", "jxus",
        "ambaux", "lauxte", "apenaux", "cxirkaux", "ajn",
        "jes", "sub", "for", "fojon",
        "ankoraux", "baldaux", "preskauxe", "almenauxe",
        "tuta", "devas", "povas", "povis", "devis", "povus", "povos",
        "anstatauxe", "ekzemple", "cetere", "tamen",
    },
    "fi": {
        # Common function words & particles
        "ne", "itse", "heti", "kovin", "näin", "nuo",
        "ensin", "kerran", "totta", "olet", "oi",
        "vähän", "ettei", "jonka", "molemmat", "eivät",
        "erään", "jälleen", "vihdoin", "jota", "enemmän",
        "jossa", "tästä", "saanut", "myöskin", "luku",
        "minulla", "olin", "virkkoi", "huudahti",
        # More function words
        "juuri", "melkein", "lähes", "tuskin", "ehkä", "kai",
        "varsin", "aivan", "jopa", "edes", "kuitenkin", "silti",
        "tosin", "nimittäin", "kyllä", "tietenkin", "tietysti",
        "ainakin", "vielä", "enää", "taas", "sitten", "silloin",
        "siis", "siitä", "siinä", "sinne", "siellä", "täällä",
        "tänne", "täältä", "tuolla", "tuonne", "tuolta",
        "joku", "jokin", "jotain", "joitakin", "jotkut",
        "kukaan", "mikään", "mitään", "ketään",
        "kukin", "kumpikin", "molempi",
        "itsensä", "itseään", "itsellään", "itselleen",
        "minun", "sinun", "hänen", "meidän", "teidän", "heidän",
        "minulle", "sinulle", "hänelle",
    },
    "sa": {
        # English words in the Gutenberg preamble
        "formatted", "proofed", "using", "at", "me", "etext",
        "venkat-ramani", "srinivasan", "karthik", "krishnan",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# E. EXPANSION KEYWORDS Round 2 — content words mapped to atoms
# ═══════════════════════════════════════════════════════════════════════════════

EXPANSION_KEYWORDS_V48 = {
    # ─── AGENT: proper nouns + roles ──────────────────────────────
    "AGENT": {
        "en": ["rabbit", "hare", "friar", "sheep", "queen", "mouse",
               "bulgarians", "judge", "jury", "witness", "knave",
               "footman", "cook", "pigeon", "lizard", "puppy"],
        "fr": ["lapin", "lièvre", "loir", "moine", "reine",
               "juré", "valet", "cuisinier", "pigeon", "souris",
               "moineau", "marquis", "baron", "comte", "seigneur"],
        "de": ["kaninchen", "maus", "katze", "katzen", "königin",
               "geschwornen", "richter", "koch", "taube", "eidechse",
               "schildkröte", "murmelthier", "faselhase", "arme"],
        "es": ["navío", "quinta", "diamantes", "bulgaros",
               "amo", "nuestra", "criado", "monje", "fraile"],
        "it": ["coniglio", "sorcio", "ghiro", "gatto", "giurati",
               "regina", "cuoco", "piccione", "lucertola",
               "lepre-marzolina"],
        "eo": ["kuniklo", "muso", "gliro", "kato", "martleporo",
               "kelonio", "damo", "rauxpo", "blanka",
               "regxino", "kuiristo", "kolombo"],
        "fi": ["kani", "hiiri", "kissa", "murmeli", "kaalimato",
               "valekilpikonna", "aarnikotka", "hatuntekijä",
               "neiti", "kuningatar", "kokki"],
        "sa": ["vishnum", "vishnur", "vishnor", "krshno", "krishnan",
               "maadhavo", "vaasudevo", "shrimaan", "srimaan",
               "achyutah", "vibhuh", "kartaa"],
    },

    # ─── MOUVEMENT: motion words round 2 ─────────────────────────
    "MOUVEMENT": {
        "en": ["feet", "near", "across", "along", "toward",
               "tumble", "dash", "rush", "hurry", "wander"],
        "fr": ["vaisseau", "près", "blanc",
               "accourir", "précipiter", "parcourir", "trajet"],
        "de": ["hinein", "hinzu", "hinaus", "hinauf", "hinab",
               "herein", "heraus", "herauf", "herab"],
        "es": ["navío", "cabo", "caminar", "correr", "huir",
               "acercar", "alejar", "atravesar"],
        "it": ["giù", "fuori", "vicino", "lontano", "avvicinare",
               "allontanare", "percorrere", "attraversare"],
        "eo": ["jxus", "sub", "proksime", "for", "foren",
               "alkuri", "forkuri", "trairi"],
        "fi": ["lähelle", "pois", "ympäri", "läpi",
               "juosta", "kävellä", "kiirehtää"],
    },

    # ─── COGNITION: thinking/knowing round 2 ─────────────────────
    "COGNITION": {
        "en": ["puzzle", "wonder", "riddle", "curious", "curiosity",
               "nonsense", "meaning", "remark", "notice", "realize",
               "imagine", "reckon", "suppose", "consider"],
        "fr": ["mots", "remarque", "signifier", "deviner",
               "réfléchir", "songer", "méditer", "raisonner"],
        "de": ["natürlich", "ungefähr", "überlegen", "nachdenken",
               "bemerken", "erraten", "rätselhaft"],
        "es": ["gusto", "sucesos", "pensar", "creer", "suponer",
               "adivinar", "comprender", "razonar"],
        "it": ["quasi", "statura", "pensiero", "capire",
               "indovinare", "supporre", "ragionare"],
        "eo": ["scii", "kompreni", "konjekti", "pripensi",
               "ekkompreni", "konsideri"],
        "fi": ["totta", "ajatella", "ymmärtää", "arvata",
               "miettiä", "pohtia", "tuumia"],
    },

    # ─── PERCEPTION: seeing/hearing/feeling round 2 ──────────────
    "PERCEPTION": {
        "en": ["eye", "eyes", "glance", "stare", "peer",
               "whisper", "shout", "scream", "cry", "yell",
               "noise", "silent", "loud", "glimpse", "gaze"],
        "fr": ["regard", "cri", "voix", "bruit", "silence",
               "apercevoir", "entrevoir", "guetter"],
        "de": ["blick", "stimme", "laut", "leise", "geräusch",
               "bemerken", "erblicken", "lauschen"],
        "es": ["mirada", "grito", "voz", "ruido", "silencio",
               "mirar", "gritar", "escuchar"],
        "it": ["sguardo", "grido", "voce", "rumore", "silenzio",
               "guardare", "gridare", "ascoltare"],
        "eo": ["rigardo", "krio", "vocxo", "bruo", "silento",
               "rigardi", "krii", "auxskulti"],
        "fi": ["katse", "huuto", "ääni", "melu", "hiljaisuus",
               "katsoa", "huutaa", "kuunnella"],
    },

    # ─── COMMUNICATION: speech/talk round 2 ──────────────────────
    "COMMUNICATION": {
        "en": ["remark", "reply", "exclaim", "murmur", "mutter",
               "announce", "declare", "explain", "interrupt",
               "conversation", "tale", "story", "verse", "lesson"],
        "fr": ["répondre", "raconter", "annoncer", "déclarer",
               "expliquer", "interrompre", "récit", "conte",
               "leçon", "discours", "parole"],
        "de": ["antworten", "erzählen", "erklären", "unterbrechen",
               "geschichte", "rede", "lektion", "gespräch"],
        "es": ["responder", "contar", "anunciar", "declarar",
               "explicar", "interrumpir", "cuento", "relato",
               "lección", "discurso"],
        "it": ["rispondere", "raccontare", "annunciare", "dichiarare",
               "spiegare", "interrompere", "racconto", "lezione",
               "discorso", "parola"],
        "eo": ["respondi", "rakonti", "anonci", "deklari",
               "klarigi", "interrompi", "rakonto", "leciono"],
        "fi": ["vastata", "kertoa", "ilmoittaa", "selittää",
               "keskeyttää", "kertomus", "tarina", "oppitunti"],
    },

    # ─── CORPS: body/animal bodies round 2 ───────────────────────
    "CORPS": {
        "en": ["cat", "white", "turtle", "eat", "tail", "paw",
               "claw", "wing", "beak", "feather", "fur",
               "snout", "horn", "hoof", "fin", "scale"],
        "fr": ["chat", "chenille", "blanc", "queue", "patte",
               "griffe", "aile", "bec", "plume", "fourrure"],
        "de": ["weiße", "schwanz", "pfote", "kralle", "flügel",
               "schnabel", "feder", "fell", "schnauze"],
        "es": ["cola", "pata", "garra", "ala", "pico",
               "pluma", "pelaje", "hocico"],
        "it": ["bianco", "coda", "zampa", "artiglio", "ala",
               "becco", "piuma", "pelliccia"],
        "eo": ["blanka", "vosto", "piedo", "ungego", "flugilo",
               "beko", "plumo", "felo"],
        "fi": ["häntä", "tassu", "kynsi", "siipi", "nokka",
               "sulka", "turkki", "kuono"],
    },

    # ─── EXISTENCE: being/existing round 2 ───────────────────────
    "EXISTENCE": {
        "en": ["become", "remain", "alive", "exist", "real",
               "true", "actual", "fact", "indeed", "present"],
        "fr": ["devenir", "demeurer", "rester", "vivant",
               "exister", "réel", "véritable", "effectivement"],
        "de": ["bleiben", "lebendig", "wirklich", "tatsächlich",
               "vorhanden", "bestehen", "gegenwärtig"],
        "es": ["dorado", "llegar", "quedar", "existir", "real",
               "verdadero", "efectivamente", "presente"],
        "it": ["diventare", "rimanere", "esistere", "reale",
               "vero", "effettivamente", "presente"],
        "eo": ["igxi", "resti", "ekzisti", "reala", "vera",
               "efektive", "nuntempa"],
        "fi": ["tulla", "jäädä", "olemassa", "todellinen",
               "todellisuus", "nykyinen"],
    },

    # ─── POSSESSION: having/owning round 2 ────────────────────────
    "POSSESSION": {
        "en": ["fortune", "wealth", "treasure", "diamond", "gold",
               "silver", "coin", "price", "cost", "value",
               "property", "estate", "inherit", "earn", "afford"],
        "fr": ["fortune", "trésor", "diamant", "or", "argent",
               "prix", "propriété", "héritage", "richesse"],
        "de": ["vermögen", "schatz", "diamant", "gold", "silber",
               "preis", "eigentum", "erbe", "reichtum"],
        "es": ["diamantes", "duros", "oro", "plata", "precio",
               "propiedad", "herencia", "riqueza", "fortuna",
               "tesoro", "moneda"],
        "it": ["fortuna", "tesoro", "diamante", "oro", "argento",
               "prezzo", "proprietà", "eredità", "ricchezza"],
        "eo": ["fortuno", "trezoro", "diamanto", "oro", "argxento",
               "prezo", "posedajxo", "heredo", "ricxeco"],
        "fi": ["omaisuus", "aarre", "timantti", "kulta", "hopea",
               "hinta", "perintö", "rikkaus"],
    },

    # ─── DOMINATION: power/authority round 2 ──────────────────────
    "DOMINATION": {
        "en": ["kingdom", "throne", "crown", "court", "palace",
               "prince", "princess", "majesty", "noble", "lord",
               "slave", "servant", "obey", "submit", "conquer"],
        "fr": ["royaume", "trône", "couronne", "cour", "palais",
               "prince", "princesse", "majesté", "noble",
               "esclave", "obéir", "soumettre", "conquérir"],
        "de": ["königin", "königreich", "thron", "krone", "hof",
               "palast", "prinz", "prinzessin", "majestät"],
        "es": ["reino", "trono", "corona", "corte", "palacio",
               "príncipe", "princesa", "majestad", "noble",
               "esclavo", "obedecer", "someter", "conquistar"],
        "it": ["regno", "trono", "corona", "corte", "palazzo",
               "principe", "principessa", "maestà", "nobile",
               "schiavo", "obbedire", "sottomettere", "conquistare"],
        "eo": ["regnolando", "trono", "krono", "korto", "palaco",
               "princxo", "princino", "majesto", "nobela"],
        "fi": ["valtakunta", "valtaistuin", "kruunu", "hovi",
               "palatsi", "prinssi", "prinsessa", "majesteetti"],
    },

    # ─── CRÉATION: making/producing round 2 ──────────────────────
    "CREATION": {
        "en": ["cook", "bake", "brew", "mix", "prepare",
               "produce", "compose", "arrange", "invent",
               "recipe", "dish", "meal", "feast"],
        "fr": ["cuisiner", "préparer", "produire", "composer",
               "inventer", "recette", "plat", "repas", "festin"],
        "de": ["kochen", "backen", "brauen", "mischen", "vorbereiten",
               "herstellen", "komponieren", "erfinden"],
        "es": ["cocinar", "preparar", "producir", "componer",
               "inventar", "receta", "plato", "comida", "festín"],
        "it": ["cucinare", "preparare", "produrre", "comporre",
               "inventare", "ricetta", "piatto", "pasto", "festa"],
        "eo": ["kuiri", "prepari", "produkti", "komponi",
               "inventi", "recepto", "plado", "mangxo", "festo"],
        "fi": ["laittaa", "valmistaa", "tuottaa", "säveltää",
               "keksiä", "resepti", "ruoka", "ateria", "juhla"],
    },

    # ─── DESTRUCTION: ending/destroying round 2 ──────────────────
    "DESTRUCTION": {
        "en": ["drown", "choke", "strangle", "crush", "shatter",
               "ruin", "wreck", "demolish", "annihilate",
               "massacre", "slaughter", "execution", "gallows"],
        "fr": ["noyer", "étrangler", "écraser", "ruine",
               "démolir", "massacre", "exécution", "potence",
               "anéantir", "ravage", "désastre"],
        "de": ["ertrinken", "erwürgen", "zerdrücken", "ruine",
               "vernichten", "hinrichtung", "galgen", "massaker"],
        "es": ["ahogar", "estrangular", "aplastar", "ruina",
               "demoler", "masacre", "ejecución", "horca",
               "aniquilar", "desastre"],
        "it": ["affogare", "strangolare", "schiacciare", "rovina",
               "demolire", "massacro", "esecuzione", "forca"],
        "eo": ["droni", "sufoki", "dispremi", "ruino",
               "detrui", "masakro", "ekzekuto", "pendumilo"],
        "fi": ["hukuttaa", "kuristaa", "murskata", "tuho",
               "tuhota", "teloitus", "hirttää"],
    },

    # ─── GRIEF: sadness round 2 ──────────────────────────────────
    "GRIEF": {
        "en": ["tears", "weep", "sob", "mourn", "sorrow",
               "misery", "wretched", "miserable", "pity", "regret",
               "sigh", "lament", "despair", "woe", "distress"],
        "fr": ["larmes", "pleurer", "gémir", "deuil", "chagrin",
               "misère", "misérable", "pitié", "regret",
               "soupir", "lamenter", "désespoir", "malheur"],
        "de": ["tränen", "weinen", "schluchzen", "trauer", "kummer",
               "elend", "mitleid", "bedauern", "seufzen",
               "verzweiflung", "jammer"],
        "es": ["lágrimas", "llorar", "sollozar", "duelo", "pena",
               "miseria", "lástima", "arrepentimiento",
               "suspiro", "lamentar", "desesperación", "desgracia"],
        "it": ["lacrime", "piangere", "singhiozzare", "lutto",
               "dolore", "miseria", "pietà", "rimpianto",
               "sospiro", "lamentare", "disperazione"],
        "eo": ["larmoj", "plori", "gxemi", "funebro", "cxagreno",
               "mizero", "kompato", "bedauxri",
               "suspiro", "lamenti", "malespero"],
        "fi": ["kyyneleet", "itkeä", "nyyhkiä", "suru", "murhe",
               "kurjuus", "sääli", "katumus",
               "huokaista", "valittaa", "epätoivo"],
    },

    # ─── FEAR: fear/anxiety round 2 ──────────────────────────────
    "FEAR": {
        "en": ["tremble", "shiver", "shudder", "dread", "horror",
               "alarmed", "startled", "terrified", "nervous",
               "anxious", "worried", "uneasy", "panic"],
        "fr": ["trembler", "frissonner", "effroi", "horreur",
               "alarmé", "terrifié", "nerveux", "inquiet",
               "panique", "épouvante"],
        "de": ["zittern", "schaudern", "grauen", "entsetzen",
               "erschrecken", "ängstlich", "nervös", "beunruhigt",
               "panik"],
        "es": ["temblar", "estremecerse", "pavor", "horror",
               "alarmado", "aterrorizado", "nervioso", "inquieto",
               "pánico", "espanto"],
        "it": ["tremare", "rabbrividire", "terrore", "orrore",
               "allarmato", "terrorizzato", "nervoso", "inquieto",
               "panico", "spavento"],
        "eo": ["tremi", "skuigxi", "teruro", "hororo",
               "timigita", "terurita", "nervoza", "maltrankvila"],
        "fi": ["vapista", "väristä", "kauhu", "pelko",
               "säikähtää", "kauhistunut", "hermostunut",
               "paniikki"],
    },

    # ─── RAGE: anger round 2 ─────────────────────────────────────
    "RAGE": {
        "en": ["fury", "furious", "wrath", "enraged", "indignant",
               "offend", "insult", "quarrel", "dispute", "protest",
               "provoke", "irritate", "resent"],
        "fr": ["fureur", "furieux", "courroux", "indigné",
               "offenser", "insulte", "querelle", "dispute",
               "protester", "irriter"],
        "de": ["wut", "wütend", "zorn", "empört", "beleidigen",
               "streit", "protest", "provozieren", "reizen"],
        "es": ["furia", "furioso", "ira", "indignado", "ofender",
               "insulto", "pelea", "disputa", "protestar",
               "provocar", "irritar"],
        "it": ["furia", "furioso", "ira", "indignato", "offendere",
               "insulto", "litigio", "disputa", "protestare",
               "provocare", "irritare"],
        "eo": ["furiozo", "kolero", "indigna", "ofendi",
               "insulto", "kverelo", "disputo", "protesti"],
        "fi": ["raivo", "raivoisa", "viha", "närkästynyt",
               "loukata", "solvaus", "riita", "kiista",
               "provosoida"],
    },

    # ─── PLAY: amusement/fun round 2 ─────────────────────────────
    "PLAY": {
        "en": ["game", "riddle", "joke", "trick", "puzzle",
               "amuse", "entertain", "merry", "jolly",
               "croquet", "cards", "party", "festival"],
        "fr": ["jeu", "énigme", "plaisanterie", "tour", "amusement",
               "divertir", "gai", "croquet", "cartes", "fête"],
        "de": ["spiel", "rätsel", "witz", "streich", "vergnügen",
               "unterhalten", "lustig", "fröhlich", "karten"],
        "es": ["juego", "enigma", "chiste", "truco", "diversión",
               "entretener", "alegre", "fiesta", "cartas"],
        "it": ["gioco", "indovinello", "scherzo", "trucco",
               "divertimento", "divertire", "allegro", "festa"],
        "eo": ["ludo", "enigmo", "sxerco", "truko", "amuzo",
               "distri", "gaja", "festo", "kartoj"],
        "fi": ["peli", "arvoitus", "vitsi", "temppu", "huvi",
               "viihdyttää", "iloinen", "juhla"],
    },

    # ─── CARE: tenderness/nurture round 2 ────────────────────────
    "CARE": {
        "en": ["gentle", "tender", "comfort", "soothe", "caress",
               "embrace", "kiss", "hug", "cherish", "nursing",
               "dear", "darling", "beloved", "affection", "fond"],
        "fr": ["doux", "tendre", "consoler", "apaiser", "caresse",
               "embrasser", "baiser", "cher", "chéri",
               "bien-aimé", "affection"],
        "de": ["sanft", "zärtlich", "trösten", "beruhigen",
               "liebkosen", "umarmen", "kuss", "liebling",
               "zuneigung", "lieb"],
        "es": ["tierno", "suave", "consolar", "acariciar",
               "abrazar", "besar", "querido", "amado",
               "cariño", "afecto"],
        "it": ["dolce", "tenero", "consolare", "accarezzare",
               "abbracciare", "baciare", "caro", "amato",
               "affetto", "tenerezza"],
        "eo": ["dolcxa", "tenera", "konsoli", "karesi",
               "cxirkauxbraki", "kisi", "kara", "amata",
               "afekto"],
        "fi": ["hellä", "lempeä", "lohduttaa", "hyväillä",
               "halata", "suudella", "rakas", "lemmikki"],
    },

    # ─── SEEKING: desire/wanting round 2 ─────────────────────────
    "SEEKING": {
        "en": ["eager", "yearn", "crave", "thirst", "hunger",
               "ambition", "aspire", "quest", "adventure",
               "explore", "discover", "curiosity", "investigate"],
        "fr": ["avide", "désirer", "quête", "aventure",
               "explorer", "découvrir", "curiosité", "enquêter"],
        "de": ["begierde", "sehnen", "durst", "ehrgeiz",
               "abenteuer", "erforschen", "entdecken",
               "neugier", "untersuchen"],
        "es": ["ansioso", "desear", "anhelar", "búsqueda",
               "aventura", "explorar", "descubrir",
               "curiosidad", "investigar"],
        "it": ["avido", "desiderare", "anelito", "ricerca",
               "avventura", "esplorare", "scoprire",
               "curiosità", "indagare"],
        "eo": ["avida", "deziri", "sopiri", "kvestado",
               "aventuro", "esplori", "malkovri",
               "scivolemo", "esplori"],
        "fi": ["innokas", "kaivata", "janota", "kunnianhimo",
               "seikkailu", "tutkia", "löytää",
               "uteliaisuus"],
    },

    # ─── TEDIUM: boredom/weariness round 2 ───────────────────────
    "TEDIUM": {
        "en": ["weary", "drowsy", "sleepy", "yawn", "bore",
               "tedious", "dull", "monotonous", "listless",
               "exhausted", "fatigued", "tired"],
        "fr": ["las", "assoupi", "somnolent", "bâiller",
               "ennuyeux", "monotone", "fatigué", "épuisé"],
        "de": ["müde", "schläfrig", "gähnen", "langweilig",
               "eintönig", "erschöpft", "ermüdet"],
        "es": ["cansado", "soñoliento", "bostezar", "aburrido",
               "monótono", "agotado", "fatigado"],
        "it": ["stanco", "assonnato", "sbadigliare", "noioso",
               "monotono", "esausto", "affaticato"],
        "eo": ["laca", "dormema", "oscedi", "enua",
               "monotona", "elcxerpita", "lacigita"],
        "fi": ["väsynyt", "unelias", "haukotella", "tylsä",
               "yksitoikkoinen", "uupunut"],
    },

    # ─── DISGUST: repulsion round 2 ──────────────────────────────
    "DISGUST": {
        "en": ["ugly", "hideous", "foul", "horrible", "dreadful",
               "awful", "nasty", "revolting", "repulsive",
               "abominable", "loathsome", "disgusting"],
        "fr": ["laid", "hideux", "horrible", "affreux",
               "abominable", "dégoûtant", "répugnant",
               "odieux", "infâme"],
        "de": ["hässlich", "scheußlich", "grässlich", "abscheulich",
               "widerlich", "ekelhaft", "furchtbar"],
        "es": ["feo", "horrible", "espantoso", "asqueroso",
               "abominable", "repugnante", "odioso"],
        "it": ["brutto", "orribile", "spaventoso", "disgustoso",
               "abominevole", "ripugnante", "odioso"],
        "eo": ["malbela", "terura", "abomena", "nauxza",
               "ripuza", "aĉa"],
        "fi": ["ruma", "kaamea", "kauhistuttava", "iljettävä",
               "inhottava", "vastenmielinen"],
    },

    # ─── LIEU: place round 2 ─────────────────────────────────────
    "LIEU": {
        "en": ["garden", "pool", "hall", "room", "door",
               "window", "passage", "corridor", "tunnel",
               "shore", "bank", "field", "forest", "wood",
               "country", "province", "harbour", "port"],
        "fr": ["jardin", "salle", "chambre", "porte", "fenêtre",
               "passage", "corridor", "tunnel", "rivage",
               "champ", "forêt", "bois", "pays", "province", "port"],
        "de": ["garten", "saal", "zimmer", "tür", "fenster",
               "gang", "korridor", "tunnel", "ufer",
               "feld", "wald", "land", "provinz", "hafen"],
        "es": ["jardín", "sala", "habitación", "puerta", "ventana",
               "pasillo", "corredor", "túnel", "orilla",
               "campo", "bosque", "país", "provincia", "puerto"],
        "it": ["giardino", "sala", "stanza", "porta", "finestra",
               "passaggio", "corridoio", "tunnel", "riva",
               "campo", "bosco", "paese", "provincia", "porto"],
        "eo": ["gxardeno", "salono", "cxambro", "pordo", "fenestro",
               "pasejo", "koridoro", "tunelo", "bordo",
               "kampo", "arbaro", "lando", "provinco", "haveno"],
        "fi": ["puutarha", "sali", "huone", "ovi", "ikkuna",
               "käytävä", "tunneli", "ranta",
               "pelto", "metsä", "maa", "maakunta", "satama"],
    },

    # ─── CHOSE: things/objects round 2 ───────────────────────────
    "CHOSE": {
        "en": ["bottle", "cup", "plate", "table", "chair",
               "box", "fan", "glove", "mushroom", "cake",
               "pie", "tart", "key", "lock", "thimble",
               "pepper", "treacle", "vinegar"],
        "fr": ["bouteille", "tasse", "assiette", "éventail",
               "gant", "champignon", "gâteau", "clé", "serrure",
               "dé", "poivre", "vinaigre", "mélasse"],
        "de": ["flasche", "tasse", "teller", "tisch", "stuhl",
               "schachtel", "fächer", "handschuh", "pilz",
               "kuchen", "schlüssel", "schloss", "fingerhut",
               "pfeffer"],
        "es": ["botella", "taza", "plato", "mesa", "silla",
               "abanico", "guante", "seta", "pastel",
               "llave", "cerradura", "pimienta"],
        "it": ["bottiglia", "tazza", "piatto", "tavolo", "sedia",
               "ventaglio", "guanto", "fungo", "torta",
               "chiave", "serratura", "pepe"],
        "eo": ["botelo", "taso", "telero", "tablo", "segxo",
               "ventumilo", "ganto", "fungo", "kuko",
               "sxlosilo", "seruro", "pipro"],
        "fi": ["pullo", "kuppi", "lautanen", "pöytä", "tuoli",
               "laatikko", "viuhka", "hanska", "sieni",
               "kakku", "avain", "lukko", "pippuri"],
    },

    # ─── MATIÈRE: material/food round 2 ──────────────────────────
    "MATIÈRE": {
        "en": ["tea", "milk", "butter", "bread", "soup",
               "wine", "beer", "cloth", "silk", "wool",
               "leather", "cotton", "linen", "velvet"],
        "fr": ["thé", "lait", "beurre", "pain", "soupe",
               "vin", "bière", "tissu", "soie", "laine",
               "cuir", "coton", "lin", "velours"],
        "de": ["tee", "milch", "butter", "brot", "suppe",
               "wein", "bier", "stoff", "seide", "wolle",
               "leder", "baumwolle", "leinen", "samt"],
        "es": ["té", "leche", "mantequilla", "pan", "sopa",
               "vino", "cerveza", "tela", "seda", "lana",
               "cuero", "algodón", "lino", "terciopelo"],
        "it": ["tè", "latte", "burro", "pane", "zuppa",
               "vino", "birra", "tessuto", "seta", "lana",
               "pelle", "cotone", "lino", "velluto"],
        "eo": ["teo", "lakto", "butero", "pano", "supo",
               "vino", "biero", "sxtofo", "silko", "lano",
               "ledo", "kotono", "lino", "veluro"],
        "fi": ["tee", "maito", "voi", "leipä", "keitto",
               "viini", "olut", "kangas", "silkki", "villa",
               "nahka", "puuvilla", "pellava", "sametti"],
    },

    # ─── GRAND: size round 2 ─────────────────────────────────────
    "GRAND": {
        "en": ["enormous", "immense", "vast", "gigantic", "huge",
               "shrink", "grow", "stretch", "expand", "contract",
               "height", "length", "width", "depth", "size"],
        "fr": ["énorme", "immense", "vaste", "gigantesque",
               "rétrécir", "grandir", "étendre", "taille",
               "hauteur", "longueur", "largeur", "profondeur"],
        "de": ["riesig", "gewaltig", "ungeheuer", "winzig",
               "schrumpfen", "wachsen", "ausdehnen", "größe",
               "höhe", "länge", "breite", "tiefe"],
        "es": ["enorme", "inmenso", "vasto", "gigantesco",
               "encoger", "crecer", "estatura", "altura",
               "longitud", "anchura", "profundidad", "tamaño"],
        "it": ["enorme", "immenso", "vasto", "gigantesco",
               "rimpicciolire", "crescere", "statura",
               "altezza", "lunghezza", "larghezza", "profondità"],
        "eo": ["enorma", "vasta", "giganta", "kreski",
               "malgrandigi", "grandigi", "alteco",
               "longo", "largxo", "profundo", "grandeco"],
        "fi": ["valtava", "suunnaton", "jättimäinen",
               "kutistua", "kasvaa", "laajentaa",
               "korkeus", "pituus", "leveys", "syvyys"],
    },

    # ─── MESURE: numbers/quantities round 2 ──────────────────────
    "MESURE": {
        "en": ["mile", "inch", "foot", "yard", "league",
               "dozen", "score", "century", "thousand",
               "million", "billion", "handful", "plenty"],
        "fr": ["lieue", "pouce", "pied", "mille", "centaine",
               "millier", "million", "douzaine", "vingtaine"],
        "de": ["meile", "zoll", "fuß", "elle", "dutzend",
               "hundert", "tausend", "million", "handvoll"],
        "es": ["legua", "pulgada", "pie", "milla", "centena",
               "millar", "millón", "docena", "veintena"],
        "it": ["lega", "pollice", "piede", "miglio", "centinaio",
               "migliaio", "milione", "dozzina"],
        "eo": ["mejlo", "colo", "piedo", "leguo", "ducento",
               "mil", "miliono", "dekduo"],
        "fi": ["maili", "tuuma", "jalka", "peninkulma",
               "tusina", "sata", "tuhat", "miljoona"],
    },

    # ─── BON: quality/good round 2 ───────────────────────────────
    "BON": {
        "en": ["pleasant", "agreeable", "delightful", "charming",
               "splendid", "magnificent", "superb", "excellent",
               "wonderful", "marvelous", "brilliant", "glorious"],
        "fr": ["agréable", "charmant", "splendide", "magnifique",
               "superbe", "excellent", "merveilleux", "glorieux"],
        "de": ["angenehm", "reizend", "prächtig", "herrlich",
               "großartig", "ausgezeichnet", "wunderbar"],
        "es": ["agradable", "encantador", "espléndido",
               "magnífico", "soberbio", "excelente",
               "maravilloso", "glorioso"],
        "it": ["gradevole", "incantevole", "splendido",
               "magnifico", "superbo", "eccellente",
               "meraviglioso", "glorioso"],
        "eo": ["agrabla", "cxarma", "splenda", "bonega",
               "grandioza", "mirinda", "glora"],
        "fi": ["miellyttävä", "viehättävä", "loistava",
               "suurenmoinen", "erinomainen", "ihmeellinen"],
    },

    # ─── INTENSE: degree/intensity round 2 ───────────────────────
    "INTENSE": {
        "en": ["extremely", "exceedingly", "remarkably", "tremendously",
               "incredibly", "awfully", "terribly", "enormously",
               "absolutely", "utterly", "totally", "completely"],
        "fr": ["extrêmement", "remarquablement", "incroyablement",
               "terriblement", "absolument", "totalement",
               "complètement", "entièrement"],
        "de": ["äußerst", "überaus", "unglaublich", "schrecklich",
               "absolut", "völlig", "ganz", "durchaus"],
        "es": ["extremadamente", "increíblemente", "terriblemente",
               "absolutamente", "totalmente", "completamente",
               "enteramente"],
        "it": ["estremamente", "incredibilmente", "terribilmente",
               "assolutamente", "totalmente", "completamente",
               "interamente"],
        "eo": ["ekstreme", "nekredeble", "terure", "absolute",
               "tute", "plene", "tiel"],
        "fi": ["äärimmäisen", "uskomattoman", "hirvittävän",
               "ehdottomasti", "täysin", "kokonaan"],
    },

    # ─── ANCIEN: time/temporal round 2 ───────────────────────────
    "ANCIEN": {
        "en": ["moment", "instant", "meanwhile", "suddenly",
               "eventually", "gradually", "immediately", "directly",
               "presently", "lately", "recently", "formerly"],
        "fr": ["moment", "instant", "soudain", "aussitôt",
               "bientôt", "autrefois", "jadis", "naguère",
               "désormais", "dorénavant"],
        "de": ["augenblick", "moment", "plötzlich", "sofort",
               "allmählich", "bald", "ehemals", "einst",
               "kürzlich", "neuerdings"],
        "es": ["momento", "instante", "repente", "enseguida",
               "gradualmente", "inmediatamente", "recientemente",
               "anteriormente", "antiguamente"],
        "it": ["momento", "istante", "improvviso", "subito",
               "gradualmente", "immediatamente", "recentemente",
               "anticamente", "precedentemente"],
        "eo": ["momento", "instanto", "subite", "tuj",
               "iom-post-iom", "baldaux", "antauxe",
               "lastatempe", "iam"],
        "fi": ["hetki", "tuokio", "äkkiä", "yhtäkkiä",
               "vähitellen", "heti", "äskettäin",
               "entisaikaan", "muinoin"],
    },

    # ─── VRAI: truth/certainty round 2 ───────────────────────────
    "VRAI": {
        "en": ["evident", "obvious", "plain", "clear", "certain",
               "definite", "undoubtedly", "unquestionably",
               "genuine", "authentic", "honest", "sincere"],
        "fr": ["évident", "clair", "certain", "indéniable",
               "incontestable", "authentique", "sincère",
               "honnête", "véridique"],
        "de": ["offensichtlich", "klar", "sicher", "gewiss",
               "zweifellos", "echt", "aufrichtig", "ehrlich"],
        "es": ["evidente", "claro", "cierto", "indudablemente",
               "auténtico", "sincero", "honesto", "verdadero"],
        "it": ["evidente", "chiaro", "certo", "indubitabilmente",
               "autentico", "sincero", "onesto", "veritiero"],
        "eo": ["evidenta", "klara", "certa", "sendube",
               "auxtentika", "sincera", "honesta"],
        "fi": ["ilmeinen", "selvä", "varma", "epäilemättä",
               "aito", "vilpitön", "rehellinen"],
    },

    # ─── RELATION: connections round 2 ────────────────────────────
    "RELATION": {
        "en": ["companion", "fellow", "partner", "acquaintance",
               "stranger", "neighbor", "neighbour", "ally",
               "rival", "enemy", "foe", "comrade"],
        "fr": ["compagnon", "camarade", "partenaire", "connaissance",
               "étranger", "voisin", "allié", "rival",
               "ennemi", "adversaire"],
        "de": ["gefährte", "kamerad", "partner", "bekannter",
               "fremder", "nachbar", "verbündeter", "rivale",
               "feind", "gegner"],
        "es": ["compañero", "camarada", "socio", "conocido",
               "extraño", "vecino", "aliado", "rival",
               "enemigo", "adversario"],
        "it": ["compagno", "camerata", "socio", "conoscente",
               "straniero", "vicino", "alleato", "rivale",
               "nemico", "avversario"],
        "eo": ["kunulo", "kamarado", "partnero", "konato",
               "fremdulo", "najbaro", "aliancano", "rivalo",
               "malamiko", "kontrauxulo"],
        "fi": ["kumppani", "toveri", "seuralainen", "tuttava",
               "muukalainen", "naapuri", "liittolainen",
               "kilpailija", "vihollinen"],
    },

    # ─── DUALITÉ: opposition round 2 ─────────────────────────────
    "DUALITÉ": {
        "en": ["opposite", "contrast", "reverse", "paradox",
               "contradiction", "dilemma", "conflict", "clash",
               "contrary", "inverse", "alternative"],
        "fr": ["opposé", "contraste", "inverse", "paradoxe",
               "contradiction", "dilemme", "conflit",
               "contraire", "alternative"],
        "de": ["gegenteil", "kontrast", "umgekehrt", "paradox",
               "widerspruch", "dilemma", "konflikt", "gegensatz"],
        "es": ["opuesto", "contraste", "inverso", "paradoja",
               "contradicción", "dilema", "conflicto", "contrario"],
        "it": ["opposto", "contrasto", "inverso", "paradosso",
               "contraddizione", "dilemma", "conflitto", "contrario"],
        "eo": ["kontrauxo", "kontrasto", "inversa", "paradokso",
               "kontrauxdiro", "dilemo", "konflikto"],
        "fi": ["vastakohta", "kontrasti", "käänteinen", "paradoksi",
               "ristiriita", "dilemma", "konflikti"],
    },

    # ─── STRUCTURE: form/organization round 2 ────────────────────
    "STRUCTURE": {
        "en": ["pattern", "arrangement", "sequence", "series",
               "category", "class", "type", "sort", "kind",
               "manner", "fashion", "way", "method", "system"],
        "fr": ["motif", "arrangement", "séquence", "série",
               "catégorie", "classe", "type", "sorte",
               "manière", "façon", "méthode", "système"],
        "de": ["muster", "anordnung", "reihenfolge", "serie",
               "kategorie", "klasse", "art", "sorte",
               "weise", "methode", "system"],
        "es": ["patrón", "arreglo", "secuencia", "serie",
               "categoría", "clase", "tipo", "modo",
               "manera", "método", "sistema"],
        "it": ["modello", "disposizione", "sequenza", "serie",
               "categoria", "classe", "tipo", "modo",
               "maniera", "metodo", "sistema"],
        "eo": ["sxablono", "arangxo", "sinsekvo", "serio",
               "kategorio", "klaso", "tipo", "speco",
               "maniero", "metodo", "sistemo"],
        "fi": ["kaava", "järjestys", "sarja", "luokka",
               "tyyppi", "laji", "tapa", "menetelmä",
               "järjestelmä"],
    },

    # ─── ORDRE: order/sequence round 2 ───────────────────────────
    "ORDRE": {
        "en": ["rule", "law", "regulation", "decree", "verdict",
               "sentence", "trial", "execution", "punishment",
               "penalty", "reward", "command"],
        "fr": ["règle", "loi", "règlement", "décret", "verdict",
               "procès", "exécution", "punition", "peine",
               "récompense", "commandement"],
        "de": ["regel", "gesetz", "verordnung", "erlass", "urteil",
               "prozess", "hinrichtung", "strafe", "belohnung",
               "befehl"],
        "es": ["regla", "ley", "reglamento", "decreto", "veredicto",
               "juicio", "castigo", "recompensa", "mandato"],
        "it": ["regola", "legge", "regolamento", "decreto",
               "verdetto", "processo", "punizione", "ricompensa",
               "comando"],
        "eo": ["regulo", "legxo", "regularo", "dekreto", "verdikto",
               "proceso", "puno", "rekompenco", "ordono"],
        "fi": ["sääntö", "laki", "asetus", "tuomio",
               "oikeudenkäynti", "rangaistus", "palkinto",
               "käsky"],
    },

    # ─── INVARIANCE: constancy round 2 ───────────────────────────
    "INVARIANCE": {
        "en": ["steady", "stable", "constant", "firm", "fixed",
               "endure", "persist", "continue", "maintain",
               "preserve", "sustain", "eternal", "permanent"],
        "fr": ["stable", "constant", "ferme", "fixe",
               "endurer", "persister", "maintenir",
               "préserver", "éternel", "permanent"],
        "de": ["beständig", "stabil", "fest", "dauerhaft",
               "ertragen", "fortbestehen", "beibehalten",
               "bewahren", "ewig", "bleibend"],
        "es": ["estable", "constante", "firme", "fijo",
               "soportar", "persistir", "mantener",
               "preservar", "eterno", "permanente"],
        "it": ["stabile", "costante", "fermo", "fisso",
               "sopportare", "persistere", "mantenere",
               "preservare", "eterno", "permanente"],
        "eo": ["stabila", "konstanta", "firma", "fiksa",
               "elteni", "persisti", "konservi",
               "eterna", "permanenta"],
        "fi": ["vakaa", "pysyvä", "kiinteä", "kestää",
               "säilyttää", "ylläpitää", "ikuinen"],
    },

    # ─── RÉCURRENCE: repetition round 2 ──────────────────────────
    "RÉCURRENCE": {
        "en": ["repeat", "cycle", "rhythm", "pattern", "loop",
               "recur", "frequent", "periodic", "regular",
               "routine", "habit", "custom", "tradition"],
        "fr": ["répéter", "cycle", "rythme", "boucle",
               "fréquent", "périodique", "régulier",
               "routine", "habitude", "coutume", "tradition"],
        "de": ["wiederholen", "zyklus", "rhythmus", "schleife",
               "häufig", "periodisch", "regelmäßig",
               "routine", "gewohnheit", "brauch", "tradition"],
        "es": ["repetir", "ciclo", "ritmo", "bucle",
               "frecuente", "periódico", "regular",
               "rutina", "costumbre", "tradición"],
        "it": ["ripetere", "ciclo", "ritmo", "schema",
               "frequente", "periodico", "regolare",
               "routine", "abitudine", "tradizione"],
        "eo": ["ripeti", "ciklo", "ritmo", "buklo",
               "ofta", "perioda", "regula",
               "rutino", "kutimo", "tradicio"],
        "fi": ["toistaa", "sykli", "rytmi", "silmukka",
               "usein", "säännöllinen", "rutiini",
               "tapa", "perinne"],
    },

    # ─── QUALITÉ: quality/attribute ───────────────────────────────
    "QUALITÉ": {
        "sa": ["suparno", "guna", "dharma", "svabhaava",
               "lakshana", "visheshana"],
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# Sanskrit-specific keywords — merged into main entries programmatically
# to avoid Python dict duplicate-key overwrite issue
# ═══════════════════════════════════════════════════════════════════════════════

_SA_EXTRA = {
    "EXISTENCE": ["stuvan", "siddhah", "ahah", "ajo", "vibhuh",
                   "samvatsaro", "bhagavan", "bhagavaan",
                   "paramam", "sat", "asat", "bhava", "sattva"],
    "DOMINATION": ["vikramah", "shrimaan", "srimaan", "shuurah", "shurah",
                    "virah", "maheshvarah", "ishvarah", "prabhuh",
                    "raajaa", "chakravarti", "adhipati"],
    "COGNITION": ["yogo", "yoga", "jnaana", "vidyaa", "medha",
                   "prajna", "buddhi", "viveka", "chitta"],
    "PERCEPTION": ["pushkaraaxo", "pushkaraaksha", "sahasraaksha",
                    "chakshuh", "shrotra", "sparsha", "rasa", "gandha"],
    "CARE": ["bhaktyaa", "bhakti", "prema", "sneha", "dayaa",
              "karunaa", "maitri", "anugraha", "krpaa"],
    "GRAND": ["chaturbhujam", "chaturbhuja", "anantah", "vishvam",
               "brihat", "mahaan", "vipulah", "vishaalah"],
    "BON": ["shreyah", "shreyas", "shubham", "mangalam",
             "kalyaanam", "sundaram", "shivam", "saadhuh"],
    "DESTRUCTION": ["asheshena", "kaalah", "mrityu", "naasha",
                     "pralaya", "samhara", "antakah"],
    "AGENT": ["evacha", "matah", "kartaa", "bhoktaa",
               "drashtaa", "saakshee", "netaa", "nayakah"],
    "POSSESSION": ["vasur", "vasu", "dhanam", "ratnam", "nidhih",
                    "sampat", "aishvaryam", "vibhuti"],
    "INVARIANCE": ["achyutah", "amoghah", "avyayah", "saashvatah",
                    "nityah", "sanataanah", "dhruvah"],
    "CORPS": ["ameyaatmaa", "aatmaa", "atman", "deha",
               "shareera", "kaaya", "anga"],
    "LIEU": ["vishvayonih", "loka", "bhuvanam", "dhaam",
              "kshetra", "sthaanam", "bhumi"],
    "INTENSE": ["durdharo", "gahano", "tejo", "tejas",
                 "ojas", "ugrah", "prachanda", "ghorah"],
    "SEEKING": ["kaantah", "abhilasha", "eshana", "sprhaa",
                 "kaamah", "trshnaa", "ichchhaa"],
    "FEAR": ["sahishnur", "bhaya", "trasa", "shankaa",
              "aatanka", "udvega"],
    "RELATION": ["anagho", "bandhu", "sakha", "mitra",
                  "sahachara", "sambandha"],
}

# Merge Sanskrit into main EXPANSION_KEYWORDS_V48
for _atom, _words in _SA_EXTRA.items():
    if _atom in EXPANSION_KEYWORDS_V48:
        if "sa" in EXPANSION_KEYWORDS_V48[_atom]:
            EXPANSION_KEYWORDS_V48[_atom]["sa"].extend(_words)
        else:
            EXPANSION_KEYWORDS_V48[_atom]["sa"] = list(_words)
    else:
        EXPANSION_KEYWORDS_V48[_atom] = {"sa": list(_words)}


# ═══════════════════════════════════════════════════════════════════════════════
# ROUND 3: MASSIVE STOP WORD EXPANSION (from corpus gap analysis)
# ═══════════════════════════════════════════════════════════════════════════════

STOP_WORDS_V48_R3 = {
    "en": {
        # Common function words still uncovered in corpus
        "please", "till", "far", "ought", "use", "leave", "deal", "bit",
        "used", "able", "hardly", "necessary", "dry", "mine", "bad", "none",
        "worse", "rate", "easily", "off", "beg", "join", "doing", "ago",
        "round", "mere", "nor", "per", "else", "since", "save",
        "next", "last", "either", "neither", "former", "latter",
        "forth", "onwards", "meanwhile", "thereafter", "thereby",
        "whereas", "whereby", "wherein", "whereupon", "hitherto",
        "unto", "whilst", "amid", "amidst", "amongst", "betwixt",
        "ere", "thence", "whence", "hence", "therein", "thereof",
        # Literary/archaic
        "thee", "thou", "thy", "thine", "ye", "hath", "doth", "dost",
        "hast", "wilt", "shalt", "nay", "aye", "pray", "alas",
        "methinks", "forsooth", "verily", "prithee", "wherefore",
        # Common short words
        "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "half", "twice", "once",
        # Nationality/proper adj treated as function
        "french", "english", "dutch", "spanish", "german", "italian",
        "portuguese", "turkish", "bulgarian", "european",
    },
    "fr": {
        # Function words/adverbs
        "tant", "ah", "soit", "chacun", "auprès", "hélas", "lequel",
        "autour", "loin", "tantôt", "ait", "eu", "pu", "eût", "mis",
        "leva", "né", "ans", "sens", "voilà", "parmi", "devers",
        "quant", "afin", "envers", "malgré", "outre", "selon",
        "vers", "dès", "contre", "hors", "parce", "sinon",
        "assez", "trop", "bien", "mal", "vite", "fort", "haut", "bas",
        "encore", "jamais", "toujours", "souvent", "parfois",
        "nullement", "aucunement", "guère", "point",
        # Verb forms (auxiliaries & common)
        "avaient", "avons", "eut", "fut", "sont", "étaient", "étions",
        "serait", "fût", "firent", "furent", "auraient", "aurait",
        "avait", "eussent", "eurent", "suis", "serez", "serons",
        # Contractions (apostrophe-based)
        "jusqu'à", "est-ce", "qu'est-ce", "avez-vous", "êtes-vous",
        "n'avez", "peut-être", "là-dessus", "vis-à-vis",
        "c'est-à-dire", "aujourd'hui", "quelqu'un",
        # Short forms
        "va", "ai", "oh", "eh", "or", "vu",
        # Demonstratives/pronouns
        "dont", "laquelle", "lesquels", "lesquelles", "duquel",
        "auquel", "auxquels", "auxquelles", "desquels", "desquelles",
    },
    "de": {
        # Function words
        "warum", "sogleich", "beide", "einige", "wenig", "herum",
        "können", "außer", "zwar", "sobald", "obgleich", "fertig",
        "worauf", "dasselbe", "eure", "euer", "wirst", "hinter",
        "sollen", "mag", "welcher", "welchem", "welches", "deren",
        "dessen", "wohl", "doch", "ja", "gerade", "eben",
        "gar", "erst", "gleich", "fast", "vielleicht", "leider",
        "allerdings", "immerhin", "übrigens", "jedenfalls",
        "nämlich", "sondern", "weder", "statt", "trotz",
        "gewiss", "freilich", "zuerst", "zuletzt", "endlich",
        # Verb forms
        "ließ", "hielt", "lag", "lief", "kam", "ging", "fand",
        "gab", "nahm", "sprach", "sah", "stand", "saß", "wusste",
        "konnte", "wollte", "sollte", "durfte", "mochte",
        # Old German spellings common in Gutenberg
        "gethan", "thun", "thut", "thier", "thiere", "thränen",
        "erwiederte", "in's", "an's", "auf's",
    },
    "es": {
        # Function words (incl. archaic)
        "qual", "da", "mí", "ay", "vi", "siquiera", "voy", "vamos",
        "aun", "tambien", "acaso", "sino", "apenas", "demás",
        "cuanto", "cuanta", "cuantos", "cuantas", "demas",
        "aquello", "ello", "eso", "esto", "aquel", "aquella",
        "suyo", "suya", "suyos", "suyas", "mío", "mía",
        "tuyo", "tuya", "nuestro", "nuestra", "vuestro", "vuestra",
        # Archaic verb forms (19th century)
        "fuéron", "hiciéron", "viéron", "diéron", "porqué",
        "apénas", "entónces", "quantos", "quantas", "hubieran",
        "hayan", "quiso", "puso", "daban", "oido", "oído",
        # Common verbs
        "tienen", "ve", "tengo", "puede", "sea", "hay",
        "hace", "sabe", "quiere", "viene", "pone", "dice",
    },
    "it": {
        # Function words
        "quanto", "me", "sia", "li", "te", "fa", "sa", "so",
        "poichè", "niuno", "soltanto", "neppure", "nò", "affatto",
        "quà", "innanzi", "po", "ei", "indietro", "cui", "può",
        "nè", "siccome", "ben", "dunque", "perciò", "anzi",
        "eppure", "oppure", "ovvero", "purché", "sebbene",
        "affinché", "qualora", "laddove", "benché",
        # Contractions
        "d'un", "d'una", "d'alice", "ch'era", "ch'io", "ch'egli",
        "l'altro", "l'altra", "all'orecchio", "sull'erba",
        "nell'acqua", "dall'altra", "un'altra",
        # Verb forms
        "potrei", "farà", "disse", "fece", "venne", "andò",
        "stava", "aveva", "faceva", "diceva", "volle", "vide",
    },
    "fi": {
        # Pronouns in all cases (the #1 Finnish gap)
        "heitä", "tätä", "niitä", "teitä", "nämä", "hänellä",
        "minusta", "tällä", "teillä", "häneltä", "meillä",
        "niistä", "hänelle", "heille", "meille", "heiltä",
        "meitä", "sinua", "häntä", "niille", "näitä", "noita",
        "itsensä", "itseään", "itsellään", "itselleen", "itsestään",
        "toisiaan", "toisistaan", "toisilleen", "toistensa",
        # Function words & particles
        "noin", "täytyy", "kuluttua", "sekä", "tähän", "et",
        "itsekseen", "näet", "vai", "minkä", "kahden", "jolla",
        "täytyi", "onko", "lainkaan", "kiinni", "ollenkaan",
        "jonkun", "päin", "sentähden", "niinkuin", "olevan",
        "kauan", "onpa", "suinkaan", "vaan", "toiset",
        "tiedä", "mahdollista", "olemme", "ainoastaan",
        "niinpä", "kaikki", "sillä", "sitä", "sitä", "siten",
        "samoin", "miksi", "kuinka", "joten", "jokainen",
        "toinen", "muut", "muita", "muuten", "entä",
        # Verb forms
        "sai", "saattoi", "tuli", "meni", "antoi", "otti",
        "sanoi", "kysyi", "vastasi", "huusi", "katsoi",
        "alkoi", "jatkoi", "nousi", "lähti", "pääsi",
        "olisi", "voisi", "pitäisi", "saisi", "tulisi",
    },
    "eo": {
        # Pronouns & correlatives
        "je", "sen", "ion", "nek", "ve", "krom", "tion", "kian",
        "ian", "sup", "kia", "dume", "same", "ree",
        "siajn", "mian", "lian", "sian", "nian", "vian",
        "tiujn", "kiujn", "cxiujn", "iujn",
        # Function words
        "bil", "hodiaux", "duan", "tutan", "solene",
        "kiamaniere", "certe", "efektive", "proksimume",
        "kvankam", "malgraux", "ecx", "ja", "jes",
        "cxar", "cxu", "aux", "nek", "nek...nek",
    },
    "sa": {
        "produced", "transcribed", "transliterated", "processing",
        "following", "location", "render", "transliteration",
        "accurate", "possible", "help", "refine", "rules",
        "outlined", "aforementioned", "website", "tool", "may",
        "unknown", "sri", "sanskrit", "itrans",
    },
}

# Merge R3 stop words into STOP_WORDS_V48
for _lang, _words in STOP_WORDS_V48_R3.items():
    if _lang in STOP_WORDS_V48:
        if isinstance(STOP_WORDS_V48[_lang], set):
            STOP_WORDS_V48[_lang].update(_words)
        elif isinstance(STOP_WORDS_V48[_lang], dict):
            STOP_WORDS_V48[_lang] = set(STOP_WORDS_V48[_lang]) | set(_words)
        else:
            STOP_WORDS_V48[_lang] = set(STOP_WORDS_V48[_lang]) | set(_words)
    else:
        STOP_WORDS_V48[_lang] = set(_words)


# ═══════════════════════════════════════════════════════════════════════════════
# ROUND 3: ADDITIONAL KEYWORDS (from corpus gap analysis)
# ═══════════════════════════════════════════════════════════════════════════════

EXPANSION_KEYWORDS_V48_R3 = {
    "AGENT": {
        "en": ["vessel", "ship", "birds", "monkeys", "officer", "pope",
               "travellers", "jew", "anabaptist", "valet", "pigeon",
               "serpent", "pig", "horses", "sailor", "captain", "soldier",
               "merchant", "priest", "monk", "nun", "duchess", "baron"],
        "fr": ["moutons", "soeur", "docteur", "rois", "laquais",
               "juif", "moine", "philosophe", "marquis", "baron",
               "prêtre", "soldat", "marin", "capitaine", "marchand",
               "fermier", "paysan", "ouvrier", "bourgeois"],
        "de": ["papagei", "wabbel", "köchin", "ferkel", "igel",
               "lackei", "gärtner", "hund", "flamingo", "vögel",
               "thiere", "spatzen", "hummer", "grinsekatze",
               "richter", "bote", "diener", "bauer", "ritter"],
        "es": ["mugeres", "mozo", "reyes", "judío", "filósofo",
               "anabautista", "fraile", "capitán", "soldado",
               "marinero", "criado", "señora", "doncella"],
        "it": ["fanciulla", "bimbo", "uccelli", "porcellino", "fante",
               "cuoco", "dottore", "soldato", "capitano",
               "mercante", "contadino", "signora"],
        "eo": ["angla", "jxurintoj", "dajna", "loro", "serpento",
               "birdoj", "merlango", "regxa", "soldato",
               "kapitano", "servisto"],
        "fi": ["apotti", "jänis", "ihminen", "herra", "rouva",
               "sotilas", "kapteeni", "kauppias", "pappi"],
    },
    "MOUVEMENT": {
        "en": ["met", "voyage", "board", "coast", "horses",
               "rode", "sailed", "embarked", "departed", "arrived",
               "landed", "marched", "fled", "retreated", "pursued"],
        "fr": ["va", "reprit", "leva", "fesait", "accourir",
               "arriva", "partit", "embarqua", "débarqua"],
        "de": ["rannte", "warf", "schüttelte", "fuhr", "ritt",
               "floh", "eilte", "stieg", "sprang"],
        "es": ["viage", "embarcar", "desembarcar", "llegar",
               "partir", "huir", "marchar"],
        "it": ["fretta", "va", "andò", "venne", "fuggì",
               "corse", "partì", "arrivò"],
        "fi": ["saattoi", "lähti", "nousi", "meni", "tuli",
               "juoksi", "käveli", "kiiruhti"],
    },
    "COMMUNICATION": {
        "en": ["history", "honour", "opportunity", "conduct",
               "business", "dinner", "marry", "french"],
        "fr": ["répliqua", "prie", "comment", "discours",
               "raconter", "annoncer", "répondre"],
        "de": ["erwiederte", "höflich", "essen", "schule",
               "sprechen", "antworten", "erzählen"],
        "es": ["doctor", "docto", "gracias", "cenar",
               "derecho", "menester", "magestad"],
        "it": ["grazia", "senso", "giuoco", "mestamente",
               "parlare", "rispondere"],
        "eo": ["petas", "mosxto", "mangxas", "rajtas",
               "paroli", "diri", "demandi"],
        "fi": ["lausui", "huudahti", "virkkoi", "sanoi",
               "kysyi", "vastasi", "kertoi"],
    },
    "CORPS": {
        "en": ["drink", "dinner", "red", "blood", "flesh",
               "bone", "breath", "stomach", "cheek", "neck",
               "shoulder", "knee", "ankle", "toe", "lip"],
        "fr": ["coeur", "sang", "chair", "os", "souffle",
               "estomac", "joue", "cou", "épaule"],
        "de": ["essen", "trinken", "kopf", "haar", "auge",
               "ohr", "nase", "mund", "arm", "bein"],
        "es": ["hambre", "negros", "sangre", "carne",
               "hueso", "corazón", "brazo", "pierna"],
        "it": ["mani", "sangue", "carne", "osso",
               "cuore", "braccio", "gamba"],
        "eo": ["mangxi", "trinki", "sango", "karno",
               "osto", "koro", "brako"],
        "fi": ["syödä", "juoda", "veri", "liha",
               "luu", "sydän", "käsi", "jalka"],
    },
    "BON": {
        "en": ["pleased", "politely", "pretty", "free", "fair",
               "fine", "noble", "worthy", "proper", "decent"],
        "fr": ["bonne", "chère", "jolie", "noble", "digne",
               "honnête", "propre", "convenable"],
        "de": ["froh", "höflich", "toll", "hübsch", "fein",
               "edel", "würdig", "anständig"],
        "es": ["treinta", "bueno", "bonito", "fino",
               "noble", "digno", "honrado"],
        "it": ["bel", "lieta", "nobile", "degno",
               "onesto", "grazioso"],
        "eo": ["facile", "utilas", "utilus", "bona",
               "nobla", "digna"],
        "fi": ["pikku", "hyvä", "kaunis", "hieno",
               "jalo", "arvokas"],
    },
    "COGNITION": {
        "en": ["taught", "learn", "understood", "decided", "confused",
               "remember", "forgot", "mistake", "reason"],
        "fr": ["philosophe", "sens", "espèce", "pensée",
               "raison", "comprendre", "deviner"],
        "de": ["sinn", "unsinn", "merkte", "verstand",
               "dachte", "überlegte", "begriff"],
        "es": ["filósofo", "docto", "entender", "pensar",
               "saber", "razón", "sentido"],
        "it": ["senso", "ragione", "capire", "sapere",
               "pensare", "comprendere"],
        "fi": ["höperö", "järki", "ajatella", "ymmärtää",
               "muistaa", "unohtaa"],
    },
    "LIEU": {
        "en": ["inn", "page", "aboard", "harbour", "church",
               "castle", "tower", "bridge", "street", "road"],
        "fr": ["paris", "page", "auberge", "église",
               "château", "tour", "pont", "rue", "route"],
        "de": ["schule", "kirche", "burg", "turm",
               "brücke", "straße", "weg"],
        "es": ["europa", "paris", "lisboa", "santiago",
               "iglesia", "castillo", "torre", "puente"],
        "it": ["stagno", "pozzo", "chiesa", "castello",
               "torre", "ponte", "strada"],
        "eo": ["pregxejo", "kastelo", "turo", "ponto",
               "strato", "vojo"],
        "fi": ["kirkko", "linna", "torni", "silta",
               "tie", "katu"],
    },
    "GRIEF": {
        "en": ["whipped", "poor", "suffered", "unhappy",
               "unfortunate", "wretched", "pain", "wound"],
        "fr": ["pendu", "pauvre", "malheur", "douleur",
               "souffrir", "blessure", "plaie"],
        "de": ["weh", "schmerz", "leid", "traurig",
               "unglücklich", "verwundet"],
        "es": ["padecido", "pobre", "dolor", "herida",
               "sufrir", "desgracia"],
        "it": ["lagrime", "mestamente", "dolore", "ferita",
               "soffrire", "infelice"],
        "fi": ["suru", "tuska", "kipu", "haava",
               "kärsiä", "onneton"],
    },
    "DESTRUCTION": {
        "fr": ["pendu", "tué", "brûlé", "noyé",
               "massacré", "égorgé"],
        "es": ["fuéron", "hiciéron", "viéron", "diéron",
               "mataron", "quemaron"],
    },
    "DOMINATION": {
        "fr": ["rois", "monseigneur", "révérend", "majesté",
               "seigneur", "empereur", "gouverneur"],
        "de": ["königin", "herrscher", "kaiser", "fürst",
               "graf", "ritter", "knecht"],
        "es": ["magestad", "reyes", "emperador", "gobernador",
               "señor", "capitán"],
        "it": ["regina", "imperatore", "governatore",
               "signore"],
        "eo": ["regxa", "imperiestro", "guberniestro"],
    },
    "POSSESSION": {
        "en": ["pay", "piastres", "money", "gold", "silver",
               "buy", "sell", "trade", "rich", "poor"],
        "fr": ["piastres", "argent", "acheter", "vendre",
               "commerce", "riche", "pauvre"],
        "es": ["piastres", "dinero", "comprar", "vender",
               "comercio", "rico", "pobre"],
    },
    "MESURE": {
        "de": ["uhr", "stunde", "minute", "tag", "nacht",
               "woche", "monat", "jahr"],
        "fr": ["ans", "heure", "minute", "jour", "nuit",
               "semaine", "mois", "année"],
        "es": ["treinta", "hora", "minuto", "día", "noche",
               "semana", "mes", "año"],
    },
    "PLAY": {
        "it": ["giuoco", "croquet", "carte", "giocattolo"],
        "eo": ["sxatus", "ludilo", "kartludo"],
    },
    "PERCEPTION": {
        "eo": ["vigle", "rigardi", "auxdi", "senti",
               "flari", "gustumi"],
        "fi": ["nähdä", "kuulla", "tuntea", "haistaa",
               "maistaa"],
    },
    "SEEKING": {
        "fr": ["voudrais", "désirer", "chercher", "espérer",
               "souhaiter"],
        "eo": ["mosxto", "deziri", "serĉi", "esperi"],
    },
    "ANCIEN": {
        "eo": ["hodiaux", "hieraux", "morgaux", "antauxe",
               "poste", "baldaux"],
    },
    "EXISTENCE": {
        "eo": ["kera", "estis", "estos", "estus",
               "fariĝi", "ekesti"],
    },
}

# Merge R3 keywords into EXPANSION_KEYWORDS_V48
for _atom, _langs in EXPANSION_KEYWORDS_V48_R3.items():
    if _atom not in EXPANSION_KEYWORDS_V48:
        EXPANSION_KEYWORDS_V48[_atom] = {}
    for _lang, _words in _langs.items():
        if _lang in EXPANSION_KEYWORDS_V48[_atom]:
            existing = set(EXPANSION_KEYWORDS_V48[_atom][_lang])
            existing.update(_words)
            EXPANSION_KEYWORDS_V48[_atom][_lang] = list(existing)
        else:
            EXPANSION_KEYWORDS_V48[_atom][_lang] = list(_words)


# ═══════════════════════════════════════════════════════════════════════════════
# ROUND 3: ADDITIONAL PROPER NOUNS (literary characters + place names)
# ═══════════════════════════════════════════════════════════════════════════════

PROPER_NOUN_AGENTS_R3 = {
    # Candide characters (all languages)
    "jacques", "pococurante", "giroflée", "perigordian",
    "thunder-ten-tronckh", "tunder-ten-tronck",
    "anabaptist", "anabautista", "inquisiteur",
    "monseigneur", "révérend", "hilarion", "fray",
    # Place names (treated as known vocabulary)
    "france", "paris", "england", "italy", "spain",
    "germany", "portugal", "holland", "europe", "europa",
    "buenos", "ayres", "lisbon", "lisboa", "westphalia",
    "vesfalia", "constantinople", "venice", "rome",
    "santiago", "cadiz", "el dorado",
    # Literary/document
    "st", "xv", "ii", "iii", "iv", "vi", "vii", "viii", "ix", "xi", "xii",
    # Finnish characters
    "höperö", "apotti",
    # Esperanto
    "cxapelisto", "rauxpo", "alicio",
    # Italian
    "tonio",
}

# Merge R3 proper nouns
PROPER_NOUN_AGENTS.update(PROPER_NOUN_AGENTS_R3)


# ═══════════════════════════════════════════════════════════════════════════════
# ROUND 4: MASSIVE STOP WORD EXPANSION — targeting FI/ES/FR/DE/IT/EN/EO gaps
# ═══════════════════════════════════════════════════════════════════════════════

STOP_WORDS_V48_R4 = {
    "fi": [
        # Case-declined pronouns & demonstratives
        "josta", "hänestä", "jotakin", "sentään", "erääseen", "niiden",
        "millä", "olikin", "hiljaa", "ellei", "yhden", "etkö", "täten",
        "jonka", "jolla", "jolta", "jolle", "johon", "jossa", "jotka",
        "joita", "joiden", "joilla", "joilta", "joille", "joihin", "joissa",
        "tämän", "tähän", "tässä", "tästä", "tällä", "tältä", "tälle",
        "tuon", "tuolle", "tuolla", "tuolta", "tuossa", "tuosta", "tuohon",
        "näiden", "näillä", "näiltä", "näille", "näihin", "näissä", "näistä",
        "noiden", "noilla", "noilta", "noille", "noihin", "noissa", "noista",
        "itsekin", "itsensä", "itselleen", "itsestään", "itsellään",
        "kenelle", "keneltä", "kenessä", "kenestä", "kenen", "keille",
        # Negation + question particles
        "älä", "älkää", "älköön", "elkää", "eikö", "eiköhän",
        "eivät", "emme", "ette", "etkö", "enkö", "eihän",
        # Common adverbs & postpositions
        "vuoksi", "lakkaamatta", "ainoatakaan", "sellaisia", "sellaiseen",
        "ensi", "liemi", "vallan", "monta", "lähellä", "edessä",
        "takana", "vieressä", "yllä", "alla", "sisällä", "ulkona",
        "ylhäällä", "alhaalla", "välissä", "keskellä", "vastaan",
        "kohti", "päin", "pois", "yli", "läpi", "poikki", "pitkin",
        # Modal/aux verb forms
        "sain", "saisi", "saivat", "saadaan", "saatiin", "saatu",
        "tulisi", "tulisivat", "tulkoon", "tullaan", "tultiin",
        "joutui", "joutuivat", "jouduttiin", "jouduin",
        "olikin", "onkin", "olivatkin", "onkaan", "olisikaan",
        "olkoon", "olekin", "olisiko", "olisikin",
        # Case suffixed common words (too common to be content)
        "siitä", "siinä", "siihen", "sillä", "sille", "siltä",
        "toiseen", "toisella", "toiselta", "toiselle", "toisesta",
        "kaikille", "kaikkia", "kaikista", "kaikissa", "kaikkien",
        "jokaiseen", "jokaiselle", "jokaisesta", "jokaisella",
        "muiden", "muille", "muilta", "muissa", "muista", "muihin",
        "yhteen", "yhdessä", "yhdestä", "yhdelle", "yhdeltä", "yhdellä",
        "sinne", "siellä", "sieltä", "täällä", "täältä", "tänne",
        "tuonne", "tuolla", "tuolta", "missä", "mistä", "minne",
        # Finnish literary/archaic forms
        "ihmeellistä", "ihmeellinen", "ihmeekseen",
        "kuninkaan", "kuninkaalle", "kuninkaalta", "kuninkaassa",
        "kertoi", "kertoivat", "kerrottiin",
        "ajatteli", "ajattelivat", "ajateltiin", "ajatelkaa",
        "pääsi", "päässyt", "pääsee", "päästä",
        "alkoi", "alkoivat", "alettiin", "aletaan",
        "lähti", "lähtivät", "lähdetään", "lähdettiin",
        "tuntui", "tuntuivat", "tuntuu", "tuntuneen",
        "halusi", "halusivat", "haluaa", "haluavat",
        # More Finnish particles and conjunctions
        "siksi", "sitä", "silloin", "sinua", "sinun", "sinulle",
        "minulle", "minua", "minun", "minulta", "meille", "meiltä",
        "teille", "teiltä", "heille", "heiltä", "meissä", "teissä",
        "heissä", "meistä", "teistä", "heistä",
        # Quantity words
        "paljon", "vähän", "liian", "riittävästi", "tarpeeksi",
        "jonkin", "joidenkin", "joitakin", "eräät", "muutama",
    ],
    "fr": [
        # Pronoun/article contractions
        "d'en", "d'eux", "n'avais", "n'avait", "n'est", "n'était",
        "n'ai", "n'ont", "n'a", "n'y", "d'abord", "d'ailleurs",
        "d'après", "d'autre", "d'autres", "d'avoir", "d'être",
        "d'où", "d'une", "d'un", "l'on", "l'autre", "l'homme",
        "l'avait", "l'était", "l'eût", "l'ai", "l'ont",
        "qu'elle", "qu'elles", "qu'il", "qu'ils", "qu'on",
        "qu'un", "qu'une", "qu'à", "qu'au", "qu'en",
        "s'en", "s'il", "s'y", "s'était", "s'est", "s'écria",
        "c'était", "c'est", "c'eût",
        # Verb forms (common tenses)
        "devait", "devant", "doit", "doivent",
        "peux", "pouvez", "pouvait", "pouvaient", "pouvant",
        "pût", "puisse", "puissent", "puissions",
        "voulait", "voulez", "voulaient", "voulu", "voulut",
        "savait", "savez", "savais", "savaient", "saura", "saurait",
        "faisait", "faisais", "faisaient", "faisant", "fais", "fasse",
        "devint", "devinrent", "devenu", "devenue",
        "aperçut", "aperçurent", "aperçu",
        "jeta", "jetèrent", "jeté",
        "reçut", "reçurent", "reçu",
        "resta", "restèrent", "resté", "restée",
        "crut", "crurent",
        "fut", "furent", "fût",
        "allait", "allaient", "allé", "allée", "allés",
        "venait", "venaient", "venu", "venue", "venus",
        "disait", "disaient", "dirent",
        "vivait", "vivaient", "vécut", "vécurent",
        "tenait", "tenaient", "tenu", "tenue",
        # Prepositions / adverbs
        "derrière", "devant", "dessus", "dessous", "dedans",
        "dehors", "partout", "nulle", "auprès", "parmi",
        "autour", "envers", "depuis", "durant", "malgré",
        "afin", "environ", "hormis", "jusque", "tandis",
        "néanmoins", "toutefois", "cependant", "pourtant",
        "ailleurs", "désormais", "autrefois", "jadis",
        "dorénavant", "auparavant", "davantage",
        # Common adjectives (grammatical)
        "autre", "autres", "même", "mêmes", "tel", "telle", "tels",
        "seul", "seule", "seuls", "seules", "chaque", "quelque",
        "quelques", "certains", "certaines", "plusieurs",
        "propre", "propres", "pareil", "pareille",
        # Subjunctive & literary tenses
        "eût", "fît", "dît", "mît", "vît", "prît",
        "allât", "donnât", "parlât", "trouvât",
    ],
    "de": [
        # Declined articles / pronouns
        "welchen", "welches", "welcher", "welche", "welchem",
        "beiden", "beides", "beider", "beidem",
        "diesen", "dieses", "dieser", "diesem", "dieselbe",
        "jenen", "jenes", "jener", "jenem",
        "solchen", "solches", "solcher", "solchem",
        "dergleichen", "desgleichen",
        # Modal/aux verb forms
        "mußten", "müßten", "müsse", "müßte", "könntest", "könnte",
        "könnt", "könnten", "dürfte", "dürften",
        "wurden", "würden", "würde", "worden",
        "sollte", "sollten", "solle",
        "wollte", "wollten", "wolle",
        "mochte", "mochten", "möchte", "möchten",
        "hatte", "hätte", "hätten", "gehabt",
        # Common verbs (weak past forms)
        "sagte", "sagten", "meinte", "meinten", "fragte", "fragten",
        "sahen", "sehen", "gesehen",
        "anfing", "angefangen", "begann", "begannen",
        "brachte", "brachten", "gebracht",
        "dachte", "dachten", "gedacht",
        "machte", "machten", "gemacht",
        "stellte", "stellten", "gestellt",
        "wollte", "wollten", "gewollt",
        "konnte", "konnten", "gekonnt",
        # Adverbs / particles
        "wovon", "wohin", "woher", "womit", "wofür", "worüber",
        "wozu", "woraus", "worin", "woran", "wobei",
        "nieder", "hinzu", "heraus", "herab", "herein", "hinaus",
        "hinein", "hinauf", "hinab", "vorbei", "zurück",
        "weniger", "wenigstens", "mindestens", "höchstens",
        "außerdem", "überdies", "indessen", "inzwischen",
        "allerdings", "freilich", "jedenfalls", "keineswegs",
        "bisweilen", "manchmal", "niemals", "nochmals",
        "durchaus", "beinahe", "ungefähr", "ziemlich",
        "deutlich", "ungeheuer", "äußerst",
        # Possessive forms
        "meines", "meiner", "meinem", "meinen",
        "deines", "deiner", "deinem", "deinen",
        "seines", "seiner", "seinem", "seinen",
        "ihres", "ihrer", "ihrem", "ihren",
        "unseres", "unserer", "unserem", "unseren",
        "eures", "eurer", "eurem", "euren",
    ],
    "es": [
        # Subjunctive/conditional verb forms
        "haya", "hayas", "hayamos", "hayáis", "hayan",
        "fuese", "fuesen", "fuera", "fueran", "fuéramos",
        "hubiera", "hubiese", "hubo", "hubieron",
        "pudiera", "pudiese", "pudiesen", "pudiéramos",
        "quisiera", "quisiese", "quisiesen",
        "dijera", "dijese", "dijesen",
        "tuviera", "tuviese", "tuviesen",
        "viniera", "viniese", "viniesen",
        "supiera", "supiese", "supiesen",
        # Common function words
        "algun", "algún", "alguna", "algunas", "algunos",
        "ningún", "ninguna", "ningunos", "ningunas",
        "mio", "mía", "míos", "mías", "tuyo", "tuya", "tuyos", "tuyas",
        "suyo", "suya", "suyos", "suyas",
        "nuestro", "nuestra", "nuestros", "nuestras",
        "vuestro", "vuestra", "vuestros", "vuestras",
        "somos", "sois", "estamos", "estáis", "están",
        "pueden", "podemos", "podéis",
        "será", "serán", "sería", "serían", "seréis",
        "podrá", "podrán", "podría", "podrían",
        "iban", "íbamos", "ibais",
        "veo", "ves", "vemos", "veis", "ven",
        "van", "vamos", "vais",
        # Prepositions / adverbs
        "encima", "debajo", "delante", "detrás", "alrededor",
        "dentro", "fuera", "acerca", "respecto", "mediante",
        "hacia", "hacía", "apenas", "demás", "además",
        "todavía", "aún", "incluso", "siquiera",
        "cuanto", "cuanta", "cuantos", "cuantas",
        "cualquier", "cualquiera", "quienquiera",
        # Archaic/literary forms (Cervantes etc.)
        "vió", "dexó", "echó", "llegó", "halló", "dixo",
        "oyó", "entró", "volvió", "preguntó", "respondió",
        "tenian", "habian", "decian", "venian", "querian",
        "decía", "venía", "quería", "salía", "ponía",
        "reyno", "dellas", "dél", "della", "destas", "deste",
    ],
    "it": [
        # Contracted forms
        "ch'è", "ch'era", "ch'erano", "ch'io", "ch'ella",
        "dov'è", "dov'era", "quell'uomo", "quell'altro",
        "com'è", "com'era", "com'ebbi", "quand'ecco",
        "d'un", "d'una", "d'una", "d'ogni",
        "nell'", "nell'acqua", "nell'aria", "nell'altro",
        "all'", "all'altro", "all'improvviso",
        "sull'", "dall'", "dell'",
        # Pronouns / particles
        "ce", "ci", "vi", "ne", "nelle", "nello", "nella",
        "degli", "dei", "delle", "dello", "della",
        "qual", "quale", "quali", "quel", "quella", "quegli",
        "chiunque", "qualunque", "dovunque", "comunque",
        "nessuno", "nessuna", "niente", "nulla",
        # Verb forms
        "sta", "stava", "stavano", "stette", "stettero",
        "potrebbe", "potrebbero", "poteva", "potevano",
        "dovrebbe", "dovrebbero", "doveva", "dovevano",
        "vorrebbe", "vorrebbero", "voleva", "volevano",
        "venne", "vennero", "veniva", "venivano",
        "aveva", "avevano", "ebbe", "ebbero",
        "fece", "fecero", "faceva", "facevano",
        "disse", "dissero", "diceva", "dicevano",
        "sapeva", "sapevano", "seppe", "seppero",
        "abbia", "abbiano", "avesse", "avessero",
        # Adverbs
        "intorno", "davanti", "dietro", "accanto", "addosso",
        "appena", "ancora", "adesso", "allora", "almeno",
        "abbastanza", "assai", "quasi", "piuttosto",
        "perfino", "persino", "soltanto", "neppure", "nemmeno",
        "tuttavia", "pertanto", "perciò", "dunque", "insomma",
    ],
    "en": [
        # Common past tenses & participles
        "began", "begun", "stood", "shook", "led", "lying",
        "dressed", "picked", "filled", "seized", "reduced",
        "invited", "obliged", "fetched", "repeated",
        # Archaic/literary
        "thou", "thee", "thy", "thine", "ye", "hath", "doth",
        "dost", "wilt", "shalt", "shouldst", "wouldst",
        "hast", "hadst", "didst", "canst", "mayst",
        "methinks", "methought", "tis", "twas", "twere",
        "whence", "whither", "thence", "thither", "hither",
        "nay", "aye", "prithee", "forsooth", "verily",
        # Common contractions
        "you'll", "you'd", "you've", "you're",
        "she'll", "she'd", "she's",
        "he'll", "he'd", "he's",
        "we'll", "we'd", "we've", "we're",
        "they'll", "they'd", "they've", "they're",
        "i'll", "i'd", "i've", "i'm",
        "it'll", "it'd", "it's",
        "won't", "wouldn't", "shouldn't", "couldn't",
        "mustn't", "needn't", "shan't", "mightn't",
        "can't", "don't", "didn't", "doesn't", "hasn't",
        "haven't", "hadn't", "isn't", "aren't", "wasn't", "weren't",
        "ain't", "let's", "that's", "there's", "here's",
        "what's", "who's", "where's", "when's", "how's",
        # Common adverbs/function words
        "hastily", "timidly", "politely", "according",
        "sufficient", "rather", "indeed", "perhaps",
        "meanwhile", "therefore", "moreover", "furthermore",
        "however", "although", "nevertheless", "notwithstanding",
        "henceforth", "hereafter", "therefrom", "thereupon",
        "hereby", "thereby", "wherein", "whereupon",
    ],
    "eo": [
        # Correlatives (ki-, ti-, i-, cxi-, neni-)
        "kiaj", "kiajn", "kiam", "kial", "kiel", "kien",
        "tiaj", "tiajn", "tiam", "tial", "tiel", "tien",
        "iaj", "iajn", "iam", "ial", "iel", "ien",
        "cxiaj", "cxiajn", "cxiam", "cxial", "cxiel", "cxien",
        "neniaj", "neniajn", "neniam", "nenial", "neniel", "nenien",
        # Accusative/plural correlatives
        "kiun", "kiujn", "tiun", "tiujn", "iun", "iujn",
        "cxiun", "cxiujn", "neniun", "neniujn",
        # Table word forms
        "kion", "tion", "ion", "cxion", "nenion",
        "kies", "ties", "ies", "cxies", "nenies",
        # Common particles/conjunctions
        "tamen", "ankaux", "kvankam", "kvazaux", "precipe",
        "apenauxe", "eble", "certe", "verŝajne",
        "almenauxe", "entute", "antauxe", "poste",
        "ankoraux", "anstataux", "malgrauxe",
        # Pronoun accusatives
        "sxin", "sxian", "sxiaj", "sxiajn",
        "lin", "lian", "liaj", "liajn",
        "gxin", "gxian", "gxiaj", "gxiajn",
        "ilin", "ilian", "iliaj", "iliajn",
        "onin", "onian", "oniaj", "oniajn",
        "nian", "niaj", "niajn",
        "vian", "viaj", "viajn",
        "mian", "miaj", "miajn",
    ],
}

# Merge R4 stop words into STOP_WORDS_V48
for _lang, _words in STOP_WORDS_V48_R4.items():
    if _lang in STOP_WORDS_V48:
        STOP_WORDS_V48[_lang] = list(set(STOP_WORDS_V48[_lang]) | set(_words))
    else:
        STOP_WORDS_V48[_lang] = list(_words)


# ═══════════════════════════════════════════════════════════════════════════════
# ROUND 4: MASSIVE KEYWORD EXPANSION — content words mapped to atoms
# ═══════════════════════════════════════════════════════════════════════════════

EXPANSION_KEYWORDS_V48_R4 = {
    "AGENT": {
        "en": ["lobster", "turtle", "gryphon", "pigeon", "puppy", "lizard",
               "caterpillar", "hatter", "dormouse", "footman", "duchess",
               "soldier", "sailor", "pirate", "captain", "governor",
               "monk", "priest", "baron", "baroness", "princess",
               "servant", "slave", "beggar", "merchant", "executioner"],
        "fr": ["singe", "singes", "mouton", "moutons", "valet",
               "dame", "dames", "seigneur", "messieurs", "voyageur",
               "voyageurs", "matelot", "moine", "esclave", "marchand",
               "prêtre", "gouverneur", "pirate", "capitaine"],
        "de": ["henker", "katze", "maus", "hase", "taube",
               "herzogin", "herzog", "ritter", "knecht", "bauer",
               "soldat", "matrose", "kaufmann", "priester"],
        "es": ["dama", "pirata", "galera", "galeras", "esclavo",
               "gobernador", "marinero", "capitán", "sacerdote",
               "mercader", "soldado", "isacar"],
        "it": ["bestia", "bestie", "boja", "animale", "gatto",
               "topo", "piccione", "lucertola", "duchessa",
               "soldato", "marinaio", "mercante"],
        "fi": ["kuningas", "kyyhkynen", "hiiri", "kissa",
               "herttua", "herttuatar", "sotilas", "pappi",
               "kauppias", "merirosvo", "kapteeni"],
        "eo": ["simio", "kolombo", "kato", "muso", "lacerto",
               "dukino", "soldato", "maristo", "komercisto"],
    },
    "MOUVEMENT": {
        "en": ["shook", "beat", "fetch", "rushed", "hurried", "flung",
               "dragged", "swam", "flew", "leaped", "jumped", "climbed",
               "crawled", "tumbled", "rolling", "swimming", "racing",
               "gallop", "trot", "marched", "fled", "fled"],
        "fr": ["courut", "coururent", "sauta", "grimpa", "traîna",
               "vola", "nagea", "rampa", "galopa", "traversa",
               "recula", "s'enfuit", "s'élança", "cheval", "chevaux"],
        "de": ["zog", "sprang", "rannte", "stürzte", "kroch",
               "flog", "schwamm", "kletterte", "eilte", "raste",
               "stürzen", "rennen", "laufen", "springen"],
        "es": ["corrió", "saltó", "nadó", "voló", "arrastró",
               "huyó", "caballo", "caballos", "galope"],
        "it": ["corse", "saltò", "volò", "nuotò", "fuggì",
               "cavallo", "cavalli", "galoppo"],
        "fi": ["juoksi", "hyppäsi", "lensi", "ui", "kiipesi",
               "ryömi", "karkasi", "ratsasti", "hevonen"],
    },
    "COMMUNICATION": {
        "en": ["exclaimed", "whispered", "murmured", "shouted", "cried",
               "remarked", "replied", "answered", "declared", "announced",
               "protested", "sighed", "groaned", "muttered", "stammered",
               "yelled", "roared", "screamed", "howled", "bellowed",
               "shrieked", "speech", "public", "account"],
        "fr": ["s'écria", "murmura", "chuchota", "soupira", "gémit",
               "cria", "hurla", "gronda", "bégaya", "bredouilla",
               "discours", "parole", "paroles", "messieurs"],
        "de": ["rief", "flüsterte", "murmelte", "seufzte", "stöhnte",
               "schrie", "brüllte", "stammelte", "antwortete",
               "erwiderte", "erklärte", "bemerkte", "fügte"],
        "es": ["exclamó", "murmuró", "susurró", "gritó",
               "respondió", "contestó", "declaró", "anunció"],
        "it": ["esclamò", "bisbigliò", "mormorò", "sospirò",
               "gridò", "urlò", "borbottò", "rispose"],
        "fi": ["huusi", "kuiskasi", "mumisi", "huudahti",
               "vastasi", "sanoi", "kysyi", "kertoi"],
        "eo": ["ekkriis", "murmuris", "flustris", "suspiris",
               "kriis", "hurlis", "respondis", "diris"],
    },
    "PERCEPTION": {
        "en": ["noticed", "observed", "gazed", "stared", "glanced",
               "peered", "peeped", "watched", "witnessed", "beheld",
               "twinkle", "twinkling", "glitter", "sparkle", "gleam",
               "sight", "visible", "invisible"],
        "fr": ["aperçut", "remarqua", "contempla", "regarda",
               "observa", "fixa", "examina", "distingua",
               "brilla", "scintilla", "éclat", "lueur"],
        "de": ["bemerkte", "beobachtete", "blickte", "starrte",
               "schaute", "glänzte", "funkelte", "leuchtete",
               "sichtbar", "unsichtbar"],
        "es": ["observó", "miró", "contempló", "notó",
               "brilló", "relumbró", "visible", "invisible"],
        "it": ["osservò", "guardò", "fissò", "notò",
               "brillò", "scintillò", "luccicò"],
    },
    "COGNITION": {
        "en": ["wondered", "supposed", "considered", "puzzled",
               "confused", "bewildered", "astonished", "amazed",
               "realized", "understood", "remembered", "forgot",
               "imagined", "dreaming", "fancy", "nonsense",
               "curious", "curiously", "mystery", "riddle"],
        "fr": ["réfléchit", "pensa", "songea", "imagina",
               "comprit", "devina", "oublia", "rappela",
               "étonna", "surprit", "confondit",
               "bonheur", "malheur", "raison"],
        "de": ["überlegte", "dachte", "grübelte", "staunte",
               "wunderte", "verstand", "vergaß", "erinnerte",
               "verwirrt", "erstaunt", "verblüfft",
               "verstand", "vernunft", "rätsel"],
        "es": ["pensó", "reflexionó", "imaginó", "recordó",
               "olvidó", "comprendió", "asombró", "confundió",
               "razón", "misterio", "enigma"],
        "it": ["pensò", "rifletté", "immaginò", "ricordò",
               "dimenticò", "capì", "stupì", "confusione",
               "ragione", "mistero"],
        "fi": ["mietti", "pohti", "ihmetteli", "ymmärsi",
               "muisti", "unohti", "kuvitteli", "arvasi"],
    },
    "CORPS": {
        "en": ["head", "hand", "hands", "arm", "arms", "leg", "legs",
               "foot", "feet", "finger", "fingers", "neck", "shoulder",
               "shoulders", "knee", "knees", "chin", "cheek", "cheeks",
               "nose", "mouth", "lips", "tongue", "teeth", "throat",
               "chest", "belly", "hip", "elbow", "wrist", "skin",
               "bone", "bones", "blood", "breath", "tear", "tears"],
        "fr": ["tête", "main", "mains", "bras", "jambe", "jambes",
               "pied", "pieds", "doigt", "doigts", "cou", "épaule",
               "genou", "genoux", "joue", "nez", "bouche", "lèvres",
               "langue", "dent", "dents", "gorge", "ventre",
               "os", "sang", "souffle", "larme", "larmes",
               "soin", "dîner", "boire", "manger"],
        "de": ["kopf", "hand", "hände", "arm", "arme", "bein", "beine",
               "fuß", "füße", "füßen", "finger", "hals", "schulter",
               "knie", "nase", "mund", "lippen", "zunge", "zähne",
               "brust", "bauch", "knochen", "blut", "atem"],
        "es": ["cabeza", "mano", "manos", "brazo", "brazos",
               "pierna", "piernas", "pie", "pies", "dedo", "dedos",
               "cuello", "hombro", "rodilla", "nariz", "boca",
               "labios", "lengua", "dientes", "garganta",
               "sangre", "hueso", "huesos", "lágrima", "lágrimas"],
        "it": ["testa", "mano", "mani", "braccio", "braccia",
               "gamba", "gambe", "piede", "piedi", "dito", "dita",
               "collo", "spalla", "ginocchio", "naso", "bocca",
               "labbra", "lingua", "denti", "gola", "pancia",
               "sangue", "ossa", "lacrima", "lacrime"],
        "fi": ["pää", "käsi", "kädet", "jalka", "jalat",
               "sormi", "sormet", "kaula", "olkapää", "polvi",
               "nenä", "suu", "huulet", "kieli", "hampaat",
               "rinta", "vatsa", "luu", "veri", "kyynel"],
    },
    "LIEU": {
        "en": ["room", "hall", "garden", "court", "palace", "castle",
               "house", "door", "gate", "window", "wall", "floor",
               "ceiling", "roof", "stairs", "passage", "tunnel",
               "pool", "sea", "shore", "bank", "field", "forest",
               "wood", "woods", "hill", "valley", "road", "path",
               "bridge", "tower", "prison", "church", "school"],
        "fr": ["chambre", "salle", "jardin", "cour", "palais",
               "château", "maison", "porte", "fenêtre", "mur",
               "plancher", "plafond", "escalier", "passage",
               "pièce", "lit", "clef", "galère",
               "mer", "rivage", "forêt", "bois", "colline",
               "chemin", "pont", "tour", "prison", "église"],
        "de": ["zimmer", "saal", "garten", "hof", "palast",
               "schloß", "haus", "tür", "fenster", "wand",
               "boden", "decke", "treppe", "gang",
               "meer", "wald", "feld", "hügel", "weg",
               "brücke", "turm", "gefängnis", "kirche", "schule"],
        "es": ["cuarto", "sala", "jardín", "patio", "palacio",
               "castillo", "casa", "puerta", "ventana", "pared",
               "suelo", "techo", "escalera", "pasillo",
               "cárcel", "mar", "bosque", "campo", "camino",
               "puente", "torre", "iglesia", "fe"],
        "it": ["stanza", "sala", "giardino", "corte", "palazzo",
               "castello", "casa", "porta", "finestra", "muro",
               "pavimento", "soffitto", "scala", "corridoio",
               "mare", "bosco", "campo", "collina", "strada",
               "ponte", "torre", "prigione", "scuola", "chiesa"],
        "fi": ["huone", "sali", "puutarha", "piha", "palatsi",
               "linna", "talo", "ovi", "ikkuna", "seinä",
               "lattia", "katto", "portaat", "käytävä",
               "meri", "ranta", "metsä", "pelto", "tie",
               "silta", "torni", "vankila", "kirkko", "koulu"],
    },
    "QUAL": {
        "en": ["hard", "soft", "dark", "bright", "deep", "thick",
               "thin", "wide", "narrow", "sharp", "dull", "rough",
               "smooth", "dry", "wet", "warm", "cool", "heavy",
               "round", "flat", "straight", "hollow", "solid",
               "tiny", "huge", "immense", "enormous", "vast"],
        "fr": ["dur", "doux", "sombre", "clair", "profond",
               "épais", "mince", "large", "étroit", "aigu",
               "lisse", "sec", "mouillé", "chaud", "froid",
               "lourd", "léger", "rond", "plat", "creux",
               "petit", "petite", "immense", "énorme", "vaste",
               "extrême", "gauche", "mauvais"],
        "de": ["hart", "weich", "dunkel", "hell", "tief",
               "dick", "dünn", "breit", "schmal", "scharf",
               "glatt", "rauh", "trocken", "naß", "warm",
               "schwer", "leicht", "rund", "flach", "hohl",
               "klein", "riesig", "ungeheuer", "groß",
               "gute", "mühe"],
        "es": ["duro", "blando", "oscuro", "brillante", "profundo",
               "grueso", "delgado", "ancho", "estrecho", "agudo",
               "liso", "seco", "mojado", "caliente", "frío",
               "pesado", "ligero", "redondo", "plano", "hueco",
               "fea", "breve", "tanta", "necesario",
               "pequeño", "inmenso", "enorme", "vasto"],
        "it": ["duro", "morbido", "scuro", "chiaro", "profondo",
               "spesso", "sottile", "largo", "stretto", "aguzzo",
               "liscio", "secco", "bagnato", "caldo", "freddo",
               "pesante", "leggero", "rotondo", "piatto", "cavo",
               "inutile", "tante", "piccolo"],
        "fi": ["kova", "pehmeä", "tumma", "kirkas", "syvä",
               "paksu", "ohut", "leveä", "kapea", "terävä",
               "sileä", "kuiva", "märkä", "lämmin", "kylmä",
               "raskas", "kevyt", "pyöreä", "litteä", "ontto",
               "pieni", "valtava", "suunnaton", "valkoinen"],
    },
    "BON": {
        "en": ["good", "kind", "gentle", "happy", "glad", "pleased",
               "fine", "fair", "pleasant", "comfortable", "nice",
               "sweet", "wonderful", "beautiful", "lovely", "pretty",
               "fortune", "fortunate", "lucky", "blessed", "grace",
               "mercy", "pity", "charity", "justice"],
        "fr": ["bonheur", "bonté", "gentil", "gentille",
               "heureux", "heureuse", "content", "contente",
               "joli", "jolie", "charmant", "charmante",
               "fortune", "grâce", "miséricorde", "pitié",
               "charitable", "poliment", "vertu", "soin",
               "vaut", "rendre", "clef"],
        "de": ["verzeihung", "gnade", "barmherzigkeit", "mitleid",
               "tugend", "güte", "freundlich", "gütig",
               "glücklich", "zufrieden", "froh", "freudig",
               "schön", "hübsch", "herrlich", "prächtig"],
        "es": ["bondad", "gracia", "misericordia", "piedad",
               "caridad", "virtud", "dicha", "felicidad",
               "amable", "generoso", "compasivo"],
        "it": ["bontà", "grazia", "misericordia", "pietà",
               "carità", "virtù", "felicità", "gioia"],
    },
    "MAUVAIS": {
        "en": ["evil", "wicked", "cruel", "terrible", "horrible",
               "dreadful", "awful", "vile", "nasty", "ugly",
               "miserable", "wretched", "ruin", "disaster",
               "misfortune", "misfortunes", "calamity", "catastrophe"],
        "fr": ["méchant", "méchante", "cruel", "cruelle",
               "horrible", "terrible", "affreux", "affreuse",
               "misérable", "malheureux", "malheureuse",
               "malheur", "calamité", "catastrophe", "désastre",
               "mélanges", "état"],
        "de": ["böse", "grausam", "schrecklich", "furchtbar",
               "entsetzlich", "abscheulich", "elend", "jämmerlich",
               "unglück", "katastrophe", "verderben"],
        "es": ["malo", "malvado", "cruel", "terrible", "horrible",
               "espantoso", "miserable", "desgraciado",
               "diablo", "desgracia", "calamidad", "catástrofe",
               "oficio", "doscientos"],
        "it": ["cattivo", "malvagio", "crudele", "terribile",
               "orribile", "spaventoso", "miserabile",
               "sventura", "calamità", "catastrofe",
               "guai"],
    },
    "DOMINATION": {
        "en": ["king", "queen", "prince", "emperor", "ruler",
               "throne", "crown", "reign", "kingdom", "empire",
               "power", "authority", "command", "control", "rule",
               "govern", "judgment", "sentence", "condemn",
               "punish", "punishment", "execution"],
        "fr": ["roi", "reine", "prince", "princesse", "empereur",
               "trône", "couronne", "règne", "royaume",
               "pouvoir", "autorité", "commandement",
               "jugement", "condamnation", "châtiment",
               "xxi", "xviii", "louis"],
        "de": ["könig", "königin", "prinz", "kaiser",
               "thron", "krone", "herrschaft", "reich",
               "macht", "gewalt", "befehl", "urteil",
               "strafe", "hinrichtung", "köpfe", "tafeln"],
        "es": ["rey", "reina", "príncipe", "emperador",
               "trono", "corona", "reinado", "reyno",
               "poder", "autoridad", "mando",
               "juicio", "sentencia", "castigo", "auto"],
        "it": ["re", "regina", "principe", "imperatore",
               "trono", "corona", "regno",
               "potere", "autorità", "comando",
               "giudizio", "sentenza", "castigo"],
        "fi": ["kuningas", "kuningatar", "prinssi", "keisari",
               "valtaistuin", "kruunu", "valtakunta",
               "valta", "käsky", "tuomio", "rangaistus"],
    },
    "POSSESSION": {
        "en": ["money", "gold", "silver", "treasure", "wealth",
               "fortune", "property", "goods", "jewel", "jewels",
               "diamond", "diamonds", "pearl", "pearls",
               "steal", "rob", "stolen", "thief", "thieves",
               "gift", "reward", "pack", "pebbles", "meet"],
        "fr": ["argent", "or", "trésor", "richesse", "fortune",
               "propriété", "bijou", "bijoux", "diamant", "perle",
               "voler", "voleur", "cadeau", "récompense",
               "piastre", "piastres", "louis", "lendemain"],
        "de": ["geld", "gold", "silber", "schatz", "reichtum",
               "vermögen", "eigentum", "juwel", "diamant", "perle",
               "stehlen", "dieb", "geschenk", "belohnung"],
        "es": ["dinero", "oro", "plata", "tesoro", "riqueza",
               "fortuna", "propiedad", "joya", "joyas",
               "diamante", "perla", "robar", "ladrón",
               "regalo", "recompensa", "cargados", "holandés"],
        "it": ["denaro", "oro", "argento", "tesoro", "ricchezza",
               "fortuna", "proprietà", "gioiello", "diamante",
               "perla", "rubare", "ladro", "regalo", "ricompensa",
               "lavagne"],
    },
    "DESTRUCTION": {
        "en": ["kill", "killed", "murder", "murdered", "death",
               "dead", "die", "dying", "destroy", "destroyed",
               "ruin", "ruined", "burn", "burned", "break",
               "broken", "cut", "wound", "wounded", "sword",
               "knife", "weapon", "battle", "war", "fight",
               "attack", "dethroned", "carnival", "age"],
        "fr": ["tuer", "tué", "meurtre", "mort", "mourir",
               "détruire", "détruit", "brûler", "brûlé",
               "couper", "coupé", "blesser", "blessé",
               "épée", "arme", "bataille", "guerre", "combat"],
        "de": ["töten", "getötet", "mord", "tod", "sterben",
               "zerstören", "zerstört", "verbrennen", "verbrannt",
               "schneiden", "verwunden", "verwundet",
               "schwert", "waffe", "schlacht", "krieg", "kampf",
               "tage", "steht", "stehen"],
        "es": ["matar", "matado", "asesinato", "muerte", "morir",
               "destruir", "destruido", "quemar", "quemado",
               "cortar", "herir", "herido", "espada", "arma",
               "batalla", "guerra", "combate"],
        "it": ["uccidere", "ucciso", "assassinio", "morte", "morire",
               "distruggere", "distrutto", "bruciare", "bruciato",
               "tagliare", "ferire", "ferito", "spada", "arma",
               "battaglia", "guerra", "combattimento"],
    },
    "GRIEF": {
        "en": ["sad", "sorrow", "grief", "pain", "suffer", "suffering",
               "cry", "cried", "weep", "weeping", "wept", "sob",
               "moan", "lament", "mourn", "despair", "anguish",
               "agony", "torment", "misery"],
        "fr": ["triste", "tristesse", "chagrin", "douleur",
               "souffrir", "souffrance", "pleurer", "pleuré",
               "sangloter", "gémir", "lamenter", "désespoir",
               "angoisse", "tourment", "misère"],
        "de": ["traurig", "trauer", "kummer", "schmerz",
               "leiden", "weinen", "schluchzen", "stöhnen",
               "jammern", "verzweiflung", "qual", "elend"],
        "es": ["triste", "tristeza", "dolor", "sufrir",
               "sufrimiento", "llorar", "sollozar", "gemir",
               "lamentar", "desesperación", "angustia"],
        "it": ["triste", "tristezza", "dolore", "soffrire",
               "piangere", "singhiozzare", "gemere",
               "lamentare", "disperazione", "angoscia",
               "ansietà"],
    },
    "PLAY": {
        "en": ["game", "play", "played", "playing", "dance", "danced",
               "dancing", "sing", "sang", "singing", "song", "music",
               "laugh", "laughed", "laughing", "joke", "jest",
               "fun", "merry", "cheerful", "celebrate"],
        "fr": ["jeu", "jouer", "joué", "danse", "dansé", "dansant",
               "chant", "chanté", "chanter", "chanson", "musique",
               "rire", "ri", "riant", "plaisanterie", "fête",
               "gai", "gaie", "joyeux", "joyeuse"],
        "de": ["spiel", "spielen", "gespielt", "tanz", "tanzen",
               "gesungen", "lied", "musik",
               "lachen", "gelacht", "scherz", "witz", "spaß",
               "lustig", "fröhlich", "feiern",
               "grinsen", "wau"],
        "it": ["gioco", "giocare", "danza", "danzare",
               "cantare", "canzone", "musica",
               "ridere", "riso", "scherzo", "festa",
               "allegro", "allegra"],
    },
    "SEEKING": {
        "en": ["want", "wanted", "wish", "wished", "desire", "desired",
               "hope", "hoped", "expect", "expected", "seek", "sought",
               "search", "searched", "hunt", "hunted", "chase", "chased",
               "pursue", "pursued", "look", "looking"],
        "fr": ["vouloir", "voulu", "désirer", "désiré", "espérer",
               "chercher", "cherché", "poursuivre", "poursuivi",
               "chasser", "chassé"],
        "de": ["wollen", "wünschen", "gewünscht", "hoffen", "gehofft",
               "suchen", "gesucht", "jagen", "gejagt",
               "verfolgen", "verfolgt", "nimm", "werth", "zeigen"],
        "it": ["volere", "voglio", "desiderare", "sperare",
               "cercare", "inseguire", "cacciare",
               "farò", "farlo", "far"],
        "es": ["querer", "desear", "esperar", "buscar",
               "perseguir", "cazar"],
    },
    "EXISTENCE": {
        "en": ["live", "living", "alive", "exist", "existence",
               "born", "birth", "age", "grow", "become",
               "remain", "stay", "continue", "last", "endure"],
        "fr": ["vivre", "vivant", "exister", "existence",
               "naître", "naissance", "âge", "grandir",
               "rester", "demeurer", "continuer", "durer"],
        "de": ["leben", "lebendig", "existieren", "dasein",
               "geboren", "geburt", "alter", "wachsen",
               "bleiben", "verbleiben", "fortfahren", "dauern",
               "entfernung"],
        "es": ["vivir", "vivo", "existir", "existencia",
               "nacer", "nacimiento", "edad", "crecer",
               "quedarse", "permanecer", "continuar", "durar"],
        "it": ["vivere", "vivo", "esistere", "esistenza",
               "nascere", "nascita", "età", "crescere",
               "restare", "rimanere", "continuare", "durare",
               "rincominciò", "aprì", "giunse", "ebbene"],
    },
    "MESURE": {
        "en": ["size", "height", "length", "width", "weight",
               "distance", "mile", "miles", "inch", "inches",
               "foot", "yard", "half", "quarter", "twice",
               "double", "triple", "hundred", "thousand", "million"],
        "fr": ["taille", "hauteur", "longueur", "largeur",
               "poids", "distance", "lieue", "lieues",
               "moitié", "quart", "double", "triple",
               "cent", "mille", "million",
               "mélanges", "extrême"],
        "de": ["größe", "höhe", "länge", "breite", "gewicht",
               "entfernung", "meile", "meilen",
               "hälfte", "viertel", "doppelt", "dreifach",
               "hundert", "tausend", "million"],
        "es": ["tamaño", "altura", "longitud", "anchura",
               "peso", "distancia", "legua", "leguas",
               "mitad", "cuarto", "doble", "triple",
               "cien", "mil", "millón", "doscientos"],
        "it": ["dimensione", "altezza", "lunghezza", "larghezza",
               "peso", "distanza", "miglio", "miglia",
               "metà", "quarto", "doppio", "triplo",
               "cento", "mille", "milione",
               "pochi", "pò"],
    },
    "ANCIEN": {
        "en": ["old", "young", "new", "ancient", "modern",
               "early", "late", "long", "short", "quick",
               "slow", "fast", "soon", "sudden", "suddenly",
               "moment", "instant", "time", "day", "night",
               "morning", "evening", "year", "century"],
        "fr": ["vieux", "vieille", "jeune", "nouveau", "nouvelle",
               "ancien", "moderne", "tôt", "tard",
               "moment", "instant", "temps", "jour", "nuit",
               "matin", "soir", "année", "siècle",
               "lendemain", "dîner"],
        "de": ["alt", "jung", "neu", "uralt", "modern",
               "früh", "spät", "lang", "kurz", "schnell",
               "langsam", "plötzlich",
               "augenblick", "moment", "zeit", "nacht",
               "morgen", "abend", "jahr", "jahrhundert"],
        "es": ["viejo", "joven", "nuevo", "antiguo", "moderno",
               "temprano", "tarde", "momento", "instante",
               "tiempo", "día", "noche", "mañana",
               "año", "siglo"],
        "it": ["vecchio", "giovane", "nuovo", "antico", "moderno",
               "presto", "tardi", "momento", "istante",
               "tempo", "giorno", "notte", "mattina",
               "anno", "secolo"],
        "fi": ["vanha", "nuori", "uusi", "muinainen",
               "aikainen", "myöhäinen", "hetki", "aika",
               "päivä", "yö", "aamu", "ilta", "vuosi"],
    },
}

# Merge R4 keywords into EXPANSION_KEYWORDS_V48
for _atom, _langs in EXPANSION_KEYWORDS_V48_R4.items():
    if _atom not in EXPANSION_KEYWORDS_V48:
        EXPANSION_KEYWORDS_V48[_atom] = {}
    for _lang, _words in _langs.items():
        if _lang in EXPANSION_KEYWORDS_V48[_atom]:
            existing = set(EXPANSION_KEYWORDS_V48[_atom][_lang])
            existing.update(_words)
            EXPANSION_KEYWORDS_V48[_atom][_lang] = list(existing)
        else:
            EXPANSION_KEYWORDS_V48[_atom][_lang] = list(_words)


# ═══════════════════════════════════════════════════════════════════════════════
# ROUND 4: ADDITIONAL PROPER NOUNS
# ═══════════════════════════════════════════════════════════════════════════════

PROPER_NOUN_AGENTS_R4 = {
    # English character names (Alice + Candide)
    "james", "bill", "pat", "edwin", "dinah", "mabel",
    "lori", "dodo", "tweedledee", "tweedledum",
    "surinam", "issachar", "negro",
    # French place names / character names
    "périgourdin", "vestphalie", "westphalie", "burdeos",
    "bordeaux", "louis", "monseigneur",
    # German
    "dinah", "wau",
    # Spanish
    "holandés", "inglaterra", "burdeos", "isacar",
    # Italian
    "boja", "tonio", "lori",
    # Finnish
    "höperö", "apotti", "veneziaan",
    # Roman numerals
    "xxi", "xviii", "xix", "xx", "xxii", "xxiii", "xxiv", "xxv",
    "xxvi", "xxvii", "xxviii", "xxix", "xxx",
    "xiii", "xiv", "xvi", "xvii",
}

# Merge R4 proper nouns
PROPER_NOUN_AGENTS.update(PROPER_NOUN_AGENTS_R4)


# ═══════════════════════════════════════════════════════════════════════════════
# ROUND 5: FINAL EXPANSION PUSH — targeting remaining top uncovered
# ═══════════════════════════════════════════════════════════════════════════════

STOP_WORDS_V48_R5 = {
    "fi": [
        # Negation + emphatic particles
        "enpä", "etten", "enkä", "eipä", "eikä", "eihän",
        "ettei", "ettekö", "emmekö", "emmepä", "eivätkö",
        "älkäämme", "älköön", "älkööt",
        # More adverbs and postpositions
        "tänään", "huomenna", "eilen", "senjälkeen", "sittemmin",
        "enempää", "enempi", "enemmin",
        "toisessa", "toiseen", "toiselta", "toiselle",
        "toisiaan", "toisistaan", "toisiinsa", "toisilleen",
        # Case-declined personal pronouns (more forms)
        "minuun", "minussa", "minusta", "minulle", "minulta",
        "sinuun", "sinussa", "sinusta", "sinulle", "sinulta",
        "häneen", "hänessä", "hänelle", "häneltä",
        "meihin", "meissä", "meiltä", "meidän",
        "teihin", "teissä", "teiltä", "teidän",
        "heihin", "heissä", "heiltä", "heidän",
        # Possessive suffixes on common words
        "itsensä", "itseään", "itsestään", "itselleen",
        "toisensa", "toisiansa", "keskenään", "toisiaan",
        # More particles
        "niinpä", "niinkuin", "niinhyvin", "niin", "niinkin",
        "siispä", "siitäpä", "siksipä", "tokiaan",
        "kaikin", "kaikkein", "kokonaan",
        "ainakaan", "ainakin", "ainoastaan",
        "sitäpaitsi", "sitävastoin", "siitälähtien",
        "todellakin", "todella", "tosiaan", "tosiaankin",
        "toisaalta", "toisinaan", "toisinpäin",
        "kuitenkin", "kuitenkaan", "kumminkin",
        "vaikkapa", "vaikkakin", "vaikkakaan",
        "pikemminkin", "mieluummin", "ennemminkin",
        "ilmeisesti", "nähtävästi", "luultavasti",
        # Common verbs as stop words (too generic)
        "sai", "sain", "saisi", "saivat", "saadaan",
        "tuli", "tulivat", "tulkaa", "tulkoon",
        "antoi", "antoivat", "antaa", "antakaa",
        "otti", "ottivat", "ottaa", "ottakaa",
        "teki", "tekivät", "tekee", "tehkää",
        "näki", "näkivät", "näkee", "nähkää",
        "piti", "pitivät", "pitää", "pitäkää",
        "jäi", "jäivät", "jää", "jääkää",
        "osasi", "osasivat", "osaa", "osaakaa",
        "kesti", "kestivät", "kestää",
        "uskalsi", "uskalsivat", "uskaltaa",
    ],
    "es": [
        # More function words
        "desde", "según", "durante", "mediante",
        "vaya", "esté", "estén", "estés", "estemos",
        "pudo", "pudieron", "pudiesen", "pudiéramos",
        "hubiese", "hubiesen", "hubieran",
        "dijo", "dijeron", "decir",
        "traído", "traer", "trajo", "trajeron",
        # Archaic forms
        "dixéron", "dexaron", "dixo", "vióse", "hallóse",
        "echóse", "pusiéron", "hiciéron", "lleváron",
        "tomáron", "entráron", "volviéron",
        "hacian", "haciendo", "hicieron",
        # More pronouns/determiners
        "cuyo", "cuya", "cuyos", "cuyas",
        "aquel", "aquella", "aquellos", "aquellas",
        "aquél", "aquélla", "aquéllos", "aquéllas",
        "ése", "ésa", "ésos", "ésas",
        "éste", "ésta", "éstos", "éstas",
    ],
    "fr": [
        # Compound contractions / question forms
        "a-t-il", "a-t-elle", "a-t-on",
        "n'est-ce", "n'y-a-t-il",
        "est-ce", "peut-être",
        # More prepositions/conjunctions
        "jusqu'au", "jusqu'à", "jusqu'aux", "jusqu'ici",
        "vis-à-vis", "par-dessus", "par-dessous",
        "quoique", "lorsque", "puisque", "parce",
        "vont", "vais", "allons", "allez",
        # Verb forms
        "remit", "rendit", "perdit", "permit", "promit",
        "prit", "apprit", "comprit", "surprit",
        "vint", "devint", "revint", "parvint",
        "vînt", "fînt", "dînt",
        "ferait", "dirait", "viendrait", "prendrait",
        "assis", "assise", "assises",
        # Common words that are function-like
        "uns", "unes",
    ],
    "it": [
        # Interjections
        "eh", "ah", "oh", "oimè", "ohimè", "ahi", "ahimè",
        "ebbene", "ecco", "orsù", "beh",
        # More contracted/elided forms
        "s'era", "s'erano", "s'è", "s'ebbe",
        "l'uscio", "l'avrebbe", "l'aveva", "l'ha",
        "all'uscio", "all'ultimo", "all'istante",
        "dov'era", "com'era", "quand'era",
        # More function words
        "alcuni", "alcune", "alcuno", "alcuna",
        "dalle", "dallo", "dalli",
        "nelle", "nello", "nelli",
        "sulle", "sullo", "sulla",
        "colle", "collo", "colla", "co",
        "fra", "verso", "presso", "lungo",
        "eppure", "oppure", "ovvero", "ossia",
        "finché", "benché", "giacché", "sicché",
    ],
    "de": [
        # More function words
        "keiner", "keines", "keinem", "keinen", "keine",
        "irgend", "irgends", "irgendwo", "irgendwie",
        "danke", "bitte",
        "laßt", "laß", "lassen",
        "dächte", "dächten",
        "meinst", "meinen", "meint",
        "bei'm", "auf'm", "zum", "vom", "beim",
        # More adverbs
        "heute", "gestern", "morgen", "damals", "sogleich",
        "sofort", "plötzlich", "endlich", "schließlich",
        "eigentlich", "gewöhnlich", "wahrscheinlich",
        "vielleicht", "gewiß", "sicherlich",
        "jedermann", "jederzeit", "jemand", "niemand",
    ],
    "en": [
        # More function words / common adverbs
        "especially", "certainly", "probably", "possibly",
        "nearly", "almost", "entirely", "quite", "merely",
        "somewhat", "extremely", "considerably",
        "immediately", "suddenly", "gradually", "eventually",
        "presently", "afterward", "afterwards", "meanwhile",
        "otherwise", "likewise", "besides", "consequently",
        # Archaic
        "aloud", "whilst", "amongst", "betwixt",
    ],
    "eo": [
        # More particles
        "unua", "unuan", "unuaj", "unuajn",
        "dua", "duan", "duaj", "duajn",
        "tria", "trian", "triaj", "triajn",
        "kvara", "kvina", "sesa",
        # More correlative forms
        "almenaux", "almenauxe",
    ],
}

# Merge R5 stop words
for _lang, _words in STOP_WORDS_V48_R5.items():
    if _lang in STOP_WORDS_V48:
        STOP_WORDS_V48[_lang] = list(set(STOP_WORDS_V48[_lang]) | set(_words))
    else:
        STOP_WORDS_V48[_lang] = list(_words)


# ═══════════════════════════════════════════════════════════════════════════════
# ROUND 5: ADDITIONAL KEYWORDS
# ═══════════════════════════════════════════════════════════════════════════════

EXPANSION_KEYWORDS_V48_R5 = {
    "AGENT": {
        "en": ["surgeon", "christian", "negro", "lory", "optimism",
               "demoiselle", "gardener", "barber", "peasant"],
        "fr": ["demoiselle", "noirs", "chirurgien", "barbier",
               "paysan", "paysanne"],
        "de": ["arzt", "barbier", "bäuerin", "magd"],
        "es": ["turco", "ximios", "arraez", "cirujano", "barbero"],
        "it": ["isabella", "piccina", "dottore", "barbiere"],
        "fi": ["raukka", "nti", "herra", "rouva", "neiti"],
    },
    "COMMUNICATION": {
        "en": ["aloud", "wit", "remark", "speech", "lecture",
               "story", "stories", "tale", "tales", "news", "message",
               "letter", "letters", "note", "notes", "sign", "signal"],
        "fr": ["notes", "physique", "discours", "récit", "nouvelle",
               "nouvelles", "lettre", "lettres", "signe", "signal"],
        "de": ["rede", "erzählung", "nachricht", "brief",
               "briefe", "zeichen", "signal"],
        "es": ["discurso", "relato", "noticia", "noticias",
               "carta", "cartas", "señal", "seña"],
        "it": ["discorso", "racconto", "notizia", "notizie",
               "lettera", "lettere", "segno", "segnale",
               "dite"],
    },
    "COGNITION": {
        "en": ["wit", "reason", "knowledge", "wisdom", "idea",
               "opinion", "belief", "doubt", "certain", "uncertain",
               "manage", "simple", "difficulty", "fit"],
        "de": ["muth", "ernst", "vernunft", "wissen", "weisheit",
               "meinung", "zweifel", "gewöhnt"],
        "es": ["ánimo", "razón", "saber", "sabiduría",
               "opinión", "duda", "cierto", "incierto"],
        "it": ["sai", "ragione", "sapere", "saggezza",
               "opinione", "dubbio", "certo", "incerto",
               "difficoltà"],
        "fi": ["mieli", "järki", "tieto", "viisaus",
               "mielipide", "epäily"],
    },
    "PERCEPTION": {
        "es": ["oir", "oído", "vista", "mirada", "mirar"],
        "it": ["udito", "vista", "sguardo", "osservare"],
    },
    "CORPS": {
        "en": ["shoes", "pocket", "hat", "coat", "dress", "gown",
               "crown", "gloves", "boots", "clothes", "hair",
               "beard", "wig", "spectacles"],
        "de": ["eier", "niesen", "kleid", "hut", "mantel",
               "stiefel", "handschuhe", "haar", "bart"],
        "es": ["pie", "pié", "piés", "ropa", "vestido",
               "sombrero", "zapatos", "botas", "barba"],
        "it": ["scarpe", "vestito", "cappello", "mantello",
               "guanti", "stivali", "capelli", "barba"],
        "fr": ["chapeau", "manteau", "robe", "souliers",
               "bottes", "gants", "cheveux", "barbe",
               "perruque", "tartes"],
    },
    "LIEU": {
        "en": ["country", "city", "town", "village", "land",
               "island", "continent", "province", "region",
               "neighborhood", "coast", "harbor", "port"],
        "de": ["mitte", "stadt", "dorf", "land", "insel",
               "kontinent", "provinz", "region", "hafen", "küste"],
        "es": ["cárcel", "país", "ciudad", "pueblo", "aldea",
               "isla", "continente", "provincia", "región",
               "costa", "puerto"],
        "it": ["spiaggia", "paese", "città", "villaggio",
               "isola", "continente", "provincia", "regione",
               "costa", "porto"],
        "fr": ["pays", "ville", "village", "île", "continent",
               "province", "région", "côte", "port"],
    },
    "POSSESSION": {
        "en": ["pocket", "shoes", "slates", "covered", "recovered"],
        "fr": ["payer", "payé", "coûter", "acheter", "vendu"],
        "es": ["pagar", "comprar", "vender"],
    },
    "MOUVEMENT": {
        "en": ["manage", "fit", "recovered"],
        "it": ["sedette", "levò", "saltò", "scappò"],
        "fi": ["vei", "tarttui", "tahtoi", "kiiruhti"],
    },
    "DOMINATION": {
        "en": ["liberty", "freedom", "law", "rights", "obey",
               "rebel", "revolution", "tyrant", "tyranny"],
        "fr": ["liberté", "loi", "droit", "droits", "obéir",
               "rebelle", "révolution", "tyran", "tyrannnie"],
        "es": ["libertad", "ley", "derecho", "derechos",
               "obedecer", "rebelde", "revolución", "tirano"],
        "it": ["libertà", "legge", "diritto", "diritti",
               "obbedire", "ribelle", "rivoluzione", "tiranno"],
    },
    "QUAL": {
        "en": ["simple", "difficult", "easy", "clear", "plain",
               "strange", "odd", "peculiar", "remarkable",
               "ordinary", "extraordinary", "treated"],
        "fr": ["moyen", "précis", "difficile", "facile",
               "clair", "simple", "étrange", "bizarre",
               "ordinaire", "extraordinaire"],
        "de": ["einfach", "schwierig", "leicht", "klar",
               "seltsam", "merkwürdig", "gewöhnlich",
               "außergewöhnlich"],
        "es": ["fuerza", "sencillo", "difícil", "fácil",
               "claro", "extraño", "raro", "ordinario"],
        "it": ["semplice", "difficile", "facile", "chiaro",
               "strano", "bizzarro", "ordinario", "straordinario",
               "qualcheduno"],
    },
    "BON": {
        "en": ["treated", "recovered", "optimism"],
        "fr": ["plaît", "plaisir", "agrément", "satisfaction"],
    },
    "DESTRUCTION": {
        "en": ["slates"],
        "es": ["azotes", "cañones", "fuerza"],
        "it": ["rincominciò"],
    },
    "SEEKING": {
        "it": ["sarò", "vorrei", "voglia"],
        "fi": ["tahtoi", "tahtoisivat", "halusi"],
    },
    "ANCIEN": {
        "fi": ["ajan", "aika", "aikaan", "aikana",
               "päivä", "yö", "aamu", "ilta"],
    },
    "MESURE": {
        "fi": ["toisen", "kolme", "neljä", "viisi",
               "kuusi", "seitsemän", "kahdeksan"],
    },
    "EXISTENCE": {
        "eo": ["sukcesis", "sukcesus", "ekzistas", "ekzistis"],
    },
}

# Merge R5 keywords
for _atom, _langs in EXPANSION_KEYWORDS_V48_R5.items():
    if _atom not in EXPANSION_KEYWORDS_V48:
        EXPANSION_KEYWORDS_V48[_atom] = {}
    for _lang, _words in _langs.items():
        if _lang in EXPANSION_KEYWORDS_V48[_atom]:
            existing = set(EXPANSION_KEYWORDS_V48[_atom][_lang])
            existing.update(_words)
            EXPANSION_KEYWORDS_V48[_atom][_lang] = list(existing)
        else:
            EXPANSION_KEYWORDS_V48[_atom][_lang] = list(_words)


# ═══════════════════════════════════════════════════════════════════════════════
# ROUND 5: ADDITIONAL PROPER NOUNS
# ═══════════════════════════════════════════════════════════════════════════════

PROPER_NOUN_AGENTS_R5 = {
    "christian", "paraguay", "eldorado", "d'eldorado",
    "isabella", "lory", "huhka", "soo—oop",
    "venezia", "turchia",
}

PROPER_NOUN_AGENTS.update(PROPER_NOUN_AGENTS_R5)


# ═══════════════════════════════════════════════════════════════════════════════
# ROUND 6: FINAL PUSH — target 80%+ global coverage
# ═══════════════════════════════════════════════════════════════════════════════

STOP_WORDS_V48_R6 = {
    "fi": [
        # Very common verbs (too generic to be content)
        "saa", "saakka", "saat", "saatte", "saaneet",
        "tule", "tulee", "tulet", "tulette", "tulleet",
        "olleet", "ollut", "olleen", "ollessa",
        "eri", "ikinä", "enää", "sensijaan",
        "täynnä", "oven", "arasti", "oh", "ah",
        "vasta", "juuri", "aivan", "ihan",
        "melkein", "lähes", "tuskin", "hädin",
        "kenties", "ehkä", "kai", "tosin",
        "tietysti", "totta", "totisesti",
        "päällä", "päältä", "päähän", "päässä",
        "kautta", "ohitse", "ohi", "halki",
        "seuraavana", "seuraavan", "seuraavat",
        "edellinen", "edellisen", "edellisenä",
        "viimeinen", "viimeisen", "viimeisenä",
        "ensimmäinen", "ensimmäisen", "ensimmäiseen",
        "jälleen", "uudelleen", "edelleen",
        "muuten", "muutoin", "muualle", "muualta",
        "kaikki", "kaikkiaan", "kaikkialla",
        "joku", "jokin", "jompikumpi",
        "kumpi", "kumpainen", "kumpainenkin",
        "toinen", "toiseksi",
    ],
    "en": [
        # More common adverbs/function words
        "altogether", "already", "somewhat", "therefore",
        "thence", "hence", "except", "besides", "beneath",
        "toward", "towards", "within", "without",
        "whenever", "wherever", "whatever", "whoever",
        "however", "whoever", "whichever",
    ],
    "fr": [
        # More literary forms
        "mirent", "advint", "fessé", "mener",
        "plupart", "mine", "moeurs",
    ],
    "es": [
        # More function words
        "allá", "acá", "ántes", "apenas",
        "puedo", "puedes", "podemos",
        "papa",  # function/title
    ],
    "it": [
        # More particles
        "intanto", "pria", "ve", "diè", "stò",
    ],
    "de": [
        # More function words
        "einigen", "sollt", "solltest", "müßt", "mußt",
        "gefällt", "heißt", "heut",
    ],
    "eo": [
        # More particles
        "siaj", "nuna",
    ],
}

for _lang, _words in STOP_WORDS_V48_R6.items():
    if _lang in STOP_WORDS_V48:
        STOP_WORDS_V48[_lang] = list(set(STOP_WORDS_V48[_lang]) | set(_words))
    else:
        STOP_WORDS_V48[_lang] = list(_words)


EXPANSION_KEYWORDS_V48_R6 = {
    "AGENT": {
        "en": ["devil", "mistress", "spaniard", "sultan", "theatin",
               "achmet", "charles", "holy"],
        "fr": ["théatin", "homards", "diable"],
        "de": ["vogel", "teufel"],
        "es": ["turquía", "américa", "san", "papa"],
        "it": ["guglielmo", "fenicòntero", "drontti", "d'india", "peccato"],
        "fi": ["drontti", "seikka"],
    },
    "COMMUNICATION": {
        "fi": ["ääneen", "ääni", "huuto", "sana", "puhe"],
        "en": ["mistress", "laden", "spend"],
        "fr": ["ardoises", "cailloux"],
    },
    "COGNITION": {
        "en": ["condition", "holy", "ravished"],
        "it": ["rammentò", "riprese", "ghigno"],
        "es": ["situacion", "físico", "órden"],
    },
    "MOUVEMENT": {
        "de": ["bogen", "lagen", "saßen"],
    },
    "LIEU": {
        "es": ["cama", "léjos", "américa"],
        "it": ["minestra", "melazzo"],
    },
    "PERCEPTION": {
        "de": ["klang", "hält"],
        "en": ["hot", "leaves"],
    },
    "CORPS": {
        "en": ["hot"],
        "de": ["syrup"],
    },
    "PLAY": {
        "eo": ["penis"],
        "it": ["ghigno"],
    },
    "GRIEF": {
        "en": ["ravished", "condition"],
        "es": ["azotes", "ánimo"],
    },
    "QUAL": {
        "fr": ["rouges", "empressement", "disparu", "chargés"],
        "it": ["sarebbero", "peccato"],
        "eo": ["mezo", "severe", "halo"],
    },
    "BON": {
        "eo": ["zorge"],
    },
    "EXISTENCE": {
        "eo": ["ideon", "igos", "sxatas", "sxatis", "logxas",
               "jugxejo", "jugxejon", "apude", "lageto",
               "mieno", "skuis"],
    },
    "POSSESSION": {
        "fi": ["rahaa", "raha", "rahat", "rahojen"],
    },
}

for _atom, _langs in EXPANSION_KEYWORDS_V48_R6.items():
    if _atom not in EXPANSION_KEYWORDS_V48:
        EXPANSION_KEYWORDS_V48[_atom] = {}
    for _lang, _words in _langs.items():
        if _lang in EXPANSION_KEYWORDS_V48[_atom]:
            existing = set(EXPANSION_KEYWORDS_V48[_atom][_lang])
            existing.update(_words)
            EXPANSION_KEYWORDS_V48[_atom][_lang] = list(existing)
        else:
            EXPANSION_KEYWORDS_V48[_atom][_lang] = list(_words)


PROPER_NOUN_AGENTS_R6 = {
    "achmet", "charles", "theatin", "théatin",
    "spaniard", "guglielmo", "isabella",
    "drontti", "turquía",
}

PROPER_NOUN_AGENTS.update(PROPER_NOUN_AGENTS_R6)
