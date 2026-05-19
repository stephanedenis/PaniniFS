---
title: Avancement & feuille de route
---

# Avancement & feuille de route

Synthèse de l'état de la recherche et des travaux en cours.

## Résultats clés (février 2026)

### Moteur sémantique 7 couches

- **34 atomes universels** validés sur **14 langues** (7 européennes + japonais, chinois, russe, néerlandais, hindi, sanskrit, arabe)
- **7/7 langues européennes ≥ 90%** de couverture lexicale :

| Langue | Couverture |
|--------|-----------|
| Anglais | 94.4% |
| Espéranto | 93.2% |
| Allemand | 91.1% |
| Finnois | 90.6% |
| Espagnol | 90.1% |
| Français | 90.1% |
| Italien | 90.1% |

### Percées multilingues

| Langue | Avant | Après | Gain | Technique |
|--------|-------|-------|------|-----------|
| Japonais | 18.8% | **74.1%** | +55.3pp | Tokenisation kanji-only + suppression furigana 《》 + OpenCC kyūjitai |
| Chinois | 33.8% | **73.9%** | +40.1pp | OpenCC traditionnel→simplifié + expansion vocabulaire |
| Russe | 16.5% | **56.3%** | +39.8pp | Stemmer Snowball + normalisation pré-réforme 1918 + 450 mots-clés |
| Néerlandais | 28.4% | **55.9%** | +27.5pp | Normalisation orthographe pré-1947 + 350 mots-clés |

Insight clé : **l'atome sémantique traverse les écritures** — les kanji japonais partagent les mêmes caractères que les hanzi chinois, permettant des gains croisés entre langues.

### Corpus et infrastructure

- Gutenberg : 62 textes, 7+ langues, ~3M mots ingérés
- Wikipédia : 973 articles, 14 langues, 2.2M mots, 34/34 atomes = 100%
- Couverture globale : **76.8%** sur ~8M mots
- Dolt : 3 bases de données (~215 Mo), schéma v3
- `text_normalizer.py` : NFC, BCP 47, détection d'époque, multi-scripts

### PaniniWeb (Rust v0.1)

Nouvelle couche d'architecture décentralisée :

- 4 crates workspace : `panini-core`, `panini-net`, `panini-api`, `panini-cli`
- 71 tests (58 core + 11 net + 2 doc)
- Persistence JSON (ChainSnapshot v1), bridge Dolt (SQL+CSV)
- Réseau P2P : libp2p avec mDNS, Gossipsub, Kademlia, Identify
- Schéma URI `panini://` — web sémantique décentralisé

## Travaux en cours

- Formalisation académique (articles) et évaluations externes
- Emballage Python : `panini/` package avec `pyproject.toml` et CLI
- Sanskrit translittéré (IAST → atomes) : problème structurel non résolu
- Gouvernance ouverte : attribution, traçabilité, éthique by design

## Feuille de route (6 phases)

| Phase | Objectif | Durée estimée |
|-------|----------|---------------|
| 0 | Assainissement — repo reflète la réalité | 2 semaines |
| 1 | Qualité & CI — tests unitaires, lint, pipeline vert | 2 semaines |
| 2 | API & Intégration — FastAPI, Web UI | 3 semaines |
| 3 | Pipeline de données robuste — Dolt reproductible | 2 semaines |
| 4 | Recherche & Expériences — E2, compression, atomes (continu) | — |
| 5 | Filesystem sémantique — `panini index` + `panini search` | 2–3 mois |
| 6 | Scalabilité & Distribution — Rust, multi-utilisateur | long terme |

Pour le détail : voir [Recherche](research/index.md) et la [Roadmap](operations/devops/roadmap.md).
