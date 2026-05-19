"""
nipada_synthesizer.py — Décomposeur syntaxique inverse nipada (§80A)

Génère du texte naturel à partir d'un tuple de molécules nipada,
sans recourir à un Content-Addressed Store (CAS).

Trois stratégies de synthèse :
    - CONCAT_DEFS      : concaténation des phrases définitionnelles complètes (baseline §79)
    - KERNEL_FLAT      : noyaux sémantiques courts, séparés par virgule
    - KERNEL_STRUCTURED: noyaux courts + connecteurs contextuels (Jaccard-aware)

La stratégie KERNEL_STRUCTURED utilise la structure atomique des molécules pour
choisir le connecteur : temporal (ORIENTATION impliquée), structural (Jaccard ≥ 0.4),
ou additif (molécules indépendantes).

Usage :
    from src.core.nipada_synthesizer import NipadaSynthesizer
    synth = NipadaSynthesizer()
    text = synth.synthesize([30, 42, 70], lang="fr", strategy="kernel_structured")
    # → "un vivant existe, se différencie et maintient des relations, pour que
    #    quelque chose change de façon irréversible et orientée, de sorte qu'une
    #    intention structure l'être par un rapport orienté vers un but."
"""

from __future__ import annotations

from typing import Literal
from src.core.nipada_engine import atoms_in, product_to_mask

# ── Stratégies disponibles ────────────────────────────────────────────────────
Strategy = Literal["concat_defs", "kernel_flat", "kernel_structured"]

# ── Noyaux sémantiques — phrases courtes (8–14 mots) combinables ──────────────
# Conçus pour être grammaticalement autonomes et juxtaposables.
# Ne commencent pas par un article défini figé pour faciliter la combinaison.
KERNELS: dict[str, dict[int, str]] = {
    "fr": {
        2:   "quelque chose existe",
        3:   "deux choses se distinguent irréductiblement",
        5:   "une relation structurelle unit deux termes",
        7:   "une direction asymétrique oriente de la source vers le but",
        6:   "quelque chose s'affirme en se distinguant du non-être",
        10:  "des parties s'assemblent en une composition structurée",
        14:  "quelque chose devient en se dirigeant vers un but",
        15:  "une différence s'exprime et se mesure comme rapport",
        21:  "deux termes s'opposent selon une asymétrie directionnelle",
        35:  "un signe renvoie à son sens selon un rapport orienté",
        30:  "un vivant existe, se différencie et maintient des relations structurées",
        42:  "quelque chose change de façon irréversible et orientée",
        70:  "une intention structure l'être par un rapport orienté vers un but",
        105: "les moments se différencient et s'ordonnent dans une direction temporelle",
        210: "être, différence, rapport et orientation s'intègrent en un tout unifié",
    },
    "en": {
        2:   "something exists",
        3:   "two things are irreducibly distinct",
        5:   "a structural relation connects two terms",
        7:   "an asymmetric direction orients from source to goal",
        6:   "something asserts itself by distinguishing from non-being",
        10:  "parts assemble into a structured composition",
        14:  "something becomes by directing itself toward a goal",
        15:  "a difference is expressed and measured as a ratio",
        21:  "two terms oppose each other along a directional asymmetry",
        35:  "a sign refers to its meaning through an oriented ratio",
        30:  "a living thing exists, differentiates from its environment and maintains relations",
        42:  "something changes in an irreversible and directed way",
        70:  "an intention structures being through a relation oriented toward a goal",
        105: "moments differentiate and order themselves in a temporal direction",
        210: "being, difference, ratio and orientation integrate into a unified whole",
    },
    "de": {
        2:   "etwas existiert",
        3:   "zwei Dinge unterscheiden sich unauflöslich",
        5:   "eine strukturelle Beziehung verbindet zwei Terme",
        7:   "eine asymmetrische Richtung führt von der Quelle zum Ziel",
        6:   "etwas behauptet sich, indem es sich vom Nicht-Sein abhebt",
        10:  "Teile fügen sich zu einer strukturierten Komposition zusammen",
        14:  "etwas wird, indem es sich auf ein Ziel hin bewegt",
        15:  "eine Differenz wird als Verhältnis ausgedrückt und gemessen",
        21:  "zwei Terme stehen in einer gerichteten Asymmetrie gegenüber",
        35:  "ein Zeichen verweist durch ein gerichtetes Verhältnis auf seine Bedeutung",
        30:  "ein Lebewesen existiert, unterscheidet sich von seiner Umgebung und pflegt Beziehungen",
        42:  "etwas verändert sich auf irreversible und gerichtete Weise",
        70:  "eine Intention strukturiert das Sein durch ein auf ein Ziel gerichtetes Verhältnis",
        105: "Momente differenzieren sich und ordnen sich in eine zeitliche Richtung",
        210: "Sein, Differenz, Verhältnis und Orientierung integrieren sich zu einem vereinten Ganzen",
    },
    "es": {
        2:   "algo existe",
        3:   "dos cosas se distinguen irreductiblemente",
        5:   "una relación estructural une dos términos",
        7:   "una dirección asimétrica orienta de la fuente al objetivo",
        6:   "algo se afirma distinguiéndose del no-ser",
        10:  "partes se ensamblan en una composición estructurada",
        14:  "algo deviene dirigiéndose hacia un objetivo",
        15:  "una diferencia se expresa y mide como razón",
        21:  "dos términos se oponen según una asimetría direccional",
        35:  "un signo remite a su significado mediante una razón orientada",
        30:  "un ser vivo existe, se diferencia de su entorno y mantiene relaciones estructuradas",
        42:  "algo cambia de forma irreversible y orientada",
        70:  "una intención estructura el ser mediante una relación orientada hacia un objetivo",
        105: "los momentos se diferencian y se ordenan en una dirección temporal",
        210: "ser, diferencia, razón y orientación se integran en un todo unificado",
    },
    "zh": {
        2:   "某物存在",
        3:   "两物不可还原地相互区别",
        5:   "结构性关系连接两个项",
        7:   "不对称方向从源指向目标",
        6:   "某物通过区别于非存在而自我确立",
        10:  "各部分组合为有结构的整体",
        14:  "某物通过朝向目标而生成",
        15:  "差异被表达并测量为比率",
        21:  "两项沿方向性不对称相对立",
        35:  "符号通过有方向的比率指向其意义",
        30:  "生命体存在、与环境区分并维持结构性关系",
        42:  "某物以不可逆且有方向的方式改变",
        70:  "意图通过朝向目标的关系来结构存在",
        105: "时刻相互区分并在时间方向上排序",
        210: "存在、差异、比率与方向整合为统一整体",
    },
}

# ── Phrases définitionnelles complètes (baseline §79 / CONCAT_DEFS) ───────────
DEFINITIONS: dict[str, dict[int, str]] = {
    "fr": {
        2:   "L'être est le pur fait d'exister, antérieur à toute différence ou relation.",
        3:   "La différence est la distinction irréductible entre deux choses, antérieure à toute relation.",
        5:   "Le rapport est la relation structurelle entre deux termes, indépendante de toute orientation.",
        7:   "L'orientation est l'asymétrie directionnelle qui distingue l'avant de l'après, la source du but.",
        6:   "L'existence est l'articulation de l'être et de la différence : quelque chose existe quand son être se distingue du non-être.",
        10:  "La composition est l'articulation de l'être et du rapport : quelque chose est composé quand son être est structuré par une relation de parties.",
        14:  "Le devenir est l'articulation de l'être et de l'orientation : quelque chose devient quand son être est dirigé vers un but.",
        15:  "La mesure est l'articulation de la différence et du rapport : quelque chose est mesuré quand une différence est exprimée en rapport.",
        21:  "L'opposition est l'articulation de la différence et de l'orientation : deux choses s'opposent quand leur différence est directionnelle.",
        35:  "La référence est l'articulation du rapport et de l'orientation : une référence est un rapport orienté du signe vers le sens.",
        30:  "La vie est l'articulation de l'être, de la différence et du rapport : un vivant existe, se différencie de son milieu et entretient avec lui des relations structurées.",
        42:  "La transformation est l'articulation de l'être, de la différence et de l'orientation : quelque chose se transforme quand son être change de façon dirigée et irréversible.",
        70:  "L'intention est l'articulation de l'être, du rapport et de l'orientation : une intention est un être structuré par un rapport orienté vers un but.",
        105: "Le temps est l'articulation de la différence, du rapport et de l'orientation : le temps est la différence ordonnée entre des moments, structurée en rapport avec une direction.",
        210: "L'intégration est l'articulation de l'être, de la différence, du rapport et de l'orientation : le tout intégré rassemble les différences existantes en relations structurées et orientées.",
    },
    "en": {
        2:   "Being is the pure fact of existing, prior to any difference or relation.",
        3:   "Difference is the irreducible distinction between two things, prior to any relation.",
        5:   "Ratio is the structural relation between two terms, independent of direction.",
        7:   "Orientation is the directional asymmetry that distinguishes before from after, source from goal.",
        6:   "Existence is the articulation of being and difference: something exists when its being is distinguished from non-being.",
        10:  "Composition is the articulation of being and ratio: something is composed when its being is structured by a relation of parts.",
        14:  "Becoming is the articulation of being and orientation: something becomes when its being is directed toward a goal.",
        15:  "Measure is the articulation of difference and ratio: something is measured when a difference is expressed as a ratio.",
        21:  "Opposition is the articulation of difference and orientation: two things are opposed when their difference is directional and asymmetric.",
        35:  "Reference is the articulation of ratio and orientation: a reference is a ratio that has a direction, pointing from sign to meaning.",
        30:  "Life is the articulation of being, difference and ratio: a living thing exists, differentiates itself from its environment and maintains structural relations with it.",
        42:  "Transformation is the articulation of being, difference and orientation: something transforms when its being changes in a directed, irreversible way.",
        70:  "Intention is the articulation of being, ratio and orientation: an intention is a being structured by a relation that is oriented toward a goal.",
        105: "Time is the articulation of difference, ratio and orientation: time is the ordered difference between moments, structured as a ratio with a direction.",
        210: "Integration is the articulation of being, difference, ratio and orientation: the integrated whole brings together existing differences into structured and oriented relations.",
    },
    "de": {
        2:   "Sein ist die reine Tatsache zu existieren, vor jeder Differenz oder Beziehung.",
        3:   "Differenz ist die irreduzible Unterscheidung zwischen zwei Dingen, vor jeder Beziehung.",
        5:   "Verhältnis ist die strukturelle Beziehung zwischen zwei Termen, unabhängig von jeder Richtung.",
        7:   "Orientierung ist die gerichtete Asymmetrie, die Vorher von Nachher und Quelle von Ziel unterscheidet.",
        6:   "Existenz ist die Artikulation von Sein und Differenz: etwas existiert, wenn sein Sein von Nicht-Sein unterschieden wird.",
        10:  "Komposition ist die Artikulation von Sein und Verhältnis: etwas ist zusammengesetzt, wenn sein Sein durch ein Teile-Verhältnis strukturiert ist.",
        14:  "Werden ist die Artikulation von Sein und Orientierung: etwas wird, wenn sein Sein auf ein Ziel hin gerichtet ist.",
        15:  "Maß ist die Artikulation von Differenz und Verhältnis: etwas ist gemessen, wenn eine Differenz als Verhältnis ausgedrückt wird.",
        21:  "Gegensatz ist die Artikulation von Differenz und Orientierung: zwei Dinge stehen im Gegensatz, wenn ihre Differenz gerichtet und asymmetrisch ist.",
        35:  "Referenz ist die Artikulation von Verhältnis und Orientierung: eine Referenz ist ein Verhältnis, das gerichtet ist — vom Zeichen zur Bedeutung.",
        30:  "Leben ist die Artikulation von Sein, Differenz und Verhältnis: ein Lebewesen existiert, unterscheidet sich von seiner Umgebung und unterhält strukturelle Beziehungen mit ihr.",
        42:  "Transformation ist die Artikulation von Sein, Differenz und Orientierung: etwas wandelt sich, wenn sein Sein sich gerichtet und irreversibel verändert.",
        70:  "Intention ist die Artikulation von Sein, Verhältnis und Orientierung: eine Intention ist ein Sein, das durch ein auf ein Ziel gerichtetes Verhältnis strukturiert ist.",
        105: "Zeit ist die Artikulation von Differenz, Verhältnis und Orientierung: Zeit ist die geordnete Differenz zwischen Momenten, als Verhältnis mit einer Richtung strukturiert.",
        210: "Integration ist die Artikulation von Sein, Differenz, Verhältnis und Orientierung: das integrierte Ganze vereint bestehende Differenzen in strukturierten und gerichteten Beziehungen.",
    },
    "es": {
        2:   "El ser es el puro hecho de existir, anterior a toda diferencia o relación.",
        3:   "La diferencia es la distinción irreductible entre dos cosas, anterior a toda relación.",
        5:   "La razón es la relación estructural entre dos términos, independiente de cualquier orientación.",
        7:   "La orientación es la asimetría direccional que distingue el antes del después, la fuente del objetivo.",
        6:   "La existencia es la articulación del ser y la diferencia: algo existe cuando su ser se distingue del no-ser.",
        10:  "La composición es la articulación del ser y la razón: algo está compuesto cuando su ser está estructurado por una relación de partes.",
        14:  "El devenir es la articulación del ser y la orientación: algo deviene cuando su ser está dirigido hacia un objetivo.",
        15:  "La medida es la articulación de la diferencia y la razón: algo se mide cuando una diferencia se expresa como razón.",
        21:  "La oposición es la articulación de la diferencia y la orientación: dos cosas se oponen cuando su diferencia es direccional y asimétrica.",
        35:  "La referencia es la articulación de la razón y la orientación: una referencia es una razón orientada del signo hacia el significado.",
        30:  "La vida es la articulación del ser, la diferencia y la razón: un ser vivo existe, se diferencia de su entorno y mantiene relaciones estructurales con él.",
        42:  "La transformación es la articulación del ser, la diferencia y la orientación: algo se transforma cuando su ser cambia de manera dirigida e irreversible.",
        70:  "La intención es la articulación del ser, la razón y la orientación: una intención es un ser estructurado por una razón orientada hacia un objetivo.",
        105: "El tiempo es la articulación de la diferencia, la razón y la orientación: el tiempo es la diferencia ordenada entre momentos, estructurada como razón con una dirección.",
        210: "La integración es la articulación del ser, la diferencia, la razón y la orientación: el todo integrado reúne las diferencias existentes en relaciones estructuradas y orientadas.",
    },
    "zh": {
        2:   "存在是纯粹的事实，先于任何差异或关系。",
        3:   "差异是两事物之间不可还原的区别，先于任何关系。",
        5:   "比率是两个项之间的结构关系，独立于任何方向。",
        7:   "方向是区分前后、源与目标的不对称性。",
        6:   "存在性是存在与差异的结合：当某物的存在与非存在相区别时，它才存在。",
        10:  "组合是存在与比率的结合：当某物的存在由部分之间的关系所结构时，它是组合的。",
        14:  "生成是存在与方向的结合：当某物的存在指向目标时，它在生成中。",
        15:  "测量是差异与比率的结合：当差异以比率表达时，就产生了测量。",
        21:  "对立是差异与方向的结合：当两事物的差异具有方向性和不对称性时，它们相互对立。",
        35:  "指涉是比率与方向的结合：指涉是一个有方向的比率，从符号指向意义。",
        30:  "生命是存在、差异与比率的结合：生命体存在，与环境区别，并与之维持结构关系。",
        42:  "转化是存在、差异与方向的结合：当某物的存在以定向且不可逆的方式改变时，它在转化。",
        70:  "意图是存在、比率与方向的结合：意图是一种由指向目标的有向关系所结构的存在。",
        105: "时间是差异、比率与方向的结合：时间是时刻之间的有序差异，被结构为具有方向的比率。",
        210: "整合是存在、差异、比率与方向的结合：整合的整体将现有的差异汇聚成结构化的有向关系。",
    },
}

# ── Connecteurs contextuels par langue ───────────────────────────────────────
# Sélectionnés selon la structure atomique de la paire de molécules :
#   - temporal   : ORIENTATION (prime 7) présente dans l'une des deux molécules
#   - structural : Jaccard atomique ≥ 0.40 (molécules partagent plusieurs atomes)
#   - additive   : molécules indépendantes (Jaccard < 0.40, pas d'ORIENTATION)
#   - final_3    : connecteur final pour la 3e molécule d'un triplet
CONNECTORS: dict[str, dict[str, str]] = {
    "fr": {
        "temporal":   "de sorte que",
        "structural": "en même temps que",
        "additive":   "et",
        "final_3":    "si bien que",
    },
    "en": {
        "temporal":   "so that",
        "structural": "while",
        "additive":   "and",
        "final_3":    "such that",
    },
    "de": {
        "temporal":   "sodass",
        "structural": "wobei",
        "additive":   "und",
        "final_3":    "sodass schließlich",
    },
    "es": {
        "temporal":   "de manera que",
        "structural": "al tiempo que",
        "additive":   "y",
        "final_3":    "de modo que",
    },
    "zh": {
        "temporal":   "从而",
        "structural": "同时",
        "additive":   "并且",
        "final_3":    "使得",
    },
}

# Prime correspondant à ORIENTATION
_ORIENT_PRIME = 7


def _jaccard_atoms(mask_a: int, mask_b: int) -> float:
    """Jaccard sur les ensembles d'atomes (primes) de deux masques."""
    a = set(atoms_in(mask_a))
    b = set(atoms_in(mask_b))
    if not a and not b:
        return 1.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def _choose_connector(
    mol_a: int, mol_b: int, lang: str, is_final: bool = False, n_total: int = 2
) -> str:
    """
    Choisit le connecteur entre deux molécules en fonction de leur structure atomique.

    Priorité :
        1. Finalisation (is_final et n_total == 3) → final_3
        2. ORIENTATION présente → temporal
        3. Jaccard ≥ 0.40 → structural
        4. Sinon → additive
    """
    if is_final and n_total == 3:
        return CONNECTORS[lang]["final_3"]

    mask_a = product_to_mask(mol_a) or 0
    mask_b = product_to_mask(mol_b) or 0
    atoms_a = set(atoms_in(mask_a))
    atoms_b = set(atoms_in(mask_b))

    if _ORIENT_PRIME in atoms_a or _ORIENT_PRIME in atoms_b:
        return CONNECTORS[lang]["temporal"]

    j = _jaccard_atoms(mask_a, mask_b)
    if j >= 0.40:
        return CONNECTORS[lang]["structural"]

    return CONNECTORS[lang]["additive"]


class NipadaSynthesizer:
    """
    Décomposeur syntaxique inverse nipada.

    Génère du texte naturel depuis un tuple de molécules nipada selon trois stratégies :

    - ``concat_defs``      : concaténation des définitions complètes (baseline §79)
    - ``kernel_flat``      : noyaux courts séparés par une virgule (ou ，pour ZH)
    - ``kernel_structured``: noyaux courts + connecteurs Jaccard-aware

    La stratégie ``kernel_structured`` est la plus proche d'un vrai décomposeur :
    elle produit des phrases cohérentes dont le sens est mesurable par embedding.
    """

    STRATEGIES: tuple[str, ...] = ("concat_defs", "kernel_flat", "kernel_structured")

    def synthesize(
        self,
        mol_ids: list[int],
        lang: str,
        strategy: Strategy = "kernel_structured",
    ) -> str:
        """
        Génère un texte en `lang` à partir des molécules `mol_ids`.

        Args:
            mol_ids : liste d'IDs molécules (valeurs nipada : 2, 3, 5, 6, 7, 10…)
            lang    : code langue parmi "fr", "en", "de", "es", "zh"
            strategy: stratégie de synthèse

        Returns:
            Texte synthétisé (phrase complète avec ponctuation finale).
        """
        if not mol_ids:
            return ""

        if lang not in KERNELS:
            raise ValueError(f"Langue inconnue: {lang!r}. Disponibles: {list(KERNELS)}")

        if strategy == "concat_defs":
            return self._concat_defs(mol_ids, lang)
        elif strategy == "kernel_flat":
            return self._kernel_flat(mol_ids, lang)
        elif strategy == "kernel_structured":
            return self._kernel_structured(mol_ids, lang)
        else:
            raise ValueError(f"Stratégie inconnue: {strategy!r}. Disponibles: {self.STRATEGIES}")

    # ── Stratégie 1 : concaténation définitions (baseline §79) ────────────────

    def _concat_defs(self, mol_ids: list[int], lang: str) -> str:
        defs_dict = DEFINITIONS.get(lang, DEFINITIONS["en"])
        parts = [defs_dict[m] for m in mol_ids if m in defs_dict]
        sep = " | " if lang != "zh" else " | "
        return sep.join(parts)

    # ── Stratégie 2 : noyaux plats ────────────────────────────────────────────

    def _kernel_flat(self, mol_ids: list[int], lang: str) -> str:
        kernels_dict = KERNELS[lang]
        parts = [kernels_dict[m] for m in mol_ids if m in kernels_dict]
        if not parts:
            return ""
        if lang == "zh":
            sep = "，"
            return sep.join(parts) + "。"
        # Première lettre en majuscule
        result = ", ".join(parts)
        return result[0].upper() + result[1:] + "."

    # ── Stratégie 3 : noyaux structurés (connecteurs Jaccard-aware) ───────────

    def _kernel_structured(self, mol_ids: list[int], lang: str) -> str:
        kernels_dict = KERNELS[lang]
        parts = [kernels_dict[m] for m in mol_ids if m in kernels_dict]
        n = len(parts)

        if n == 0:
            return ""

        if n == 1:
            text = parts[0]
            if lang == "zh":
                return text + "。"
            return text[0].upper() + text[1:] + "."

        if lang == "zh":
            # ZH : noyaux séparés par connecteurs chinois
            result = parts[0]
            for i in range(1, n):
                is_final = (i == n - 1)
                conn = _choose_connector(
                    mol_ids[i - 1], mol_ids[i], lang,
                    is_final=(is_final and n == 3), n_total=n
                )
                result += conn + parts[i]
            return result + "。"

        # Langues avec alphabet latin
        if n == 2:
            conn = _choose_connector(mol_ids[0], mol_ids[1], lang)
            result = f"{parts[0]}, {conn} {parts[1]}"
            return result[0].upper() + result[1:] + "."

        if n == 3:
            # m0 ─conn01─ m1 ─conn_final─ m2
            conn01 = _choose_connector(mol_ids[0], mol_ids[1], lang)
            conn_f = _choose_connector(
                mol_ids[1], mol_ids[2], lang, is_final=True, n_total=3
            )
            result = f"{parts[0]}, {conn01} {parts[1]}, {conn_f} {parts[2]}"
            return result[0].upper() + result[1:] + "."

        # n ≥ 4 : cascade de connecteurs
        tokens = [parts[0]]
        for i in range(1, n):
            is_final = (i == n - 1)
            conn = _choose_connector(
                mol_ids[i - 1], mol_ids[i], lang,
                is_final=is_final, n_total=n
            )
            tokens.append(f", {conn} {parts[i]}")
        result = "".join(tokens)
        return result[0].upper() + result[1:] + "."


# ═══════════════════════════════════════════════════════════════════════════════
# §81 — Synthèse adaptative
# ═══════════════════════════════════════════════════════════════════════════════

# Connecteur de transition cross-type (def → kernel ou kernel → def)
_CROSS_CONNECTORS: dict[str, str] = {
    "fr": "en outre,",
    "en": "moreover,",
    "de": "außerdem",
    "es": "además,",
    "zh": "此外",
}

# Primes RAPPORT et ORIENTATION
_RAPPORT_PRIME = 5


def _is_architectural(mol_id: int) -> bool:
    """
    Retourne True si la molécule est "architecturale" : définition > noyau.

    Règle empirique issue de §80A :
        - 4 atomes → INTÉGRATION (210)  : abstraction maximale, defs gagnent
        - 3 atomes, RAPPORT(5) ET ORIENTATION(7) présents → TEMPS (105), INTENTION (70)
          Ces molécules combinent structure et direction, leur définition est
          sémanticquement plus dense que le noyau court.

    Pour toutes les autres molécules, le noyau court donne un cycle_sim
    égal ou supérieur à la définition complète.
    """
    mask = product_to_mask(mol_id) or 0
    primes = set(atoms_in(mask))
    n = len(primes)
    return n >= 4 or (n == 3 and _RAPPORT_PRIME in primes and _ORIENT_PRIME in primes)


def _mol_type(mol_id: int) -> str:
    """Retourne 'def' (architectural) ou 'kernel' (naturel)."""
    return "def" if _is_architectural(mol_id) else "kernel"


# Catalogue des types par mol_id (pour référence rapide)
MOL_TYPES: dict[int, str] = {m: _mol_type(m) for m in [
    2, 3, 5, 7, 6, 10, 14, 15, 21, 35, 30, 42, 70, 105, 210
]}


class NipadaAdaptiveSynthesizer:
    """
    §81 — Synthèse adaptative nipada.

    Sélectionne automatiquement la meilleure stratégie *par molécule* selon
    son niveau d'abstraction structurale, puis assemble les fragments avec des
    connecteurs appropriés.

    Règle de sélection (issue de §80A) :
        - Molécule "architecturale" (n_atomes≥4 ou RAPPORT+ORIENTATION à n≥3)
          → phrase définitionnelle complète
        - Molécule "naturelle" (tous les autres cas)
          → noyau sémantique court

    Molécules architecturales : TEMPS(105), INTENTION(70), INTÉGRATION(210).
    Molécules naturelles       : les 12 restantes.

    L'assemblage est hybride :
        - Bloc tout-kernel     → connecteurs kernel_structured (Jaccard-aware)
        - Bloc tout-def        → séparateur " | "
        - Blocs mixtes kernel/def → connecteur cross-type + ponctuation adaptée

    Usage :
        synth = NipadaAdaptiveSynthesizer()
        text = synth.synthesize([105, 30, 3], lang="fr")
        # 105 → def (TEMPS), 30 → kernel (VIE), 3 → kernel (DIFFÉRENCE)
        # → "Le temps est l'articulation de la différence, du rapport et de l'orientation…
        #    en outre, un vivant existe, se différencie et maintient des relations
        #    structurées, et deux choses se distinguent irréductiblement."
    """

    def __init__(self) -> None:
        self._base = NipadaSynthesizer()

    def synthesize(self, mol_ids: list[int], lang: str) -> str:
        """
        Génère un texte adaptatif depuis les molécules `mol_ids` en langue `lang`.

        Retourne une phrase complète avec ponctuation finale.
        """
        if not mol_ids:
            return ""
        if lang not in KERNELS:
            raise ValueError(f"Langue inconnue: {lang!r}. Disponibles: {list(KERNELS)}")

        types = [_mol_type(m) for m in mol_ids]

        # Cas uniforme → déléguer directement
        if all(t == "kernel" for t in types):
            return self._base.synthesize(mol_ids, lang, strategy="kernel_structured")
        if all(t == "def" for t in types):
            return self._base.synthesize(mol_ids, lang, strategy="concat_defs")

        # Cas mixte → assemblage hybride
        return self._hybrid(mol_ids, types, lang)

    def _hybrid(self, mol_ids: list[int], types: list[str], lang: str) -> str:
        """
        Assemble des fragments kernel et def en alternance.

        Stratégie :
            1. Regrouper les molécules en runs consécutifs de même type.
            2. Générer le texte de chaque run (kernel_structured ou concat_defs).
            3. Joindre les runs avec le connecteur cross-type.
        """
        # Construire les runs
        runs: list[tuple[str, list[int]]] = []
        current_type = types[0]
        current_run: list[int] = [mol_ids[0]]

        for mol_id, t in zip(mol_ids[1:], types[1:]):
            if t == current_type:
                current_run.append(mol_id)
            else:
                runs.append((current_type, current_run))
                current_type = t
                current_run = [mol_id]
        runs.append((current_type, current_run))

        # Générer chaque run
        parts: list[tuple[str, str]] = []  # (type, text)
        for run_type, run_mols in runs:
            if run_type == "kernel":
                text = self._base.synthesize(run_mols, lang, strategy="kernel_structured")
                # Retirer la ponctuation finale pour la jointure
                text = text.rstrip(".。")
            else:  # def
                defs_dict = DEFINITIONS.get(lang, DEFINITIONS["en"])
                texts = [defs_dict[m] for m in run_mols if m in defs_dict]
                sep = " | "
                text = sep.join(t.rstrip(".。") for t in texts)
            parts.append((run_type, text))

        if not parts:
            return ""

        # Assembler les runs
        cross_conn = _CROSS_CONNECTORS[lang]
        result_parts: list[str] = [parts[0][1]]

        for prev_type, curr_text in parts[1:]:
            if lang == "zh":
                result_parts.append(cross_conn + curr_text)
            else:
                result_parts.append(f" {cross_conn} {curr_text}")

        result = "".join(result_parts)

        # Capitaliser et ponctuer
        if lang == "zh":
            return result + "。"
        return result[0].upper() + result[1:] + "."

    def explain(self, mol_ids: list[int]) -> dict[int, str]:
        """Retourne le type sélectionné pour chaque molécule (pour diagnostic)."""
        return {m: _mol_type(m) for m in mol_ids}
