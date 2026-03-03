---
title: Lexical coverage results
---

# Lexical Coverage Results — PaniniFS Engine

This page documents the lexical coverage metrics of the PaniniFS semantic engine on two corpora: the Gutenberg corpus (classic texts) and the Wikipedia corpus.

!!! info "Metric"
    **Lexical coverage** measures the proportion of content words (after removing function words) to which at least one semantic atom can be assigned without adding a new primitive.

---

## Global state — expanded Gutenberg corpus (v4.8.16)

**62 files · 12 languages · ~5.8M words** (state: February 2026)

| Language | Code | Coverage | Family | Script |
|----------|------|---------|--------|--------|
| English | `en` | **81.4%** | IE/Germanic | Latin |
| German | `de` | **81.4%** | IE/Germanic | Latin |
| French | `fr` | **79.4%** | IE/Romance | Latin |
| Chinese | `zh` | **76.6%** | Sino-Tibetan | CJK |
| Japanese | `ja` | **74.1%** | Japonic | CJK |
| Esperanto | `eo` | **73.2%** | Constructed | Latin |
| Finnish | `fi` | **71.7%** | Uralic | Latin |
| Italian | `it` | **71.1%** | IE/Romance | Latin |
| Spanish | `es` | **68.7%** | IE/Romance | Latin |
| Russian | `ru` | **56.3%** | IE/Slavic | Cyrillic |
| Dutch | `nl` | **55.9%** | IE/Germanic | Latin |
| Sanskrit | `sa` | **10.7%** | IE/Indic | IAST transliteration |
| **Global** | — | **76.8%** | — | — |

> **Note**: Scores on the expanded corpus (62 files, hard texts including 14th-century Dante, pre-1918 Russian spelling, pre-1947 Dutch spelling) are lower than scores on the original 11-file corpus, where 7/7 EU languages reached ≥ 90%.

---

## Original Gutenberg corpus — 7 European languages (v4.8.11)

**11 files · 7 languages · calibrated classical corpus**

| Language | Coverage | Status |
|----------|---------|--------|
| English | **94.4%** | 🟢 |
| Esperanto | **93.2%** | 🟢 |
| German | **91.1%** | 🟢 |
| Finnish | **90.6%** | 🟢 |
| Spanish | **90.1%** | 🟢 |
| French | **90.1%** | 🟢 |
| Italian | **90.1%** | 🟢 |
| **Global** | **91.2%** | 🎯 |

**Milestone**: 7/7 European languages ≥ 90%, achieved with v4.8.11 (February 21, 2026).

---

## Wikipedia corpus (v4.7 — Wikipedia Audit)

**973 articles · 14 languages · 2.2M words**

- 34/34 atoms covered across all languages = **100%** atom presence
- Cross-language cosine similarity (FR↔ZH = 0.904, EN↔FR = 0.93)
- 14 languages include: EN, FR, DE, ES, IT, FI, EO, PT, NL, JA, ZH, HI, SA, AR

---

## Version progression — EU original corpus

Evolution on the original Gutenberg EU corpus (11 files), from v4.8.2 to v4.8.11:

| Version | New entries | Global gain | Coverage | Milestone |
|---------|------------|------------|---------|-----------|
| v4.8.2 | base | — | 85.1% | |
| v4.8.3 | 771 | +2.3pp | 87.4% | |
| v4.8.4 | 584 | +1.4pp | 88.8% | |
| v4.8.5 | algo fixes | +0.2pp | 89.0% | |
| v4.8.6 | 400 | +0.4pp | 89.4% | |
| v4.8.7 | 307 | +0.7pp | 90.1% | 🎯 90% global |
| v4.8.8 | 136 | +0.4pp | 90.5% | FR ≥ 90% |
| v4.8.9 | 113 | +0.3pp | 90.8% | |
| v4.8.10 | 110 | +0.2pp | 91.0% | |
| v4.8.11 | 124 | +0.2pp | 91.2% | 🎯 7/7 EU ≥ 90% |
| **Total** | **~2,550** | **+6.1pp** | **91.2%** | |

---

## Multilingual breakthroughs — expanded corpus (v4.8.12 → v4.8.16)

After expansion to 62 files including non-European languages:

### Japanese: 18.8% → 74.1% (+55.3pp)

| File | Content | Before | After |
|------|---------|--------|-------|
| pg1982 | Rashomon (Akutagawa) | 18.8% | 74.0% |
| pg31617 | Shisei (Tanizaki) | — | 71.9% |
| pg31757 | Omedetaki hito (Mushanokoji) | — | 78.4% |

**Techniques**: kanji-only tokenization, furigana `《》` stripping, OpenCC kyūjitai → simplified.

### Chinese: 33.8% → 73.9% (+40.1pp)

**Techniques**: OpenCC traditional→simplified, CJK punctuation filter, 471 entries (347 keywords, 64 stop words, 60 proper nouns).

### Russian: 16.5% → 56.3% (+39.8pp total)

| File | Content | Before | After |
|------|---------|--------|-------|
| pg16527 | Commercial text | — | 64.4% |
| pg14741 | Derzhavin, spiritual odes | 21.8% | 48.9% |
| pg30774 | Travelers in Muscovy (pre-1918 spelling) | 13.6% | 41.8% |

**Techniques**: Snowball Russian stemmer, pre-1918 spelling normalizer (ъ, ѣ→е, і→и), 450 keywords, 250 stop words.

### Dutch: 28.4% → 55.9% (+27.5pp total)

| File | Content | Before | After |
|------|---------|--------|-------|
| pg17525 | Buysse, Flemish prose | 41.7% | 52.5% |
| pg18066 | Columbus, exploration | 37.9% | 56.8% |

**Techniques**: Snowball Dutch stemmer, 48-pair pre-1947 spelling table (zoo→zo, groote→grote), 350 keywords, 180 stop words.

---

## Notable per-file results (expanded EU corpus, v4.8.15)

| File | Language | Content | Coverage |
|------|----------|---------|---------|
| pg1232 | EN | The Prince (Machiavelli) | 83.6% |
| pg2407 | DE | Also Sprach Zarathustra | 89.1% |
| pg2000 | ES | Don Quijote | 86.4% |
| pg17989 | FR | De la Terre à la Lune (Verne) | 90.1% |
| pg1012 | IT | Divina Commedia (Dante, 14th c.) | ~81% |
| pg16328 | EN | Beowulf (ancient poetry) | 81.6% |
| pg74 | EN | Tom Sawyer (Twain) | 83.6% |
| pg5185 | EN | Kalevala EN | 80.9% |

---

## Cross-language spillover effects

The v4.8.14 validation revealed untargeted gains due to kanji/hanzi sharing:

| Language | Before v4.8.14 | After | Gain |
|----------|---------------|-------|------|
| Esperanto | 67.3% | 73.2% | +5.9pp |
| Finnish | 66.0% | 71.7% | +5.7pp |
| German | 77.8% | 80.6% | +2.8pp |
| Chinese | 73.9% | 76.6% | +2.7pp |
| French | 75.8% | 78.4% | +2.6pp |

**Key insight**: Japanese kanji share characters with Chinese hanzi; coverage gained for one language automatically benefits the other, confirming that the semantic atom is **writing-system-independent**.

---

## Infrastructure and reproducibility

| Component | Description |
|-----------|-------------|
| Engine | `seven_layers_engine.py` — 3,320 lines, 14 languages, 34 atoms |
| Finnish lemmatizer | `voikko` — inflected forms, past participles |
| Stemmers | Snowball for EN/FR/DE/ES/IT/FI/EO/RU/NL (9 languages) |
| Normalizer | `text_normalizer.py` — NFC, BCP 47, NFKC CJK, epoch detection |
| Russian normalization | `normalize_prereform_ru()` — pre-1918 spelling |
| CJK normalization | OpenCC `t2s` (traditional→simplified) |
| Dutch normalization | 48-pair pre-1947 spelling table |
| Dolt corpus | 3 databases (~215 MB), schema v3, ×877 optimization |

---

## See also

- [Universal atoms (34)](universal-atoms.md) — complete table
- [Semantic universals](semantic-universals.md) — validation protocol
- [Dhātu Framework](../dhatu-framework.md) — overview
- [Progress & roadmap](../avancement.md)
