---
title: Stratégie calcul gratuit
status: draft
---

# Stratégie calcul gratuit / Cloud-Free Compute

Cette page résume les stratégies de calcul distribué et gratuit (Google Colab, GitHub Actions, cloud public) utilisées dans PaniniFS pour l'ingestion et l'analyse de corpus massifs.

## Principes

- Privilégier les ressources gratuites (Colab, GitHub Actions, Kaggle) pour les tâches intensives
- Conception asynchrone : les jobs s'exécutent en arrière-plan, les résultats sont persistés dans Dolt
- Résilience : reprendre automatiquement après une interruption (checkpoints)

## Ressources utilisées

| Plateforme | Usage | Limite gratuite |
|------------|-------|-----------------|
| Google Colab | Analyse corpus, ingestion Wikipedia | ~4h GPU/session |
| GitHub Actions | CI, déploiement docs, exports | 2 000 min/mois |
| Local (Totoro) | Développement, tests | Illimité |

## Corpus traités

- Gutenberg : 62 textes, ~3M mots, 14 langues
- Wikipedia : 973 articles, 2.2M mots, 14 langues (dumps complets disponibles : 63.6 GB compressé)

## Voir aussi

- [Avancement & feuille de route](../avancement.md)
- [Recherche](index.md)
