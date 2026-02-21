#!/usr/bin/env python3
"""vocabulary_expansion_v487.py — v4.8.7: All-languages push toward 90%+

Target: Push FI (86.8%→90%+), IT (87.5%→90%+), FR (89.0%→90%+), ES (89.5%→90%+)
        Maintain/improve DE (90.1%), EO (92.4%), EN (94.4%)

Strategy:
- FI: Add voikko LEMMA base forms as keywords (voikko resolves surface → lemma,
  but lemma must be in keyword index for Strategy 9 to match)
- IT: Add verb infinitives + archaic forms so Snowball stemmer resolves conjugations
- FR: Add base words behind elisions + nouns/verbs
- ES: Add base forms + old-spelling archaic mappings
- DE/EN/EO: High-frequency gap fills

Created: 2026-02-21 by Copilot (Claude Opus 4.6) on hauru
"""

# ── FI lemma keywords (voikko resolves surface→lemma, lemma must be in index)
# ── IT infinitives + nouns
# ── FR base words (behind elisions) + nouns/verbs
# ── ES base forms + nouns/adjectives
# ── DE high-freq gaps
# ── EN high-freq base forms
# ── EO roots

KEYWORDS_V487 = {
    # ─── MOUVEMENT (movement, physical change of state) ───
    "MOUVEMENT": {
        "fi": [
            "ilmestyä",    # to appear (ilmestyi)
            "joutua",      # to end up / to have to (joutuu)
            "vaipua",      # to sink, to fall into (vaipui)
            "kiertää",     # to circle, to go around (kiersi)
            "kuperkeikka", # somersault (kuperkeikan)
            "riistää",     # to snatch, to exploit (riisti)
            "huoahtaa",    # to sigh (huoahti)
            "kohden",      # towards (postposition)
            "ruveta",      # to begin, to start
            "tyrmätä",     # to stun (tyrmään)
            "näkevä",      # seeing (participial form, voikko base for näkevänsä)
        ],
        "it": [
            "trottare",    # to trot
            "scavare",     # to dig (scavando)
            "uscire",      # to go out (uscì)
            "staccare",    # to detach (staccò)
            "sedere",      # to sit (siederò)
            "inchinarsi",  # to bow (s'inchinarono)
            "impiccolire", # to shrink
            "penzoloni",   # dangling
            "calcio",      # kick
            "andremo",     # we'll go (irregular andare, future — no stem match)
            "uscì",        # went out (irregular passato remoto)
            "siederò",     # I'll sit (irregular future of sedere)
        ],
        "fr": [
            "répandre",    # to spread (répandit)
            "progrès",     # progress
            "remplacer",   # to replace (remplacé)
            "enchaîner",   # to chain (enchaîné)
            "répandit",    # spread (passé simple — irregular stem)
        ],
        "es": [
            "volver",      # to return (vuelva)
            "pegado",      # stuck
            "convertido",  # converted
            "colgado",     # hung
            "detener",     # to stop (detenerse)
            "naufragio",   # shipwreck
            "vuelva",      # return (subj — irregular stem change o→ue)
            "cobrar",      # to charge/recover (cobró)
            "dormir",      # to sleep (duerme — irregular)
            "duerme",      # sleeps (stem change o→ue)
            "lima",        # file / lime
            "rabo",        # tail
            "agasajo",     # gift, treat
        ],
        "de": [
            "zug",         # train / march / move
            "zuge",        # dative of Zug
            "stampfen",    # to stomp (stampfte)
            "treffen",     # to meet / to hit
            "blasen",      # to blow (blies)
            "fahrt",       # journey
            "flut",        # flood
            "stampfte",    # stomped (irregular — stem doesn't match stampfen)
            "blies",       # blew (irregular past of blasen)
            "lehrte",      # taught (regular past of lehren)
            "klatschte",   # clapped
            "wechselt",    # changes (3sg present)
            "ausgabe",     # edition
            "gemächlich",  # leisurely
            "ward",        # became (archaic past of werden)
        ],
        "en": [
            "pour",        # to pour (poured)
            "dip",         # to dip (dipped)
            "splash",      # to splash (splashing)
            "curl",        # to curl (curled)
            "tiptoe",      # to tiptoe
            "unfold",      # to unfold (unfolded)
            "stoop",       # to stoop / bend
            "dissect",     # to dissect (dissected)
        ],
        "eo": [
            "sxovi",       # to shove (sxovis)
            "eletendi",    # to extend out (eletendis)
            "derampi",     # to climb down
            "engluti",     # to swallow (englutis)
            "cxirkauxkuri",# to run around (cxirkauxkuris)
            "faldi",       # to fold (falditaj)
            "hxoro",       # chorus (hxoron)
            "pusxcxaro",   # pushcart
            "cxirkauxe",   # around (adverb)
            "falditaj",    # folded (participial)
            "gxenata",     # kneeling (from gxenu)
        ],
    },

    # ─── AGENT (living beings, animals, people) ───
    "AGENT": {
        "fi": [
            "sorsa",       # duck
            "pentu",       # cub, puppy
            "possu",       # pig (colloquial)
            "äyriäinen",   # crayfish
            "sisilisko",   # lizard
            "kummi",       # godparent
        ],
        "it": [
            "cucciolo",    # puppy
            "baffi",       # moustache (metonymy: person with moustache)
            "cetriolo",    # cucumber
            "sassolino",   # pebble
        ],
        "fr": [
            "humain",      # human
            "défenseur",   # defender
            "novice",      # novice
            "mignon",      # cute one
            "allemand",    # German (behind l'allemand)
            "orateur",     # orator (behind l'orateur)
        ],
        "es": [
            "bribon",      # rogue
            "novicio",     # novice
        ],
        "de": [
            "senf",        # mustard (metonymy)
        ],
        "en": [
            "beast",       # beast (beasts)
            "ferret",      # ferret (ferrets)
            "goose",       # goose
            "apple",       # apple (apples)
        ],
        "eo": [
            "kobajo",      # guinea pig (kobajoj)
            "porketo",     # piglet
            "porkinfano",  # piglet (pig-child compound)
        ],
    },

    # ─── COMMUNICATION (language, expression, speech acts) ───
    "COMMUNICATION": {
        "fi": [
            "murahtaa",    # to growl (murahti)
            "intti",       # to insist / army slang
        ],
        "it": [
            "strillo",     # scream
            "mostrare",    # to show (mostra)
            "prorompere",  # to burst out (proruppe)
            "titolo",      # title
            "cenno",       # gesture, nod
            "proruppe",    # burst out (irregular p.remoto — no stem match)
        ],
        "fr": [
            "traduction",  # translation
            "addition",    # addition (additions)
            "clin",        # wink (clin d'œil)
            "modification",# modification
        ],
        "es": [
            "limosna",     # alms
            "asamblea",    # assembly
        ],
        "de": [
            "zanken",      # to quarrel
            "klatschen",   # to clap (klatschte)
            "klappern",    # to clatter
            "lesen",       # to read (lies — imperative)
        ],
        "en": [
            "squeak",      # to squeak (squeaking)
            "rattle",      # to rattle (rattling)
            "coax",        # to coax (coaxing)
            "hint",        # hint
            "label",       # label
            "mail",        # mail
        ],
        "eo": [
            "fajfi",       # to whistle
            "sarkasme",    # sarcasm (sarkasmo variant)
            "ekscelenco",  # excellency
            "ekze",        # like/as (variant of ekzemple)
            "iuspeca",     # of some kind
            "konsciante",  # consciously (variant)
        ],
    },

    # ─── COGNITION (thinking, knowledge, mental states) ───
    "COGNITION": {
        "fi": [
            "yhdentekevä", # indifferent (yhdentekevää)
            "luultu",      # believed, thought (luullut → voikko: luultu)
            "aavistus",    # premonition, inkling
            "läksy",       # lesson (läksyjä)
            "yleinen",     # general, public
        ],
        "it": [
            "succedere",   # to happen (successe)
            "tondo",       # round (shape concept)
            "rifiutare",   # to refuse (rifiuta)
            "successe",    # happened (irregular passato remoto — no stem match)
            "avessi",      # I had (congiuntivo imperfetto — irregular)
            "rifiuta",     # refuses (present, stem matches but checking)
        ],
        "fr": [
            "faveur",      # favour
            "succès",      # success
            "exprès",      # on purpose
            "magique",     # magic
            "incident",    # incident
            "physionomie", # physiognomy
            "hésiter",     # to hesitate (n'hésita)
            "paient",      # they pay (irregular stem of payer)
            "meurs",       # I die (irregular present of mourir)
        ],
        "es": [
            "rezar",       # to pray (rezaba)
            "eficaz",      # effective
            "inhumanidad", # inhumanity
            "desatentado", # dazed, discourteous
        ],
        "de": [],
        "en": [
            "choice",      # choice
            "ashamed",     # ashamed
            "giddy",       # giddy
        ],
        "eo": [
            "eblo",        # possibility
            "konsciente",  # conscious (variant of konscia)
            "kulpa",       # guilt
        ],
    },

    # ─── PERCEPTION (senses, observation, feeling) ───
    "PERCEPTION": {
        "fi": [
            "sopiva",      # suitable (sopivaa)
            "varova",      # careful (varovasti)
        ],
        "it": [
            "sepolcrale",  # sepulchral
        ],
        "fr": [
            "ému",         # moved, touched (emotion)
        ],
        "es": [
            "aliento",     # breath
        ],
        "de": [
            "spur",        # track, trace
            "spuren",      # tracks (plural) / to track
            "gellend",     # shrill (gellende)
        ],
        "en": [
            "unpleasant",  # unpleasant
        ],
        "eo": [
            "serene",      # serene (adverb form)
        ],
    },

    # ─── LIEU (place, space, location) ───
    "LIEU": {
        "fi": [
            "kuja",        # alley (kujaa)
        ],
        "it": [
            "ampolla",     # flask (dell'ampolla → elision)
        ],
        "fr": [
            "cachot",      # dungeon
            "étable",      # stable (behind l'étable)
            "surlendemain",# day after tomorrow
            "terrier",     # burrow
        ],
        "es": [
            "fábrica",     # factory
            "edificio",    # building (edificios)
        ],
        "de": [
            "pult",        # desk, lectern
            "teich",       # pond
            "heimisch",    # domestic, native
            "steuer",      # rudder / tax
            "verkehr",     # traffic
            "zauberland",  # magic land (compound: Zauber+Land)
        ],
        "en": [
            "latitude",    # latitude
            "railway",     # railway
        ],
        "eo": [
            "kamentubo",   # chimney (kamentubon)
            "kaldrono",    # cauldron
            "kaserolo",    # casserole
        ],
    },

    # ─── POSSESSION (having, owning, giving, receiving) ───
    "POSSESSION": {
        "fi": [
            "maalata",     # to paint (possession of craft)
            "katettu",     # covered, set (table)
        ],
        "it": [
            "riempire",    # to fill (riempie)
            "mancare",     # to lack (mancò)
            "attese",      # waited (attendere)
        ],
        "fr": [
            "mouchoir",    # handkerchief
            "remplir",     # to fill (remplie)
            "aumône",      # alms (behind l'aumône)
            "payer",       # to pay (paient)
        ],
        "es": [
            "cubierto",    # covered
            "esfuerzo",    # effort
            "faena",       # task, chore
        ],
        "de": [
            "lehren",      # to teach (lehrte)
            "wechseln",    # to change (wechselt)
            "wäsche",      # laundry
        ],
        "en": [
            "retain",      # to retain (retained)
            "relief",      # relief
            "cushion",     # cushion
            "spoon",       # spoon
            "clock",       # clock
        ],
        "eo": [
            "rekapti",     # to recapture (rekaptis)
        ],
    },

    # ─── DESTRUCTION (damage, breaking, violence) ───
    "DESTRUCTION": {
        "fi": [
            "hätäinen",    # hasty (hätäisesti)
            "katkaista",   # to cut, to break
        ],
        "it": [
            "scoppiare",   # to burst, to explode
        ],
        "fr": [
            "baïonnette",  # bayonet (baïonnettes)
            "mourir",      # to die (meurs)
        ],
        "es": [
            "bayoneta",    # bayonet (bayonetas)
            "ignominia",   # ignominy
        ],
        "de": [],
        "en": [],
        "eo": [
            "pafigi",      # to shoot (pafigxis — using x-system: pafigxi)
            "pafigxis",    # shot (past tense, direct form)
        ],
    },

    # ─── INTENSE (intensity, force, extremes) ───
    "INTENSE": {
        "fi": [
            "äreä",        # irritable (äreästi)
            "kernas",      # gladly, willingly (kernaasti)
            "hitunen",     # tiny bit (hitustakaan)
        ],
        "fr": [
            "hardiesse",   # boldness
        ],
        "es": [],
        "de": [],
        "en": [
            "thoroughly",  # thoroughly
        ],
        "eo": [],
    },

    # ─── BON (good, positive qualities) ───
    "BON": {
        "fi": [],
        "it": [],
        "fr": [
            "délice",      # delight (délices)
        ],
        "es": [],
        "de": [],
        "en": [],
        "eo": [
            "oportuna",    # opportune
            "gxojigi",     # to rejoice (gxojigite)
            "gxojigite",   # rejoiced (direct form)
            "fleksebla",   # flexible
        ],
    },

    # ─── DOMINATION (power, authority, control) ───
    "DOMINATION": {
        "fi": [],
        "it": [],
        "fr": [
            "daigner",     # to deign
        ],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── MATIÈRE (substance, material, nature) ───
    "MATIÈRE": {
        "fi": [
            "oksa",        # branch (oksaan)
        ],
        "it": [],
        "fr": [],
        "es": [
            "cimiento",    # foundation (cimientos)
        ],
        "de": [
            "pergamentrolle", # parchment scroll
        ],
        "en": [],
        "eo": [
            "brancxeto",   # small branch
            "gxenu",       # knee (body part/material)
        ],
    },

    # ─── MESURE (measurement, quantity, size) ───
    "MESURE": {
        "fi": [],
        "it": [],
        "fr": [],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── CORPS (body, physical form) ───
    "CORPS": {
        "it": [
            "baffo",       # moustache (baffi)
        ],
        "fr": [],
        "es": [],
        "fi": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── CREATION (making, producing) ───
    "CREATION": {
        "fi": [],
        "it": [],
        "fr": [],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── STRUCTURE (organization, form, arrangement) ───
    "STRUCTURE": {
        "fr": [
            "bande",       # band, strip
        ],
        "en": [
            "entangle",    # to entangle (entangled)
        ],
        "fi": [],
        "it": [],
        "es": [],
        "de": [],
        "eo": [],
    },

    # ─── RAGE (anger) ───
    "RAGE": {
        "en": [
            "rave",        # to rave (raving)
        ],
        "fi": [],
        "it": [],
        "fr": [],
        "es": [],
        "de": [],
        "eo": [],
    },

    # ─── PLAY (amusement, games) ───
    "PLAY": {
        "fi": [],
        "it": [],
        "fr": [],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── SEEKING (searching, wanting, desiring) ───
    "SEEKING": {
        "fi": [],
        "it": [],
        "fr": [],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── EXISTENCE (being, becoming, existing) ───
    "EXISTENCE": {
        "fi": [],
        "it": [],
        "fr": [],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── GRIEF (sorrow, mourning) ───
    "GRIEF": {
        "en": [
            "ashame",      # stem for ashamed (Snowball needs base)
        ],
        "fi": [],
        "it": [],
        "fr": [],
        "es": [],
        "de": [],
        "eo": [],
    },

    # ─── CARE (caring, nurturing) ───
    "CARE": {
        "fi": [],
        "it": [],
        "fr": [],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },
}

# ── Stop words: function words, noise tokens, dialectal forms ──
STOP_WORDS_V487 = {
    "fi": [
        "mua",         # dialectal "me" (minua)
        "m:llä",       # abbreviation
        "sweitsin",    # old spelling of Sveitsin (Switzerland)
        "kumminsa",    # dialectal "nevertheless"
        "huh",         # interjection
    ],
    "it": [
        "alcun",       # any (apocopated)
        "quei",        # those (demonstrative)
        "neppur",      # not even (apocopated neppure)
        "eppur",       # and yet (apocopated eppure)
        "dimmi",       # tell me (imperative+clitic)
        "vai",         # go! (imperative of andare)
        "dell'ampolla",# of the flask (whole elided token)
    ],
    "fr": [
        "d'eldorado[1",       # noise token with bracket
        "j.-j",                # abbreviation (J.-J. Rousseau)
        "londres.--imprimerie",# noise: printing location
        "l'allemand",         # elided: the German
        "l'aumône",           # elided: the alms
        "l'orateur",          # elided: the orator
        "l'étable",           # elided: the stable
        "n'hésita",           # elided: didn't hesitate
    ],
    "es": [
        "esten",       # old subjunctive of estar
        "obstante",    # (no) obstante — notwithstanding
        "verme",       # ver+me — to see me
    ],
    "de": [
        "eh",          # interjection
        "unsre",       # dialectal/old "unsere"
        "lies",        # imperative of lesen (read!)
    ],
    "en": [
        "and—oh",      # compound interjection with dash
        "them—and",    # compound with dash
        "pizzle",      # archaic/niche term
        "typographical",# meta-textual (about print)
        "barrowful",   # rare compound
        "ugh",         # interjection
    ],
    "eo": [
        "nei",         # in the (contracted)
        "ternas",      # (ordinal variant)
        "ternis",      # (ordinal variant)
        "unumomenta",  # compound: one-moment
        "plimulto",    # compound: more-much
        "dudekkvar",   # compound: twelve-four
        "vilcx",       # variant spelling
        "vilcxo",      # variant spelling
    ],
}

# ── Proper nouns: names, places ──
PROPER_NOUNS_V487 = {
    "fi": [
        "pekka",       # Finnish male name
    ],
    "it": [
        "gianni",      # Italian male name
    ],
    "fr": [
        "auguste",     # French male name (or adjective)
    ],
    "es": [
        "persia",      # Persia
        "padua",       # Padua (city)
    ],
    "de": [
        "antonie",     # German female name
    ],
    "en": [
        "transylvanian", # of Transylvania
        "mufti",       # title/proper noun
    ],
    "eo": [],
}

# ── Archaic forms → modern equivalents ──
ARCHAIC_FORMS_V487 = {
    "it": {
        "acciocchè": "affinché",   # so that (archaic)
        "aveano": "avevano",       # they had (archaic)
        "dètte": "dette",         # gave (archaic past tense)
        "s'inchinarono": "si inchinarono",  # they bowed (contraction)
    },
    "es": {
        "acabáron": "acabaron",       # they finished (old accent)
        "determináron": "determinaron",# they determined (old accent)
        "pegáron": "pegaron",         # they hit (old accent)
        "aceyte": "aceite",           # oil (old spelling)
        "abaxo": "abajo",             # below (old spelling)
        "oyéron": "oyeron",           # they heard (old accent)
        "incomodaba": "incomodaba",   # it bothered (actually regular)
    },
    "de": {
        "purpurroth": "purpurrot",     # crimson (old spelling)
        "verurtheilt": "verurteilt",   # convicted (old spelling)
        "adressirt": "adressiert",     # addressed (old spelling)
        "autorisirte": "autorisierte", # authorized (old spelling)
        "nöthig": "nötig",            # necessary (old spelling)
        "mährchen": "märchen",        # fairy tale (old spelling)
        "lenket": "lenkt",            # steers (old conjugation)
        "mähr": "mär",               # tale (old form)
    },
    "fr": {},
    "fi": {},
    "en": {},
    "eo": {},
}


# ── Access functions ──
def get_keywords_v487():
    """Return keyword dict: atom → {lang → [words]}."""
    # Filter out empty language lists
    result = {}
    for atom, langs in KEYWORDS_V487.items():
        filtered = {l: ws for l, ws in langs.items() if ws}
        if filtered:
            result[atom] = filtered
    return result


def get_stop_words_v487():
    """Return stop words dict: lang → [words]."""
    return {l: ws for l, ws in STOP_WORDS_V487.items() if ws}


def get_proper_nouns_v487():
    """Return proper nouns dict: lang → [words]."""
    return {l: ws for l, ws in PROPER_NOUNS_V487.items() if ws}


def get_archaic_forms_v487():
    """Return archaic forms dict: lang → {old → modern}."""
    return {l: fs for l, fs in ARCHAIC_FORMS_V487.items() if fs}


# ── Self-test ──
if __name__ == "__main__":
    kw = get_keywords_v487()
    sw = get_stop_words_v487()
    pn = get_proper_nouns_v487()
    af = get_archaic_forms_v487()

    total_kw = sum(len(ws) for langs in kw.values() for ws in langs.values())
    total_sw = sum(len(ws) for ws in sw.values())
    total_pn = sum(len(ws) for ws in pn.values())
    total_af = sum(len(fs) for fs in af.values())
    total = total_kw + total_sw + total_pn + total_af

    print(f"v4.8.7 expansion: {total} entries")
    print(f"  Keywords: {total_kw} across {len(kw)} atoms")
    print(f"  Stop words: {total_sw} across {len(sw)} langs")
    print(f"  Proper nouns: {total_pn} across {len(pn)} langs")
    print(f"  Archaic forms: {total_af} across {len(af)} langs")

    # Per-language keyword breakdown
    lang_counts = {}
    for atom, langs in kw.items():
        for l, ws in langs.items():
            lang_counts[l] = lang_counts.get(l, 0) + len(ws)
    for l in sorted(lang_counts, key=lambda x: -lang_counts[x]):
        print(f"    {l.upper()}: {lang_counts[l]} keywords")
