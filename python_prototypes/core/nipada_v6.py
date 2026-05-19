"""
nipada_v6.py — 6e atome TEMPS(13) + corrections kernels (§87/§88/§89)
======================================================================

Motivation (§86 lacunes critiques) :
    §87 — NARRATION alignment=0.042 : la dimension temporelle est absente du
          système à 5 atomes. RÉCIT(462)=2×3×7×11 produit des textes agentifs,
          pas chronologiques. Solution : TEMPS(13) comme 6e prime.

    §88 — QUESTION accuracy=0.0% : JUGEMENT(165)=3×5×11 est sémantiquement
          trop proche d'ORDRE. Solution : INTERROGATION(143)=11×13 — molecule
          qui encode la suspension interrogative (SUJET qui s'arrête dans le TEMPS).

    §89 — Pont sémantique nipada↔naturel : kernels calibrés pour être plus
          proches du registre naturel (temporal pour narration, 1re personne
          réflexive pour introspection, suspendu pour question).

6e prime : TEMPS = 13
======================
Avec {2,3,5,7,11,13}, 63 molécules non-vides (2^6 - 1).
Les 32 nouvelles molécules contiennent le facteur 13.

Molécules TEMPS sélectionnées :
    13    TEMPS           {13}
    26    ÉVOLUTION       {2, 13}        — ÊTRE×TEMPS
    39    CHANGEMENT      {3, 13}        — DIFFÉRENCE×TEMPS
    65    DURÉE           {5, 13}        — RAPPORT×TEMPS
    91    TRAJECTOIRE     {7, 13}        — ORIENTATION×TEMPS
   143    INTERROGATION   {11, 13}       — SUJET×TEMPS  ← clé §88 QUESTION
    78    DEVENIR         {2, 3, 13}     — ÊTRE×DIFFÉRENCE×TEMPS
   130    PROCESSUS       {2, 5, 13}     — ÊTRE×RAPPORT×TEMPS
   182    AVANCEMENT      {2, 7, 13}     — ÊTRE×ORIENTATION×TEMPS
   195    TRANSITION      {3, 5, 13}     — DIFFÉRENCE×RAPPORT×TEMPS
   273    SUCCESSION      {3, 7, 13}     — DIFFÉRENCE×ORIENTATION×TEMPS  ← narration
   286    PRÉSENCE_T      {2, 11, 13}    — ÊTRE×SUJET×TEMPS
   429    QUESTIONNEMENT  {3, 11, 13}    — DIFFÉRENCE×SUJET×TEMPS
   455    SÉQUENCE        {5, 7, 13}     — RAPPORT×ORIENTATION×TEMPS
   715    DÉLIBÉRATION    {5, 11, 13}    — RAPPORT×SUJET×TEMPS
  1001    DÉCISION        {7, 11, 13}    — ORIENTATION×SUJET×TEMPS

Modes V6 (MODES_V6) :
    "description"  : [2, 5, 3]          — inchangé §82
    "définition"   : [385, 66]           — inchangé §82
    "proclamation" : [33, 55, 77]        — inchangé §82
    "question"     : [143, 165, 11]      — §88 : INTERROGATION(11×13) en tête
    "ordre"        : [154, 231]          — inchangé §82
    "narration"    : [13, 78, 273]       — §87 : TEMPS+DEVENIR+SUCCESSION
    "introspection": [2310, 22, 26]      — §89 : +ÉVOLUTION(2×13) pont naturel
"""

from __future__ import annotations

from src.core.nipada_subject import (
    NipadaExtendedSynthesizer,
    KERNELS_SUJET, DEFINITIONS_SUJET, SUJET_ATOMS,
    atoms_in_5, _is_architectural_5, MOL_TYPES_5,
    _kernel_of, _def_of, _choose_connector_5, _CONNECTORS_5,
    SUJET_MOL_IDS,
)
from src.core.nipada_synthesizer import (
    KERNELS, DEFINITIONS,
    _ORIENT_PRIME, _RAPPORT_PRIME, _CROSS_CONNECTORS,
)

# ══════════════════════════════════════════════════════════════════════════════
# Constantes — 6e prime
# ══════════════════════════════════════════════════════════════════════════════

TEMPS_PRIME = 13

# Décomposition prime des molécules TEMPS (multiples de 13 seulement)
TEMPS_ATOMS: dict[int, frozenset[int]] = {
    13:   frozenset({13}),
    26:   frozenset({2, 13}),
    39:   frozenset({3, 13}),
    65:   frozenset({5, 13}),
    91:   frozenset({7, 13}),
    143:  frozenset({11, 13}),
    78:   frozenset({2, 3, 13}),
    130:  frozenset({2, 5, 13}),
    182:  frozenset({2, 7, 13}),
    195:  frozenset({3, 5, 13}),
    273:  frozenset({3, 7, 13}),
    286:  frozenset({2, 11, 13}),
    429:  frozenset({3, 11, 13}),
    455:  frozenset({5, 7, 13}),
    715:  frozenset({5, 11, 13}),
    1001: frozenset({7, 11, 13}),
}

TEMPS_MOL_IDS = list(TEMPS_ATOMS.keys())

TEMPS_MOL_NAMES: dict[str, dict[int, str]] = {
    "fr": {
        13:   "TEMPS",         26:   "ÉVOLUTION",    39:   "CHANGEMENT",
        65:   "DURÉE",         91:   "TRAJECTOIRE",  143:  "INTERROGATION",
        78:   "DEVENIR",       130:  "PROCESSUS",    182:  "AVANCEMENT",
        195:  "TRANSITION",    273:  "SUCCESSION",   286:  "PRÉSENCE_T",
        429:  "QUESTIONNEMENT",455:  "SÉQUENCE",     715:  "DÉLIBÉRATION",
        1001: "DÉCISION",
    },
    "en": {
        13:   "TIME",          26:   "EVOLUTION",    39:   "CHANGE",
        65:   "DURATION",      91:   "TRAJECTORY",   143:  "INTERROGATION",
        78:   "BECOMING",      130:  "PROCESS",      182:  "ADVANCEMENT",
        195:  "TRANSITION",    273:  "SUCCESSION",   286:  "TEMPORAL_PRESENCE",
        429:  "QUESTIONING",   455:  "SEQUENCE",     715:  "DELIBERATION",
        1001: "DECISION",
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# Modes V6 (§87–§89 corrections)
# ══════════════════════════════════════════════════════════════════════════════

MODES_V6: dict[str, list[int]] = {
    "description":   [2, 5, 3],        # ÊTRE×RAPPORT×DIFFÉRENCE — §82 inchangé
    "définition":    [385, 66],         # SENS+IDENTITÉ — §82 inchangé
    "proclamation":  [33, 55, 77],      # NORME×DROIT×LIBERTÉ — §82 inchangé
    "question":      [143, 165, 11],    # §88 : INTERROGATION(11×13) en tête
    "ordre":         [154, 231],        # PROJET×RÉSISTANCE — §82 inchangé
    "narration":     [13, 78, 273],     # §87 : TEMPS+DEVENIR(2×3×13)+SUCCESSION(3×7×13)
    "introspection": [2310, 22, 26],    # §89 : CONSCIENCE+PRÉSENCE+ÉVOLUTION(2×13)
}

# ══════════════════════════════════════════════════════════════════════════════
# Noyaux sémantiques TEMPS — §89 : calibrés pour le registre naturel
# ══════════════════════════════════════════════════════════════════════════════

KERNELS_V6: dict[str, dict[int, str]] = {
    "fr": {
        # — narration —
        13:   "des événements se succèdent dans l'ordre du temps : d'abord, puis, enfin",
        78:   "ce qui était a changé et est devenu autre chose au fil du temps",
        273:  "des états distincts se sont succédé dans un ordre orienté du passé vers le présent",
        # — question —
        143:  "un sujet se demande et interroge ce qu'il ne comprend pas encore",
        429:  "un sujet pose une question sur une différence dont la réponse lui est inconnue",
        # — introspection —
        26:   "un être se retrouve différent en se retournant sur lui-même à travers le temps",
        286:  "une présence se manifeste à un sujet qui s'observe lui-même dans la durée",
        # — autres molécules temporelles —
        39:   "une différence se creuse progressivement entre deux états au fil du temps",
        65:   "un rapport persiste et se transforme dans la durée à travers les changements",
        91:   "une direction se poursuit dans le temps à travers une série d'étapes successives",
        130:  "un processus déploie un être dans ses différentes phases au fil du temps",
        182:  "un être avance dans une direction en passant par des états successifs dans le temps",
        195:  "un rapport différent s'établit par la transition progressive d'un état à un autre",
        455:  "une séquence ordonne des rapports distincts dans une progression orientée dans le temps",
        715:  "un sujet délibère entre différents rapports possibles selon leur durée dans le temps",
        1001: "un sujet oriente sa décision en tenant compte de la trajectoire temporelle",
    },
    "en": {
        # — narration —
        13:   "events follow one another in the order of time: first, then, finally",
        78:   "what was has changed and become something else in the course of time",
        273:  "distinct states followed one another in a directed order from past to present",
        # — question —
        143:  "a subject wonders and asks what it does not yet understand",
        429:  "a subject raises a question about a difference whose answer is unknown",
        # — introspection —
        26:   "a being finds itself changed upon turning back to look at itself through time",
        286:  "a presence manifests to a subject who observes itself across time",
        # — autres —
        39:   "a difference gradually deepens between two states over the course of time",
        65:   "a relation persists and transforms in duration through successive changes",
        91:   "a direction is sustained through time across a series of successive steps",
        130:  "a process unfolds a being through its successive phases over time",
        182:  "a being advances in a direction by passing through successive states in time",
        195:  "a different relation is established through the gradual transition from one state to another",
        455:  "a sequence orders distinct relations in a directed progression through time",
        715:  "a subject deliberates between possible relations according to their duration in time",
        1001: "a subject orients its decision by taking into account the temporal trajectory",
    },
    "de": {
        13:   "Ereignisse folgen aufeinander in der Ordnung der Zeit: zuerst, dann, schließlich",
        78:   "was war, hat sich verändert und ist im Laufe der Zeit zu etwas anderem geworden",
        273:  "verschiedene Zustände folgten in gerichteter Ordnung aufeinander, vom Vergangenen zum Gegenwärtigen",
        143:  "ein Subjekt fragt sich und stellt in Frage, was es noch nicht versteht",
        429:  "ein Subjekt stellt eine Frage über eine Differenz, deren Antwort ihm unbekannt ist",
        26:   "ein Wesen findet sich verändert, wenn es sich in der Zeit auf sich selbst zurückwendet",
        286:  "eine Präsenz manifestiert sich einem Subjekt, das sich selbst im Laufe der Zeit beobachtet",
        39:   "eine Differenz vertieft sich allmählich zwischen zwei Zuständen im Laufe der Zeit",
        65:   "ein Verhältnis hält an und wandelt sich in der Dauer durch aufeinanderfolgende Veränderungen",
        91:   "eine Richtung setzt sich durch die Zeit über eine Reihe aufeinanderfolgender Schritte fort",
        130:  "ein Prozess entfaltet ein Sein durch seine aufeinanderfolgenden Phasen im Laufe der Zeit",
        182:  "ein Sein schreitet in einer Richtung voran, indem es im Laufe der Zeit aufeinanderfolgende Zustände durchläuft",
        195:  "ein anderes Verhältnis entsteht durch den allmählichen Übergang von einem Zustand zum anderen",
        455:  "eine Sequenz ordnet unterschiedliche Verhältnisse in einem gerichteten Fortschreiten durch die Zeit",
        715:  "ein Subjekt überlegt zwischen möglichen Verhältnissen entsprechend ihrer Dauer in der Zeit",
        1001: "ein Subjekt richtet seine Entscheidung aus, indem es die zeitliche Trajektorie berücksichtigt",
    },
    "es": {
        13:   "los eventos se suceden en el orden del tiempo: primero, luego, finalmente",
        78:   "lo que era ha cambiado y se ha convertido en otra cosa con el paso del tiempo",
        273:  "estados distintos se sucedieron en un orden orientado del pasado hacia el presente",
        143:  "un sujeto se pregunta e interroga lo que aún no comprende",
        429:  "un sujeto plantea una pregunta sobre una diferencia cuya respuesta desconoce",
        26:   "un ser se encuentra diferente al volverse sobre sí mismo a través del tiempo",
        286:  "una presencia se manifiesta a un sujeto que se observa a sí mismo a lo largo del tiempo",
        39:   "una diferencia se profundiza gradualmente entre dos estados con el paso del tiempo",
        65:   "una relación persiste y se transforma en la duración a través de los cambios sucesivos",
        91:   "una dirección se mantiene en el tiempo a través de una serie de etapas sucesivas",
        130:  "un proceso despliega un ser a través de sus fases sucesivas en el tiempo",
        182:  "un ser avanza en una dirección pasando por estados sucesivos en el tiempo",
        195:  "una relación diferente se establece mediante la transición gradual de un estado a otro",
        455:  "una secuencia ordena distintas relaciones en una progresión orientada a través del tiempo",
        715:  "un sujeto delibera entre relaciones posibles según su duración en el tiempo",
        1001: "un sujeto orienta su decisión teniendo en cuenta la trayectoria temporal",
    },
    "zh": {
        13:   "事件在时间秩序中相继发生：先是、然后、最终",
        78:   "曾经所是的已经改变，随着时间的流逝变成了另一种东西",
        273:  "不同的状态按照从过去到现在的定向顺序相继出现",
        143:  "一个主体自我追问，质疑其尚未理解的事物",
        429:  "一个主体就一个他不知道答案的差异提出疑问",
        26:   "一个存在者回望自身时，发现自己随时间而改变",
        286:  "一种在场向一个自我观察随时间变化的主体显现",
        39:   "两种状态之间的差异随着时间的流逝逐渐加深",
        65:   "一种关系在持续时间内通过相继的变化中持续并转变",
        91:   "一个方向通过一系列相继的步骤在时间中持续延伸",
        130:  "一个过程随时间在其相继的各个阶段中展开存在",
        182:  "一个存在者在时间中通过相继的状态沿着一个方向前进",
        195:  "通过从一种状态到另一种状态的渐进过渡，建立起不同的关系",
        455:  "一个序列在时间中按定向进展将不同关系排序",
        715:  "一个主体根据不同关系在时间中的持续时间在它们之间加以考量",
        1001: "一个主体通过考虑时间轨迹来定向其决定",
    },
}

# Définitions architecturales V6 (molécules avec n_atomes ≥ 4 incluant TEMPS)
# Pour l'instant, toutes les molécules TEMPS listées ont ≤ 3 atomes → kernel type.
DEFINITIONS_V6: dict[str, dict[int, str]] = {la: {} for la in ["fr", "en", "de", "es", "zh"]}

# ══════════════════════════════════════════════════════════════════════════════
# Utilitaires V6
# ══════════════════════════════════════════════════════════════════════════════

def is_temps_molecule(mol_id: int) -> bool:
    """Vrai si mol_id est une molécule TEMPS (contient le facteur 13)."""
    return mol_id in TEMPS_ATOMS


def atoms_in_6(mol_id: int) -> frozenset[int]:
    """Décomposition prime d'une molécule — couche 6 atomes."""
    if mol_id in TEMPS_ATOMS:
        return TEMPS_ATOMS[mol_id]
    return atoms_in_5(mol_id)


def _is_architectural_6(mol_id: int) -> bool:
    """
    Règle architecturale étendue couche 6 atomes :
        - n_atomes ≥ 4          → architectural → définition
        - n_atomes = 3, RAPPORT(5) ET ORIENT(7) présents → architectural
    """
    if mol_id in TEMPS_ATOMS:
        primes = TEMPS_ATOMS[mol_id]
        n = len(primes)
        return n >= 4 or (n == 3 and _RAPPORT_PRIME in primes and _ORIENT_PRIME in primes)
    return _is_architectural_5(mol_id)


# Table de types pour toutes les molécules (4+5+6 atomes)
_ALL_MOL_IDS_6 = list(MOL_TYPES_5.keys()) + TEMPS_MOL_IDS
MOL_TYPES_6: dict[int, str] = {
    m: ("def" if _is_architectural_6(m) else "kernel")
    for m in _ALL_MOL_IDS_6
}


def _jaccard_6(a: int, b: int) -> float:
    """Jaccard sur les primes de deux molécules (couche 6 atomes)."""
    pa = atoms_in_6(a)
    pb = atoms_in_6(b)
    if not pa and not pb:
        return 1.0
    return len(pa & pb) / len(pa | pb) if (pa | pb) else 0.0


def _kernel_of_v6(mol_id: int, lang: str) -> str:
    """Récupère le noyau d'une molécule — V6 en priorité, puis §82, puis §81."""
    if mol_id in KERNELS_V6.get(lang, {}):
        return KERNELS_V6[lang][mol_id]
    return _kernel_of(mol_id, lang)


def _def_of_v6(mol_id: int, lang: str) -> str:
    """Récupère la définition d'une molécule — V6 en priorité, puis §82."""
    if mol_id in DEFINITIONS_V6.get(lang, {}):
        return DEFINITIONS_V6[lang][mol_id]
    return _def_of(mol_id, lang)


def _choose_connector_6(mol_a: int, mol_b: int, lang: str,
                          is_final: bool = False, n_total: int = 2) -> str:
    conns = _CONNECTORS_5[lang]
    if is_final and n_total == 3:
        return conns["final_3"]
    pa = atoms_in_6(mol_a)
    pb = atoms_in_6(mol_b)
    if _ORIENT_PRIME in pa or _ORIENT_PRIME in pb or TEMPS_PRIME in pa or TEMPS_PRIME in pb:
        return conns["temporal"]
    j = _jaccard_6(mol_a, mol_b)
    if j >= 0.40:
        return conns["structural"]
    return conns["additive"]


# ══════════════════════════════════════════════════════════════════════════════
# Synthétiseur V6 (§87–§89) — couche 6 atomes
# ══════════════════════════════════════════════════════════════════════════════

class NipadaV6Synthesizer(NipadaExtendedSynthesizer):
    """
    §87–§89 — Synthétiseur nipada V6 (6 atomes : ÊTRE/DIFF/RAPP/ORIENT/SUJET/TEMPS).

    Étend NipadaExtendedSynthesizer (§82) en ajoutant :
    - 16 nouvelles molécules TEMPS (multiples de 13)
    - Kernels calibrés sur le registre naturel (§89)
    - INTERROGATION(143) pour discriminer la question (§88)
    - TEMPS/DEVENIR/SUCCESSION pour la narration chronologique (§87)
    - ÉVOLUTION(26) pour l'introspection rétrospective (§89)

    Usage :
        synth = NipadaV6Synthesizer()
        # narration (§87)
        text = synth.synthesize([13, 78, 273], lang="fr")
        # question (§88)
        text = synth.synthesize([143, 165, 11], lang="fr")
    """

    def synthesize(self, mol_ids: list[int], lang: str) -> str:
        if not mol_ids:
            return ""
        valid_langs = set(KERNELS_V6.keys())
        if lang not in valid_langs:
            raise ValueError(f"Langue inconnue: {lang!r}")

        types = [MOL_TYPES_6.get(m, "kernel") for m in mol_ids]

        if all(t == "kernel" for t in types):
            return self._kernel_structured_v6(mol_ids, lang)
        if all(t == "def" for t in types):
            return self._concat_defs_v6(mol_ids, lang)
        return self._hybrid_v6(mol_ids, types, lang)

    def _concat_defs_v6(self, mol_ids: list[int], lang: str) -> str:
        parts = [_def_of_v6(m, lang).rstrip(".。") for m in mol_ids]
        sep = " | "
        result = sep.join(parts)
        if lang == "zh":
            return result + "。"
        return result[0].upper() + result[1:] + "."

    def _kernel_structured_v6(self, mol_ids: list[int], lang: str) -> str:
        parts = [_kernel_of_v6(m, lang) for m in mol_ids]
        n = len(parts)
        if n == 0:
            return ""
        if n == 1:
            t = parts[0]
            return (t + "。") if lang == "zh" else (t[0].upper() + t[1:] + ".")
        if lang == "zh":
            result = parts[0]
            for i in range(1, n):
                conn = _choose_connector_6(mol_ids[i-1], mol_ids[i], lang,
                                            is_final=(i == n-1 and n == 3), n_total=n)
                result += conn + parts[i]
            return result + "。"
        if n == 2:
            conn = _choose_connector_6(mol_ids[0], mol_ids[1], lang)
            r = f"{parts[0]}, {conn} {parts[1]}"
            return r[0].upper() + r[1:] + "."
        if n == 3:
            c01 = _choose_connector_6(mol_ids[0], mol_ids[1], lang)
            c12 = _choose_connector_6(mol_ids[1], mol_ids[2], lang,
                                       is_final=True, n_total=3)
            r = f"{parts[0]}, {c01} {parts[1]}, {c12} {parts[2]}"
            return r[0].upper() + r[1:] + "."
        tokens = [parts[0]]
        for i in range(1, n):
            c = _choose_connector_6(mol_ids[i-1], mol_ids[i], lang,
                                     is_final=(i == n-1), n_total=n)
            tokens.append(f", {c} {parts[i]}")
        r = "".join(tokens)
        return r[0].upper() + r[1:] + "."

    def _hybrid_v6(self, mol_ids: list[int], types: list[str], lang: str) -> str:
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

        parts: list[str] = []
        for run_type, run_mols in runs:
            if run_type == "kernel":
                text = self._kernel_structured_v6(run_mols, lang).rstrip(".。")
            else:
                texts = [_def_of_v6(m, lang).rstrip(".。") for m in run_mols]
                text = " | ".join(texts)
            parts.append(text)

        cross = _CROSS_CONNECTORS[lang]
        if lang == "zh":
            result = cross.join(parts) + "。"
        else:
            result = f" {cross} ".join(parts)
            result = result[0].upper() + result[1:] + "."
        return result
