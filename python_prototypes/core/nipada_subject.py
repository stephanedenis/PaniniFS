"""
nipada_subject.py — 5e atome SUJET(11) — couche phénoménologique nipada (§82)

Motivation (McLuhan) :
    Le medium est le message. Les 4 atomes existants {ÊTRE(2), DIFFÉRENCE(3),
    RAPPORT(5), ORIENTATION(7)} couvrent la couche *ontologique* — la structure
    des relations entre entités. Mais DUDH_1a ("Tous les êtres humains naissent
    libres et égaux en dignité et en droits") obtient systématiquement cycle_sim≈0.21
    avec l'encodage [ÊTRE+VIE+EXISTENCE] : la phrase ne décrit pas une structure,
    elle PROCLAME — et la proclamation requiert un observateur.

    SUJET(11) est le 5e atome : l'observateur, le porteur, le soi réflexif.
    Il ouvre la couche phénoménologique (qui énonce, pour qui, dans quel cadre).

5e prime : 11 — SUJET
======================
Avec {2,3,5,7,11}, 31 molécules non-vides (2^5 - 1).
Les 16 nouvelles molécules contiennent le facteur 11.

Molécules SUJET (IDs = produits incluant 11) :
    11   SUJET        {11}
    22   PRÉSENCE     {2,11}
    33   NORME        {3,11}
    55   DROIT        {5,11}
    77   LIBERTÉ      {7,11}
    66   IDENTITÉ     {2,3,11}
   110   VALEUR       {2,5,11}
   154   PROJET       {2,7,11}
   165   JUGEMENT     {3,5,11}
   231   RÉSISTANCE   {3,7,11}
   385   SENS         {5,7,11}   ← architectural (RAPPORT+ORIENT+SUJET)
   330   LANGAGE      {2,3,5,11}  ← architectural (n=4)
   462   RÉCIT        {2,3,7,11}  ← architectural (n=4)
   770   DIGNITÉ      {2,5,7,11}  ← architectural (n=4)
  1155   MÉMOIRE      {3,5,7,11}  ← architectural (n=4)
  2310   CONSCIENCE   {2,3,5,7,11} ← architectural (n=5)

Règle architecturale étendue (issue de §80A/§81) :
    - n_atomes ≥ 4          → architectural → définition
    - n_atomes = 3, RAPPORT(5) ET ORIENT(7) présents → architectural → définition
    Architecturales SUJET : SENS(385), LANGAGE(330), RÉCIT(462), DIGNITÉ(770),
                             MÉMOIRE(1155), CONSCIENCE(2310)

Hypothèse §82 :
    DUDH_1a re-encodée avec [DIGNITÉ(770), LIBERTÉ(77), DROIT(55)]
    produit cycle_sim > 0.50 — soit plus du double du score §79 (≈0.21).
"""

from __future__ import annotations

from src.core.nipada_synthesizer import (
    KERNELS, DEFINITIONS, NipadaSynthesizer,
    _ORIENT_PRIME, _RAPPORT_PRIME, _CROSS_CONNECTORS,
)

# ══════════════════════════════════════════════════════════════════════════════
# Constantes
# ══════════════════════════════════════════════════════════════════════════════

SUJET_PRIME = 11

# Décomposition prime de chaque molécule SUJET (lookup direct)
SUJET_ATOMS: dict[int, frozenset[int]] = {
    11:   frozenset({11}),
    22:   frozenset({2,  11}),
    33:   frozenset({3,  11}),
    55:   frozenset({5,  11}),
    77:   frozenset({7,  11}),
    66:   frozenset({2,  3,  11}),
    110:  frozenset({2,  5,  11}),
    154:  frozenset({2,  7,  11}),
    165:  frozenset({3,  5,  11}),
    231:  frozenset({3,  7,  11}),
    385:  frozenset({5,  7,  11}),
    330:  frozenset({2,  3,  5,  11}),
    462:  frozenset({2,  3,  7,  11}),
    770:  frozenset({2,  5,  7,  11}),
    1155: frozenset({3,  5,  7,  11}),
    2310: frozenset({2,  3,  5,  7,  11}),
}

SUJET_MOL_IDS = list(SUJET_ATOMS.keys())

SUJET_MOL_NAMES: dict[str, dict[int, str]] = {
    "fr": {
        11:   "SUJET",      22:   "PRÉSENCE",   33:   "NORME",     55:   "DROIT",
        77:   "LIBERTÉ",    66:   "IDENTITÉ",   110:  "VALEUR",    154:  "PROJET",
        165:  "JUGEMENT",   231:  "RÉSISTANCE", 385:  "SENS",      330:  "LANGAGE",
        462:  "RÉCIT",      770:  "DIGNITÉ",    1155: "MÉMOIRE",   2310: "CONSCIENCE",
    },
    "en": {
        11:   "SUBJECT",    22:   "PRESENCE",   33:   "NORM",      55:   "RIGHT",
        77:   "FREEDOM",    66:   "IDENTITY",   110:  "VALUE",     154:  "PROJECT",
        165:  "JUDGMENT",   231:  "RESISTANCE", 385:  "MEANING",   330:  "LANGUAGE",
        462:  "NARRATIVE",  770:  "DIGNITY",    1155: "MEMORY",    2310: "CONSCIOUSNESS",
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# Noyaux sémantiques SUJET (8–14 mots, combinables)
# ══════════════════════════════════════════════════════════════════════════════

KERNELS_SUJET: dict[str, dict[int, str]] = {
    "fr": {
        11:   "un observateur se rapporte à lui-même comme point de référence",
        22:   "quelque chose se manifeste à un sujet qui le perçoit",
        33:   "un sujet pose une distinction comme règle obligatoire",
        55:   "un sujet établit une relation comme droit ou devoir",
        77:   "un sujet choisit librement la direction de son action",
        66:   "un sujet se distingue lui-même de ce qu'il n'est pas",
        110:  "un sujet institue une relation de valeur entre deux êtres",
        154:  "un sujet oriente son être vers une fin librement choisie",
        165:  "un sujet évalue une différence selon un rapport normatif",
        231:  "un sujet s'oppose à ce qui contredit sa direction propre",
        385:  "un sujet oriente un rapport vers une signification qui lui est propre",
        330:  "un sujet structure ses différences en système de relations porteuses de sens",
        462:  "un sujet organise son être et ses différences dans une trame narrative orientée",
        770:  "un être porte en lui le rapport orienté qui fonde sa valeur propre",
        1155: "un sujet retient les différences ordonnées dans une durée orientée",
        2310: "un sujet intègre être, différence, rapport et orientation en une expérience unifiée",
    },
    "en": {
        11:   "an observer relates to itself as a reference point",
        22:   "something manifests itself to a subject who perceives it",
        33:   "a subject posits a distinction as an obligatory rule",
        55:   "a subject establishes a relation as right or duty",
        77:   "a subject freely chooses the direction of its action",
        66:   "a subject distinguishes itself from what it is not",
        110:  "a subject institutes a relation of value between two beings",
        154:  "a subject orients its being toward a freely chosen end",
        165:  "a subject evaluates a difference according to a normative standard",
        231:  "a subject opposes what contradicts its chosen direction",
        385:  "a subject orients a relation toward a meaning proper to itself",
        330:  "a subject structures its differences into a system of meaning-bearing relations",
        462:  "a subject organizes its being and differences in a directed narrative framework",
        770:  "a being carries within itself the oriented relation that grounds its own value",
        1155: "a subject retains ordered differences in a directed duration",
        2310: "a subject integrates being, difference, ratio and orientation into a unified experience",
    },
    "de": {
        11:   "ein Beobachter bezieht sich auf sich selbst als Referenzpunkt",
        22:   "etwas manifestiert sich einem Subjekt, das es wahrnimmt",
        33:   "ein Subjekt setzt eine Unterscheidung als verbindliche Regel",
        55:   "ein Subjekt etabliert eine Beziehung als Recht oder Pflicht",
        77:   "ein Subjekt wählt frei die Richtung seines Handelns",
        66:   "ein Subjekt unterscheidet sich selbst von dem, was es nicht ist",
        110:  "ein Subjekt begründet eine Wertbeziehung zwischen zwei Wesen",
        154:  "ein Subjekt richtet sein Sein auf ein frei gewähltes Ziel",
        165:  "ein Subjekt bewertet eine Differenz nach einem normativen Maßstab",
        231:  "ein Subjekt widersetzt sich dem, was seiner Richtung widerspricht",
        385:  "ein Subjekt richtet eine Beziehung auf eine ihm eigene Bedeutung aus",
        330:  "ein Subjekt strukturiert seine Differenzen zu einem bedeutungstragenden Beziehungssystem",
        462:  "ein Subjekt organisiert sein Sein und seine Differenzen in einem gerichteten narrativen Rahmen",
        770:  "ein Wesen trägt in sich die gerichtete Beziehung, die seinen eigenen Wert begründet",
        1155: "ein Subjekt bewahrt geordnete Differenzen in einer gerichteten Dauer",
        2310: "ein Subjekt integriert Sein, Differenz, Verhältnis und Orientierung in eine einheitliche Erfahrung",
    },
    "es": {
        11:   "un observador se refiere a sí mismo como punto de referencia",
        22:   "algo se manifiesta a un sujeto que lo percibe",
        33:   "un sujeto establece una distinción como regla obligatoria",
        55:   "un sujeto establece una relación como derecho o deber",
        77:   "un sujeto elige libremente la dirección de su acción",
        66:   "un sujeto se distingue a sí mismo de lo que no es",
        110:  "un sujeto instituye una relación de valor entre dos seres",
        154:  "un sujeto orienta su ser hacia un fin libremente elegido",
        165:  "un sujeto evalúa una diferencia según un estándar normativo",
        231:  "un sujeto se opone a lo que contradice su dirección elegida",
        385:  "un sujeto orienta una relación hacia un significado que le es propio",
        330:  "un sujeto estructura sus diferencias en un sistema de relaciones portadoras de sentido",
        462:  "un sujeto organiza su ser y sus diferencias en un marco narrativo orientado",
        770:  "un ser lleva en sí la relación orientada que funda su propio valor",
        1155: "un sujeto retiene diferencias ordenadas en una duración orientada",
        2310: "un sujeto integra ser, diferencia, razón y orientación en una experiencia unificada",
    },
    "zh": {
        11:   "观察者以自身为参照点与自身发生关系",
        22:   "某物向感知它的主体显现",
        33:   "主体将某种区别设立为强制性规则",
        55:   "主体将某种关系确立为权利或义务",
        77:   "主体自由选择其行动的方向",
        66:   "主体将自身区别于其所不是的东西",
        110:  "主体在两个存在之间建立价值关系",
        154:  "主体将其存在朝向自由选择的目的",
        165:  "主体依据规范标准评价差异",
        231:  "主体抵制与其方向相矛盾的东西",
        385:  "主体将关系朝向属于自身固有的意义",
        330:  "主体将其差异结构为承载意义的关系系统",
        462:  "主体在定向叙事框架中组织其存在与差异",
        770:  "存在者自身携带着奠定其固有价值的定向关系",
        1155: "主体在定向持续时间中保留有序的差异",
        2310: "主体将存在、差异、比率与方向整合为统一的经验",
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# Phrases définitionnelles SUJET (couche §82)
# ══════════════════════════════════════════════════════════════════════════════

DEFINITIONS_SUJET: dict[str, dict[int, str]] = {
    "fr": {
        11:   "Le sujet est l'observateur irréductible : le point de référence qui se rapporte à lui-même, antérieur à toute relation à l'autre.",
        22:   "La présence est l'articulation de l'être et du sujet : quelque chose est présent quand son être se manifeste à un sujet qui le perçoit.",
        33:   "La norme est l'articulation de la différence et du sujet : une norme est une distinction posée par un sujet comme règle obligatoire pour lui-même ou pour d'autres.",
        55:   "Le droit est l'articulation du rapport et du sujet : un droit est une relation établie par un sujet comme légitime et contraignante pour les autres.",
        77:   "La liberté est l'articulation de l'orientation et du sujet : la liberté est le pouvoir qu'a un sujet d'orienter lui-même son action vers un but qu'il a choisi.",
        66:   "L'identité est l'articulation de l'être, de la différence et du sujet : un sujet a une identité quand il se distingue lui-même, de façon stable, de ce qu'il n'est pas.",
        110:  "La valeur est l'articulation de l'être, du rapport et du sujet : une valeur est une relation établie par un sujet entre deux êtres, instituant l'un comme mesure de l'autre.",
        154:  "Le projet est l'articulation de l'être, de l'orientation et du sujet : un projet est un être orienté par un sujet vers une fin qu'il a librement choisie.",
        165:  "Le jugement est l'articulation de la différence, du rapport et du sujet : un jugement est la mesure d'une différence par un sujet selon un rapport normatif.",
        231:  "La résistance est l'articulation de la différence, de l'orientation et du sujet : un sujet résiste quand il oppose sa propre direction à une différence extérieure qui la contrarie.",
        385:  "Le sens est l'articulation du rapport, de l'orientation et du sujet : le sens est un rapport orienté par un sujet vers une signification qui lui est propre et irréductible.",
        330:  "Le langage est l'articulation de l'être, de la différence, du rapport et du sujet : un langage est un système dans lequel un sujet structure ses différences en relations porteuses de sens.",
        462:  "Le récit est l'articulation de l'être, de la différence, de l'orientation et du sujet : un récit est l'organisation par un sujet de ses différences dans une trame temporelle orientée.",
        770:  "La dignité est l'articulation de l'être, du rapport, de l'orientation et du sujet : la dignité est le rapport orienté qu'un être entretient avec lui-même, qui fonde sa valeur propre et irréductible à toute appréciation extérieure.",
        1155: "La mémoire est l'articulation de la différence, du rapport, de l'orientation et du sujet : la mémoire est la rétention par un sujet des différences ordonnées dans une durée orientée vers le présent.",
        2310: "La conscience est l'articulation de l'être, de la différence, du rapport, de l'orientation et du sujet : la conscience est l'intégration subjective totale — un sujet qui intègre son être, ses différences, ses rapports et ses orientations en une expérience unifiée et réflexive.",
    },
    "en": {
        11:   "Subject is the irreducible observer: the reference point that relates to itself prior to any relation to the other.",
        22:   "Presence is the articulation of being and subject: something is present when its being manifests to a subject who perceives it.",
        33:   "Norm is the articulation of difference and subject: a norm is a distinction posited by a subject as an obligatory rule for itself or for others.",
        55:   "Right is the articulation of ratio and subject: a right is a relation established by a subject as legitimate and binding for others.",
        77:   "Freedom is the articulation of orientation and subject: freedom is the power a subject has to orient its own action toward a goal it has chosen.",
        66:   "Identity is the articulation of being, difference and subject: a subject has an identity when it stably distinguishes itself from what it is not.",
        110:  "Value is the articulation of being, ratio and subject: a value is a relation established by a subject between two beings, instituting one as the measure of the other.",
        154:  "Project is the articulation of being, orientation and subject: a project is a being oriented by a subject toward an end it has freely chosen.",
        165:  "Judgment is the articulation of difference, ratio and subject: a judgment is the measure of a difference by a subject according to a normative standard.",
        231:  "Resistance is the articulation of difference, orientation and subject: a subject resists when it opposes its own direction to an external difference that contradicts it.",
        385:  "Meaning is the articulation of ratio, orientation and subject: meaning is a ratio oriented by a subject toward a significance that is proper and irreducible to it.",
        330:  "Language is the articulation of being, difference, ratio and subject: a language is a system in which a subject structures its differences into meaning-bearing relations.",
        462:  "Narrative is the articulation of being, difference, orientation and subject: a narrative is a subject's organization of its differences in a directed temporal framework.",
        770:  "Dignity is the articulation of being, ratio, orientation and subject: dignity is the oriented relation a being maintains with itself, grounding its own value irreducible to any external appraisal.",
        1155: "Memory is the articulation of difference, ratio, orientation and subject: memory is a subject's retention of ordered differences in a duration oriented toward the present.",
        2310: "Consciousness is the articulation of being, difference, ratio, orientation and subject: consciousness is total subjective integration — a subject that integrates its being, differences, relations and orientations into a unified and reflexive experience.",
    },
    "de": {
        11:   "Subjekt ist der irreduzible Beobachter: der Referenzpunkt, der sich auf sich selbst bezieht, vor jeder Beziehung zum Anderen.",
        22:   "Präsenz ist die Artikulation von Sein und Subjekt: etwas ist präsent, wenn sein Sein sich einem Subjekt manifestiert, das es wahrnimmt.",
        33:   "Norm ist die Artikulation von Differenz und Subjekt: eine Norm ist eine Unterscheidung, die ein Subjekt als verbindliche Regel für sich selbst oder andere setzt.",
        55:   "Recht ist die Artikulation von Verhältnis und Subjekt: ein Recht ist eine Beziehung, die ein Subjekt als legitim und für andere verbindlich begründet.",
        77:   "Freiheit ist die Artikulation von Orientierung und Subjekt: Freiheit ist die Macht eines Subjekts, sein Handeln selbst auf ein gewähltes Ziel auszurichten.",
        66:   "Identität ist die Artikulation von Sein, Differenz und Subjekt: ein Subjekt hat Identität, wenn es sich stabil von dem unterscheidet, was es nicht ist.",
        110:  "Wert ist die Artikulation von Sein, Verhältnis und Subjekt: ein Wert ist eine Beziehung, die ein Subjekt zwischen zwei Wesen begründet, indem es das eine als Maß des anderen einsetzt.",
        154:  "Projekt ist die Artikulation von Sein, Orientierung und Subjekt: ein Projekt ist ein Sein, das ein Subjekt auf ein frei gewähltes Ziel ausrichtet.",
        165:  "Urteil ist die Artikulation von Differenz, Verhältnis und Subjekt: ein Urteil ist die Messung einer Differenz durch ein Subjekt nach einem normativen Maßstab.",
        231:  "Widerstand ist die Artikulation von Differenz, Orientierung und Subjekt: ein Subjekt leistet Widerstand, wenn es seiner eigenen Richtung gegen eine widersprechende äußere Differenz entgegensetzt.",
        385:  "Sinn ist die Artikulation von Verhältnis, Orientierung und Subjekt: Sinn ist ein Verhältnis, das ein Subjekt auf eine ihm eigene und irreduzible Bedeutung ausrichtet.",
        330:  "Sprache ist die Artikulation von Sein, Differenz, Verhältnis und Subjekt: eine Sprache ist ein System, in dem ein Subjekt seine Differenzen zu bedeutungstragenden Beziehungen strukturiert.",
        462:  "Erzählung ist die Artikulation von Sein, Differenz, Orientierung und Subjekt: eine Erzählung ist die Organisation der Differenzen eines Subjekts in einem gerichteten zeitlichen Rahmen.",
        770:  "Würde ist die Artikulation von Sein, Verhältnis, Orientierung und Subjekt: Würde ist die gerichtete Beziehung, die ein Wesen mit sich selbst unterhält und die seinen eigenen, jeder äußeren Bewertung irreduziblen Wert begründet.",
        1155: "Gedächtnis ist die Artikulation von Differenz, Verhältnis, Orientierung und Subjekt: Gedächtnis ist die Aufbewahrung geordneter Differenzen durch ein Subjekt in einer auf die Gegenwart gerichteten Dauer.",
        2310: "Bewusstsein ist die Artikulation von Sein, Differenz, Verhältnis, Orientierung und Subjekt: Bewusstsein ist totale subjektive Integration — ein Subjekt, das Sein, Differenzen, Beziehungen und Orientierungen in eine einheitliche und reflexive Erfahrung integriert.",
    },
    "es": {
        11:   "El sujeto es el observador irreductible: el punto de referencia que se refiere a sí mismo, anterior a toda relación con el otro.",
        22:   "La presencia es la articulación del ser y el sujeto: algo es presente cuando su ser se manifiesta a un sujeto que lo percibe.",
        33:   "La norma es la articulación de la diferencia y el sujeto: una norma es una distinción establecida por un sujeto como regla obligatoria para sí mismo o para otros.",
        55:   "El derecho es la articulación de la razón y el sujeto: un derecho es una relación establecida por un sujeto como legítima y vinculante para los demás.",
        77:   "La libertad es la articulación de la orientación y el sujeto: la libertad es el poder que tiene un sujeto para orientar su propia acción hacia un objetivo que ha elegido.",
        66:   "La identidad es la articulación del ser, la diferencia y el sujeto: un sujeto tiene identidad cuando se distingue establemente de lo que no es.",
        110:  "El valor es la articulación del ser, la razón y el sujeto: un valor es una relación establecida por un sujeto entre dos seres, instituyendo uno como medida del otro.",
        154:  "El proyecto es la articulación del ser, la orientación y el sujeto: un proyecto es un ser orientado por un sujeto hacia un fin libremente elegido.",
        165:  "El juicio es la articulación de la diferencia, la razón y el sujeto: un juicio es la medición de una diferencia por un sujeto según un estándar normativo.",
        231:  "La resistencia es la articulación de la diferencia, la orientación y el sujeto: un sujeto resiste cuando opone su propia dirección a una diferencia externa que la contradice.",
        385:  "El sentido es la articulación de la razón, la orientación y el sujeto: el sentido es una razón orientada por un sujeto hacia un significado que le es propio e irreductible.",
        330:  "El lenguaje es la articulación del ser, la diferencia, la razón y el sujeto: un lenguaje es un sistema en el que un sujeto estructura sus diferencias en relaciones portadoras de sentido.",
        462:  "El relato es la articulación del ser, la diferencia, la orientación y el sujeto: un relato es la organización por un sujeto de sus diferencias en un marco temporal orientado.",
        770:  "La dignidad es la articulación del ser, la razón, la orientación y el sujeto: la dignidad es la relación orientada que un ser mantiene consigo mismo, que funda su propio valor irreductible a cualquier apreciación externa.",
        1155: "La memoria es la articulación de la diferencia, la razón, la orientación y el sujeto: la memoria es la retención por un sujeto de diferencias ordenadas en una duración orientada hacia el presente.",
        2310: "La consciencia es la articulación del ser, la diferencia, la razón, la orientación y el sujeto: la consciencia es la integración subjetiva total — un sujeto que integra su ser, diferencias, relaciones y orientaciones en una experiencia unificada y reflexiva.",
    },
    "zh": {
        11:   "主体是不可还原的观察者：在任何与他者的关系之前，以自身为参照点与自身发生关系。",
        22:   "在场是存在与主体的结合：当某物的存在向感知它的主体显现时，它便在场。",
        33:   "规范是差异与主体的结合：规范是主体为自身或他人设立的作为强制性规则的区别。",
        55:   "权利是比率与主体的结合：权利是主体确立的、对他人具有合法约束力的关系。",
        77:   "自由是方向与主体的结合：自由是主体将其行动自我导向其所选择目标的能力。",
        66:   "同一性是存在、差异与主体的结合：当主体将自身稳定地区别于其所不是的东西时，它具有同一性。",
        110:  "价值是存在、比率与主体的结合：价值是主体在两个存在之间建立的关系，以一者为另一者的尺度。",
        154:  "计划是存在、方向与主体的结合：计划是主体将其存在导向其自由选择的目的。",
        165:  "判断是差异、比率与主体的结合：判断是主体依据规范标准对差异的测量。",
        231:  "抵抗是差异、方向与主体的结合：当主体以自身方向对抗与之矛盾的外部差异时，它在抵抗。",
        385:  "意义是比率、方向与主体的结合：意义是主体将关系朝向其固有且不可还原的意涵所进行的定向。",
        330:  "语言是存在、差异、比率与主体的结合：语言是一种系统，在其中主体将差异结构为承载意义的关系。",
        462:  "叙事是存在、差异、方向与主体的结合：叙事是主体将其差异在定向时间框架中的组织。",
        770:  "尊严是存在、比率、方向与主体的结合：尊严是存在者与自身维持的定向关系，它奠定其固有价值，不可还原为任何外部评价。",
        1155: "记忆是差异、比率、方向与主体的结合：记忆是主体对有序差异在朝向当下的定向时间中的保留。",
        2310: "意识是存在、差异、比率、方向与主体的结合：意识是总体主体性整合——主体将其存在、差异、关系与方向整合为统一的反思性经验。",
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# Fonctions utilitaires SUJET
# ══════════════════════════════════════════════════════════════════════════════

def is_subject_molecule(mol_id: int) -> bool:
    """Vrai si mol_id appartient à la couche SUJET (contient le facteur 11)."""
    return mol_id in SUJET_ATOMS


def atoms_in_5(mol_id: int) -> frozenset[int]:
    """
    Retourne les primes d'une molécule — couche 5 atomes.

    Fonctionne pour les molécules originales ({2,3,5,7}) ET les molécules SUJET.
    """
    if mol_id in SUJET_ATOMS:
        return SUJET_ATOMS[mol_id]
    # Molécules originales : décomposition directe
    primes: set[int] = set()
    remaining = mol_id
    for p in (2, 3, 5, 7):
        if remaining % p == 0:
            remaining //= p
            primes.add(p)
    return frozenset(primes) if remaining == 1 else frozenset()


def _is_architectural_5(mol_id: int) -> bool:
    """
    Règle architecturale étendue (§80A + §82) :
        - n_atomes ≥ 4          → architectural → définition
        - n_atomes = 3, RAPPORT(5) ET ORIENT(7) présents → architectural
        Architecturales SUJET : SENS(385), LANGAGE(330), RÉCIT(462), DIGNITÉ(770),
                                 MÉMOIRE(1155), CONSCIENCE(2310)
    """
    primes = atoms_in_5(mol_id)
    n = len(primes)
    return n >= 4 or (n == 3 and _RAPPORT_PRIME in primes and _ORIENT_PRIME in primes)


# Table de types pour toutes les molécules (4+5 atomes)
_ALL_MOL_IDS_5 = [2,3,5,7,6,10,14,15,21,35,30,42,70,105,210] + SUJET_MOL_IDS
MOL_TYPES_5: dict[int, str] = {
    m: ("def" if _is_architectural_5(m) else "kernel")
    for m in _ALL_MOL_IDS_5
}


def _jaccard_5(a: int, b: int) -> float:
    """Jaccard sur les primes de deux molécules (couche 5 atomes)."""
    pa = atoms_in_5(a)
    pb = atoms_in_5(b)
    if not pa and not pb:
        return 1.0
    return len(pa & pb) / len(pa | pb) if (pa | pb) else 0.0


# ══════════════════════════════════════════════════════════════════════════════
# Synthétiseur étendu (§82) — couche 5 atomes
# ══════════════════════════════════════════════════════════════════════════════

# Connecteurs Jaccard-aware pour SUJET molecules (même que §80A)
_CONNECTORS_5: dict[str, dict[str, str]] = {
    "fr": {"temporal": "de sorte que", "structural": "en même temps que",
           "additive": "et", "final_3": "si bien que"},
    "en": {"temporal": "so that", "structural": "while",
           "additive": "and", "final_3": "such that"},
    "de": {"temporal": "sodass", "structural": "wobei",
           "additive": "und", "final_3": "sodass schließlich"},
    "es": {"temporal": "de manera que", "structural": "al tiempo que",
           "additive": "y", "final_3": "de modo que"},
    "zh": {"temporal": "从而", "structural": "同时",
           "additive": "并且", "final_3": "使得"},
}


def _kernel_of(mol_id: int, lang: str) -> str:
    """Récupère le noyau d'une molécule — couche 4 ou 5 atomes."""
    if mol_id in SUJET_ATOMS:
        return KERNELS_SUJET[lang][mol_id]
    return KERNELS[lang][mol_id]


def _def_of(mol_id: int, lang: str) -> str:
    """Récupère la définition d'une molécule — couche 4 ou 5 atomes."""
    if mol_id in SUJET_ATOMS:
        return DEFINITIONS_SUJET[lang][mol_id]
    return DEFINITIONS[lang][mol_id]


def _choose_connector_5(mol_a: int, mol_b: int, lang: str,
                         is_final: bool = False, n_total: int = 2) -> str:
    conns = _CONNECTORS_5[lang]
    if is_final and n_total == 3:
        return conns["final_3"]
    pa = atoms_in_5(mol_a)
    pb = atoms_in_5(mol_b)
    if _ORIENT_PRIME in pa or _ORIENT_PRIME in pb:
        return conns["temporal"]
    j = _jaccard_5(mol_a, mol_b)
    if j >= 0.40:
        return conns["structural"]
    return conns["additive"]


class NipadaExtendedSynthesizer:
    """
    §82 — Synthétiseur étendu nipada (couche 5 atomes : ÊTRE/DIFF/RAPP/ORIENT/SUJET).

    Gère les molécules des couches 4 et 5 indifféremment.
    Applique la règle adaptative §81 étendue pour sélectionner kernel vs définition.

    Usage :
        synth = NipadaExtendedSynthesizer()
        # DUDH_1a re-encodée avec SUJET molecules
        text = synth.synthesize([770, 77, 55], lang="fr")
        # → "La dignité est le rapport orienté qui fonde la valeur propre d'un être…
        #    de sorte qu'un sujet choisit librement la direction de son action,
        #    si bien qu'un sujet établit une relation comme droit ou devoir."
    """

    def synthesize(self, mol_ids: list[int], lang: str) -> str:
        if not mol_ids:
            return ""
        if lang not in KERNELS_SUJET:
            raise ValueError(f"Langue inconnue: {lang!r}")

        types = [MOL_TYPES_5.get(m, "kernel") for m in mol_ids]

        if all(t == "kernel" for t in types):
            return self._kernel_structured(mol_ids, lang)
        if all(t == "def" for t in types):
            return self._concat_defs(mol_ids, lang)
        return self._hybrid(mol_ids, types, lang)

    def _concat_defs(self, mol_ids: list[int], lang: str) -> str:
        parts = [_def_of(m, lang).rstrip(".。") for m in mol_ids]
        sep = " | "
        result = sep.join(parts)
        if lang == "zh":
            return result + "。"
        return result[0].upper() + result[1:] + "."

    def _kernel_structured(self, mol_ids: list[int], lang: str) -> str:
        parts = [_kernel_of(m, lang) for m in mol_ids]
        n = len(parts)
        if n == 0:
            return ""
        if n == 1:
            t = parts[0]
            return (t + "。") if lang == "zh" else (t[0].upper() + t[1:] + ".")
        if lang == "zh":
            result = parts[0]
            for i in range(1, n):
                conn = _choose_connector_5(mol_ids[i-1], mol_ids[i], lang,
                                            is_final=(i == n-1 and n == 3), n_total=n)
                result += conn + parts[i]
            return result + "。"
        if n == 2:
            conn = _choose_connector_5(mol_ids[0], mol_ids[1], lang)
            r = f"{parts[0]}, {conn} {parts[1]}"
            return r[0].upper() + r[1:] + "."
        if n == 3:
            c01 = _choose_connector_5(mol_ids[0], mol_ids[1], lang)
            c12 = _choose_connector_5(mol_ids[1], mol_ids[2], lang,
                                       is_final=True, n_total=3)
            r = f"{parts[0]}, {c01} {parts[1]}, {c12} {parts[2]}"
            return r[0].upper() + r[1:] + "."
        tokens = [parts[0]]
        for i in range(1, n):
            c = _choose_connector_5(mol_ids[i-1], mol_ids[i], lang,
                                     is_final=(i == n-1), n_total=n)
            tokens.append(f", {c} {parts[i]}")
        r = "".join(tokens)
        return r[0].upper() + r[1:] + "."

    def _hybrid(self, mol_ids: list[int], types: list[str], lang: str) -> str:
        """Assemblage hybride (même logique que NipadaAdaptiveSynthesizer._hybrid)."""
        # Construire les runs
        runs: list[tuple[str, list[int]]] = []
        cur_type = types[0]
        cur_run  = [mol_ids[0]]
        for m, t in zip(mol_ids[1:], types[1:]):
            if t == cur_type:
                cur_run.append(m)
            else:
                runs.append((cur_type, cur_run))
                cur_type, cur_run = t, [m]
        runs.append((cur_type, cur_run))

        # Générer chaque run
        parts: list[str] = []
        for run_type, run_mols in runs:
            if run_type == "kernel":
                text = self._kernel_structured(run_mols, lang).rstrip(".。")
            else:
                texts = [_def_of(m, lang).rstrip(".。") for m in run_mols]
                text = " | ".join(texts)
            parts.append(text)

        cross = _CROSS_CONNECTORS[lang]
        if lang == "zh":
            result = cross.join(parts) + "。"
        else:
            result = f" {cross} ".join(parts)
            result = result[0].upper() + result[1:] + "."
        return result
