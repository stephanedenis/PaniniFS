---
title: What's new (14 days)
---

# What's new — February 2026

Summary of major advances from the February 2026 research session.

## 🎯 Lexical coverage: 7/7 European languages ≥ 90%

Validated on Gutenberg corpus (37 texts) and Wikipedia (973 articles):

| Language | Coverage |
|----------|---------|
| English | 94.4% |
| Esperanto | 93.2% |
| German | 91.1% |
| Finnish | 90.6% |
| Spanish | 90.1% |
| French | 90.1% |
| Italian | 90.1% |

## 🔥 Major multilingual breakthroughs

### Japanese: 18.8% → 74.1% (+55.3pp)

- Kanji-only tokenization (furigana 《》 stripping)
- OpenCC kyūjitai normalization (旧字体 → modern forms)
- **Insight**: semantic atoms cross writing systems — Japanese kanji share Chinese hanzi characters

### Chinese: 33.8% → 73.9% (+40.1pp)

- OpenCC traditional→simplified
- 471 new entries (347 keywords, 64 stop words, 60 proper nouns)

### Russian: 16.5% → 56.3% (+39.8pp total)

- Snowball Russian stemmer activated
- Pre-1918-reform spelling normalizer: final ъ, ѣ→е, і→и, ѳ→ф
- 450 keywords, 250 stop words

### Dutch: 28.4% → 55.9% (+27.5pp total)

- Snowball Dutch stemmer activated
- 48-pair pre-1947 spelling table (zoo→zo, groote→grote, schoone→schone…)
- 350 keywords, 180 stop words

## 📊 Global state (v4.8.16)

- **14 languages**, **62 Gutenberg texts + 973 Wikipedia articles**
- Global coverage: **76.8%** (~8M words)
- 7/7 EU languages ≥ 90%, 12/14 languages ≥ 55%

## 🦀 PaniniWeb (Rust v0.1)

New decentralized architecture layer:

- 4-crate workspace, 71 tests
- JSON persistence (ChainSnapshot), Dolt bridge (SQL+CSV export)
- P2P network: libp2p mDNS + Gossipsub + Kademlia + Identify
- `panini://` URI scheme — decentralized semantic web

## 📥 Wikipedia corpus

- 14 languages, 63.6 GB compressed (~65M articles available)
- 973 articles ingested, 2.2M words, 34/34 atoms = 100%

## 🔬 Infrastructure

- `text_normalizer.py`: NFC, BCP 47, epoch detection, 5 scripts
- ISO 639 / ISO 15924 / BCP 47 / Unicode CLDR standards audited for 14 languages
- Dolt: 3 databases (~215 MB), schema v3, ×877 optimization (from 3.9h → 16s)

## Discoveries

- Baby sign foundation — validation of pre-linguistic gestural primitives
- Dhātu core set — 7 informational operators (COMM, ITER, TRANS, DECIDE, LOCATE, GROUP, SEQ)
- Conceptual atoms revision — 34 universal primitives validated

## See also

- [Progress & roadmap](../avancement.md)
- [Book > Full reading](../livre/lecture-integrale.md)
- [Publications](../publications.md)
