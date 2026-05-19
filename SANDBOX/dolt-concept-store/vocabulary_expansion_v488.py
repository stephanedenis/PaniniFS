#!/usr/bin/env python3
"""vocabulary_expansion_v488.py — v4.8.8: Push FR/IT/FI above 90%

Target: FR 89.7%→90%+, IT 88.2%→90%+, FI 87.7%→90%+
Strategy:
- FI: voikko lemma injection (top50 gap words → add lemmas as keywords)
- IT: Pinocchio verb forms + archaic contractions as stop words
- FR: nouns/adjectives/verbs at freq=4-5 + proper nouns + elisions

Created: 2026-02-21 by Copilot (Claude Opus 4.6) on hauru
"""

KEYWORDS_V488 = {
    # ─── MOUVEMENT ───
    "MOUVEMENT": {
        "fi": [
            "saattaa",       # to escort/cause (saata)
            "ennättää",      # to have time for (ennätti)
            "ehtiä",         # to have time (ehti, ehtineet)
            "johdattaa",     # to lead (johdatti)
            "esiintyä",      # to appear (esiintyi)
            "ryhtyä",        # to start doing (ryhtyä)
            "niiata",        # to curtsy (niiata)
            "vaipuva",       # sinking (vaipuvansa)
        ],
        "it": [
            "sollevare",     # to lift (sollevata)
            "risvegliare",   # to wake up (risvegliati)
            "stropicciare",  # to rub (stropicciandosi)
        ],
        "fr": [
            "retrouver",     # to find again (retrouva)
            "refermer",      # to close again (referme)
            "détourner",     # to divert (détourner)
            "aborder",       # to approach (l'aborda)
        ],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── AGENT ───
    "AGENT": {
        "fi": [
            "rapu",          # crab
            "piru",          # devil
            "kersantti",     # sergeant
            "valkoturska",   # white cod (compound)
        ],
        "it": [
            "miche",         # loaves (pl of mica)
            "selvaggia",     # wild (fem adj/noun)
        ],
        "fr": [
            "sexe",          # sex/gender
            "aiglon",        # eaglet (l'aiglon)
        ],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── COMMUNICATION ───
    "COMMUNICATION": {
        "fi": [
            "keskustella",   # to discuss (keskustelivat)
        ],
        "it": [
            "grugnire",      # to grunt
            "grugnì",        # grunted (irregular passato remoto)
        ],
        "fr": [
            "proférer",      # to utter
            "emphase",       # emphasis
            "inexprimable",  # inexpressible
            "exprimer",      # to express (s'exprimer)
        ],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── PERCEPTION ───
    "PERCEPTION": {
        "fi": [
            "tuikea",        # stern (tuikeasti)
            "ihailtava",     # admirable (ihailtavia)
            "ihme",          # wonder, miracle (ihmettä)
            "ihastus",       # delight (ihastuksissaan)
            "riippuva",      # hanging (riippuvan)
        ],
        "it": [
            "tocco",         # touch
            "rosso",         # red
            "sdegnosa",      # scornful
            "sdegnosamente", # scornfully
            "affissandola",  # staring at her (compound gerund)
        ],
        "fr": [
            "fraîcheur",     # freshness
            "extase",        # ecstasy
            "rauque",        # hoarse
            "fraîche",       # fresh (fem)
            "frisé",         # curly (frisés)
        ],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── LIEU ───
    "LIEU": {
        "fi": [
            "kenttä",        # field (kenttää)
            "pinta",         # surface (pinnalla)
            "sohva",         # sofa (sohvalle)
            "krokettikenttä",# croquet field (compound)
            "liivintasku",   # vest pocket (compound)
        ],
        "it": [],
        "fr": [
            "haie",          # hedge
            "nid",           # nest
        ],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── COGNITION ───
    "COGNITION": {
        "fi": [
            "paha",          # bad (pahasta)
            "intohimoinen",  # passionate (intohimoisesti)
        ],
        "it": [],
        "fr": [
            "convaincu",     # convinced
            "universel",     # universal (universelle)
        ],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── POSSESSION ───
    "POSSESSION": {
        "fi": [
            "palvelu",       # service (palvelukseen)
            "kannattaa",     # to support/be worth (kannatti)
            "toimitus",      # delivery/editorial
        ],
        "it": [
            "dò",            # I give (dare, 1sg present)
            "condannare",    # to condemn (condannati)
        ],
        "fr": [
            "couvrir",       # to cover (couvrent)
            "garnir",        # to garnish (garnies)
            "boîte",         # box
            "gousset",       # watch pocket
        ],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── DESTRUCTION ───
    "DESTRUCTION": {
        "fi": [],
        "it": [
            "mozzare",       # to cut off (mozzatele)
        ],
        "fr": [
            "fracas",        # crash, din
            "débris",        # debris
            "fendre",        # to split (fendu)
            "funeste",       # fatal
            "fouet",         # whip
            "fouetter",      # to whip (fouetté)
            "érailler",      # to scratch (éraillés)
        ],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── MATIÈRE ───
    "MATIÈRE": {
        "fi": [
            "illallinen",    # dinner (illallisen)
        ],
        "it": [],
        "fr": [
            "lard",          # lard/bacon
            "vêtir",         # to dress (vêtus)
            "rafraîchissement",# refreshment (rafraîchissements)
            "rouet",         # spinning wheel
        ],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── MESURE ───
    "MESURE": {
        "fi": [
            "penikulma",     # league (distance)
            "kauan",         # long (time)
        ],
        "it": [],
        "fr": [
            "dimanche",      # Sunday
        ],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── PLAY ───
    "PLAY": {
        "fi": [
            "näytelmä",      # play (theatrical, näytelmiä)
            "teeseura",      # tea party
        ],
        "it": [
            "concerto",      # concert
            "ruzzo",         # play/fun
        ],
        "fr": [
            "cocasse",       # comical
        ],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── BON ───
    "BON": {
        "fi": [],
        "it": [
            "trionfo",       # triumph
            "garbatezza",    # politeness
        ],
        "fr": [
            "efficace",      # effective
            "rémission",     # remission
            "ravissant",     # delightful
        ],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── INTENSE ───
    "INTENSE": {
        "fi": [],
        "it": [],
        "fr": [
            "téméraire",     # reckless
        ],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── DOMINATION ───
    "DOMINATION": {
        "fi": [
            "pakotettu",     # forced (pakotettu — voikko base)
        ],
        "it": [],
        "fr": [
            "résister",      # to resist (résisté)
        ],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── GRAND ───
    "GRAND": {
        "fi": [],
        "it": [
            "intiera",       # whole (archaic variant of intera)
        ],
        "fr": [],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── STRUCTURE ───
    "STRUCTURE": {
        "fi": [],
        "it": [],
        "fr": [
            "désordre",      # disorder
            "étiquette",     # label/etiquette
        ],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── GRIEF ───
    "GRIEF": {
        "fi": [],
        "it": [
            "disdegno",      # disdain
        ],
        "fr": [
            "boudeur",       # sulky
        ],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── DISGUST ───
    "DISGUST": {
        "fi": [],
        "it": [],
        "fr": [],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── SEEKING ───
    "SEEKING": {
        "fi": [],
        "it": [],
        "fr": [
            "retrouva",     # found again (passé simple — irregular stem)
        ],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── ORDRE ───
    "ORDRE": {
        "fi": [],
        "it": [],
        "fr": [],
        "es": [],
        "de": [],
        "en": [],
        "eo": [],
    },

    # ─── MAUVAIS ───
    "MAUVAIS": {
        "fi": [],
        "it": [],
        "fr": [],
        "es": [],
    },
}

# ── Stop words ──
STOP_WORDS_V488 = {
    "fi": [
        "ois",           # dialectal "would be" (olisi)
        "ku-ulta",       # hyphenated noise
        "suklaatia",     # chocolate (no voikko analysis, dialectal)
        "hekin",         # they too
        "molemmille",    # to both (molempi)
        "molemmista",    # from both (molempi)
        "ohoh",          # interjection
        "ensimäistä",    # first (ordinal, function)
        "taa",           # dialectal/noise
        "neekeri",       # historical offensive term (context: old texts)
        "etenkin",       # especially (adverb, function-like)
        "aimo",          # decent/generous (dialectal)
        "kauemmin",      # longer (comparative)
        "uniseksi",      # sleepy (dialectal)
        "läiskis",       # dialectal/onomatopoeia
    ],
    "it": [
        "lai",           # archaic article/pronoun
        "vuol",          # wants (apocopated volere)
        "potrà",         # will be able (potere future)
        "abbiam",        # we have (apocopated abbiamo)
        "ch'_io",        # that I (archaic contraction)
        "fè",            # made/did (archaic fare past)
        "siate",         # be (congiuntivo presente of essere)
        "fo",            # I make (archaic 1sg of fare)
        "dagli",         # from the / give him (article+prep)
        "l'uso",         # the use (elided)
    ],
    "fr": [
        "nôtre",         # ours (possessive)
        "l'aborda",      # elided: approached him/her
        "s'exprimer",    # elided: to express oneself
        "s'étendant",    # elided: extending
        "l'aiglon",      # elided: the eaglet
    ],
    "es": [],
    "de": [],
    "en": [],
    "eo": [],
}

# ── Proper nouns ──
PROPER_NOUNS_V488 = {
    "fr": [
        "padoue",        # Padua
        "badajos",       # Badajoz (Spanish city)
        "northumbrie",   # Northumbria
    ],
    "fi": [],
    "it": [],
    "es": [],
    "de": [],
    "en": [],
    "eo": [],
}

# ── Archaic forms ──
ARCHAIC_FORMS_V488 = {
    "it": {
        "stroppia": "storpia",      # twists (dialectal)
        "intiera": "intera",        # whole (old spelling)
        "bruttificazione": "bruttificazione", # ugly-making (Pinocchio neologism)
    },
    "fi": {},
    "fr": {},
    "es": {},
    "de": {},
    "en": {},
    "eo": {},
}


def get_keywords_v488():
    result = {}
    for atom, langs in KEYWORDS_V488.items():
        filtered = {l: ws for l, ws in langs.items() if ws}
        if filtered:
            result[atom] = filtered
    return result

def get_stop_words_v488():
    return {l: ws for l, ws in STOP_WORDS_V488.items() if ws}

def get_proper_nouns_v488():
    return {l: ws for l, ws in PROPER_NOUNS_V488.items() if ws}

def get_archaic_forms_v488():
    return {l: fs for l, fs in ARCHAIC_FORMS_V488.items() if fs}


if __name__ == "__main__":
    kw = get_keywords_v488()
    sw = get_stop_words_v488()
    pn = get_proper_nouns_v488()
    af = get_archaic_forms_v488()

    total_kw = sum(len(ws) for langs in kw.values() for ws in langs.values())
    total_sw = sum(len(ws) for ws in sw.values())
    total_pn = sum(len(ws) for ws in pn.values())
    total_af = sum(len(fs) for fs in af.values())
    total = total_kw + total_sw + total_pn + total_af

    print(f"v4.8.8 expansion: {total} entries")
    print(f"  Keywords: {total_kw} across {len(kw)} atoms")
    print(f"  Stop words: {total_sw} across {len(sw)} langs")
    print(f"  Proper nouns: {total_pn} across {len(pn)} langs")
    print(f"  Archaic forms: {total_af} across {len(af)} langs")

    lang_counts = {}
    for atom, langs in kw.items():
        for l, ws in langs.items():
            lang_counts[l] = lang_counts.get(l, 0) + len(ws)
    for l in sorted(lang_counts, key=lambda x: -lang_counts[x]):
        print(f"    {l.upper()}: {lang_counts[l]} keywords")
