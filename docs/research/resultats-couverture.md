---
title: Résultats de couverture lexicale
---

# Résultats de couverture lexicale — Moteur PaniniFS

Cette page documente les métriques de couverture lexicale du moteur sémantique PaniniFS sur deux corpus : le corpus Gutenberg (textes classiques) et le corpus Wikipédia.

!!! info "Métrique"
    La **couverture lexicale** mesure la proportion de mots de contenu (après suppression des mots fonctionnels) dont au moins un atome sémantique peut être assigné sans ajout de nouvelle primitive.

---

## État global — corpus Gutenberg élargi (v4.8.16)

**62 fichiers · 12 langues · ~5.8M mots** (état : février 2026)

| Langue | Code | Couverture | Famille | Écriture |
|--------|------|-----------|---------|---------|
| Anglais | `en` | **81.4%** | Indo-européen/Germanique | Latin |
| Allemand | `de` | **81.4%** | Indo-européen/Germanique | Latin |
| Français | `fr` | **79.4%** | Indo-européen/Roman | Latin |
| Espéranto | `eo` | **73.2%** | Construit | Latin |
| Japonais | `ja` | **74.1%** | Japonique | CJK |
| Chinois | `zh` | **76.6%** | Sino-tibétain | CJK |
| Italien | `it` | **71.1%** | Indo-européen/Roman | Latin |
| Finnois | `fi` | **71.7%** | Ouralique | Latin |
| Espagnol | `es` | **68.7%** | Indo-européen/Roman | Latin |
| Russe | `ru` | **56.3%** | Indo-européen/Slave | Cyrillique |
| Néerlandais | `nl` | **55.9%** | Indo-européen/Germanique | Latin |
| Sanskrit | `sa` | **10.7%** | Indo-européen/Indique | IAST translittéré |
| **Global** | — | **76.8%** | — | — |

> **Note** : Les scores sur corpus élargi (62 fichiers, textes difficiles dont Dante XIVe s., orthographe russe pré-1918, orthographe néerlandaise pré-1947) sont inférieurs aux scores sur le corpus original (11 fichiers, textes modernes), qui montraient 7/7 langues EU ≥ 90%.

---

## Corpus Gutenberg original — 7 langues européennes (v4.8.11)

**11 fichiers · 7 langues · corpus classique calibré**

| Langue | Couverture | Statut |
|--------|-----------|--------|
| Anglais | **94.4%** | 🟢 |
| Espéranto | **93.2%** | 🟢 |
| Allemand | **91.1%** | 🟢 |
| Finnois | **90.6%** | 🟢 |
| Espagnol | **90.1%** | 🟢 |
| Français | **90.1%** | 🟢 |
| Italien | **90.1%** | 🟢 |
| **Global** | **91.2%** | 🎯 |

**Milestone** : 7/7 langues européennes ≥ 90%, atteint en v4.8.11 (21 février 2026).

---

## Corpus Wikipédia (v4.7 — Wikipedia Audit)

**973 articles · 14 langues · 2.2M mots**

- 34/34 atomes couverts sur toutes les langues = **100%** de présence atomique
- Similarité cosinus cross-langue (FR↔ZH = 0.904, EN↔FR = 0.93)
- Les 14 langues incluent : EN, FR, DE, ES, IT, FI, EO, PT, NL, JA, ZH, HI, SA, AR

---

## Progression version par version — corpus EU original

Évolution sur le corpus Gutenberg EU original (11 fichiers), de v4.8.2 à v4.8.11 :

| Version | Nouvelles entrées | Gain global | Couverture | Milestone |
|---------|------------------|------------|-----------|-----------|
| v4.8.2 | base | — | 85.1% | |
| v4.8.3 | 771 | +2.3pp | 87.4% | |
| v4.8.4 | 584 | +1.4pp | 88.8% | |
| v4.8.5 | corrections algo | +0.2pp | 89.0% | |
| v4.8.6 | 400 | +0.4pp | 89.4% | |
| v4.8.7 | 307 | +0.7pp | 90.1% | 🎯 90% global |
| v4.8.8 | 136 | +0.4pp | 90.5% | FR ≥ 90% |
| v4.8.9 | 113 | +0.3pp | 90.8% | |
| v4.8.10 | 110 | +0.2pp | 91.0% | |
| v4.8.11 | 124 | +0.2pp | 91.2% | 🎯 7/7 EU ≥ 90% |
| **Total** | **~2 550** | **+6.1pp** | **91.2%** | |

---

## Percées multilingues — corpus élargi (v4.8.12 → v4.8.16)

Après extension à 62 fichiers incluant langues non-européennes :

### Japonais : 18.8% → 74.1% (+55.3pp)

| Fichier | Contenu | Avant | Après |
|---------|---------|-------|-------|
| pg1982 | Rashomon (Akutagawa) | 18.8% | 74.0% |
| pg31617 | Shisei (Tanizaki) | — | 71.9% |
| pg31757 | Omedetaki hito (Mushanokoji) | — | 78.4% |

**Techniques** : tokenisation kanji-only, suppression furigana `《》`, OpenCC kyūjitai → simplifié.

### Chinois : 33.8% → 73.9% (+40.1pp)

**Techniques** : OpenCC traditionnel→simplifié, filtre ponctuation CJK, 471 entrées (347 mots-clés, 64 stop words, 60 noms propres).

### Russe : 16.5% → 56.3% (+39.8pp total)

| Fichier | Contenu | Avant | Après |
|---------|---------|-------|-------|
| pg16527 | Texte commercial | — | 64.4% |
| pg14741 | Derjavine, odes spirituelles | 21.8% | 48.9% |
| pg30774 | Voyageurs en Moscovie (pré-réforme 1918) | 13.6% | 41.8% |

**Techniques** : stemmer Snowball russe, normaliseur orthographe pré-1918 (ъ, ѣ→е, і→и), 450 mots-clés, 250 stop words.

### Néerlandais : 28.4% → 55.9% (+27.5pp total)

| Fichier | Contenu | Avant | Après |
|---------|---------|-------|-------|
| pg17525 | Buysse, prose flamande | 41.7% | 52.5% |
| pg18066 | Columbus, exploration | 37.9% | 56.8% |

**Techniques** : stemmer Snowball néerlandais, table 48 paires orthographe pré-1947 (zoo→zo, groote→grote), 350 mots-clés, 180 stop words.

---

## Résultats notables par fichier (corpus EU élargi, v4.8.15)

| Fichier | Langue | Contenu | Couverture |
|---------|--------|---------|-----------|
| pg1232 | EN | The Prince (Machiavel) | 83.6% |
| pg2407 | DE | Also Sprach Zarathustra | 89.1% |
| pg2000 | ES | Don Quijote | 86.4% |
| pg17989 | FR | De la Terre à la Lune (Verne) | 90.1% |
| pg1012 | IT | Divina Commedia (Dante, XIVe s.) | ~81% |
| pg16328 | EN | Beowulf (poésie ancienne) | 81.6% |
| pg74 | EN | Tom Sawyer (Twain) | 83.6% |
| pg5185 | EN | Kalevala EN | 80.9% |

---

## Effets de bord croisés (spillover)

La validation de v4.8.14 a révélé des gains non ciblés dus aux partages kanji/hanzi :

| Langue | Avant v4.8.14 | Après | Δ |
|--------|--------------|-------|---|
| Espéranto | 67.3% | 73.2% | +5.9pp |
| Finnois | 66.0% | 71.7% | +5.7pp |
| Allemand | 77.8% | 80.6% | +2.8pp |
| Chinois | 73.9% | 76.6% | +2.7pp |
| Français | 75.8% | 78.4% | +2.6pp |

**Insight clé** : les kanji japonais partagent les caractères hanzi chinois ; une couverture acquise pour l'une bénéficie automatiquement à l'autre, confirmant que l'atome sémantique est **indépendant de l'écriture**.

---

## Infrastructure et reproductibilité

| Composant | Description |
|-----------|-------------|
| Moteur | `seven_layers_engine.py` — 3 320 lignes, 14 langues, 34 atomes |
| Lemmatiseur finnois | `voikko` — formes fléchies, participes passés |
| Stemmers | Snowball pour EN/FR/DE/ES/IT/FI/EO/RU/NL (9 langues) |
| Normaliseur | `text_normalizer.py` — NFC, BCP 47, NFKC CJK, époque |
| Normalisation russe | `normalize_prereform_ru()` — orthographe pré-1918 |
| Normalisation CJK | OpenCC `t2s` (traditionnel→simplifié) |
| Normalisation NL | Table 48 paires orthographe pré-1947 |
| Corpus Dolt | 3 bases (~215 Mo), schéma v3, optimisation ×877 |

---

## Voir aussi

- [Atomes universaux (34)](atomes-universaux.md) — tableau complet
- [Universaux sémantiques](universaux-semantique.md) — protocole de validation
- [Cadre Dhātu](../dhatu-framework.md) — vue d'ensemble
- [Avancement & feuille de route](../avancement.md)
