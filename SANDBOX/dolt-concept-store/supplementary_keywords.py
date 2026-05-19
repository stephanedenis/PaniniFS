#!/usr/bin/env python3
"""supplementary_keywords.py — Dutch (nl) & Portuguese (pt) keyword extensions.

Adds keyword sets for all 34 semantic atoms in Dutch and Portuguese.
These are merged into ATOM_KEYWORDS at import time alongside exotic_keywords.

Part of PaniniFS v4.3.1 — completing 10-language Latin-script coverage.

Design notes:
  - nl keywords use standard (Algemeen Nederlands / ABN) spelling
  - pt keywords use Brazilian+European forms when they differ,
    since Gutenberg Portuguese texts include both varieties
  - Each atom has 10-20 keywords per language, matching the density of
    existing keyword sets (en=545, fr=503, de=443 etc.)
"""

SUPPLEMENTARY_KEYWORDS = {
    # ═══════════════════════════════════════════════════════════════════
    # PROC atoms — predicative (actions, events)
    # ═══════════════════════════════════════════════════════════════════
    "MOUVEMENT": {
        "nl": ["gaan", "komen", "lopen", "vallen", "rennen", "vliegen",
               "springen", "bewegen", "rijden", "zwemmen", "stappen",
               "volgen", "vluchten", "naderen", "wijken", "reizen",
               "kruipen", "sluipen", "wandelen", "klimmen"],
        "pt": ["ir", "vir", "correr", "cair", "andar", "voar", "saltar",
               "mover", "nadar", "caminhar", "seguir", "fugir", "subir",
               "descer", "partir", "chegar", "viajar", "pular",
               "arrastar", "escorregar"],
    },
    "COGNITION": {
        "nl": ["denken", "weten", "begrijpen", "geloven", "herinneren",
               "overwegen", "leren", "kennen", "gedachte", "verstand",
               "rede", "menen", "vermoeden", "inzien", "beseffen",
               "oordelen", "bedenken", "geest"],
        "pt": ["pensar", "saber", "entender", "crer", "lembrar",
               "compreender", "aprender", "imaginar", "conhecer",
               "considerar", "pensamento", "razão", "mente", "juízo",
               "refletir", "raciocinar", "conceber", "meditar"],
    },
    "PERCEPTION": {
        "nl": ["zien", "horen", "kijken", "voelen", "ruiken", "proeven",
               "waarnemen", "merken", "oog", "oor", "blik", "geluid",
               "opmerken", "aanschouwen", "licht", "klank", "turen",
               "gadeslaan", "bemerken"],
        "pt": ["ver", "ouvir", "olhar", "sentir", "cheirar", "provar",
               "perceber", "notar", "olho", "ouvido", "som", "luz",
               "observar", "contemplar", "enxergar", "visão",
               "escutar", "tocar", "aroma"],
    },
    "COMMUNICATION": {
        "nl": ["zeggen", "spreken", "vragen", "antwoorden", "roepen",
               "schreeuwen", "fluisteren", "vertellen", "woord", "stem",
               "taal", "praten", "verhalen", "meedelen", "verkondigen",
               "uitroepen", "gesprek", "rede", "beweren", "zingen"],
        "pt": ["dizer", "falar", "perguntar", "responder", "chamar",
               "gritar", "sussurrar", "contar", "palavra", "voz",
               "língua", "conversar", "narrar", "declarar", "proclamar",
               "exclamar", "discurso", "cantar", "clamar", "anunciar"],
    },
    "CREATION": {
        "nl": ["maken", "scheppen", "bouwen", "schrijven", "tekenen",
               "groeien", "werken", "produceren", "weven", "vormen",
               "uitvinden", "ontwerpen", "vervaardigen", "bewerken",
               "kweken", "smeden", "schilderen", "ambacht"],
        "pt": ["fazer", "criar", "construir", "escrever", "desenhar",
               "crescer", "trabalhar", "produzir", "tecer", "formar",
               "inventar", "fabricar", "cultivar", "plantar",
               "compor", "pintar", "moldar", "forjar"],
    },
    "EXISTENCE": {
        "nl": ["zijn", "bestaan", "leven", "sterven", "worden", "blijven",
               "geboren", "dood", "werkelijk", "waar", "wezen",
               "verschijnen", "verdwijnen", "ontstaan", "vergaan"],
        "pt": ["ser", "estar", "existir", "viver", "morrer", "nascer",
               "ficar", "tornar", "morte", "vida", "real", "verdade",
               "aparecer", "desaparecer", "permanecer", "sobreviver"],
    },
    "DESTRUCTION": {
        "nl": ["vernietigen", "doden", "breken", "snijden", "branden",
               "scheuren", "oorlog", "strijd", "vechten", "aanvallen",
               "slaan", "verwoesten", "verpletteren", "slag",
               "vernielen", "neerslaan", "steken", "verbrijzelen"],
        "pt": ["destruir", "matar", "quebrar", "cortar", "queimar",
               "rasgar", "guerra", "batalha", "lutar", "atacar",
               "golpear", "devastar", "esmagar", "combate",
               "arruinar", "derrotar", "ferir", "espada"],
    },
    "POSSESSION": {
        "nl": ["hebben", "bezitten", "geven", "nemen", "verliezen",
               "kopen", "verkopen", "vinden", "stelen", "geld",
               "schat", "rijk", "arm", "eigendom", "erven",
               "verdienen", "sparen", "betalen", "schuld", "goud"],
        "pt": ["ter", "possuir", "dar", "tomar", "perder", "comprar",
               "vender", "achar", "roubar", "dinheiro", "tesouro",
               "rico", "pobre", "propriedade", "herdar",
               "ganhar", "ouro", "prata", "fortuna", "bens"],
    },
    "DOMINATION": {
        "nl": ["koning", "koningin", "heersen", "bevelen", "gehoorzamen",
               "macht", "wet", "straffen", "regeren", "gezag",
               "heer", "meester", "knecht", "onderwerpen", "troon",
               "kroon", "dwingen", "gebieden", "dienaar", "vorst"],
        "pt": ["rei", "rainha", "reinar", "mandar", "obedecer",
               "poder", "lei", "punir", "governar", "autoridade",
               "senhor", "mestre", "servo", "submeter", "trono",
               "coroa", "forçar", "ordenar", "príncipe", "imperador"],
    },
    # ═══════════════════════════════════════════════════════════════════
    # EMOT atoms — emotional processes
    # ═══════════════════════════════════════════════════════════════════
    "SEEKING": {
        "nl": ["zoeken", "willen", "verlangen", "wensen", "hopen",
               "streven", "jagen", "begeren", "dorsten", "hongeren",
               "nastreven", "behoefte", "drang", "ambitie",
               "doel", "trachten", "pogen"],
        "pt": ["procurar", "querer", "desejar", "esperar", "buscar",
               "aspirar", "caçar", "ambicionar", "sede", "fome",
               "almejar", "necessidade", "anseio", "meta",
               "perseguir", "cobiçar", "ânsia"],
    },
    "FEAR": {
        "nl": ["angst", "vrezen", "schrik", "bang", "verschrikken",
               "paniek", "beven", "sidderen", "ongerust", "huiveren",
               "vrees", "ontzetting", "schrikken", "gruwel",
               "angstig", "bevreesd", "rillen"],
        "pt": ["medo", "temer", "terror", "receio", "assustar",
               "pânico", "tremer", "horror", "pavor", "susto",
               "espanto", "amedrontar", "arrepiar", "temor",
               "assombrar", "apavorar", "fobia"],
    },
    "CARE": {
        "nl": ["liefde", "houden", "zorgen", "koesteren", "beschermen",
               "troosten", "helpen", "teder", "vriendschap", "lief",
               "genegenheid", "warmte", "omhelzen", "redden",
               "mededogen", "barmhartig", "verzorgen"],
        "pt": ["amor", "amar", "cuidar", "proteger", "consolar",
               "ajudar", "carinho", "amizade", "querido", "afeto",
               "ternura", "abraçar", "salvar", "compaixão",
               "bondade", "piedade", "adorar"],
    },
    "GRIEF": {
        "nl": ["verdriet", "huilen", "treuren", "lijden", "wenen",
               "droefheid", "smart", "pijn", "rouw", "tranen",
               "weeklagen", "jammeren", "snikken", "leed",
               "hartzeer", "beklagen", "treurig"],
        "pt": ["tristeza", "chorar", "sofrer", "lamentar", "dor",
               "pena", "lágrima", "luto", "mágoa", "aflição",
               "angústia", "soluçar", "gemer", "desespero",
               "pesar", "infeliz", "pranto"],
    },
    "RAGE": {
        "nl": ["woede", "toorn", "wraak", "haat", "razen", "woedend",
               "gramschap", "verbolgen", "drift", "boosheid",
               "razernij", "vergelding", "tieren", "vloeken",
               "razen", "woest", "vergramd"],
        "pt": ["raiva", "ira", "fúria", "ódio", "vingança", "furioso",
               "cólera", "enfurecer", "indignação", "rancor",
               "irado", "arder", "maldição", "revolta",
               "furor", "encolerizar", "colérico"],
    },
    "DISGUST": {
        "nl": ["walging", "walgen", "afkeer", "verachten", "minachten",
               "weerzin", "walgelijk", "bederf", "stank", "smerig",
               "afschuw", "gruwelen", "verafschuwen", "bah",
               "misselijk", "afstotend", "vies"],
        "pt": ["nojo", "repugnância", "asco", "desprezar", "repugnar",
               "aversão", "nojento", "podridão", "fedor", "sujo",
               "horror", "abominar", "detestar", "repelir",
               "nauseante", "asqueroso", "imundo"],
    },
    "PLAY": {
        "nl": ["spelen", "lachen", "vreugde", "plezier", "dansen",
               "feest", "zingen", "genieten", "vrolijk", "humor",
               "grappen", "vermaak", "pret", "lol",
               "schertsen", "blij", "jolig"],
        "pt": ["brincar", "rir", "alegria", "prazer", "dançar",
               "festa", "cantar", "divertir", "feliz", "humor",
               "piada", "entretenimento", "diversão", "gozo",
               "gracejo", "contente", "folgar"],
    },
    "TEDIUM": {
        "nl": ["verveling", "vervelen", "moe", "vermoeidheid", "lusteloos",
               "saai", "monotoon", "eentonig", "apathie", "onverschillig",
               "mat", "traag", "loom", "futloos",
               "slaperig", "lauw", "lethargisch"],
        "pt": ["tédio", "entediar", "cansaço", "cansado", "aborrecimento",
               "monótono", "apatia", "indiferente", "fastio",
               "desânimo", "preguiça", "sonolento", "maçante",
               "enfadonho", "letárgico", "languor", "desinteresse"],
    },
    # ═══════════════════════════════════════════════════════════════════
    # ABS atoms — abstract structures
    # ═══════════════════════════════════════════════════════════════════
    "RELATION": {
        "nl": ["relatie", "verband", "verbinding", "band", "tussen",
               "verwantschap", "betrekking", "samenhang", "koppeling",
               "verhouding", "connectie", "link", "schakel",
               "associatie", "correlatie", "wisselwerking"],
        "pt": ["relação", "vínculo", "conexão", "laço", "entre",
               "parentesco", "ligação", "associação", "elo",
               "correspondência", "correlação", "interação",
               "nexo", "afinidade", "enlace", "junção"],
    },
    "STRUCTURE": {
        "nl": ["structuur", "vorm", "patroon", "systeem", "orde",
               "bouw", "samenstelling", "organisatie", "schema",
               "hiërarchie", "netwerk", "raamwerk", "opbouw",
               "constructie", "rangschikking", "architectuur"],
        "pt": ["estrutura", "forma", "padrão", "sistema", "ordem",
               "construção", "composição", "organização", "esquema",
               "hierarquia", "rede", "quadro", "configuração",
               "arquitetura", "arranjo", "disposição"],
    },
    "ORDRE": {
        "nl": ["orde", "regel", "wet", "rij", "rangorde", "volgorde",
               "reeks", "rangschikking", "discipline", "regelmaat",
               "logica", "methode", "classificatie", "categorie",
               "hiërarchie", "opeenvolging", "ordening"],
        "pt": ["ordem", "regra", "lei", "fila", "hierarquia", "sequência",
               "série", "classificação", "disciplina", "regularidade",
               "lógica", "método", "categoria", "organização",
               "sucessão", "arranjo", "ordenação"],
    },
    "MESURE": {
        "nl": ["meten", "maat", "getal", "telling", "gewicht", "hoeveelheid",
               "lengte", "grootte", "breedte", "hoogte", "diepte",
               "afstand", "berekening", "evenredigheid",
               "verhouding", "omvang", "schaal"],
        "pt": ["medir", "medida", "número", "contagem", "peso", "quantidade",
               "comprimento", "tamanho", "largura", "altura", "profundidade",
               "distância", "cálculo", "proporção",
               "extensão", "escala", "dimensão"],
    },
    "RÉCURRENCE": {
        "nl": ["herhaling", "cyclus", "ritme", "terugkeer", "patroon",
               "weer", "opnieuw", "steeds", "telkens", "gewoonte",
               "traditie", "seizoen", "periode", "kringloop",
               "frequentie", "refrein", "routine"],
        "pt": ["repetição", "ciclo", "ritmo", "retorno", "padrão",
               "novamente", "sempre", "hábito", "tradição",
               "estação", "período", "frequência", "rotina",
               "refrão", "recorrente", "periódico", "constante"],
    },
    "INVARIANCE": {
        "nl": ["onveranderlijk", "vast", "bestendig", "eeuwig", "altijd",
               "onwrikbaar", "permanent", "stabiel", "constante",
               "absoluut", "onwankelbaar", "duurzaam", "onveranderbaar",
               "oneindig", "tijdloos", "onsterfelijk"],
        "pt": ["imutável", "fixo", "constante", "eterno", "sempre",
               "permanente", "estável", "absoluto", "perpétuo",
               "imortal", "inalterável", "durável", "infinito",
               "atemporal", "invariável", "perene"],
    },
    "DUALITÉ": {
        "nl": ["tegenstelling", "paar", "dubbel", "tweeledig", "contrast",
               "twee", "spiegel", "paradox", "tegendeel", "tweevoudig",
               "ambivalentie", "polariteit", "symmetrie", "dualiteit",
               "evenwicht", "tegenpool", "dubbelzinnig"],
        "pt": ["oposição", "par", "duplo", "contraste", "dois",
               "espelho", "paradoxo", "contrário", "ambivalência",
               "polaridade", "simetria", "dualidade", "equilíbrio",
               "dicotomia", "antítese", "dual", "ambíguo"],
    },
    # ═══════════════════════════════════════════════════════════════════
    # ENT atoms — entities (objects, substances)
    # ═══════════════════════════════════════════════════════════════════
    "CHOSE": {
        "nl": ["ding", "zaak", "voorwerp", "object", "iets", "stuk",
               "artikel", "element", "materie", "exemplaar",
               "goederen", "waar", "spul", "bezit"],
        "pt": ["coisa", "objeto", "algo", "item", "artigo",
               "elemento", "matéria", "peça", "bem", "pertence",
               "substância", "mercadoria", "produto", "treco"],
    },
    "AGENT": {
        "nl": ["mens", "persoon", "man", "vrouw", "kind", "volk",
               "iemand", "heer", "dame", "jongen", "meisje",
               "burger", "individu", "bewoner", "inwoner",
               "figuur", "karakter", "held"],
        "pt": ["pessoa", "homem", "mulher", "criança", "povo",
               "alguém", "senhor", "senhora", "menino", "menina",
               "cidadão", "indivíduo", "habitante", "figura",
               "personagem", "herói", "gente", "sujeito"],
    },
    "CORPS": {
        "nl": ["lichaam", "hoofd", "hand", "oog", "hart", "been",
               "arm", "voet", "borst", "mond", "gezicht", "bloed",
               "bot", "huid", "haar", "vinger", "rug", "schouder"],
        "pt": ["corpo", "cabeça", "mão", "olho", "coração", "perna",
               "braço", "pé", "peito", "boca", "rosto", "sangue",
               "osso", "pele", "cabelo", "dedo", "costas", "ombro"],
    },
    "LIEU": {
        "nl": ["plaats", "huis", "kamer", "stad", "land", "wereld",
               "dorp", "tuin", "bos", "berg", "zee", "rivier",
               "straat", "weg", "veld", "grond", "hemel", "aarde",
               "kasteel", "kerk"],
        "pt": ["lugar", "casa", "quarto", "cidade", "país", "mundo",
               "aldeia", "jardim", "floresta", "monte", "mar", "rio",
               "rua", "caminho", "campo", "terra", "céu", "castelo",
               "igreja", "palácio"],
    },
    "MATIÈRE": {
        "nl": ["water", "vuur", "steen", "hout", "ijzer", "goud",
               "zilver", "aarde", "lucht", "stof", "klei", "zand",
               "glas", "leer", "doek", "wol", "metaal", "lood"],
        "pt": ["água", "fogo", "pedra", "madeira", "ferro", "ouro",
               "prata", "terra", "ar", "pó", "barro", "areia",
               "vidro", "couro", "pano", "lã", "metal", "chumbo"],
    },
    # ═══════════════════════════════════════════════════════════════════
    # QUAL atoms — qualitative (properties, attributes)
    # ═══════════════════════════════════════════════════════════════════
    "BON": {
        "nl": ["goed", "mooi", "schoon", "prachtig", "fraai", "lief",
               "uitstekend", "voortreffelijk", "edel", "deugd",
               "volmaakt", "heilig", "genade", "gezegende",
               "zuiver", "wijs", "rechtvaardig"],
        "pt": ["bom", "belo", "bonito", "formoso", "lindo", "nobre",
               "excelente", "perfeito", "virtuoso", "sagrado",
               "puro", "sábio", "justo", "gracioso",
               "divino", "santo", "sublime"],
    },
    "GRAND": {
        "nl": ["groot", "lang", "hoog", "enorm", "breed", "wijd",
               "reusachtig", "machtig", "kolossaal", "immens",
               "ontzaglijk", "geweldig", "groots", "massief",
               "omvangrijk", "uitgestrekt", "onmetelijk"],
        "pt": ["grande", "alto", "enorme", "largo", "vasto", "amplo",
               "imenso", "colossal", "gigante", "poderoso",
               "majestoso", "grandioso", "monumental", "massivo",
               "extenso", "magnífico", "descomunal"],
    },
    "VRAI": {
        "nl": ["waar", "echt", "werkelijk", "waarheid", "juist", "recht",
               "oprecht", "eerlijk", "waarachtig", "zeker",
               "onbetwistbaar", "betrouwbaar", "authentiek",
               "feitelijk", "gewis", "getrouw", "geloofwaardig"],
        "pt": ["verdade", "verdadeiro", "real", "certo", "justo",
               "honesto", "sincero", "autêntico", "exato",
               "fiel", "genuíno", "legítimo", "verídico",
               "correto", "incontestável", "confiável", "fidedigno"],
    },
    "INTENSE": {
        "nl": ["heel", "zeer", "sterk", "krachtig", "hevig", "intens",
               "geweldig", "vurig", "onstuimig", "verschrikkelijk",
               "ontzettend", "buitengewoon", "heftig", "machtig",
               "overweldigend", "formidabel", "verbazingwekkend"],
        "pt": ["muito", "forte", "intenso", "poderoso", "violento",
               "feroz", "ardente", "terrível", "extraordinário",
               "formidável", "tremendo", "avassalador", "veemente",
               "imenso", "profundo", "extremo", "enérgico"],
    },
    "ANCIEN": {
        "nl": ["oud", "vroeger", "eeuwen", "verleden", "eertijds",
               "antiek", "oeroude", "weleer", "voorouder",
               "voormalig", "eens", "lang geleden", "oudheid",
               "traditie", "erfenis", "overlevering", "oeroud"],
        "pt": ["antigo", "velho", "outrora", "passado", "séculos",
               "ancestral", "arcaico", "remoto", "antepassado",
               "primitivo", "imemorial", "antiquíssimo", "antiguidade",
               "tradição", "herança", "pretérito", "milenar"],
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# Supplementary structural/function words
# ═══════════════════════════════════════════════════════════════════════════════

SUPPLEMENTARY_NEGATION_WORDS = {
    "nl": ["niet", "geen", "nooit", "nergens", "niemand", "niets",
           "noch", "nimmer"],
    "pt": ["não", "nenhum", "nunca", "ninguém", "nada", "jamais",
           "nem", "tampouco"],
}

SUPPLEMENTARY_QUANTIFIER_WORDS = {
    "nl": ["veel", "weinig", "alle", "elk", "ieder", "sommige",
           "meer", "minder", "meeste", "enige", "talrijk",
           "verscheidene", "geheel", "genoeg"],
    "pt": ["muito", "pouco", "todo", "cada", "algum", "vários",
           "mais", "menos", "maioria", "bastante", "numeroso",
           "diversos", "inteiro", "suficiente"],
}

SUPPLEMENTARY_MODIFIER_WORDS = {
    "nl": ["heel", "zeer", "nogal", "tamelijk", "vrij", "bijzonder",
           "buitengewoon", "enorm", "uiterst", "werkelijk",
           "ontzettend", "geweldig", "alleszins", "volstrekt"],
    "pt": ["muito", "bastante", "bem", "tão", "extremamente",
           "incrivelmente", "completamente", "absolutamente",
           "realmente", "verdadeiramente", "totalmente",
           "inteiramente", "profundamente", "enormemente"],
}


# ═══════════════════════════════════════════════════════════════════════════════
# LANGUAGE PROFILES for nl and pt
# ═══════════════════════════════════════════════════════════════════════════════

SUPPLEMENTARY_LANGUAGE_PROFILES = {
    "nl": {
        "lang_name": "Dutch",
        "word_order": "SOV",
        "morphological_richness": "medium",
        "case_system": False,
        "grammatical_gender": True,
        "agglutinative": False,
        "avg_sentence_length_preference": 20.0,
        "subordination_tendency": "high",
        "formality_levels": "2-tier",
        "notes": "V2 in main clauses, SOV in subordinates (like German). "
                 "Compound nouns. No case system (unlike German). "
                 "De/het article system (common/neuter gender).",
        "determiners": {"de", "het", "een", "dit", "dat", "deze", "die",
                        "mijn", "jouw", "zijn", "haar", "ons", "onze",
                        "hun", "uw", "elk", "ieder", "alle", "welk",
                        "enig", "sommige", "geen"},
        "prepositions": {"in", "op", "aan", "van", "met", "voor", "door",
                         "uit", "om", "na", "naar", "bij", "tot", "over",
                         "onder", "tussen", "tegen", "zonder", "langs",
                         "tijdens", "achter", "boven", "beneden", "sedert"},
        "conjunctions": {"en", "maar", "of", "want", "dus", "noch",
                         "omdat", "dat", "als", "wanneer", "terwijl",
                         "hoewel", "ofschoon", "tenzij", "zodat",
                         "voordat", "nadat", "sinds", "opdat",
                         "echter", "toch", "nochtans", "desondanks"},
        "pronouns": {"ik", "mij", "me", "jij", "je", "jou", "hij", "hem",
                     "zij", "ze", "haar", "het", "wij", "we", "ons",
                     "jullie", "u", "hen", "hun", "zich", "men",
                     "wie", "wat", "welke", "die", "dat",
                     "iemand", "niemand", "iets", "niets", "alles"},
        "auxiliaries": {"zijn", "is", "ben", "bent", "was", "waren",
                        "hebben", "heeft", "heb", "hebt", "had", "hadden",
                        "worden", "wordt", "werd", "werden",
                        "zullen", "zal", "zou", "zouden",
                        "kunnen", "kan", "kon", "konden",
                        "moeten", "moet", "moest", "moesten",
                        "mogen", "mag", "mocht", "mochten",
                        "willen", "wil", "wilde", "wilden"},
        "negations": {"niet", "geen", "nooit", "nergens", "niemand",
                      "niets", "noch", "nimmer", "geenszins"},
        "past_markers": {"was", "waren", "had", "hadden", "deed", "werd"},
        "present_markers": {"is", "ben", "zijn", "heeft", "heb", "doe"},
        "future_markers": {"zal", "zullen", "gaan"},
        "formal_markers": {"evenwel", "derhalve", "dienovereenkomstig",
                           "bijgevolg", "bovendien", "voorts", "aldus"},
        "archaic_markers": {"gij", "ge", "uw", "uwer", "dezer", "welaan",
                            "zijne", "hare", "alzo", "mitsdien",
                            "gansch", "alzoo", "zulks"},
        "literary_markers": {"ach", "helaas", "wee", "zie", "welaan",
                             "voorwaar", "eilaas"},
        "temporal_connectors": {"dan", "daarna", "vervolgens", "eerder",
                                "toen", "terwijl", "ondertussen",
                                "plotseling", "opeens", "eindelijk",
                                "tenslotte", "weldra", "inmiddels"},
        "causal_connectors": {"want", "omdat", "doordat", "daarom",
                              "derhalve", "dus", "bijgevolg", "immers"},
        "adversative_connectors": {"maar", "echter", "toch", "hoewel",
                                   "nochtans", "desondanks", "ofschoon",
                                   "niettemin", "daarentegen"},
        "additive_connectors": {"en", "ook", "bovendien", "daarnaast",
                                "tevens", "eveneens", "voorts"},
        "measurement_system": "metric",
        "cultural_food": {"brood", "kaas", "boter", "stamppot", "pap",
                          "bier", "jenever", "haring"},
    },
    "pt": {
        "lang_name": "Portuguese",
        "word_order": "SVO",
        "morphological_richness": "high",
        "case_system": False,
        "grammatical_gender": True,
        "agglutinative": False,
        "avg_sentence_length_preference": 22.0,
        "subordination_tendency": "high",
        "formality_levels": "3-tier",
        "notes": "Rich verb morphology with personal infinitive (unique among "
                 "Romance languages). ser/estar distinction. Future subjunctive "
                 "still productive. Brazilian vs European variants.",
        "determiners": {"o", "a", "os", "as", "um", "uma", "uns", "umas",
                        "este", "esta", "estes", "estas",
                        "esse", "essa", "esses", "essas",
                        "aquele", "aquela", "aqueles", "aquelas",
                        "meu", "minha", "teu", "tua", "seu", "sua",
                        "nosso", "nossa", "vosso", "vossa"},
        "prepositions": {"de", "em", "a", "com", "por", "para", "sem",
                         "sobre", "entre", "até", "desde", "após",
                         "contra", "durante", "sob", "perante",
                         "ante", "através", "mediante", "conforme"},
        "conjunctions": {"e", "mas", "ou", "nem", "porém", "pois",
                         "porque", "que", "se", "quando", "enquanto",
                         "embora", "como", "já que", "visto que",
                         "contudo", "todavia", "entretanto",
                         "conquanto", "senão", "portanto", "logo"},
        "pronouns": {"eu", "me", "mim", "tu", "te", "ti", "ele", "ela",
                     "lhe", "o", "a", "nós", "nos", "vós", "vos",
                     "eles", "elas", "lhes", "os", "as", "se", "si",
                     "quem", "que", "qual", "cujo", "onde",
                     "alguém", "ninguém", "algo", "nada", "tudo"},
        "auxiliaries": {"ser", "é", "sou", "és", "somos", "são",
                        "era", "foi", "foram", "estar", "está", "estou",
                        "ter", "tem", "tenho", "tens", "temos", "têm",
                        "tinha", "teve", "tiveram",
                        "haver", "há", "hei", "houve", "havia"},
        "negations": {"não", "nunca", "jamais", "nada", "ninguém",
                      "nenhum", "nem", "tampouco", "sequer"},
        "past_markers": {"pretérito perfeito", "imperfeito"},
        "present_markers": {"presente"},
        "future_markers": {"futuro"},
        "formal_markers": {"outrossim", "destarte", "porquanto",
                           "mormente", "ademais", "doravante"},
        "archaic_markers": {"vós", "vossa mercê", "donde", "alhures",
                            "outrem", "mister", "assaz", "aquém",
                            "sobredito", "suso", "ínclito"},
        "literary_markers": {"ai", "eis", "oxalá", "ó", "ora"},
        "temporal_connectors": {"depois", "antes", "então", "quando",
                                "enquanto", "logo", "de repente",
                                "subitamente", "finalmente", "enfim",
                                "em breve", "entretanto", "outrora"},
        "causal_connectors": {"porque", "pois", "já que", "visto que",
                              "portanto", "logo", "por conseguinte",
                              "assim"},
        "adversative_connectors": {"mas", "porém", "contudo", "todavia",
                                   "embora", "apesar de", "entretanto",
                                   "não obstante", "conquanto"},
        "additive_connectors": {"e", "também", "além disso", "ainda",
                                "igualmente", "outrossim"},
        "measurement_system": "metric",
        "cultural_food": {"pão", "vinho", "azeite", "bacalhau", "arroz",
                          "feijão", "café", "mandioca"},
    },
}


def merge_supplementary_keywords(atom_keywords):
    """Merge SUPPLEMENTARY_KEYWORDS into the main ATOM_KEYWORDS dictionary.

    Called at module load time by gutenberg_multilingual_validator.py.
    Modifies atom_keywords in-place.
    """
    for atom, lang_dict in SUPPLEMENTARY_KEYWORDS.items():
        if atom not in atom_keywords:
            continue
        for lang, keywords in lang_dict.items():
            if lang not in atom_keywords[atom]:
                atom_keywords[atom][lang] = keywords[:]
            else:
                existing = set(atom_keywords[atom][lang])
                atom_keywords[atom][lang].extend(
                    kw for kw in keywords if kw not in existing
                )
