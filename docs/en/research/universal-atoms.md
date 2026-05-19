---
title: Universal atoms — complete table
---

# The 34 Universal Atoms of PaniniFS

The PaniniFS semantic engine relies on **34 semantic atoms** distributed across 4 ontological categories and 6 layers of abstraction. These atoms form the minimal vocabulary for encoding most human concepts in any natural language.

!!! info "Naming convention"
    Atom names (MOUVEMENT, COGNITION, CRÉATION…) are **canonical identifiers** in UPPERCASE. They are defined in French in the source code (`import_panlang_v2.py`) and serve as universal, language-independent identifiers. The Python code and Dolt databases use these French names as stable keys. English equivalents are shown in the "Operational meaning" column.

!!! success "Validation"
    These 34 atoms have been validated across **14 languages** and **~8M words** (Gutenberg + Wikipedia).
    Atom presence coverage: **34/34 = 100%** on the 14-language Wikipedia corpus.

---

## Summary table of the 34 atoms

### Layer 3a — Semantic predicates (9 atoms)

| Atom | Category | Operational meaning | NSM primes | Sanskrit dhātu |
|------|----------|---------------------|------------|----------------|
| **MOUVEMENT** | PROCESS | Spatial displacement | MOVE | √gam |
| **COGNITION** | PROCESS/QUALITY | Thinking, knowledge | THINK, KNOW | √jñā |
| **PERCEPTION** | PROCESS/QUALITY | Seeing, hearing, sensing | SEE, HEAR | √dṛś |
| **COMMUNICATION** | PROCESS/RELATION | Saying, transmitting | SAY | √vac |
| **CRÉATION** | PROCESS | Making, causing | DO, HAPPEN | √kṛ |
| **EXISTENCE** | ENTITY/PROCESS | Being, existing | EXIST, THERE IS | √as |
| **DESTRUCTION** | PROCESS | Dying, breaking | DIE | — |
| **POSSESSION** | RELATION/PROCESS | Having, obtaining | HAVE | √labh |
| **DOMINATION** | MODALITY/RELATION | Wanting, being able to | WANT, CAN | √īś |

### Layer 3c — Emotional axes (8 atoms)

| Atom | Category | Operational meaning | NSM primes | Sanskrit dhātu |
|------|----------|---------------------|------------|----------------|
| **SEEKING** | QUALITY/PROCESS | Seeking, desiring | WANT | √iṣ |
| **FEAR** | QUALITY/PROCESS | Fear, dread | FEEL | √bhī |
| **CARE** | QUALITY/RELATION | Care, love | FEEL, GOOD | √snuh |
| **GRIEF** | QUALITY/PROCESS | Sorrow, sadness | FEEL, BAD | √śuc |
| **RAGE** | QUALITY/PROCESS | Anger, fury | FEEL, BAD | √krudh |
| **DISGUST** | QUALITY/PROCESS | Disgust, rejection | FEEL, BAD | √jugupsā |
| **PLAY** | QUALITY/PROCESS | Play, pleasure | FEEL, GOOD | √krīḍ |
| **TEDIUM** | QUALITY/PROCESS | Boredom, weariness | FEEL, BAD | √glai |

### Layer 4 — Abstract atoms (7 atoms)

| Atom | Category | Operational meaning | NSM primes | Jackendoff |
|------|----------|---------------------|------------|-----------|
| **RELATION** | RELATION | Link between entities | LIKE, OF, WITH | — |
| **STRUCTURE** | STRUCTURE/RELATION | Organization, hierarchy | PART, KIND | — |
| **INVARIANCE** | QUALITY/STRUCTURE | Stability, persistence | SAME | STAY |
| **RÉCURRENCE** | PROCESS/STRUCTURE | Repetition, iteration | AGAIN, MORE | — |
| **DUALITÉ** | RELATION/MODALITY | Opposition, negation, condition | OTHER, NOT, IF | — |
| **MESURE** | QUALITY/RELATION | Quantity, size, degree | BIG, SMALL, MUCH | AMOUNT |
| **ORDRE** | RELATION/STRUCTURE | Sequence, before/after | BEFORE, AFTER, ABOVE | — |

### Layer 5 — Entity atoms (5 atoms)

| Atom | Category | Operational meaning | NSM primes | Jackendoff |
|------|----------|---------------------|------------|-----------|
| **CHOSE** | ENTITY | Object, substance | SOMETHING, THING | THING |
| **AGENT** | ENTITY/PROCESS | Animate being, person | SOMEONE, PEOPLE, I, YOU | — |
| **CORPS** | ENTITY/STRUCTURE | Physical body, body part | BODY | — |
| **LIEU** | ENTITY/STRUCTURE | Location, position | WHERE, PLACE, HERE | PLACE |
| **MATIÈRE** | ENTITY/QUALITY | Substance, material | PART | — |

### Layer 6 — Quality atoms (5 atoms)

| Atom | Category | Operational meaning | NSM primes | Aristotle |
|------|----------|---------------------|------------|----------|
| **BON** | QUALITY | Positive value, good | GOOD | ποιότης |
| **GRAND** | QUALITY/ENTITY | Size, greatness | BIG | ποιότης |
| **VRAI** | QUALITY/MODALITY | Truth, accuracy | TRUE | ποιότης |
| **INTENSE** | QUALITY/PROCESS | Intensity, degree | VERY, MUCH | ποιότης |
| **ANCIEN** | QUALITY/PROCESS | Age, duration | BEFORE, A LONG TIME | ποιότης |

---

## Distribution by ontological category

| Category | Sanskrit | Atoms | Count |
|----------|---------|-------|-------|
| **PROCESS** (dominant) | kriyā | MOUVEMENT, COGNITION, COMMUNICATION, CRÉATION, EXISTENCE, DESTRUCTION, POSSESSION, SEEKING, FEAR, CARE, GRIEF, RAGE, DISGUST, PLAY, TEDIUM, RÉCURRENCE | ~16 |
| **RELATION** (dominant) | sambandha | DOMINATION, POSSESSION, RELATION, STRUCTURE, INVARIANCE, ORDRE | ~6 |
| **QUALITY** (dominant) | guṇa | PERCEPTION, COGNITION, BON, GRAND, VRAI, INTENSE, ANCIEN, MESURE | ~8 |
| **ENTITY** (dominant) | dravya | CHOSE, AGENT, CORPS, LIEU, MATIÈRE, EXISTENCE | ~6 |

> Note: categories are indicative; many atoms span multiple categories (e.g., COGNITION is 70% PROCESS + 30% QUALITY).

---

## The 7 dhātu informational operators

Alongside the 34 analytical atoms, PaniniFS uses **7 dhātu operators** for high-level information flow encoding:

| Dhātu | Operation | Sub-primitives |
|-------|-----------|----------------|
| **COMM** | Communicate/share | channel, source, target |
| **ITER** | Iterate/repeat | loop, frequency, accumulation |
| **TRANS** | Transform | input, operation, output |
| **DECIDE** | Choose/regulate | criteria, thresholds, branches |
| **LOCATE** | Locate/anchor | position, context, landmarks |
| **GROUP** | Group/structure | collection, membership |
| **SEQ** | Sequence/order | order, dependencies, timeline |

**Mapping to the 34 atoms**:
- COMM ↔ COMMUNICATION, RELATION
- ITER ↔ RÉCURRENCE, MESURE
- TRANS ↔ CRÉATION, DESTRUCTION, MOUVEMENT
- DECIDE ↔ DOMINATION, DUALITÉ
- LOCATE ↔ LIEU, ORDRE, RELATION
- GROUP ↔ STRUCTURE, RELATION
- SEQ ↔ ORDRE, RÉCURRENCE

---

## Theoretical cross-references

PaniniFS's 34 atoms are cross-referenced against several semantic systems:

| System | References | Correspondence |
|--------|-----------|----------------|
| **NSM** (Natural Semantic Metalanguage) | Wierzbicka 1972, Goddard 2002 | Universal primes: GOOD, BAD, BIG, SMALL, THINK, KNOW, FEEL, SAY, DO, HAPPEN… |
| **Jackendoff** | Conceptual Semantics 1990 | GO, STAY, BE, CAUSE, LET, INCH, HAVE, AFFECT, THING, PLACE, AMOUNT |
| **Pustejovsky** | Generative Lexicon 1995 | Qualia: FORMAL, AGENTIVE, TELIC, CONSTITUTIVE |
| **Sanskrit dhātu** | Pāṇini Ashtādhyāyī | √gam, √jñā, √dṛś, √vac, √kṛ, √as, √labh, √iṣ, √bhī… |

---

## Encoding example

**Sentence**: "The cat hunts the mouse."

| Segment | Atom(s) | Category |
|---------|---------|---------|
| The cat | AGENT | ENTITY |
| hunts | MOUVEMENT + DESTRUCTION | PROCESS |
| the mouse | CHOSE + PATIENT | ENTITY |
| (habitual) | RÉCURRENCE | ABS |

**Representation**: `[AGENT:cat][MOUVEMENT][DESTRUCTION][CHOSE:mouse][RÉCURRENCE]`

---

## See also

- [Coverage results](coverage-results.md) — validation metrics on corpus
- [Semantic universals](semantic-universals.md) — validation protocol
- [Dhātu experiments v0.1](experiences-dhatu-typologie-v0-1.md) — typological corpus
- [Dhātu inventory v0.1](dhatu-inventory-v0-1.md) — YAML format
- [Dhātu Framework](../dhatu-framework.md) — overview
