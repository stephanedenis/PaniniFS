---
title: Progress & roadmap
---

# Progress & roadmap

Summary of research state and ongoing work.

## Key results (February 2026)

### 7-layer semantic engine

- **34 universal atoms** validated across **14 languages** (7 European + Japanese, Chinese, Russian, Dutch, Hindi, Sanskrit, Arabic)
- **7/7 European languages ≥ 90%** lexical coverage:

| Language | Coverage |
|----------|---------|
| English | 94.4% |
| Esperanto | 93.2% |
| German | 91.1% |
| Finnish | 90.6% |
| Spanish | 90.1% |
| French | 90.1% |
| Italian | 90.1% |

### Multilingual breakthroughs

| Language | Before | After | Gain | Technique |
|----------|--------|-------|------|-----------|
| Japanese | 18.8% | **74.1%** | +55.3pp | Kanji-only tokenization + furigana 《》 stripping + OpenCC kyūjitai |
| Chinese | 33.8% | **73.9%** | +40.1pp | OpenCC traditional→simplified + vocabulary expansion |
| Russian | 16.5% | **56.3%** | +39.8pp | Snowball stemmer + pre-1918-reform spelling normalization + 450 keywords |
| Dutch | 28.4% | **55.9%** | +27.5pp | Pre-1947 spelling normalization + 350 keywords |

Key insight: **semantic atoms cross writing systems** — Japanese kanji share the same characters as Chinese hanzi, enabling cross-language gains.

### Corpus and infrastructure

- Gutenberg: 62 texts, 7+ languages, ~3M words ingested
- Wikipedia: 973 articles, 14 languages, 2.2M words, 34/34 atoms = 100%
- Global coverage: **76.8%** across ~8M words
- Dolt: 3 databases (~215 MB), schema v3
- `text_normalizer.py`: NFC, BCP 47, epoch detection, multi-script

### PaniniWeb (Rust v0.1)

New decentralized architecture layer:

- 4-crate workspace: `panini-core`, `panini-net`, `panini-api`, `panini-cli`
- 71 tests (58 core + 11 net + 2 doc)
- JSON persistence (ChainSnapshot v1), Dolt bridge (SQL+CSV)
- P2P network: libp2p with mDNS, Gossipsub, Kademlia, Identify
- `panini://` URI scheme — decentralized semantic web

## Ongoing work

- Academic formalization (papers) and external evaluations
- Python packaging: `panini/` package with `pyproject.toml` and CLI
- Transliterated Sanskrit (IAST → atoms): structural issue not yet resolved
- Open governance: attribution, traceability, ethics by design

## Roadmap (6 phases)

| Phase | Goal | Estimated duration |
|-------|------|-------------------|
| 0 | Cleanup — repo reflects reality | 2 weeks |
| 1 | Quality & CI — unit tests, lint, green pipeline | 2 weeks |
| 2 | API & Integration — FastAPI, Web UI | 3 weeks |
| 3 | Robust data pipeline — reproducible Dolt | 2 weeks |
| 4 | Research & Experiments — E2, compression, atoms (ongoing) | — |
| 5 | Semantic filesystem — `panini index` + `panini search` | 2–3 months |
| 6 | Scalability & Distribution — Rust, multi-user | long term |

For details: see [Research](research/index.md) and the [Roadmap](operations/devops/roadmap.md).
