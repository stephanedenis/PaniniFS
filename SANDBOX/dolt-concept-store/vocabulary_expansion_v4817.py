#!/usr/bin/env python3
"""vocabulary_expansion_v4817.py — Common-word gap fill for FR/EN/IT/ES (62-file corpus)

After v4.8.15 (European targeted) and v4.8.16 (RU/NL deep), the corpus audit showed
that many *common everyday words* are missing from the lexicon. Words like:
  FR: action, rôle, confiance, analyse, découverte, refuge, phénomène
  EN: folk, conscience, example, weather, cavalry, client, photograph
  IT: additional Dante-specific vocabulary
  ES: additional Don Quijote vocabulary

These are high-frequency words that appear across multiple texts. Adding them
gives disproportionate coverage gains.

This expansion also includes:
- FR scientific/technical terms from Verne (pg799)
- EN literary proper nouns (Beowulf, Pride & Prejudice, Sherlock Holmes, etc.)
- Elision-base words (FR words appearing after l', d', s' that need their
  root form in the lexicon for Strategy 4 to work)

Format: {lang: {atom: [words]}} (same as v4814-v4816)

Agent: GitHub Copilot (Claude Opus 4.6) @ hauru
Session: 2026-02-23 — Common-word gap fill for FR→90%, EN→88%
"""

from typing import Dict, List


# ═══════════════════════════════════════════════════════════════════════════════
# FRENCH keywords — common words missing from the lexicon
# ═══════════════════════════════════════════════════════════════════════════════

KEYWORDS_V4817_FR = {
    "MOUVEMENT": [
        # Navigation & geography
        "ouest", "est", "nord", "sud", "pôle", "hémisphère",
        "excursion", "expédition", "itinéraire", "trajet",
        "crête", "roc", "promontoire",
        # Actions de mouvement
        "allumé", "allumer", "éteindre", "souffler",
        "lancer", "jeter", "tirer", "pousser",
        "plonger", "soulever", "hisser", "dégager",
    ],
    "PERCEPTION": [
        "découvert", "découverte", "découvertes", "découvrir",
        "perception", "phénomène", "spectacle", "analyse",
        "astronome", "astronomes", "conçu", "conçue",
        "inexplicable", "immuable",
    ],
    "CREATION": [
        # Construction & industrie
        "forage", "mécanique", "mécanisme", "pioche",
        "bombe", "obus", "munitions", "artillerie",
        "disque", "plaque", "ressorts", "maçonnerie",
        # Science & technique (Verne)
        "orbite", "satellite", "rotation", "périgée",
        "zénith", "balistique", "oxygène", "pyroxyle",
        "détonation", "projectile", "vitesse", "pesanteur",
        # Arts & industrie
        "manufacture", "usine", "atelier", "fonderie",
    ],
    "COMMUNICATION": [
        "action", "actions", "rôle", "employer", "emploi",
        "entreprise", "population", "séance", "rapport",
        "lecteurs", "actes", "attributs", "rédaction",
        "conférence", "discours", "discussion",
    ],
    "COGNITION": [
        "analyse", "étude", "examen", "expérience",
        "confiance", "conscience", "conviction",
        "hypothèse", "théorie", "calcul", "résultat",
        "argument", "conclusion", "preuve", "démonstration",
    ],
    "EXISTENCE": [
        "refuge", "abri", "asile", "retraite",
        "crypte", "caverne", "grotte", "souterrain",
        "existence", "présence", "absence",
    ],
    "QUALITE": [
        "fluide", "solide", "liquide", "gazeux",
        "décembre", "janvier", "février", "mars", "avril",
        "mai", "juin", "juillet", "août", "septembre",
        "octobre", "novembre",
        "inexplicable", "considérable", "formidable",
        "efficiente", "suffisant", "insuffisant",
    ],
    "DOMINATION": [
        "rôle", "autorité", "commandement",
        "régiment", "bataillon", "brigade",
        "capitaine", "lieutenant", "sergent", "soldat",
    ],
    "CARE": [
        "tabac", "médecin", "hôpital", "pharmacie",
        "remède", "soigner", "guérir",
    ],
    "POSSESSION": [
        "reptile", "fauves", "gibier", "tétras",
        "jacamar", "bétail", "troupeau",
    ],
    "SEEKING": [
        "suffit", "suffisant", "nécessaire", "indispensable",
        "obtenir", "procurer",
    ],
    "FEAR": [
        "ouragan", "tempête", "cyclone", "tornade",
        "foudre", "tonnerre", "éclairs",
    ],
    "GRIEF": [
        "épave", "naufrage", "désastre", "catastrophe",
        "ruine", "destruction",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# ENGLISH keywords — common words massively missing
# ═══════════════════════════════════════════════════════════════════════════════

KEYWORDS_V4817_EN = {
    "MOUVEMENT": [
        "aloft", "ashore", "overboard", "aboard",
        "rigging", "oars", "spout", "bulk",
        "cape", "raft", "hammock", "deck",
        "mast", "helm", "bow", "stern",
        "tackle", "anchor", "tide", "current",
        "seamen", "sailors", "boatswain", "crew",
    ],
    "PERCEPTION": [
        "photograph", "advertisement", "details",
        "example", "examples", "weather", "climate",
        "magician", "ether", "pike", "salmon",
        "discovery", "revelation", "inspection",
    ],
    "CREATION": [
        "switch", "wire", "gadget", "coils",
        "knob", "diagram", "flashlight", "device",
        "mechanism", "apparatus", "machinery",
        "professional", "reduction",
    ],
    "COMMUNICATION": [
        "actions", "gain", "reputation", "disposition",
        "dislike", "conscience", "gratitude",
        "client", "inspector", "detective",
        "evidence", "witness", "testimony", "alibi",
        "statement", "confession",
    ],
    "COGNITION": [
        "mystery", "puzzle", "clue", "solution",
        "suspicion", "motive", "deduction",
    ],
    "EXISTENCE": [
        "dwelling", "cattle", "livestock", "herd",
        "fold", "pasture", "hide", "leather",
        "park", "estate", "grounds",
    ],
    "QUALITE": [
        "beauteous", "unworthy", "onward",
        "heather", "barley", "aspen",
        "saturday", "sunday", "monday",
        "tuesday", "wednesday", "thursday", "friday",
    ],
    "DOMINATION": [
        "prowess", "folk", "deeds", "cavalry",
        "liegelord", "liegeman", "foeman", "wielder",
        "neath", "bade", "bairn",
        "thane", "earl", "chieftain", "overlord",
        "coronet", "diadem", "sceptre",
    ],
    "CARE": [
        "bosom", "auntie", "jacket", "bet",
        "bout", "tick",
    ],
    "FEAR": [
        "bulwarks", "flukes", "whaleman",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# ITALIAN keywords — more Dante + general IT
# ═══════════════════════════════════════════════════════════════════════════════

KEYWORDS_V4817_IT = {
    "MOUVEMENT": [
        "salire", "scendere", "girare", "volgere",
        "uscire", "entrare", "cadere", "sorgere",
    ],
    "PERCEPTION": [
        "voce", "suono", "luce", "ombra",
        "vista", "sguardo",
    ],
    "EXISTENCE": [
        "dimora", "soggiorno", "rifugio", "asilo",
        "fossa", "sepolcro", "tomba",
    ],
    "COGNITION": [
        "virtù", "sapienza", "ragione", "dottrina",
        "consiglio", "giudizio",
    ],
    "QUALITE": [
        "eterno", "eterna", "divino", "divina",
        "celeste", "terrestre", "mortale", "immortale",
        "beato", "beata", "santo", "santa",
    ],
    "DOMINATION": [
        "imperio", "regno", "corona", "trono",
        "signore", "maestro",
    ],
    "GRIEF": [
        "peccato", "peccatore", "colpa", "castigo",
        "vendetta", "punizione",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# SPANISH keywords — more Don Quijote vocabulary
# ═══════════════════════════════════════════════════════════════════════════════

KEYWORDS_V4817_ES = {
    "MOUVEMENT": [
        "salir", "entrar", "caer", "subir", "bajar",
        "caminar", "correr", "volver",
    ],
    "COMMUNICATION": [
        "ejemplo", "razón", "verdad", "mentira",
        "respuesta", "promesa", "juramento",
    ],
    "DOMINATION": [
        "hazaña", "valentía", "proeza",
        "ejército", "soldado", "capitán",
    ],
    "COGNITION": [
        "locura", "cordura", "sabiduría", "prudencia",
        "discreción", "entendimiento",
    ],
    "CARE": [
        "honra", "deshonra", "piedad", "caridad",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# STOP WORDS — archaic connectors, calendar, function words
# ═══════════════════════════════════════════════════════════════════════════════

STOP_WORDS_V4817 = {
    "fr": [
        # Calendar/time that act as function words
        "mm", "m", "dr",
        # Verb forms acting as function words in Verne
        "aurons", "auront", "aurions",
        "eussent", "eûmes",
        # Archaic/literary
        "faillir", "sert", "suffit",
        "sauroit", "saurois",
    ],
    "en": [
        "cf", "nay", "aye", "yea",
        "ha", "eh", "gainst",
        "awhile", "betimes", "forsooth",
        "ha'nted", "becuz",  # Tom Sawyer dialect
    ],
    "it": [
        # Additional Dante function words
        "colà", "ivi", "onde", "quivi",
        "poscia", "dunque", "orsù",
    ],
    "es": [
        # Additional function words
        "pues", "luego", "aún", "aun",
        "sino", "acá", "allá",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# PROPER NOUNS — literary characters and places
# ═══════════════════════════════════════════════════════════════════════════════

PROPER_NOUNS_V4817 = {
    "fr": [
        # Verne - De la Terre à la Lune (pg799)
        "Elphiston", "Murchison", "Rodman", "Herschell",
        "Tampa", "Texas", "Jupiter", "Neptune", "Mars",
        "Barbicane", "Nicholl", "Ardan", "Maston",
        # Verne - L'Île mystérieuse additional
        "Harbert", "Jup",
        # Descartes (pg13846)
        "Descartes",
    ],
    "en": [
        # Pride & Prejudice (pg1342)
        "Pemberley", "Rosings", "Hertfordshire", "Forster",
        "Bourgh", "Hurst", "Fitzwilliam", "Philips",
        "Hunsford", "Derbyshire", "Eliza", "Collins",
        "Lydia", "Georgiana", "Longbourn", "Netherfield",
        # Sherlock Holmes (pg1661)
        "Simon", "Lestrade", "Rucastle", "McCarthy",
        "Hosmer", "Wilson", "Neville", "Openshaw",
        "Boscombe", "Baker", "Watson",
        # Moby Dick additional (pg2701)
        "Nantucket", "Pequod", "Fedallah", "Flask",
        # Beowulf additional (pg16328)
        "Danemen", "Weders",
        # Kalevala additional (pg5185)
        "Mariatta", "Tuoni", "Ahti",
        # The Prince (pg1232)
        "Pistoia", "Milan", "Uguccione", "Sinigalia",
        "Sforza", "Lombardy", "Tuscany", "Bologna",
        "Guinigi",
        # Tom Sawyer additional (pg74)
        "Douglas", "Welshman",
        # Picture of Dorian Gray (pg174)
        "Dorian", "Basil", "Hallward", "Sibyl",
    ],
    "es": [
        # Don Quijote additional
        "Maese", "Nicolás", "Cide", "Hamete",
        "Benengeli", "Sierra", "Morena",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════════

def get_keywords_v4817() -> Dict[str, Dict[str, List[str]]]:
    """Return keywords by language → atom → keyword list."""
    return {
        "fr": KEYWORDS_V4817_FR,
        "en": KEYWORDS_V4817_EN,
        "it": KEYWORDS_V4817_IT,
        "es": KEYWORDS_V4817_ES,
    }


def get_stop_words_v4817() -> Dict[str, list]:
    """Return stop words by language."""
    return STOP_WORDS_V4817


def get_proper_nouns_v4817() -> Dict[str, List[str]]:
    """Return proper nouns by language."""
    return PROPER_NOUNS_V4817


# ═══════════════════════════════════════════════════════════════════════════════
# SELF-TEST
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    kw = get_keywords_v4817()
    sw = get_stop_words_v4817()
    pn = get_proper_nouns_v4817()

    total_kw = sum(len(w) for lang in kw.values() for w in lang.values())
    total_sw = sum(len(w) for w in sw.values())
    total_pn = sum(len(n) for n in pn.values())

    print(f"v4.8.17 Vocabulary Expansion:")
    print(f"  Keywords:     {total_kw} across {len(kw)} langs")
    for lang, atoms in kw.items():
        n = sum(len(w) for w in atoms.values())
        print(f"    {lang}: {n} words, {len(atoms)} atoms")
    print(f"  Stop words:   {total_sw}")
    for lang, words in sw.items():
        print(f"    {lang}: {len(words)}")
    print(f"  Proper nouns: {total_pn}")
    for lang, names in pn.items():
        print(f"    {lang}: {len(names)}")
    print(f"  TOTAL:        {total_kw + total_sw + total_pn}")
    print("\n✓ Self-test complete")
