---
title: Vue d'ensemble de la recherche
---

# Vue d'ensemble de la recherche

Cette section synthétise les axes de recherche actifs de PaniniFS et leurs résultats.

---

## Résultats clés (état : février 2026)

| Métrique | Valeur |
|---------|--------|
| Atomes universaux | **34 atomes** (6 couches, 4 catégories) |
| Langues couvertes | **14 langues** validées |
| Couverture globale | **76.8%** (62 fichiers, ~5.8M mots) |
| Couverture EU | **7/7 langues ≥ 90%** (corpus calibré) |
| Corpus Wikipédia | 34/34 atomes présents = **100%** sur 14 langues |
| Percée maximale | Japonais : **18.8% → 74.1%** (+55.3pp) |

Voir les [résultats détaillés de couverture →](resultats-couverture.md)

---

## Axes majeurs

### 1. Atomes universaux et validation multilingue

- [Atomes universaux — tableau complet](atomes-universaux.md) — les 34 atomes avec catégories, primitives NSM, dhātu sanscrit
- [Résultats de couverture](resultats-couverture.md) — tableaux détaillés par langue et par version
- [Universaux sémantiques](universaux-semantique.md) — protocole de validation, hypothèses, micro-cas
- [Inventaire Dhātu v0.1](inventaire-dhatu-v0-1.md) — format YAML minimal

### 2. Validation typologique et expériences

- [Expériences Dhātu v0.1 et typologie](experiences-dhatu-typologie-v0-1.md) — échantillon 20 langues child-directed
- Découvertes clés :
  - Baby sign validation — primitives gestuelles pré-linguistiques
  - Dhātu core set — 7 opérateurs informationnels (COMM, ITER, TRANS, DECIDE, LOCATE, GROUP, SEQ)
  - Insight inter-langues : kanji japonais ↔ hanzi chinois → atome indépendant de l'écriture

### 3. Langage humain et développement

- [Langage humain et développement](langage-humain-developpement.md) — jalons 0–6 ans et dhātu
- Alignement jalons d'acquisition → primitives sémantiques

### 4. Compression sémantique

- [Compression sémantique](compression-semantique.md) — métriques, protocole, implémentation
- Résultats corpus jouet : 12 phrases, taux = 1.0, moyenne 3.67 primitives/encodage

### 5. Stratégies cloud et infrastructure

- [Stratégie calcul gratuit](cloud-free-compute.md) — Colab, GitHub Actions, pipeline distribué

---

## Sommaire des universaux sémantiques

Les 34 atomes PaniniFS sont organisés en **4 catégories ontologiques** :

| Catégorie | Atomes (sélection) | Sanskrit |
|-----------|--------------------|---------|
| **PROCESSUS** | MOUVEMENT, COGNITION, COMMUNICATION, CRÉATION, EXISTENCE, SEEKING, FEAR, CARE… | kriyā |
| **RELATION** | RELATION, STRUCTURE, INVARIANCE, ORDRE, DOMINATION | sambandha |
| **QUALITÉ** | BON, GRAND, VRAI, INTENSE, ANCIEN, MESURE, PERCEPTION | guṇa |
| **ENTITÉ** | CHOSE, AGENT, CORPS, LIEU, MATIÈRE | dravya |

Correspondances théoriques :
- **NSM** (Wierzbicka) : GOOD, BAD, THINK, KNOW, FEEL, SAY, DO, HAPPEN, MOVE…
- **Jackendoff** : GO, STAY, BE, CAUSE, HAVE, THING, PLACE, AMOUNT
- **Pustejovsky** : FORMAL, AGENTIVE, TELIC, CONSTITUTIVE
- **Pāṇini** : √gam, √jñā, √dṛś, √vac, √kṛ, √as, √labh…

Voir le [tableau complet →](atomes-universaux.md)

---

## Lecture intégrale (livre)

- Version web, lecture continue: [Livre > Lecture intégrale](../livre/lecture-integrale.md)

## Quoi de neuf (14 jours)

Voir: [Quoi de neuf](whats-new.md)
