---
title: Quoi de neuf (14 jours)
---

# Quoi de neuf — Février 2026

Synthèse des avancées majeures de la session de recherche de février 2026.

## 🎯 Couverture lexicale : 7/7 langues européennes ≥ 90%

Résultat validé sur le corpus Gutenberg (37 textes) et Wikipédia (973 articles) :

| Langue | Couverture |
|--------|-----------|
| Anglais | 94.4% |
| Espéranto | 93.2% |
| Allemand | 91.1% |
| Finnois | 90.6% |
| Espagnol | 90.1% |
| Français | 90.1% |
| Italien | 90.1% |

## 🔥 Percées multilingues majeures

### Japonais : 18.8% → 74.1% (+55.3pp)

- Tokenisation kanji-only (suppression des furigana 《》)
- Normalisation OpenCC kyūjitai (旧字体 → formes modernes)
- **Insight** : l'atome sémantique traverse les écritures — les kanji japonais partagent les caractères hanzi chinois

### Chinois : 33.8% → 73.9% (+40.1pp)

- OpenCC traditionnel→simplifié
- 471 nouvelles entrées (347 mots-clés, 64 stop words, 60 noms propres)

### Russe : 16.5% → 56.3% (+39.8pp total)

- Stemmer Snowball russe activé
- Normaliseur orthographe pré-réforme 1918 : ъ final, ѣ→е, і→и, ѳ→ф
- 450 mots-clés, 250 stop words

### Néerlandais : 28.4% → 55.9% (+27.5pp total)

- Stemmer Snowball néerlandais activé
- Table 48 paires orthographe pré-1947 (zoo→zo, groote→grote, schoone→schone…)
- 350 mots-clés, 180 stop words

## 📊 État global (v4.8.16)

- **14 langues**, **62 textes Gutenberg + 973 articles Wikipédia**
- Couverture globale : **76.8%** (~8M mots)
- 7/7 langues EU ≥ 90%, 12/14 langues ≥ 55%

## 🦀 PaniniWeb (Rust v0.1)

Nouvelle couche d'architecture décentralisée :

- 4 crates workspace, 71 tests
- Persistence JSON (ChainSnapshot), bridge Dolt (SQL+CSV export)
- Réseau P2P : libp2p mDNS + Gossipsub + Kademlia + Identify
- `panini://` URI scheme — web sémantique décentralisé

## 📥 Corpus Wikipédia

- 14 langues, 63.6 GB compressé (~65M articles disponibles)
- 973 articles ingérés, 2.2M mots, 34/34 atomes = 100%

## 🔬 Infrastructure

- `text_normalizer.py` : NFC, BCP 47, détection d'époque, 5 écritures
- Normes ISO 639 / ISO 15924 / BCP 47 / Unicode CLDR auditées sur 14 langues
- Dolt : 3 bases (~215 Mo), schéma v3, optimisation ×877 (de 3.9h → 16s)

## Découvertes

- Baby sign foundation — validation des primitives gestuelles pré-linguistiques
- Dhātu core set — 7 opérateurs informationnels (COMM, ITER, TRANS, DECIDE, LOCATE, GROUP, SEQ)
- Révision atomes conceptuels — 34 primitives universelles validées

## Voir aussi

- [Avancement & feuille de route](../avancement.md)
- [Livre > Lecture intégrale](../livre/lecture-integrale.md)
- [Publications](../publications.md)
