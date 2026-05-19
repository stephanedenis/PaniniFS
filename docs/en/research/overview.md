---
title: Research overview
---

# Research overview

This page summarizes PaniniFS's active research tracks and their results.

---

## Key results (state: February 2026)

| Metric | Value |
|--------|-------|
| Universal atoms | **34 atoms** (6 layers, 4 categories) |
| Languages covered | **14 languages** validated |
| Global coverage | **76.8%** (62 files, ~5.8M words) |
| EU coverage | **7/7 languages ≥ 90%** (calibrated corpus) |
| Wikipedia corpus | 34/34 atoms present = **100%** across 14 languages |
| Max breakthrough | Japanese: **18.8% → 74.1%** (+55.3pp) |

See [detailed coverage results →](coverage-results.md)

---

## Main tracks

### 1. Universal atoms and multilingual validation

- [Universal atoms — complete table](universal-atoms.md) — all 34 atoms with categories, NSM primes, Sanskrit dhātu
- [Coverage results](coverage-results.md) — detailed tables by language and version
- [Semantic universals](semantic-universals.md) — validation protocol, hypotheses, micro-cases
- [Dhātu inventory v0.1](dhatu-inventory-v0-1.md) — minimal YAML format

### 2. Typological validation and experiments

- [Dhātu experiments v0.1 and typology](experiences-dhatu-typologie-v0-1.md) — 20-language child-directed sample
- Key discoveries:
  - Baby sign validation — pre-linguistic gestural primitives
  - Dhātu core set — 7 informational operators (COMM, ITER, TRANS, DECIDE, LOCATE, GROUP, SEQ)
  - Cross-language insight: Japanese kanji ↔ Chinese hanzi → atom independent of writing system

### 3. Human language and development

- [Human language and development](human-language-development.md) — 0–6 year milestones and dhātu
- Acquisition milestone alignment → semantic primitives

### 4. Semantic compression

- [Semantic compression](semantic-compression.md) — metrics, protocol, implementation
- Toy corpus results: 12 sentences, coverage rate = 1.0, avg 3.67 primitives/encoding

### 5. Cloud strategies and infrastructure

- [Cloud-free compute](cloud-free-compute.md) — Colab, GitHub Actions, distributed pipeline

---

## Summary of semantic universals

PaniniFS's 34 atoms are organized into **4 ontological categories**:

| Category | Atoms (selection) | Sanskrit |
|----------|-------------------|---------|
| **PROCESS** | MOUVEMENT, COGNITION, COMMUNICATION, CRÉATION, EXISTENCE, SEEKING, FEAR, CARE… | kriyā |
| **RELATION** | RELATION, STRUCTURE, INVARIANCE, ORDRE, DOMINATION | sambandha |
| **QUALITY** | BON, GRAND, VRAI, INTENSE, ANCIEN, MESURE, PERCEPTION | guṇa |
| **ENTITY** | CHOSE, AGENT, CORPS, LIEU, MATIÈRE | dravya |

Theoretical cross-references:
- **NSM** (Wierzbicka): GOOD, BAD, THINK, KNOW, FEEL, SAY, DO, HAPPEN, MOVE…
- **Jackendoff**: GO, STAY, BE, CAUSE, HAVE, THING, PLACE, AMOUNT
- **Pustejovsky**: FORMAL, AGENTIVE, TELIC, CONSTITUTIVE
- **Pāṇini**: √gam, √jñā, √dṛś, √vac, √kṛ, √as, √labh…

See the [complete table →](universal-atoms.md)

---

## Full reading (book)

- Web version, continuous reading: [Book > Full reading](../livre/lecture-integrale.md)

## What's new (14 days)

See: [What's new](whats-new.md)
