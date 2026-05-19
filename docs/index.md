# Pāṇini File System

> **Plateforme de traitement et stockage d'information métalinguistique.** Un modèle sémantique universel de 34 atomes, validé sur 14 langues et ~8 millions de mots.

---

## 🔬 Le modèle principal — 34 atomes universels

Le cœur de PaniniFS est un **vocabulaire sémantique minimal** de 34 atomes répartis en 4 catégories ontologiques et 6 couches d'abstraction. Ces atomes permettent d'encoder l'essentiel des concepts humains dans n'importe quelle langue.

### Les 4 catégories ontologiques

!!! note "Identifiants canoniques"
    Les noms d'atomes sont des identifiants canoniques en MAJUSCULES, indépendants de la langue. La plupart sont définis en français ; les axes émotionnels (SEEKING, FEAR, CARE…) utilisent les noms anglais de la nomenclature Panksepp.

| Catégorie | Sanskrit | Atomes — identifiants canoniques (sélection) |
|-----------|----------|----------------------------------------------|
| **PROCESSUS** | kriyā | MOUVEMENT, COGNITION, COMMUNICATION, CRÉATION, SEEKING, FEAR, CARE, GRIEF… |
| **RELATION** | sambandha | RELATION, STRUCTURE, INVARIANCE, DOMINATION, ORDRE… |
| **QUALITÉ** | guṇa | BON, GRAND, VRAI, INTENSE, ANCIEN, MESURE, PERCEPTION… |
| **ENTITÉ** | dravya | CHOSE, AGENT, CORPS, LIEU, MATIÈRE, EXISTENCE… |

→ [Tableau complet des 34 atomes](research/atomes-universaux.md)

### Les 7 opérateurs dhātu informationnels

En complément, **7 opérateurs dhātu** encodent les flux d'information à haut niveau :
`COMM · ITER · TRANS · DECIDE · LOCATE · GROUP · SEQ`

→ [Cadre Dhātu](dhatu-framework.md)

---

## 📊 Résultats validés — février 2026

!!! success "7/7 langues européennes ≥ 90% de couverture lexicale"
    Corpus Gutenberg original (11 fichiers, textes modernes) :

    | Langue | Couverture |
    |--------|-----------|
    | Anglais | **94.4%** |
    | Espéranto | **93.2%** |
    | Allemand | **91.1%** |
    | Finnois | **90.6%** |
    | Espagnol | **90.1%** |
    | Français | **90.1%** |
    | Italien | **90.1%** |

!!! tip "Percées multilingues majeures"
    | Langue | Avant | Après | Gain | Technique clé |
    |--------|-------|-------|------|---------------|
    | 🇯🇵 Japonais | 18.8% | **74.1%** | +55pp | Tokenisation kanji-only + suppression furigana |
    | 🇨🇳 Chinois | 33.8% | **73.9%** | +40pp | OpenCC traditionnel→simplifié |
    | 🇷🇺 Russe | 16.5% | **56.3%** | +40pp | Stemmer Snowball + normalisation pré-1918 |
    | 🇳🇱 Néerlandais | 28.4% | **55.9%** | +28pp | Normalisation orthographe pré-1947 |

!!! info "Couverture globale"
    **76.8%** sur 62 textes Gutenberg + 973 articles Wikipédia (~8M mots, 14 langues).
    Présence des 34/34 atomes = **100%** sur le corpus Wikipédia multilingue.

→ [Résultats détaillés de couverture](research/resultats-couverture.md) · [Quoi de neuf](research/whats-new.md)

---

## 🔑 Découverte clé

> **L'atome sémantique est indépendant de l'écriture.** Les kanji japonais partagent les mêmes caractères que les hanzi chinois — une couverture acquise pour le chinois bénéficie directement au japonais. Cela confirme que les 34 atomes dhātu sont de véritables universaux conceptuels, au-delà des systèmes d'écriture.

---

## 🦀 PaniniWeb — Architecture décentralisée (Rust v0.1)

- 4 crates workspace : `panini-core`, `panini-net`, `panini-api`, `panini-cli`
- 71 tests (58 core + 11 net + 2 doc)
- Réseau P2P : libp2p avec mDNS, Gossipsub, Kademlia
- Schéma URI `panini://` — web sémantique décentralisé

---

## 🌍 Vision sociale et éthique

Ce projet place la société avant la technique. Objectif : rendre l'information réellement utile, accessible et traçable pour tous.

- Inclusion et accessibilité par défaut
- Attribution et provenance des idées (mémoire collective)
- Gouvernance ouverte, alignée avec la Déclaration de Montréal

→ [Vision sociale](vision-sociale.md) · [Références](references.md)

---

## Navigation rapide

| Section | Description |
|---------|-------------|
| [Recherche](research/overview.md) | Vue d'ensemble des axes de recherche |
| [Atomes universaux (34)](research/atomes-universaux.md) | Tableau complet avec NSM, Jackendoff, dhātu |
| [Résultats de couverture](research/resultats-couverture.md) | Métriques détaillées par langue et corpus |
| [Cadre Dhātu](dhatu-framework.md) | Les 7 opérateurs + 34 atomes |
| [Avancement & feuille de route](avancement.md) | État du projet et roadmap |
| [Livre](livre/index.md) | Documentation complète |

---

## Me retrouver

- GitHub: [stephanedenis](https://github.com/stephanedenis)
- LinkedIn: [neuronspikes](https://www.linkedin.com/in/neuronspikes)
- Publications (Medium/Leanpub): [Publications](publications.md)
- Le site est bilingue FR/EN — menu de langue en haut à droite
