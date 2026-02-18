#!/usr/bin/env python3
"""
morpho_semantic_bridge.py — Pont morphologie ↔ sémantique

Objectif : Résoudre n'importe quelle forme fléchie vers son lemme d'atome,
en exploitant :
  1. Tables de verbes irréguliers par langue
  2. Lemmatisation rule-based par suppression de suffixes
  3. Inférence par familles de langues (cognats romans, germaniques)
  4. Racines étymologiques partagées (latin, proto-germanique, sanskrit)

Principe : mot_surface → candidats_lemmes → match ATOM_KEYWORDS → atome(s)

L'inférence inter-langues fonctionne ainsi :
  - Si "fell" (EN) n'est pas dans ATOM_KEYWORDS, on le résout en "fall" (lemme EN)
  - Si un mot DE inconnu ressemble à un cognat EN, on hérite de l'atome
  - Les familles romanes (FR/IT/ES) partagent des racines latines communes
  - EO est dérivable mécaniquement (suffixes réguliers + racines romanes)
  - FI est agglutinant : on dépile les suffixes de cas/personne

Usage :
  from morpho_semantic_bridge import resolve_word, lemmatize
"""

import re
from collections import defaultdict

# ═══════════════════════════════════════════════════════════════════════════════
# 1. TABLES DE VERBES IRRÉGULIERS
# ═══════════════════════════════════════════════════════════════════════════════
# Chaque entrée : {forme_fléchie: lemme_infinitif}
# On ne couvre que les verbes présents dans ATOM_KEYWORDS ou fréquents dans
# les textes littéraires du XIXe (Alice, Candide).

IRREGULAR_VERBS = {
    "en": {
        # MOUVEMENT
        "fell": "fall", "fallen": "fall", "falling": "fall", "falls": "fall",
        "went": "go", "gone": "go", "goes": "go", "going": "go",
        "came": "come", "coming": "come", "comes": "come",
        "ran": "run", "running": "run", "runs": "run",
        "flew": "fly", "flown": "fly", "flying": "fly", "flies": "fly",
        "swam": "swim", "swum": "swim", "swimming": "swim",
        "slid": "slide", "sliding": "slide",
        "walked": "walk", "walking": "walk",
        "jumped": "jump", "jumping": "jump",
        "moved": "move", "moving": "move",
        "rushed": "rush", "rushing": "rush",
        "hurried": "hurry", "hurrying": "hurry",
        "tumbled": "tumble", "tumbling": "tumble",
        "followed": "follow", "following": "follow",
        "chased": "chase", "chasing": "chase",
        "wandered": "wander", "wandering": "wander",
        # PERCEPTION
        "saw": "see", "seen": "see", "seeing": "see", "sees": "see",
        "heard": "hear", "hearing": "hear", "hears": "hear",
        "looked": "look", "looking": "look", "looks": "look",
        "watched": "watch", "watching": "watch",
        "felt": "feel", "feeling": "feel", "feels": "feel",
        "noticed": "notice", "noticing": "notice",
        "observed": "observe", "observing": "observe",
        "appeared": "appear", "appearing": "appear", "appears": "appear",
        "seemed": "seem", "seeming": "seem", "seems": "seem",
        "smelled": "smell", "smelling": "smell",
        "tasted": "taste", "tasting": "taste",
        # COGNITION
        "thought": "think", "thinking": "think", "thinks": "think",
        "knew": "know", "known": "know", "knowing": "know", "knows": "know",
        "understood": "understand", "understanding": "understand",
        "believed": "believe", "believing": "believe", "believes": "believe",
        "remembered": "remember", "remembering": "remember",
        "wondered": "wonder", "wondering": "wonder",
        "considered": "consider", "considering": "consider",
        "realized": "realize", "realizing": "realize",
        "imagined": "imagine", "imagining": "imagine",
        "learned": "learn", "learnt": "learn", "learning": "learn",
        # COMMUNICATION
        "said": "say", "saying": "say", "says": "say",
        "told": "tell", "telling": "tell", "tells": "tell",
        "asked": "ask", "asking": "ask", "asks": "ask",
        "spoke": "speak", "spoken": "speak", "speaking": "speak",
        "answered": "answer", "answering": "answer",
        "replied": "reply", "replying": "reply",
        "called": "call", "calling": "call", "calls": "call",
        "cried": "cry", "crying": "cry", "cries": "cry",
        "shouted": "shout", "shouting": "shout",
        "whispered": "whisper", "whispering": "whisper",
        "talked": "talk", "talking": "talk",
        "declared": "declare", "declaring": "declare",
        # EXISTENCE
        "was": "be", "were": "be", "been": "be", "being": "be",
        "is": "be", "am": "be", "are": "be",
        "existed": "exist", "existing": "exist", "exists": "exist",
        "lived": "live", "living": "live", "lives": "live",
        "died": "die", "dying": "die", "dies": "die",
        "became": "become", "becoming": "become", "becomes": "become",
        "remained": "remain", "remaining": "remain",
        "stayed": "stay", "staying": "stay",
        # POSSESSION
        "had": "have", "having": "have", "has": "have",
        "gave": "give", "given": "give", "giving": "give", "gives": "give",
        "took": "take", "taken": "take", "taking": "take", "takes": "take",
        "got": "get", "gotten": "get", "getting": "get", "gets": "get",
        "kept": "keep", "keeping": "keep", "keeps": "keep",
        "lost": "lose", "losing": "lose", "loses": "lose",
        "found": "find", "finding": "find", "finds": "find",
        "stole": "steal", "stolen": "steal", "stealing": "steal",
        "bought": "buy", "buying": "buy",
        "sold": "sell", "selling": "sell",
        # CREATION
        "made": "make", "making": "make", "makes": "make",
        "created": "create", "creating": "create",
        "built": "build", "building": "build",
        "grew": "grow", "grown": "grow", "growing": "grow",
        "produced": "produce", "producing": "produce",
        "invented": "invent", "inventing": "invent",
        "wrote": "write", "written": "write", "writing": "write",
        "drew": "draw", "drawn": "draw", "drawing": "draw",
        "painted": "paint", "painting": "paint",
        "worked": "work", "working": "work",
        # DESTRUCTION
        "destroyed": "destroy", "destroying": "destroy",
        "broke": "break", "broken": "break", "breaking": "break",
        "killed": "kill", "killing": "kill",
        "burned": "burn", "burnt": "burn", "burning": "burn",
        "tore": "tear", "torn": "tear", "tearing": "tear",
        "smashed": "smash", "smashing": "smash",
        "crushed": "crush", "crushing": "crush",
        "fought": "fight", "fighting": "fight",
        "attacked": "attack", "attacking": "attack",
        # DOMINATION
        "ruled": "rule", "ruling": "rule",
        "commanded": "command", "commanding": "command",
        "ordered": "order", "ordering": "order",
        "obeyed": "obey", "obeying": "obey",
        "judged": "judge", "judging": "judge",
        "punished": "punish", "punishing": "punish",
        "forced": "force", "forcing": "force",
        "controlled": "control", "controlling": "control",
        # SEEKING
        "wanted": "want", "wanting": "want", "wants": "want",
        "desired": "desire", "desiring": "desire",
        "sought": "seek", "seeking": "seek",
        "searched": "search", "searching": "search",
        "explored": "explore", "exploring": "explore",
        "expected": "expect", "expecting": "expect",
        "hoped": "hope", "hoping": "hope",
        "wished": "wish", "wishing": "wish",
        # FEAR
        "feared": "fear", "fearing": "fear",
        "frightened": "frighten", "frightening": "frighten",
        "scared": "scare", "scaring": "scare",
        "trembled": "tremble", "trembling": "tremble",
        "fled": "flee", "fleeing": "flee",
        "escaped": "escape", "escaping": "escape",
        # CARE
        "loved": "love", "loving": "love",
        "protected": "protect", "protecting": "protect",
        "comforted": "comfort", "comforting": "comfort",
        "embraced": "embrace", "embracing": "embrace",
        "nurtured": "nurture", "nurturing": "nurture",
        # PLAY
        "played": "play", "playing": "play",
        "laughed": "laugh", "laughing": "laugh",
        "amused": "amuse", "amusing": "amuse",
        "danced": "dance", "dancing": "dance",
        "celebrated": "celebrate", "celebrating": "celebrate",
        # GRIEF
        "mourned": "mourn", "mourning": "mourn",
        "wept": "weep", "weeping": "weep",
        "missed": "miss", "missing": "miss",
        "lamented": "lament", "lamenting": "lament",
        # RAGE
        "angered": "anger",
        "irritated": "irritate", "irritating": "irritate",
        "annoyed": "annoy", "annoying": "annoy",
        # DISGUST
        "disgusted": "disgust", "disgusting": "disgust",
        "loathed": "loathe", "loathing": "loathe",
        "abhorred": "abhor", "abhorring": "abhor",
    },

    "fr": {
        # MOUVEMENT — passé simple, imparfait, participe, futur
        "alla": "aller", "allait": "aller", "allèrent": "aller", "allé": "aller",
        "allée": "aller", "allés": "aller", "allant": "aller", "va": "aller",
        "irai": "aller", "iras": "aller", "ira": "aller", "iront": "aller",
        "vint": "venir", "venait": "venir", "vinrent": "venir", "venu": "venir",
        "venue": "venir", "viens": "venir", "vient": "venir", "venant": "venir",
        "viendra": "venir",
        "courut": "courir", "courait": "courir", "couru": "courir",
        "courant": "courir", "court": "courir", "courra": "courir",
        "tomba": "tomber", "tombait": "tomber", "tombé": "tomber",
        "tombée": "tomber", "tombant": "tomber", "tombe": "tomber",
        "marchait": "marcher", "marcha": "marcher", "marché": "marcher",
        "marchant": "marcher",
        "sauta": "sauter", "sautait": "sauter", "sauté": "sauter",
        "bougeait": "bouger", "bougea": "bouger", "bougé": "bouger",
        "volait": "voler", "vola": "voler", "volé": "voler",
        "suivit": "suivre", "suivait": "suivre", "suivi": "suivre",
        "suivant": "suivre", "suit": "suivre",
        "poursuivit": "poursuivre", "poursuivait": "poursuivre",
        "poursuivi": "poursuivre",
        "glissa": "glisser", "glissait": "glisser", "glissé": "glisser",
        "descendit": "descendre", "descendait": "descendre",
        "descendu": "descendre", "descendant": "descendre",
        "monta": "monter", "montait": "monter", "monté": "monter",
        # PERCEPTION
        "vit": "voir", "voyait": "voir", "vu": "voir", "vue": "voir",
        "voit": "voir", "voyant": "voir", "verra": "voir", "virent": "voir",
        "entendit": "entendre", "entendait": "entendre", "entendu": "entendre",
        "entendant": "entendre", "entend": "entendre",
        "regardait": "regarder", "regarda": "regarder", "regardé": "regarder",
        "regardant": "regarder",
        "sentit": "sentir", "sentait": "sentir", "senti": "sentir",
        "sentant": "sentir", "sent": "sentir",
        "remarqua": "remarquer", "remarquait": "remarquer",
        "remarqué": "remarquer",
        "observait": "observer", "observa": "observer", "observé": "observer",
        "paraissait": "paraître", "parut": "paraître", "paru": "paraître",
        "semblait": "sembler", "sembla": "sembler", "semblé": "sembler",
        # COGNITION
        "pensait": "penser", "pensa": "penser", "pensé": "penser",
        "pensant": "penser",
        "savait": "savoir", "sut": "savoir", "su": "savoir",
        "sachant": "savoir", "sais": "savoir", "sait": "savoir",
        "comprit": "comprendre", "comprenait": "comprendre",
        "compris": "comprendre", "comprenant": "comprendre",
        "comprend": "comprendre",
        "croyait": "croire", "crut": "croire", "cru": "croire",
        "croyant": "croire", "croit": "croire",
        "souvint": "souvenir", "souvenait": "souvenir",
        "réfléchissait": "réfléchir", "réfléchit": "réfléchir",
        "imaginait": "imaginer", "imagina": "imaginer", "imaginé": "imaginer",
        "apprit": "apprendre", "apprenait": "apprendre",
        "appris": "apprendre", "apprenant": "apprendre",
        # COMMUNICATION
        "dit": "dire", "disait": "dire", "dirent": "dire",
        "disant": "dire", "dis": "dire",
        "parlait": "parler", "parla": "parler", "parlé": "parler",
        "parlant": "parler",
        "demanda": "demander", "demandait": "demander",
        "demandé": "demander", "demandant": "demander",
        "répondit": "répondre", "répondait": "répondre",
        "répondu": "répondre", "répondant": "répondre",
        "appela": "appeler", "appelait": "appeler", "appelé": "appeler",
        "cria": "crier", "criait": "crier", "crié": "crier",
        "criant": "crier",
        "murmura": "murmurer", "murmurait": "murmurer",
        "murmuré": "murmurer",
        "déclara": "déclarer", "déclarait": "déclarer",
        "raconta": "raconter", "racontait": "raconter",
        "raconté": "raconter",
        # EXISTENCE
        "était": "être", "fut": "être", "été": "être",
        "étaient": "être", "étant": "être", "est": "être",
        "suis": "être", "sommes": "être", "êtes": "être", "sont": "être",
        "sera": "être", "serait": "être", "seront": "être",
        "fût": "être", "furent": "être",
        "existait": "exister", "exista": "exister",
        "vivait": "vivre", "vécut": "vivre", "vécu": "vivre",
        "vivant": "vivre", "vit_vivre": "vivre",
        "mourut": "mourir", "mourait": "mourir", "mort": "mourir",
        "mourant": "mourir", "meurt": "mourir",
        "devint": "devenir", "devenait": "devenir", "devenu": "devenir",
        "devient": "devenir",
        "restait": "rester", "resta": "rester", "resté": "rester",
        "naquit": "naître", "naissait": "naître", "né": "naître",
        "née": "naître",
        # POSSESSION
        "avait": "avoir", "eut": "avoir", "eu": "avoir",
        "ayant": "avoir", "ont": "avoir", "aura": "avoir",
        "eurent": "avoir", "aurait": "avoir",
        "donna": "donner", "donnait": "donner", "donné": "donner",
        "prit": "prendre", "prenait": "prendre", "pris": "prendre",
        "prenant": "prendre", "prend": "prendre",
        "gardait": "garder", "garda": "garder", "gardé": "garder",
        "perdit": "perdre", "perdait": "perdre", "perdu": "perdre",
        "perdant": "perdre",
        "trouva": "trouver", "trouvait": "trouver", "trouvé": "trouver",
        "trouvant": "trouver",
        "vola_voler": "voler",  # sens possession (disambiguation needed)
        # CREATION
        "fit": "faire", "faisait": "faire", "fait": "faire",
        "faisant": "faire", "font": "faire", "fera": "faire",
        "firent": "faire",
        "créa": "créer", "créait": "créer", "créé": "créer",
        "construisit": "construire", "construisait": "construire",
        "construit": "construire",
        "poussait": "pousser", "poussa": "pousser", "poussé": "pousser",
        "écrivit": "écrire", "écrivait": "écrire", "écrit": "écrire",
        "écrivant": "écrire",
        "dessina": "dessiner", "dessinait": "dessiner", "dessiné": "dessiner",
        "peignit": "peindre", "peignait": "peindre", "peint": "peindre",
        "travailla": "travailler", "travaillait": "travailler",
        "travaillé": "travailler",
        # DESTRUCTION
        "détruisit": "détruire", "détruisait": "détruire",
        "détruit": "détruire",
        "cassa": "casser", "cassait": "casser", "cassé": "casser",
        "tua": "tuer", "tuait": "tuer", "tué": "tuer",
        "coupa": "couper", "coupait": "couper", "coupé": "couper",
        "brûla": "brûler", "brûlait": "brûler", "brûlé": "brûler",
        "déchira": "déchirer", "déchirait": "déchirer", "déchiré": "déchirer",
        "écrasa": "écraser", "écrasait": "écraser", "écrasé": "écraser",
        "combattit": "combattre", "combattait": "combattre",
        "combattu": "combattre",
        "attaqua": "attaquer", "attaquait": "attaquer", "attaqué": "attaquer",
        # DOMINATION
        "régna": "régner", "régnait": "régner", "régné": "régner",
        "commanda": "commander", "commandait": "commander",
        "commandé": "commander",
        "ordonna": "ordonner", "ordonnait": "ordonner", "ordonné": "ordonner",
        "obéit": "obéir", "obéissait": "obéir", "obéi": "obéir",
        "jugea": "juger", "jugeait": "juger", "jugé": "juger",
        "punit": "punir", "punissait": "punir",
        # SEEKING
        "voulait": "vouloir", "voulut": "vouloir", "voulu": "vouloir",
        "voulant": "vouloir", "veut": "vouloir", "veux": "vouloir",
        "désirait": "désirer", "désira": "désirer", "désiré": "désirer",
        "cherchait": "chercher", "chercha": "chercher", "cherché": "chercher",
        "espérait": "espérer", "espéra": "espérer", "espéré": "espérer",
        "attendait": "attendre", "attendit": "attendre", "attendu": "attendre",
        "souhaitait": "souhaiter", "souhaita": "souhaiter",
        # FEAR
        "craignait": "craindre", "craignit": "craindre",
        "craint": "craindre",
        "effraya": "effrayer", "effrayait": "effrayer", "effrayé": "effrayer",
        "tremblait": "trembler", "trembla": "trembler", "tremblé": "trembler",
        "fuyait": "fuir", "fuit": "fuir", "fui": "fuir",
        # CARE
        "aimait": "aimer", "aima": "aimer", "aimé": "aimer",
        "aimée": "aimer", "aimant": "aimer",
        "protégea": "protéger", "protégeait": "protéger",
        "protégé": "protéger",
        "consola": "consoler", "consolait": "consoler", "consolé": "consoler",
        "embrassa": "embrasser", "embrassait": "embrasser",
        "embrassé": "embrasser",
        # PLAY
        "jouait": "jouer", "joua": "jouer", "joué": "jouer",
        "riait": "rire", "rit": "rire", "ri": "rire", "riant": "rire",
        "dansait": "danser", "dansa": "danser", "dansé": "danser",
        # GRIEF
        "pleurait": "pleurer", "pleura": "pleurer", "pleuré": "pleurer",
    },

    "de": {
        # MOUVEMENT — Präteritum (littéraire), Partizip II, Präsens
        "ging": "gehen", "gegangen": "gehen", "geht": "gehen",
        "gehend": "gehen",
        "kam": "kommen", "gekommen": "kommen", "kommt": "kommen",
        "kommend": "kommen",
        "lief": "laufen", "gelaufen": "laufen", "läuft": "laufen",
        "laufend": "laufen",
        "fiel": "fallen", "gefallen": "fallen", "fällt": "fallen",
        "fallend": "fallen",
        "sprang": "springen", "gesprungen": "springen",
        "flog": "fliegen", "geflogen": "fliegen", "fliegt": "fliegen",
        "folgte": "folgen", "gefolgt": "folgen", "folgend": "folgen",
        "eilte": "eilen", "geeilt": "eilen",
        "wanderte": "wandern", "gewandert": "wandern",
        "stürzte": "stürzen", "gestürzt": "stürzen",
        "glitt": "gleiten", "geglitten": "gleiten",
        # PERCEPTION
        "sah": "sehen", "gesehen": "sehen", "sieht": "sehen",
        "sehend": "sehen",
        "hörte": "hören", "gehört": "hören", "hörend": "hören",
        "schaute": "schauen", "geschaut": "schauen",
        "fühlte": "fühlen", "gefühlt": "fühlen", "fühlend": "fühlen",
        "bemerkte": "bemerken", "bemerkt": "bemerken",
        "beobachtete": "beobachten", "beobachtet": "beobachten",
        "schien": "scheinen", "geschienen": "scheinen", "scheint": "scheinen",
        "roch": "riechen", "gerochen": "riechen",
        "schmeckte": "schmecken", "geschmeckt": "schmecken",
        # COGNITION
        "dachte": "denken", "gedacht": "denken", "denkt": "denken",
        "denkend": "denken",
        "wusste": "wissen", "gewusst": "wissen", "weiß": "wissen",
        "verstand": "verstehen", "verstanden": "verstehen",
        "versteht": "verstehen",
        "glaubte": "glauben", "geglaubt": "glauben",
        "erinnerte": "erinnern", "erinnert": "erinnern",
        "überlegte": "überlegen", "überlegt": "überlegen",
        "stellte": "vorstellen", "vorgestellt": "vorstellen",
        "lernte": "lernen", "gelernt": "lernen",
        # COMMUNICATION
        "sagte": "sagen", "gesagt": "sagen", "sagt": "sagen",
        "sagend": "sagen",
        "sprach": "sprechen", "gesprochen": "sprechen",
        "spricht": "sprechen", "sprechend": "sprechen",
        "fragte": "fragen", "gefragt": "fragen", "fragend": "fragen",
        "antwortete": "antworten", "geantwortet": "antworten",
        "rief": "rufen", "gerufen": "rufen", "rufend": "rufen",
        "schrie": "schreien", "geschrien": "schreien",
        "schreiend": "schreien",
        "flüsterte": "flüstern", "geflüstert": "flüstern",
        "erzählte": "erzählen", "erzählt": "erzählen",
        # EXISTENCE
        "war": "sein", "gewesen": "sein", "ist": "sein",
        "sind": "sein", "seiend": "sein", "wäre": "sein",
        "waren": "sein",
        "lebte": "leben", "gelebt": "leben", "lebt": "leben",
        "starb": "sterben", "gestorben": "sterben", "stirbt": "sterben",
        "wurde": "werden", "geworden": "werden", "wird": "werden",
        "blieb": "bleiben", "geblieben": "bleiben", "bleibt": "bleiben",
        # POSSESSION
        "hatte": "haben", "gehabt": "haben", "hat": "haben",
        "habend": "haben", "hatten": "haben",
        "gab": "geben", "gegeben": "geben", "gibt": "geben",
        "gebend": "geben",
        "nahm": "nehmen", "genommen": "nehmen", "nimmt": "nehmen",
        "nehmend": "nehmen",
        "behielt": "behalten", "behalten_pp": "behalten",
        "verlor": "verlieren", "verloren": "verlieren",
        "fand": "finden", "gefunden": "finden", "findet": "finden",
        "stahl": "stehlen", "gestohlen": "stehlen",
        "kaufte": "kaufen", "gekauft": "kaufen",
        "verkaufte": "verkaufen", "verkauft": "verkaufen",
        # CREATION
        "machte": "machen", "gemacht": "machen", "macht": "machen",
        "schuf": "schaffen", "geschaffen": "schaffen",
        "baute": "bauen", "gebaut": "bauen",
        "wuchs": "wachsen", "gewachsen": "wachsen", "wächst": "wachsen",
        "erzeugte": "erzeugen", "erzeugt": "erzeugen",
        "erfand": "erfinden", "erfunden": "erfinden",
        "schrieb": "schreiben", "geschrieben": "schreiben",
        "zeichnete": "zeichnen", "gezeichnet": "zeichnen",
        "malte": "malen", "gemalt": "malen",
        "arbeitete": "arbeiten", "gearbeitet": "arbeiten",
        # DESTRUCTION
        "zerstörte": "zerstören", "zerstört": "zerstören",
        "brach": "brechen", "gebrochen": "brechen", "bricht": "brechen",
        "tötete": "töten", "getötet": "töten",
        "schnitt": "schneiden", "geschnitten": "schneiden",
        "brannte": "brennen", "gebrannt": "brennen",
        "zerriss": "zerreißen", "zerrissen": "zerreißen",
        "zermalmte": "zermalmen", "zermalmt": "zermalmen",
        "kämpfte": "kämpfen", "gekämpft": "kämpfen",
        # DOMINATION
        "herrschte": "herrschen", "geherrscht": "herrschen",
        "befahl": "befehlen", "befohlen": "befehlen", "befiehlt": "befehlen",
        "gehorchte": "gehorchen", "gehorcht": "gehorchen",
        "richtete": "richten", "gerichtet": "richten",
        "strafte": "strafen", "gestraft": "strafen",
        # SEEKING
        "wollte": "wollen", "gewollt": "wollen", "will": "wollen",
        "suchte": "suchen", "gesucht": "suchen",
        "hoffte": "hoffen", "gehofft": "hoffen",
        "erwartete": "erwarten", "erwartet": "erwarten",
        "wünschte": "wünschen", "gewünscht": "wünschen",
        "erforschte": "erforschen", "erforscht": "erforschen",
        # FEAR
        "fürchtete": "fürchten", "gefürchtet": "fürchten",
        "erschrak": "erschrecken", "erschrocken": "erschrecken",
        "zitterte": "zittern", "gezittert": "zittern",
        "floh": "fliehen", "geflohen": "fliehen",
        # CARE
        "liebte": "lieben", "geliebt": "lieben",
        "schützte": "schützen", "geschützt": "schützen",
        "tröstete": "trösten", "getröstet": "trösten",
        "umarmte": "umarmen", "umarmt": "umarmen",
        # PLAY
        "spielte": "spielen", "gespielt": "spielen",
        "lachte": "lachen", "gelacht": "lachen", "lachend": "lachen",
        "tanzte": "tanzen", "getanzt": "tanzen",
        # GRIEF
        "weinte": "weinen", "geweint": "weinen", "weinend": "weinen",
    },

    "it": {
        # MOUVEMENT — passato remoto, imperfetto, participio
        "andò": "andare", "andava": "andare", "andato": "andare",
        "andata": "andare", "andando": "andare", "va": "andare",
        "venne": "venire", "veniva": "venire", "venuto": "venire",
        "venendo": "venire", "viene": "venire",
        "corse": "correre", "correva": "correre", "corso": "correre",
        "correndo": "correre",
        "cadde": "cadere", "cadeva": "cadere", "caduto": "cadere",
        "cadendo": "cadere", "cade": "cadere",
        "camminò": "camminare", "camminava": "camminare",
        "camminando": "camminare",
        "saltò": "saltare", "saltava": "saltare", "saltando": "saltare",
        "volò": "volare", "volava": "volare", "volando": "volare",
        "seguì": "seguire", "seguiva": "seguire", "seguito": "seguire",
        "seguendo": "seguire",
        "scivolò": "scivolare", "scivolava": "scivolare",
        "scese": "scendere", "scendeva": "scendere", "sceso": "scendere",
        # PERCEPTION
        "vide": "vedere", "vedeva": "vedere", "visto": "vedere",
        "vedendo": "vedere", "vede": "vedere",
        "sentì": "sentire", "sentiva": "sentire", "sentito": "sentire",
        "sentendo": "sentire",
        "guardò": "guardare", "guardava": "guardare",
        "guardando": "guardare",
        "osservò": "osservare", "osservava": "osservare",
        "notò": "notare", "notava": "notare",
        "sembrò": "sembrare", "sembrava": "sembrare", "sembrando": "sembrare",
        "apparve": "apparire", "appariva": "apparire", "apparso": "apparire",
        # COGNITION
        "pensò": "pensare", "pensava": "pensare", "pensando": "pensare",
        "seppe": "sapere", "sapeva": "sapere", "saputo": "sapere",
        "capì": "capire", "capiva": "capire", "capito": "capire",
        "capendo": "capire",
        "credette": "credere", "credeva": "credere", "creduto": "credere",
        "ricordò": "ricordare", "ricordava": "ricordare",
        "immaginò": "immaginare", "immaginava": "immaginare",
        "imparò": "imparare", "imparava": "imparare",
        # COMMUNICATION
        "disse": "dire", "diceva": "dire", "detto": "dire",
        "dicendo": "dire", "dice": "dire",
        "parlò": "parlare", "parlava": "parlare", "parlando": "parlare",
        "chiese": "chiedere", "chiedeva": "chiedere", "chiesto": "chiedere",
        "chiedendo": "chiedere",
        "rispose": "rispondere", "rispondeva": "rispondere",
        "risposto": "rispondere",
        "chiamò": "chiamare", "chiamava": "chiamare",
        "gridò": "gridare", "gridava": "gridare", "gridando": "gridare",
        "sussurrò": "sussurrare", "sussurrava": "sussurrare",
        "raccontò": "raccontare", "raccontava": "raccontare",
        # EXISTENCE
        "era": "essere", "fu": "essere", "stato": "essere",
        "stata": "essere", "erano": "essere", "essendo": "essere",
        "esisteva": "esistere",
        "visse": "vivere", "viveva": "vivere", "vissuto": "vivere",
        "morì": "morire", "moriva": "morire", "morto": "morire",
        "diventò": "diventare", "diventava": "diventare",
        "restò": "restare", "restava": "restare",
        "nacque": "nascere", "nasceva": "nascere", "nato": "nascere",
        # POSSESSION
        "ebbe": "avere", "aveva": "avere", "avuto": "avere",
        "avendo": "avere", "ha": "avere",
        "diede": "dare", "dava": "dare", "dato": "dare", "dando": "dare",
        "prese": "prendere", "prendeva": "prendere", "preso": "prendere",
        "prendendo": "prendere",
        "tenne": "tenere", "teneva": "tenere", "tenuto": "tenere",
        "perse": "perdere", "perdeva": "perdere", "perso": "perdere",
        "trovò": "trovare", "trovava": "trovare", "trovato": "trovare",
        "rubò": "rubare", "rubava": "rubare",
        # CREATION
        "fece": "fare", "faceva": "fare", "fatto": "fare",
        "facendo": "fare", "fa": "fare",
        "creò": "creare", "creava": "creare", "creato": "creare",
        "costruì": "costruire", "costruiva": "costruire",
        "costruito": "costruire",
        "crebbe": "crescere", "cresceva": "crescere",
        "cresciuto": "crescere",
        "scrisse": "scrivere", "scriveva": "scrivere",
        "scritto": "scrivere",
        "disegnò": "disegnare", "disegnava": "disegnare",
        "lavorò": "lavorare", "lavorava": "lavorare",
        # DESTRUCTION
        "distrusse": "distruggere", "distruggeva": "distruggere",
        "distrutto": "distruggere",
        "ruppe": "rompere", "rompeva": "rompere", "rotto": "rompere",
        "uccise": "uccidere", "uccideva": "uccidere", "ucciso": "uccidere",
        "tagliò": "tagliare", "tagliava": "tagliare",
        "bruciò": "bruciare", "bruciava": "bruciare",
        "combatté": "combattere", "combatteva": "combattere",
        # DOMINATION
        "regnò": "regnare", "regnava": "regnare",
        "comandò": "comandare", "comandava": "comandare",
        "obbedì": "obbedire", "obbediva": "obbedire",
        "giudicò": "giudicare", "giudicava": "giudicare",
        "punì": "punire", "puniva": "punire",
        # SEEKING
        "volle": "volere", "voleva": "volere", "voluto": "volere",
        "volendo": "volere", "vuole": "volere",
        "desiderò": "desiderare", "desiderava": "desiderare",
        "cercò": "cercare", "cercava": "cercare", "cercando": "cercare",
        "sperò": "sperare", "sperava": "sperare",
        "aspettò": "aspettare", "aspettava": "aspettare",
        # FEAR
        "temette": "temere", "temeva": "temere",
        "spaventò": "spaventare", "spaventava": "spaventare",
        "tremò": "tremare", "tremava": "tremare",
        "fuggì": "fuggire", "fuggiva": "fuggire", "fuggendo": "fuggire",
        # CARE
        "amò": "amare", "amava": "amare", "amato": "amare",
        "amando": "amare",
        "protesse": "proteggere", "proteggeva": "proteggere",
        "consolò": "consolare", "consolava": "consolare",
        "abbracciò": "abbracciare", "abbracciava": "abbracciare",
        # PLAY
        "giocò": "giocare", "giocava": "giocare",
        "rise": "ridere", "rideva": "ridere", "ridendo": "ridere",
    },

    "es": {
        # MOUVEMENT — pretérito indefinido, imperfecto
        "fue": "ir", "iba": "ir", "ido": "ir", "yendo": "ir",
        "vino": "venir", "venía": "venir", "venido": "venir",
        "corrió": "correr", "corría": "correr", "corriendo": "correr",
        "cayó": "caer", "caía": "caer", "caído": "caer", "cayendo": "caer",
        "caminó": "caminar", "caminaba": "caminar", "caminando": "caminar",
        "saltó": "saltar", "saltaba": "saltar", "saltando": "saltar",
        "voló": "volar", "volaba": "volar", "volando": "volar",
        "siguió": "seguir", "seguía": "seguir", "siguiendo": "seguir",
        "huyó": "huir", "huía": "huir", "huyendo": "huir",
        "bajó": "bajar", "bajaba": "bajar", "bajando": "bajar",
        "paseó": "pasear", "paseaba": "pasear",
        # PERCEPTION
        "vio": "ver", "veía": "ver", "visto": "ver", "viendo": "ver",
        "oyó": "oír", "oía": "oír", "oído": "oír", "oyendo": "oír",
        "miró": "mirar", "miraba": "mirar", "mirando": "mirar",
        "sintió": "sentir", "sentía": "sentir", "sintiendo": "sentir",
        "notó": "notar", "notaba": "notar",
        "observó": "observar", "observaba": "observar",
        "pareció": "parecer", "parecía": "parecer",
        # COGNITION
        "pensó": "pensar", "pensaba": "pensar", "pensando": "pensar",
        "supo": "saber", "sabía": "saber", "sabiendo": "saber",
        "comprendió": "comprender", "comprendía": "comprender",
        "creyó": "creer", "creía": "creer", "creyendo": "creer",
        "recordó": "recordar", "recordaba": "recordar",
        "imaginó": "imaginar", "imaginaba": "imaginar",
        "aprendió": "aprender", "aprendía": "aprender",
        # COMMUNICATION
        "dijo": "decir", "decía": "decir", "dicho": "decir",
        "diciendo": "decir",
        "habló": "hablar", "hablaba": "hablar", "hablando": "hablar",
        "preguntó": "preguntar", "preguntaba": "preguntar",
        "respondió": "responder", "respondía": "responder",
        "llamó": "llamar", "llamaba": "llamar",
        "gritó": "gritar", "gritaba": "gritar", "gritando": "gritar",
        "contó": "contar", "contaba": "contar",
        # EXISTENCE
        "era": "ser", "fue_ser": "ser", "sido": "ser", "siendo": "ser",
        "estaba": "estar", "estuvo": "estar", "estado": "estar",
        "vivió": "vivir", "vivía": "vivir",
        "murió": "morir", "moría": "morir", "muerto": "morir",
        "nació": "nacer", "nacía": "nacer",
        # POSSESSION
        "tuvo": "tener", "tenía": "tener", "tenido": "tener",
        "teniendo": "tener",
        "dio": "dar", "daba": "dar", "dado": "dar", "dando": "dar",
        "tomó": "tomar", "tomaba": "tomar",
        "perdió": "perder", "perdía": "perder",
        "encontró": "encontrar", "encontraba": "encontrar",
        "robó": "robar", "robaba": "robar",
        "compró": "comprar", "compraba": "comprar",
        "vendió": "vender", "vendía": "vender",
        # CREATION
        "hizo": "hacer", "hacía": "hacer", "hecho": "hacer",
        "haciendo": "hacer",
        "creó": "crear", "creaba": "crear",
        "construyó": "construir", "construía": "construir",
        "creció": "crecer", "crecía": "crecer",
        "escribió": "escribir", "escribía": "escribir",
        "dibujó": "dibujar", "dibujaba": "dibujar",
        "trabajó": "trabajar", "trabajaba": "trabajar",
        # DESTRUCTION
        "destruyó": "destruir", "destruía": "destruir",
        "rompió": "romper", "rompía": "romper", "roto": "romper",
        "mató": "matar", "mataba": "matar",
        "cortó": "cortar", "cortaba": "cortar",
        "quemó": "quemar", "quemaba": "quemar",
        "aplastó": "aplastar", "aplastaba": "aplastar",
        "combatió": "combatir", "combatía": "combatir",
        "atacó": "atacar", "atacaba": "atacar",
    },

    "eo": {
        # Esperanto est RÉGULIER — les suffixes sont mécaniques :
        #   -as (présent), -is (passé), -os (futur), -us (conditionnel),
        #   -u (impératif), -i (infinitif)
        #   -anta/-inta/-onta (participes actifs)
        #   -ata/-ita/-ota (participes passifs)
        # On ne couvre ici que les formes les plus fréquentes du corpus.
        "iris": "iri", "iras": "iri", "iros": "iri", "iru": "iri",
        "iranta": "iri", "irinta": "iri",
        "venis": "veni", "venas": "veni", "venos": "veni",
        "kuris": "kuri", "kuras": "kuri",
        "falis": "fali", "falas": "fali", "falos": "fali",
        "marŝis": "marŝi", "marŝas": "marŝi",
        "saltis": "salti", "saltas": "salti",
        "flugis": "flugi", "flugas": "flugi",
        "sekvis": "sekvi", "sekvas": "sekvi",
        # PERCEPTION
        "vidis": "vidi", "vidas": "vidi", "vidinta": "vidi",
        "aŭdis": "aŭdi", "aŭdas": "aŭdi",
        "rigardis": "rigardi", "rigardas": "rigardi",
        "sentis": "senti", "sentas": "senti",
        "rimarkis": "rimarki", "rimarkas": "rimarki",
        "observis": "observi", "observas": "observi",
        "ŝajnis": "ŝajni", "ŝajnas": "ŝajni",
        # COGNITION
        "pensis": "pensi", "pensas": "pensi",
        "sciis": "scii", "scias": "scii",
        "komprenis": "kompreni", "komprenas": "kompreni",
        "kredis": "kredi", "kredas": "kredi",
        "memoris": "memori", "memoras": "memori",
        "imagis": "imagi", "imagas": "imagi",
        "lernis": "lerni", "lernas": "lerni",
        # COMMUNICATION
        "diris": "diri", "diras": "diri",
        "parolis": "paroli", "parolas": "paroli",
        "demandis": "demandi", "demandas": "demandi",
        "respondis": "respondi", "respondas": "respondi",
        "vokis": "voki", "vokas": "voki",
        "kriis": "krii", "krias": "krii",
        # EXISTENCE
        "estis": "esti", "estas": "esti", "estos": "esti", "estus": "esti",
        "estu": "esti",
        "ekzistis": "ekzisti", "ekzistas": "ekzisti",
        "vivis": "vivi", "vivas": "vivi",
        "mortis": "morti", "mortas": "morti",
        "fariĝis": "fariĝi", "fariĝas": "fariĝi",
        "restis": "resti", "restas": "resti",
        # POSSESSION
        "havis": "havi", "havas": "havi",
        "posedis": "posedi", "posedas": "posedi",
        "donis": "doni", "donas": "doni",
        "prenis": "preni", "prenas": "preni",
        "gardis": "gardi", "gardas": "gardi",
        "perdis": "perdi", "perdas": "perdi",
        "trovis": "trovi", "trovas": "trovi",
        "ŝtelis": "ŝteli", "ŝtelas": "ŝteli",
        # CREATION
        "faris": "fari", "faras": "fari",
        "kreis": "krei", "kreas": "krei",
        "konstruis": "konstrui", "konstruas": "konstrui",
        "kreskis": "kreski", "kreskas": "kreski",
        "produktis": "produkti", "produktas": "produkti",
        "skribis": "skribi", "skribas": "skribi",
        "laboris": "labori", "laboras": "labori",
        # DESTRUCTION
        "detruis": "detrui", "detruas": "detrui",
        "rompis": "rompi", "rompas": "rompi",
        "mortigis": "mortigi", "mortigas": "mortigi",
        "tranĉis": "tranĉi", "tranĉas": "tranĉi",
        "brulis": "bruli", "brulas": "bruli",
        # DOMINATION
        "regis": "regi", "regas": "regi",
        "ordonis": "ordoni", "ordonas": "ordoni",
        "obeis": "obei", "obeas": "obei",
        "juĝis": "juĝi", "juĝas": "juĝi",
        "punis": "puni", "punas": "puni",
        # SEEKING
        "volis": "voli", "volas": "voli",
        "deziris": "deziri", "deziras": "deziri",
        "serĉis": "serĉi", "serĉas": "serĉi",
        "esperis": "esperi", "esperas": "esperi",
        # FEAR
        "timis": "timi", "timas": "timi",
        "timigis": "timigi", "timigas": "timigi",
        "tremis": "tremi", "tremas": "tremi",
        "fuĝis": "fuĝi", "fuĝas": "fuĝi",
        # CARE
        "amis": "ami", "amas": "ami",
        "protektis": "protekti", "protektas": "protekti",
        "konsolis": "konsoli", "konsolas": "konsoli",
        # PLAY
        "ludis": "ludi", "ludas": "ludi",
        "ridis": "ridi", "ridas": "ridi",
        "festis": "festi", "festas": "festi",
    },

    "fi": {
        # Finnish — passé (-i), conditionnel (-isi), participe (-nut/-nyt),
        # formes personnelles courantes dans le corpus Alice/Candide.
        # Le finnois est AGGLUTINANT : la base change peu mais les suffixes
        # s'empilent (cas + personne + nombre).
        # MOUVEMENT
        "meni": "mennä", "menee": "mennä", "mennyt": "mennä",
        "menisi": "mennä", "menivät": "mennä",
        "tuli": "tulla", "tulee": "tulla", "tullut": "tulla",
        "tulisi": "tulla", "tulivat": "tulla",
        "juoksi": "juosta", "juoksee": "juosta", "juossut": "juosta",
        "juoksivat": "juosta",
        "putosi": "pudota", "putoaa": "pudota", "pudonnut": "pudota",
        "putosivat": "pudota",
        "käveli": "kävellä", "kävelee": "kävellä", "kävellyt": "kävellä",
        "hyppäsi": "hypätä", "hyppää": "hypätä", "hypännyt": "hypätä",
        "lensi": "lentää", "lentää_pres": "lentää", "lentänyt": "lentää",
        "seurasi": "seurata", "seuraa": "seurata", "seurannut": "seurata",
        # PERCEPTION
        "näki": "nähdä", "näkee": "nähdä", "nähnyt": "nähdä",
        "näkisi": "nähdä", "näkivät": "nähdä",
        "kuuli": "kuulla", "kuulee": "kuulla", "kuullut": "kuulla",
        "kuulivat": "kuulla",
        "katsoi": "katsoa", "katsoo": "katsoa", "katsonut": "katsoa",
        "tunsi": "tuntea", "tuntee": "tuntea", "tuntenut": "tuntea",
        "huomasi": "huomata", "huomaa": "huomata", "huomannut": "huomata",
        "näytti": "näyttää", "näyttää_pres": "näyttää", "näyttänyt": "näyttää",
        # COGNITION
        "ajatteli": "ajatella", "ajattelee": "ajatella",
        "ajatellut": "ajatella",
        "tiesi": "tietää", "tietää_pres": "tietää", "tiennyt": "tietää",
        "ymmärsi": "ymmärtää", "ymmärtää_pres": "ymmärtää",
        "ymmärtänyt": "ymmärtää",
        "uskoi": "uskoa", "uskoo": "uskoa", "uskonut": "uskoa",
        "muisti": "muistaa", "muistaa_pres": "muistaa", "muistanut": "muistaa",
        "kuvitteli": "kuvitella", "kuvittelee": "kuvitella",
        "oppi": "oppia", "oppii": "oppia", "oppinut": "oppia",
        # COMMUNICATION
        "sanoi": "sanoa", "sanoo": "sanoa", "sanonut": "sanoa",
        "sanoivat": "sanoa",
        "puhui": "puhua", "puhuu": "puhua", "puhunut": "puhua",
        "kysyi": "kysyä", "kysyy": "kysyä", "kysynyt": "kysyä",
        "vastasi": "vastata", "vastaa": "vastata", "vastannut": "vastata",
        "huusi": "huutaa", "huutaa_pres": "huutaa", "huutanut": "huutaa",
        "kuiski": "kuiskaa",
        # EXISTENCE
        "oli": "olla", "on": "olla", "ollut": "olla",
        "olisi": "olla", "olivat": "olla", "ovat": "olla",
        "eli": "elää", "elää_pres": "elää", "elänyt": "elää",
        "kuoli": "kuolla", "kuolee": "kuolla", "kuollut": "kuolla",
        "syntyi": "syntyä", "syntyy": "syntyä", "syntynyt": "syntyä",
        "jäi": "jäädä", "jää": "jäädä", "jäänyt": "jäädä",
        # POSSESSION
        "omisti": "omistaa", "omistaa_pres": "omistaa",
        "antoi": "antaa", "antaa_pres": "antaa", "antanut": "antaa",
        "antoivat": "antaa",
        "otti": "ottaa", "ottaa_pres": "ottaa", "ottanut": "ottaa",
        "piti": "pitää", "pitää_pres": "pitää", "pitänyt": "pitää",
        "menetti": "menettää", "menettää_pres": "menettää",
        "löysi": "löytää", "löytää_pres": "löytää", "löytänyt": "löytää",
        "osti": "ostaa", "ostaa_pres": "ostaa",
        "myi": "myydä", "myy": "myydä",
        # CREATION
        "teki": "tehdä", "tekee": "tehdä", "tehnyt": "tehdä",
        "tekivät": "tehdä",
        "loi": "luoda", "luo": "luoda", "luonut": "luoda",
        "rakensi": "rakentaa", "rakentaa_pres": "rakentaa",
        "kasvoi": "kasvaa", "kasvaa_pres": "kasvaa", "kasvanut": "kasvaa",
        "kirjoitti": "kirjoittaa", "kirjoittaa_pres": "kirjoittaa",
        "työskenteli": "työskennellä",
        # DESTRUCTION
        "tuhosi": "tuhota", "tuhoaa": "tuhota",
        "rikkoi": "rikkoa", "rikkoo": "rikkoa",
        "tappoi": "tappaa", "tappaa_pres": "tappaa",
        "leikkasi": "leikata", "leikkaa": "leikata",
        "poltti": "polttaa", "polttaa_pres": "polttaa",
        "taisteli": "taistella", "taistelee": "taistella",
        # DOMINATION
        "hallitsi": "hallita", "hallitsee": "hallita",
        "käski": "käskeä", "käskee": "käskeä",
        "totteli": "totella", "tottelee": "totella",
        "tuomitsi": "tuomita", "tuomitsee": "tuomita",
        # SEEKING
        "halusi": "haluta", "haluaa": "haluta", "halunnut": "haluta",
        "etsi": "etsiä", "etsii": "etsiä", "etsinyt": "etsiä",
        "toivoi": "toivoa", "toivoo": "toivoa",
        "odotti": "odottaa", "odottaa_pres": "odottaa",
        # FEAR
        "pelkäsi": "pelätä", "pelkää": "pelätä",
        "säikähti": "säikähtää",
        "vapisi": "vapista", "vapisee": "vapista",
        "pakeni": "paeta", "pakenee": "paeta",
        # CARE
        "rakasti": "rakastaa", "rakastaa_pres": "rakastaa",
        "suojeli": "suojella", "suojelee": "suojella",
        "lohdotti": "lohduttaa",
        "halasi": "halata", "halaa": "halata",
        # PLAY
        "leikki": "leikkiä", "leikkii": "leikkiä",
        "nauroi": "nauraa", "nauraa_pres": "nauraa", "nauranut": "nauraa",
        "tanssi": "tanssia", "tanssii": "tanssia",
        # GRIEF
        "itki": "itkeä", "itkee": "itkeä", "itkenyt": "itkeä",
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# 2. LEMMATISATION RULE-BASED PAR SUFFIXES
# ═══════════════════════════════════════════════════════════════════════════════
# Pour les formes régulières non couvertes par les tables d'irréguliers.
# Principe : on dépile les suffixes flexionnels pour retrouver un stem
# qui match un mot-clé de ATOM_KEYWORDS.

# Suffixes verbaux par langue, du plus long au plus court (priorité greedy)
VERB_SUFFIXES = {
    "en": [
        # Participes et gérondifs
        ("ying", 1, "y"),     # dying → die + y = die ✗, mais couvert par irréguliers
        ("ying", 2, ""),      # studying → stud → study (via fallback)
        ("ting", 1, "t"),     # cutting → cut
        ("ning", 1, "n"),     # running → run
        ("ling", 1, "l"),     # falling → fall (MAIS: aussi noms en -ling)
        ("ping", 1, "p"),     # dropping → drop
        ("bing", 1, "b"),     # robbing → rob
        ("ming", 1, "m"),     # swimming → swim
        ("ding", 1, "d"),     # adding → add
        ("ging", 1, "g"),     # digging → dig
        ("ing", 0, "e"),      # coming → come, making → make
        ("ing", 0, ""),       # walk+ing → walk
        ("ied", 0, "y"),      # hurried → hurry
        ("ted", 1, "t"),      # batted → bat
        ("ned", 1, "n"),      # planned → plan
        ("ped", 1, "p"),      # dropped → drop
        ("bed", 1, "b"),      # robbed → rob
        ("med", 1, "m"),      # slammed → slam
        ("ded", 1, "d"),      # added → add
        ("ged", 1, "g"),      # tagged → tag
        ("ed", 0, "e"),       # hoped → hope
        ("ed", 0, ""),        # walked → walk
        ("ies", 0, "y"),      # hurries → hurry
        ("es", 0, ""),        # watches → watch
        ("s", 0, ""),         # walks → walk
    ],
    "fr": [
        # Passé simple
        ("èrent", 0, "er"),   # tombèrent → tomber
        ("âmes", 0, "er"),    # tombâmes → tomber
        ("âtes", 0, "er"),    # tombâtes → tomber
        # Imparfait
        ("aient", 0, "er"),   # marchaient → marcher
        ("ais", 0, "er"),     # marchais → marcher
        ("ait", 0, "er"),     # marchait → marcher
        ("ions", 0, "er"),    # marchions → marcher
        ("iez", 0, "er"),     # marchiez → marcher
        # Participe présent
        ("ant", 0, "er"),     # marchant → marcher
        # Participe passé -er verbs
        ("ée", 0, "er"),      # tombée → tomber
        ("és", 0, "er"),      # tombés → tomber
        ("ées", 0, "er"),     # tombées → tomber
        ("é", 0, "er"),       # tombé → tomber
        # Futur / conditionnel
        ("erai", 0, "er"),    # marcherai → marcher
        ("eras", 0, "er"),    # marcheras → marcher
        ("era", 0, "er"),     # marchera → marcher
        ("erons", 0, "er"),   # marcherons → marcher
        ("eront", 0, "er"),   # marcheront → marcher
        ("erais", 0, "er"),   # marcherais → marcher
        ("erait", 0, "er"),   # marcherait → marcher
        # Présent
        ("ons", 0, "er"),     # marchons → marcher
        ("ez", 0, "er"),      # marchez → marcher
        ("ent", 0, "er"),     # marchent → marcher
        ("e", 0, "er"),       # marche → marcher
        ("es", 0, "er"),      # marches → marcher
    ],
    "de": [
        # Partizip II (ge- prefix + -t/-en suffix)
        # Handled specially in lemmatize() function
        # Präteritum regular
        ("ete", 0, "en"),     # machete → machen (weak verbs)
        ("eten", 0, "en"),    # macheten → machen
        ("test", 0, "en"),    # machtest → machen
        ("tet", 0, "en"),     # machtet → machen
        ("te", 0, "en"),      # machte → machen
        ("ten", 0, "en"),     # machten → machen
        # Präsens
        ("est", 0, "en"),     # machest → machen
        ("et", 0, "en"),      # machet → machen
        ("st", 0, "en"),      # machst → machen
        ("t", 0, "en"),       # macht → machen
        ("e", 0, "en"),       # mache → machen
        ("en", 0, "en"),      # identity: machen → machen
    ],
    "it": [
        # Passato remoto
        ("arono", 0, "are"),  # camminarono → camminare
        ("arono", 0, "ere"),
        ("irono", 0, "ire"),  # seguirono → seguire
        ("ava", 0, "are"),    # camminava → camminare
        ("avo", 0, "are"),
        ("avi", 0, "are"),
        ("ando", 0, "are"),   # camminando → camminare
        ("endo", 0, "ere"),   # scrivendo → scrivere
        ("ato", 0, "are"),    # camminato → camminare
        ("ata", 0, "are"),
        ("ito", 0, "ire"),    # seguito → seguire
        ("ita", 0, "ire"),
        ("uto", 0, "ere"),    # creduto → credere
        ("uta", 0, "ere"),
        ("ava", 0, "are"),
        ("eva", 0, "ere"),    # scriveva → scrivere
        ("iva", 0, "ire"),    # seguiva → seguire
        ("iamo", 0, "are"),
        ("amo", 0, "are"),
        ("ano", 0, "are"),
        ("ono", 0, "ere"),
        ("ono", 0, "ire"),
        ("a", 0, "are"),      # cammin+a → camminare
        ("e", 0, "ere"),
        ("e", 0, "ire"),
    ],
    "es": [
        # Pretérito indefinido
        ("aron", 0, "ar"),    # caminaron → caminar
        ("ieron", 0, "er"),   # corrieron → correr
        ("ieron", 0, "ir"),
        ("aba", 0, "ar"),     # caminaba → caminar
        ("aba", 0, "er"),
        ("ía", 0, "ir"),      # seguía → seguir
        ("ía", 0, "er"),      # corría → correr
        ("ando", 0, "ar"),    # caminando → caminar
        ("iendo", 0, "er"),   # corriendo → correr
        ("iendo", 0, "ir"),   # siguiendo → seguir
        ("ado", 0, "ar"),     # caminado → caminar
        ("ido", 0, "er"),     # corrido → correr
        ("ido", 0, "ir"),
        ("amos", 0, "ar"),
        ("an", 0, "ar"),
        ("en", 0, "er"),
        ("ó", 0, "ar"),       # caminó → caminar
        ("ió", 0, "er"),      # corrió → correr
        ("ió", 0, "ir"),
    ],
    "eo": [
        # Esperanto is FULLY REGULAR: stem + suffix
        ("is", 0, "i"),       # iris → iri (passé)
        ("as", 0, "i"),       # iras → iri (présent)
        ("os", 0, "i"),       # iros → iri (futur)
        ("us", 0, "i"),       # irus → iri (conditionnel)
        ("u", 0, "i"),        # iru → iri (impératif)
        ("anta", 0, "i"),     # iranta → iri (participe actif présent)
        ("inta", 0, "i"),     # irinta → iri (participe actif passé)
        ("onta", 0, "i"),     # ironta → iri (participe actif futur)
        ("ata", 0, "i"),      # irata → iri (participe passif présent)
        ("ita", 0, "i"),      # irita → iri (participe passif passé)
        ("ota", 0, "i"),      # irota → iri (participe passif futur)
        ("ante", 0, "i"),     # accusative participles
        ("inte", 0, "i"),
        ("onte", 0, "i"),
        # Substantifs/Adjectifs
        ("oj", 0, "o"),       # hundoj → hundo (pluriel)
        ("ojn", 0, "o"),      # hundojn → hundo (acc pluriel)
        ("on", 0, "o"),       # hundon → hundo (accusatif)
        ("aj", 0, "a"),       # grandaj → granda (adj pluriel)
        ("ajn", 0, "a"),      # grandajn → granda (adj acc pluriel)
        ("an", 0, "a"),       # grandan → granda (adj accusatif)
        ("en", 0, "e"),       # rapiden → rapide (adv accusatif, rare)
    ],
    "fi": [
        # Finnish case suffixes (most common — 15 cases total)
        # Partitive
        ("tta", 0, ""),       # kissaa → kissa (partitive)
        ("ttä", 0, ""),
        ("ta", 0, ""),
        ("tä", 0, ""),
        ("a", 0, ""),         # kissaa → kissa
        ("ä", 0, ""),
        # Inessive
        ("ssa", 0, ""),       # talossa → talo
        ("ssä", 0, ""),
        # Elative
        ("sta", 0, ""),       # talosta → talo
        ("stä", 0, ""),
        # Illative
        ("seen", 0, ""),      # taloon → talo (more complex, simplified)
        # Adessive
        ("lla", 0, ""),       # pöydällä → pöytä (consonant gradation not handled)
        ("llä", 0, ""),
        # Ablative
        ("lta", 0, ""),       # pöydältä → pöytä
        ("ltä", 0, ""),
        # Allative
        ("lle", 0, ""),       # pöydälle → pöytä
        # Essive
        ("na", 0, ""),        # kissana → kissa
        ("nä", 0, ""),
        # Genitive
        ("n", 0, ""),         # kissan → kissa
        # Verb past tense
        ("si", 0, ""),        # juoksi → juok... (not useful without consonant gradation)
        ("vat", 0, ""),       # juoksivat → juoksi... (3pl)
        ("vät", 0, ""),
        # Past participle
        ("nut", 0, ""),       # juossut → (stem, complex)
        ("nyt", 0, ""),
        ("neet", 0, ""),      # juosseet → (stem, complex)
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# 3. INFÉRENCE PAR FAMILLES DE LANGUES — COGNATS
# ═══════════════════════════════════════════════════════════════════════════════
# Racines partagées entre langues parentes.
# Format : {racine_commune: {atome: [(lang, keywords)...]}}
# L'idée : si on trouve une racine latine dans un mot IT/ES/FR inconnu,
# on peut inférer l'atome.

# Familles de langues
LANGUAGE_FAMILIES = {
    "romance": ["fr", "it", "es", "eo"],   # Latin → FR/IT/ES/EO
    "germanic": ["en", "de"],               # Proto-germanique → EN/DE
    "finno_ugric": ["fi"],                  # Isolé dans notre corpus
}

# Racines latines partagées (Romance) : racine → atome
# Le moteur cherche si le mot contient la racine.
LATIN_ROOTS = {
    # MOUVEMENT ← movēre, cadere, currere, venīre, ambulāre, saltāre, volāre
    "mov": "MOUVEMENT",   "muov": "MOUVEMENT",   # mouvoir/muovere/mover
    "cad": "MOUVEMENT",   "ca": "MOUVEMENT",      # cadere/caer (ambigu, gardé court)
    "curr": "MOUVEMENT",  "corr": "MOUVEMENT",    # currere/correre/correr
    "cours": "MOUVEMENT", "cour": "MOUVEMENT",    # courir/cours/course
    "ven": "MOUVEMENT",   "vien": "MOUVEMENT",    # venire/venir
    "march": "MOUVEMENT", "cammin": "MOUVEMENT",  # marcher/camminare
    "salt": "MOUVEMENT",  "saut": "MOUVEMENT",    # saltare/sauter/saltar
    "vol": "MOUVEMENT",                           # volare/voler/volar (ambigu avec voler=steal)
    "descend": "MOUVEMENT", "scend": "MOUVEMENT",
    "mont": "MOUVEMENT",  "subi": "MOUVEMENT",    # monter/subir
    "gliss": "MOUVEMENT", "scivol": "MOUVEMENT",  # glisser/scivolare

    # PERCEPTION ← vidēre, audīre, sentīre, spectāre
    "vid": "PERCEPTION",  "ved": "PERCEPTION",    # videre/vedere/ver
    "voi": "PERCEPTION",  "vu": "PERCEPTION",     # voir/vu
    "audit": "PERCEPTION", "aud": "PERCEPTION",   # audire/aŭdi
    "entend": "PERCEPTION",                        # entendre (FR)
    "sent": "PERCEPTION",                          # sentire/sentir
    "guard": "PERCEPTION", "regard": "PERCEPTION", # guardare/regarder
    "observ": "PERCEPTION",                        # observer/osservare/observar
    "remarqu": "PERCEPTION",                       # remarquer
    "sembl": "PERCEPTION", "sembr": "PERCEPTION",  # sembler/sembrare
    "paraitr": "PERCEPTION", "appar": "PERCEPTION", # paraître/apparire

    # COGNITION ← pensāre, cognōscere, crēdere, intellegere
    "pens": "COGNITION",                           # pensare/penser/pensar
    "cogn": "COGNITION",  "conn": "COGNITION",    # cognoscere/connaître/conocer
    "cred": "COGNITION",  "croi": "COGNITION",    # credere/croire/creer
    "comprend": "COGNITION", "compren": "COGNITION", # comprendre/comprendere/comprender
    "capir": "COGNITION", "capi": "COGNITION",    # capire (IT)
    "sav": "COGNITION",   "sap": "COGNITION",     # savoir/sapere/saber
    "imagin": "COGNITION",                         # imaginer/immaginare/imaginar
    "ricord": "COGNITION", "record": "COGNITION",  # ricordare/recordar
    "réfléch": "COGNITION",                        # réfléchir
    "apprendr": "COGNITION", "apprend": "COGNITION", # apprendre
    "impar": "COGNITION",                          # imparare (IT)
    "lern": "COGNITION",                           # lerni (EO)

    # COMMUNICATION ← dīcere, loquī, parlāre, respondēre
    "dic": "COMMUNICATION", "dir": "COMMUNICATION", # dicere/dire/decir
    "parl": "COMMUNICATION", "habl": "COMMUNICATION", # parlare/parler/hablar
    "demand": "COMMUNICATION",                      # demander/demandare
    "pregunt": "COMMUNICATION", "chied": "COMMUNICATION", # preguntar/chiedere
    "respond": "COMMUNICATION", "rispond": "COMMUNICATION", # responder/rispondere/répondre
    "appel": "COMMUNICATION", "chiam": "COMMUNICATION", # appeler/chiamare/llamar
    "llam": "COMMUNICATION",
    "cri": "COMMUNICATION", "grid": "COMMUNICATION", # crier/gridare/gritar
    "grit": "COMMUNICATION",
    "murmur": "COMMUNICATION", "sussurr": "COMMUNICATION", # murmurer/sussurrare
    "racont": "COMMUNICATION", "raccont": "COMMUNICATION", # raconter/raccontare
    "cont": "COMMUNICATION",                        # contar (ES)
    "déclar": "COMMUNICATION",                       # déclarer

    # EXISTENCE ← esse, existere, vīvere, morī, nascī
    "exist": "EXISTENCE",                            # exister/esistere/existir
    "viv": "EXISTENCE",  "vécu": "EXISTENCE",       # vivre/vivere/vivir
    "mour": "EXISTENCE", "mor": "EXISTENCE",        # mourir/morire/morir
    "naitr": "EXISTENCE", "nasc": "EXISTENCE",      # naître/nascere/nacer
    "rest": "EXISTENCE",                             # rester/restare (ambigu)
    "deven": "EXISTENCE", "divent": "EXISTENCE",    # devenir/diventare

    # POSSESSION ← habēre, dare, prehendere, perdere, invēnīre
    "poss": "POSSESSION", "posed": "POSSESSION",    # posséder/possedere/poseer
    "donn": "POSSESSION", "don": "POSSESSION",      # donner/doni/dar
    "prend": "POSSESSION", "prend": "POSSESSION",   # prendre/prendere
    "tom": "POSSESSION",                             # tomar (ES)
    "gard": "POSSESSION",                            # garder/gardi
    "perd": "POSSESSION",                            # perdre/perdere/perder
    "trouv": "POSSESSION", "trov": "POSSESSION",    # trouver/trovare
    "encontr": "POSSESSION",                         # encontrar (ES)
    "vol_steal": "POSSESSION",                       # voler/rubare (ambigu!)
    "achet": "POSSESSION", "compr": "POSSESSION",    # acheter/comprare/comprar
    "vend": "POSSESSION",                            # vendre/vendere/vender

    # CREATION ← facere, creāre, construere, scrībere
    "cré": "CREATION",  "crea": "CREATION",        # créer/creare/crear
    "constru": "CREATION", "costru": "CREATION",   # construire/costruire/construir
    "produc": "CREATION", "produkt": "CREATION",   # produire/produrre/producir
    "invent": "CREATION",                           # inventer/inventare/inventar
    "écriv": "CREATION", "scriv": "CREATION",      # écrire/scrivere/escribir
    "escrib": "CREATION",
    "dessin": "CREATION", "disegn": "CREATION",    # dessiner/disegnare/dibujar
    "peind": "CREATION", "pint": "CREATION",       # peindre/dipingere/pintar
    "travail": "CREATION", "lavor": "CREATION",    # travailler/lavorare/trabajar
    "trabaj": "CREATION",

    # DESTRUCTION ← destruere, frangere, occīdere, ūrere
    "détru": "DESTRUCTION", "distru": "DESTRUCTION", # détruire/distruggere/destruir
    "destru": "DESTRUCTION",
    "cass": "DESTRUCTION", "romp": "DESTRUCTION",    # casser/rompere/romper
    "tu": "DESTRUCTION",                              # tuer (FR, trop court et ambigu — gardé mais prudent)
    "uccid": "DESTRUCTION", "mat": "DESTRUCTION",    # uccidere/matar
    "coup": "DESTRUCTION", "tagli": "DESTRUCTION",   # couper/tagliare/cortar
    "cort": "DESTRUCTION",
    "brûl": "DESTRUCTION", "bruci": "DESTRUCTION",   # brûler/bruciare/quemar
    "quem": "DESTRUCTION",
    "écras": "DESTRUCTION", "schiacc": "DESTRUCTION", # écraser/schiacciare
    "combatt": "DESTRUCTION", "combat": "DESTRUCTION", # combattre/combattere/combatir

    # DOMINATION ← rēx, rēgīna, iūdicāre, pūnīre, lēx
    "règn": "DOMINATION", "regn": "DOMINATION",     # régner/regnare/reinar
    "command": "DOMINATION", "comand": "DOMINATION", # commander/comandare
    "ordonn": "DOMINATION", "ordon": "DOMINATION",   # ordonner/ordoni
    "obé": "DOMINATION", "obbed": "DOMINATION",     # obéir/obbedire/obedecer
    "obed": "DOMINATION",
    "jug": "DOMINATION", "giudic": "DOMINATION",    # juger/giudicare/juzgar
    "juzg": "DOMINATION",
    "pun": "DOMINATION",                             # punir/punire/castigar

    # SEEKING ← volēre, dēsīderāre, quaerere, spērāre
    "voul": "SEEKING",   "vol_want": "SEEKING",     # vouloir/volere
    "désir": "SEEKING",  "desider": "SEEKING",      # désirer/desiderare/desear
    "dese": "SEEKING",
    "cherch": "SEEKING", "cerc": "SEEKING",          # chercher/cercare/buscar
    "busc": "SEEKING",
    "espér": "SEEKING",  "sper": "SEEKING",          # espérer/sperare/esperar
    "attend": "SEEKING", "aspett": "SEEKING",        # attendre/aspettare
    "souhait": "SEEKING",                             # souhaiter

    # FEAR ← timēre, fugere, tremere
    "craind": "FEAR",   "craint": "FEAR",            # craindre
    "tem": "FEAR",                                    # temere/temer (ambigu: temps)
    "effray": "FEAR",   "spavent": "FEAR",           # effrayer/spaventare
    "asust": "FEAR",
    "trembl": "FEAR",   "trem": "FEAR",              # trembler/tremare/temblar
    "tembl": "FEAR",
    "fu": "FEAR",        "fugg": "FEAR",             # fuir/fuggire (trop court, ambigu)
    "hu": "FEAR",                                    # huir (ES, court)

    # CARE ← amāre, prōtegere, cōnsōlārī
    "aim": "CARE",      "am_love": "CARE",           # aimer/amare/amar
    "protég": "CARE",   "protegg": "CARE",           # protéger/proteggere/proteger
    "proteg": "CARE",
    "consol": "CARE",                                 # consoler/consolare/consolar
    "embrass": "CARE",  "abbracc": "CARE",           # embrasser/abbracciare/abrazar
    "abraz": "CARE",

    # PLAY ← iocāre, rīdēre, gaudēre
    "jou": "PLAY",     "gioc": "PLAY",              # jouer/giocare/jugar
    "jug": "PLAY",                                   # jugar (ES, collision avec juger — context required)
    "ri_laugh": "PLAY", "rid": "PLAY",              # rire/ridere/reír
    "danse": "PLAY",    "danz": "PLAY",             # danser/danzare/bailar
    "fest": "PLAY",                                  # fête/festa/fiesta

    # GRIEF ← plōrāre, lacrimāre
    "pleur": "GRIEF",   "piang": "GRIEF",           # pleurer/piangere
    "llor": "GRIEF",                                 # llorar (ES)
    "larm": "GRIEF",    "lacrim": "GRIEF",          # larmes/lacrime/lágrimas
    "lágrima": "GRIEF",
    "deuil": "GRIEF",   "lutt": "GRIEF",            # deuil/lutto/duelo
    "duel": "GRIEF",
    "désespoir": "GRIEF", "disperaz": "GRIEF",      # désespoir/disperazione
    "desesper": "GRIEF",
}

# Racines germaniques partagées (EN ↔ DE)
GERMANIC_ROOTS = {
    # Proto-germanique → English/German cognats
    # MOUVEMENT
    "fall": "MOUVEMENT",  "geh": "MOUVEMENT",
    "komm": "MOUVEMENT",  "com": "MOUVEMENT",
    "lauf": "MOUVEMENT",  "run": "MOUVEMENT",
    "spring": "MOUVEMENT", "jump": "MOUVEMENT",
    "flieg": "MOUVEMENT", "fly": "MOUVEMENT",
    "folg": "MOUVEMENT",  "follow": "MOUVEMENT",
    "eil": "MOUVEMENT",   "rush": "MOUVEMENT",
    "wander": "MOUVEMENT",
    "stürz": "MOUVEMENT", "tumbl": "MOUVEMENT",
    "gleit": "MOUVEMENT", "slid": "MOUVEMENT",

    # PERCEPTION
    "seh": "PERCEPTION",  "see": "PERCEPTION",
    "hör": "PERCEPTION",  "hear": "PERCEPTION",
    "schau": "PERCEPTION", "look": "PERCEPTION",
    "fühl": "PERCEPTION",  "feel": "PERCEPTION",
    "riech": "PERCEPTION", "smell": "PERCEPTION",
    "schmeck": "PERCEPTION", "tast": "PERCEPTION",
    "bemerk": "PERCEPTION", "notic": "PERCEPTION",
    "beobacht": "PERCEPTION",

    # COGNITION
    "denk": "COGNITION",  "think": "COGNITION",
    "wiss": "COGNITION",  "know": "COGNITION",
    "versteh": "COGNITION", "understand": "COGNITION",
    "glaub": "COGNITION",  "believ": "COGNITION",
    "erinner": "COGNITION", "remember": "COGNITION",
    "überleg": "COGNITION", "consider": "COGNITION",
    "vorstell": "COGNITION", "imagin": "COGNITION",

    # COMMUNICATION
    "sag": "COMMUNICATION", "say": "COMMUNICATION",
    "sprech": "COMMUNICATION", "speak": "COMMUNICATION",
    "frag": "COMMUNICATION",  "ask": "COMMUNICATION",
    "antwort": "COMMUNICATION", "answer": "COMMUNICATION",
    "ruf": "COMMUNICATION",   "call": "COMMUNICATION",
    "schrei": "COMMUNICATION", "shout": "COMMUNICATION",
    "flüster": "COMMUNICATION", "whisper": "COMMUNICATION",
    "erzähl": "COMMUNICATION", "tell": "COMMUNICATION",

    # EXISTENCE
    "leb": "EXISTENCE",  "liv": "EXISTENCE",
    "sterb": "EXISTENCE", "die": "EXISTENCE",
    "werd": "EXISTENCE", "becom": "EXISTENCE",
    "bleib": "EXISTENCE", "remain": "EXISTENCE",
    "gebor": "EXISTENCE", "born": "EXISTENCE",

    # POSSESSION
    "hab": "EXISTENCE",  "hav": "POSSESSION",
    "geb": "POSSESSION", "giv": "POSSESSION",
    "nehm": "POSSESSION", "tak": "POSSESSION",
    "behalt": "POSSESSION", "keep": "POSSESSION",
    "verlier": "POSSESSION", "los": "POSSESSION",
    "find": "POSSESSION",
    "stehl": "POSSESSION", "steal": "POSSESSION",
    "kauf": "POSSESSION", "buy": "POSSESSION",
    "verkauf": "POSSESSION", "sell": "POSSESSION",

    # CREATION
    "mach": "CREATION",  "mak": "CREATION",
    "schaff": "CREATION", "creat": "CREATION",
    "bau": "CREATION",   "build": "CREATION",
    "wachs": "CREATION", "grow": "CREATION",
    "erzeug": "CREATION", "produc": "CREATION",
    "erfind": "CREATION", "invent": "CREATION",
    "schreib": "CREATION", "writ": "CREATION",
    "zeichn": "CREATION", "draw": "CREATION",
    "mal": "CREATION",   "paint": "CREATION",
    "arbeit": "CREATION", "work": "CREATION",

    # DESTRUCTION
    "zerstör": "DESTRUCTION", "destroy": "DESTRUCTION",
    "brech": "DESTRUCTION",  "break": "DESTRUCTION",
    "tö": "DESTRUCTION",     "kill": "DESTRUCTION",
    "schneid": "DESTRUCTION", "cut": "DESTRUCTION",
    "brenn": "DESTRUCTION",   "burn": "DESTRUCTION",
    "zerreiß": "DESTRUCTION", "tear": "DESTRUCTION",
    "zermalm": "DESTRUCTION", "crush": "DESTRUCTION",
    "kämpf": "DESTRUCTION",   "fight": "DESTRUCTION",

    # DOMINATION
    "herrsch": "DOMINATION", "rul": "DOMINATION",
    "befehl": "DOMINATION",  "command": "DOMINATION",
    "gehorch": "DOMINATION", "obey": "DOMINATION",
    "richt": "DOMINATION",   "judg": "DOMINATION",
    "straf": "DOMINATION",   "punish": "DOMINATION",

    # SEEKING
    "woll": "SEEKING",  "want": "SEEKING",
    "such": "SEEKING",  "search": "SEEKING",
    "neugier": "SEEKING", "curious": "SEEKING",
    "hoff": "SEEKING",   "hop": "SEEKING",
    "erwart": "SEEKING",  "expect": "SEEKING",
    "wünsch": "SEEKING",  "wish": "SEEKING",
    "erforsch": "SEEKING", "explor": "SEEKING",

    # FEAR
    "fürcht": "FEAR",  "fear": "FEAR",
    "schreck": "FEAR", "fright": "FEAR",
    "zitter": "FEAR",  "trembl": "FEAR",
    "flieh": "FEAR",   "flee": "FEAR",

    # CARE
    "lieb": "CARE",  "lov": "CARE",
    "schütz": "CARE", "protect": "CARE",
    "tröst": "CARE",  "comfort": "CARE",
    "umarm": "CARE",  "embrac": "CARE",

    # PLAY
    "spiel": "PLAY",  "play": "PLAY",
    "lach": "PLAY",   "laugh": "PLAY",
    "tanz": "PLAY",   "danc": "PLAY",

    # GRIEF
    "traurig": "GRIEF", "sad": "GRIEF",
    "wein": "GRIEF",    "weep": "GRIEF",
    "Trän": "GRIEF",    "tear_cry": "GRIEF",
}

# Minimum root length to avoid false positives
MIN_ROOT_LENGTH = 3


# ═══════════════════════════════════════════════════════════════════════════════
# 4. FONCTIONS PUBLIQUES
# ═══════════════════════════════════════════════════════════════════════════════

def lemmatize(word, lang):
    """Résout une forme fléchie vers son lemme candidat.
    
    Stratégie :
      1. Lookup dans les tables d'irréguliers (exact match)
      2. German ge- prefix stripping (Partizip II)
      3. Suffix stripping rule-based
      4. Fallback : le mot lui-même
    
    Retourne : liste de (lemme_candidat, method, confidence) triée par confiance.
    """
    word_clean = word.lower().strip('.,;:!?"\'"()[]{}—–-…""''«»')
    if len(word_clean) < 2:
        return [(word_clean, "identity", 0.1)]
    
    candidates = []
    
    # 1. Lookup irréguliers (confiance maximale)
    irr = IRREGULAR_VERBS.get(lang, {})
    if word_clean in irr:
        candidates.append((irr[word_clean], "irregular_table", 0.98))
    
    # 2. German: ge- prefix (Partizip II: ge+stem+t/en)
    if lang == "de" and word_clean.startswith("ge") and len(word_clean) > 4:
        stem = word_clean[2:]  # strip ge-
        if stem.endswith("t"):
            candidates.append((stem[:-1] + "en", "ge_prefix_weak", 0.75))
        elif stem.endswith("en"):
            candidates.append((stem, "ge_prefix_strong", 0.75))
    
    # 3. Suffix stripping
    suffixes = VERB_SUFFIXES.get(lang, [])
    for suffix, trim_extra, replacement in suffixes:
        if word_clean.endswith(suffix) and len(word_clean) > len(suffix) + 1:
            stem = word_clean[:len(word_clean) - len(suffix) - trim_extra]
            lemma_candidate = stem + replacement
            if lemma_candidate != word_clean and len(lemma_candidate) >= 2:
                # Higher confidence for longer suffix matches
                conf = 0.55 + min(0.20, len(suffix) * 0.04)
                candidates.append((lemma_candidate, f"suffix_{suffix}", conf))
    
    # 4. Identity (always present as fallback)
    candidates.append((word_clean, "identity", 0.50))
    
    # Deduplicate by lemma, keeping highest confidence
    seen = {}
    for lemma, method, conf in candidates:
        if lemma not in seen or conf > seen[lemma][1]:
            seen[lemma] = (method, conf)
    
    result = [(lemma, method, conf) for lemma, (method, conf) in seen.items()]
    result.sort(key=lambda x: -x[2])
    return result


def infer_atom_from_roots(word, lang):
    """Cherche si le mot contient une racine connue (latine ou germanique).
    
    Retourne : liste de (atom_id, root_matched, confidence, method) ou [].
    """
    word_lower = word.lower().strip('.,;:!?"\'"()[]{}—–-…""''«»')
    if len(word_lower) < MIN_ROOT_LENGTH:
        return []
    
    results = []
    
    # Choisir les tables de racines selon la famille
    root_tables = []
    if lang in ("fr", "it", "es", "eo"):
        root_tables.append(("latin_root", LATIN_ROOTS))
    if lang in ("en", "de"):
        root_tables.append(("germanic_root", GERMANIC_ROOTS))
    if lang == "en":
        # English also has heavy Latin/French influence
        root_tables.append(("latin_loan", LATIN_ROOTS))
    if lang == "eo":
        # Esperanto also has Germanic elements
        root_tables.append(("germanic_loan", GERMANIC_ROOTS))
    
    for method, root_table in root_tables:
        for root, atom in root_table.items():
            if len(root) < MIN_ROOT_LENGTH:
                continue
            # Must contain the root, not just start with a single char
            if root in word_lower:
                # Confidence based on root length vs word length
                ratio = len(root) / len(word_lower)
                conf = 0.40 + min(0.35, ratio * 0.50)
                # Boost if root is at beginning of word
                if word_lower.startswith(root):
                    conf += 0.10
                results.append((atom, root, min(conf, 0.85), method))
    
    # Deduplicate by atom, keeping highest confidence
    seen = {}
    for atom, root, conf, method in results:
        if atom not in seen or conf > seen[atom][1]:
            seen[atom] = (root, conf, method)
    
    final = [(atom, root, conf, method) for atom, (root, conf, method) in seen.items()]
    final.sort(key=lambda x: -x[2])
    return final


def resolve_word(word, lang, atom_keywords):
    """Point d'entrée principal : résout un mot vers ses atomes possibles.
    
    Stratégie en cascade :
      1. Match direct dans ATOM_KEYWORDS (confiance 0.95)
      2. Lemmatisation → match dans ATOM_KEYWORDS (confiance 0.85-0.98)
      3. Inférence par racines étymologiques (confiance 0.40-0.85)
    
    Args:
        word: forme de surface (ex: "fell", "tomba", "fiel")
        lang: code langue (ex: "en", "fr", "de")
        atom_keywords: dict ATOM_KEYWORDS
    
    Returns:
        list of dict: [{atom_id, lemma, confidence, method, disambiguation}, ...]
    """
    word_clean = word.lower().strip('.,;:!?"\'"()[]{}—–-…""''«»')
    if len(word_clean) < 2:
        return []
    
    results = []
    
    # --- ÉTAPE 1 : Match direct dans ATOM_KEYWORDS ---
    for atom, kw_by_lang in atom_keywords.items():
        if lang not in kw_by_lang:
            continue
        for kw in kw_by_lang[lang]:
            kw_lower = kw.lower()
            if word_clean == kw_lower:
                results.append({
                    "atom_id": atom,
                    "lemma": kw,
                    "confidence": 0.95,
                    "method": "direct_match",
                    "disambiguation": None,
                })
                break
            elif len(kw_lower) >= 4 and word_clean.startswith(
                    kw_lower[:max(4, len(kw_lower) - 2)]):
                results.append({
                    "atom_id": atom,
                    "lemma": kw,
                    "confidence": 0.80,
                    "method": "prefix_match",
                    "disambiguation": None,
                })
                break
    
    if results:
        return results
    
    # --- ÉTAPE 2 : Lemmatisation → match dans ATOM_KEYWORDS ---
    lemma_candidates = lemmatize(word_clean, lang)
    
    for lemma, lem_method, lem_conf in lemma_candidates:
        if lem_method == "identity":
            continue  # Skip identity, already tried in step 1
        
        for atom, kw_by_lang in atom_keywords.items():
            if lang not in kw_by_lang:
                continue
            for kw in kw_by_lang[lang]:
                kw_lower = kw.lower()
                if lemma == kw_lower:
                    # Combine lemmatizer confidence with match confidence
                    combined = min(lem_conf * 0.95, 0.95)
                    results.append({
                        "atom_id": atom,
                        "lemma": kw,
                        "confidence": round(combined, 3),
                        "method": f"lemma:{lem_method}",
                        "disambiguation": f"{word_clean} → {lemma} ({lem_method})",
                    })
                    break
                elif len(kw_lower) >= 4 and lemma.startswith(
                        kw_lower[:max(4, len(kw_lower) - 2)]):
                    combined = min(lem_conf * 0.80, 0.90)
                    results.append({
                        "atom_id": atom,
                        "lemma": kw,
                        "confidence": round(combined, 3),
                        "method": f"lemma_prefix:{lem_method}",
                        "disambiguation": f"{word_clean} → {lemma} ≈ {kw} ({lem_method})",
                    })
                    break
    
    if results:
        return results
    
    # --- ÉTAPE 3 : Inférence par racines étymologiques ---
    root_matches = infer_atom_from_roots(word_clean, lang)
    
    for atom, root, conf, root_method in root_matches:
        results.append({
            "atom_id": atom,
            "lemma": f"*{root}",  # Asterisk = racine reconstruite
            "confidence": round(conf, 3),
            "method": f"root:{root_method}",
            "disambiguation": f"{word_clean} ← racine '{root}' ({root_method})",
        })
    
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# 5. FONCTIONS D'INFÉRENCE INTER-LANGUES
# ═══════════════════════════════════════════════════════════════════════════════

def get_language_family(lang):
    """Retourne la famille de langues."""
    for family, members in LANGUAGE_FAMILIES.items():
        if lang in members:
            return family
    return "isolate"


def get_sibling_languages(lang):
    """Retourne les langues parentes (même famille)."""
    family = get_language_family(lang)
    if family == "isolate":
        return []
    return [l for l in LANGUAGE_FAMILIES[family] if l != lang]


def cross_language_inference(word, source_lang, atom_keywords):
    """Si un mot n'est résolu dans aucun atome pour sa langue,
    cherche dans les langues parentes.
    
    Ex: mot IT inconnu, on cherche dans FR/ES si un cognat existe.
    
    Retourne : list of dict avec confiance réduite (× 0.7)
    """
    siblings = get_sibling_languages(source_lang)
    if not siblings:
        return []
    
    results = []
    word_clean = word.lower().strip('.,;:!?"\'"()[]{}—–-…""''«»')
    
    for sib_lang in siblings:
        sib_results = resolve_word(word_clean, sib_lang, atom_keywords)
        for r in sib_results:
            # Reduce confidence — cross-language inference is less sure
            results.append({
                "atom_id": r["atom_id"],
                "lemma": r["lemma"],
                "confidence": round(r["confidence"] * 0.70, 3),
                "method": f"cross_lang:{source_lang}→{sib_lang}:{r['method']}",
                "disambiguation": (f"{word_clean}({source_lang}) ≈ "
                                   f"{r['lemma']}({sib_lang}) — inférence inter-langues"),
            })
    
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# 6. RÉSOLUTION COMPLÈTE (cascade 4 étapes)
# ═══════════════════════════════════════════════════════════════════════════════

def resolve_word_full(word, lang, atom_keywords):
    """Résolution complète avec fallback inter-langues.
    
    Cascade :
      1. Match direct ATOM_KEYWORDS
      2. Lemmatisation → ATOM_KEYWORDS  
      3. Racines étymologiques
      4. Inférence inter-langues (langues parentes)
    
    Returns:
        list of dict, best match first
    """
    # Steps 1-3
    results = resolve_word(word, lang, atom_keywords)
    
    if not results:
        # Step 4: cross-language inference
        results = cross_language_inference(word, lang, atom_keywords)
    
    # Deduplicate by atom_id, keep best confidence
    seen = {}
    for r in results:
        aid = r["atom_id"]
        if aid not in seen or r["confidence"] > seen[aid]["confidence"]:
            seen[aid] = r
    
    final = list(seen.values())
    final.sort(key=lambda x: -x["confidence"])
    return final
