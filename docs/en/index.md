# Pāṇini File System

> **Metalinguistic information processing and storage platform.** A universal semantic model of 34 atoms, validated across 14 languages and ~8 million words.

---

## 🔬 The Main Model — 34 Universal Atoms

The core of PaniniFS is a **minimal semantic vocabulary** of 34 atoms distributed across 4 ontological categories and 6 layers of abstraction. These atoms encode the essentials of human concepts in any language.

### The 4 Ontological Categories

!!! note "Canonical identifiers"
    Atom names are uppercase canonical identifiers, language-independent. Most are French-named; emotional axes (SEEKING, FEAR, CARE…) use Panksepp's English nomenclature. English meanings are shown in parentheses.

| Category | Sanskrit | Atoms — canonical identifiers (with English meaning) |
|----------|----------|------------------------------------------------------|
| **PROCESS** | kriyā | MOUVEMENT (movement), COGNITION, COMMUNICATION, CRÉATION (creation), SEEKING, FEAR, CARE, GRIEF… |
| **RELATION** | sambandha | RELATION, STRUCTURE, INVARIANCE, DOMINATION, ORDRE (order)… |
| **QUALITY** | guṇa | BON (good), GRAND (big), VRAI (true), INTENSE, ANCIEN (old), MESURE (measure), PERCEPTION… |
| **ENTITY** | dravya | CHOSE (thing), AGENT, CORPS (body), LIEU (place), MATIÈRE (matter), EXISTENCE… |

→ [Complete table of the 34 atoms](research/atomes-universaux.md)

### The 7 Informational Dhātu Operators

Additionally, **7 dhātu operators** encode information flows at a high level:
`COMM · ITER · TRANS · DECIDE · LOCATE · GROUP · SEQ`

→ [Dhātu Framework](dhatu-framework.md)

---

## 📊 Validated Results — February 2026

!!! success "7/7 European languages ≥ 90% lexical coverage"
    Gutenberg original corpus (11 files, modern texts):

    | Language | Coverage |
    |----------|---------|
    | English | **94.4%** |
    | Esperanto | **93.2%** |
    | German | **91.1%** |
    | Finnish | **90.6%** |
    | Spanish | **90.1%** |
    | French | **90.1%** |
    | Italian | **90.1%** |

!!! tip "Major Multilingual Breakthroughs"
    | Language | Before | After | Gain | Key technique |
    |----------|--------|-------|------|---------------|
    | 🇯🇵 Japanese | 18.8% | **74.1%** | +55pp | Kanji-only tokenization + furigana stripping |
    | 🇨🇳 Chinese | 33.8% | **73.9%** | +40pp | OpenCC traditional→simplified |
    | 🇷🇺 Russian | 16.5% | **56.3%** | +40pp | Snowball stemmer + pre-1918 normalization |
    | 🇳🇱 Dutch | 28.4% | **55.9%** | +28pp | Pre-1947 spelling normalization |

!!! info "Global coverage"
    **76.8%** across 62 Gutenberg texts + 973 Wikipedia articles (~8M words, 14 languages).
    34/34 atoms present = **100%** on the multilingual Wikipedia corpus.

→ [Detailed coverage results](research/resultats-couverture.md) · [What's new](research/whats-new.md)

---

## 🔑 Key Discovery

> **The semantic atom is independent of writing system.** Japanese kanji share the same characters as Chinese hanzi — coverage gained for Chinese directly benefits Japanese. This confirms that the 34 dhātu atoms are genuine conceptual universals, transcending writing systems.

---

## 🦀 PaniniWeb — Decentralized Architecture (Rust v0.1)

- 4 crates workspace: `panini-core`, `panini-net`, `panini-api`, `panini-cli`
- 71 tests (58 core + 11 net + 2 doc)
- P2P network: libp2p with mDNS, Gossipsub, Kademlia
- `panini://` URI scheme — decentralized semantic web

---

## 🌍 Social Vision and Ethics

Society before tech. Goal: make information truly useful, accessible and traceable to everyone.

- Inclusion and accessibility by default
- Attribution and idea provenance (collective memory)
- Open governance, aligned with the Montreal Declaration

→ [Social vision](vision-sociale.md) · [References](references.md)

---

## Quick Navigation

| Section | Description |
|---------|-------------|
| [Research](research/overview.md) | Overview of research axes |
| [Universal Atoms (34)](research/atomes-universaux.md) | Full table with NSM, Jackendoff, dhātu |
| [Coverage Results](research/resultats-couverture.md) | Detailed metrics by language and corpus |
| [Dhātu Framework](dhatu-framework.md) | The 7 operators + 34 atoms |
| [Progress & roadmap](avancement.md) | Project status and roadmap |
| [Book](livre/index.md) | Complete documentation |

---

## Find Me

- GitHub: [stephanedenis](https://github.com/stephanedenis)
- LinkedIn: [neuronspikes](https://www.linkedin.com/in/neuronspikes)
- Publications (Medium/Leanpub): [Publications](publications.md)
- The site is bilingual FR/EN — language toggle top right
