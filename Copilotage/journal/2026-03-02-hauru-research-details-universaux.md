## Contexte

Enrichissement du site https://paninifs.org/ avec les détails des recherches récentes.
Demande spécifique : tableaux détaillés des résultats et sommaire des universaux sémantiques.

Suite directe de la session de mise à jour bilingue du matin (2026-03-02-hauru-website-update-bilingual.md).

## Décisions clés

### 1. Deux nouvelles pages de résultats (FR + EN)

**Constat** : La page `avancement.md` existante donne les chiffres clés, mais sans détail
par fichier, sans progression version-par-version, et sans explication des techniques.

**Décision** : Créer `docs/research/resultats-couverture.md` (FR) et
`docs/en/research/coverage-results.md` (EN) avec :
- Tableau global 12 langues × couverture (corpus élargi v4.8.16)
- Tableau 7 langues EU × couverture (corpus calibré v4.8.11)
- Tableau Wikipédia (14 langues, 100% présence atomique)
- Progression version par version : v4.8.2 → v4.8.11 (+6.1pp en 10 versions)
- Percées multilingues avec détails par fichier (ja/zh/ru/nl)
- Résultats notables par fichier (Dante, Zarathustra, Don Quijote, Verne, Beowulf...)
- Effets de bord croisés (spillover kanji/hanzi)
- Tableau infrastructure et reproductibilité

**Impact** : Documentation complète et traçable des résultats expérimentaux.

### 2. Deux nouvelles pages d'atomes (FR + EN)

**Constat** : La page `dhatu-framework.md` existante liste les 34 atomes dans un tableau
simple. Aucune page ne documente : les couches d'abstraction, les primitives NSM, les
correspondances Jackendoff/Pustejovsky, les dhātu sanscrit, les catégories ontologiques,
ni les exemples d'encodage.

**Décision** : Créer `docs/research/atomes-universaux.md` (FR) et
`docs/en/research/universal-atoms.md` (EN) avec :
- Tableaux complets par couche (3a prédicats, 3c émotions, 4 abstraits, 5 entités, 6 qualités)
- Pour chaque atome : catégorie, sens opérationnel, primitives NSM, dhātu sanscrit, Jackendoff
- Tableau des 7 opérateurs dhātu informationnels et mapping vers les 34 atomes
- Tableau des correspondances théoriques (NSM, Jackendoff, Pustejovsky, Pāṇini)
- Exemple d'encodage : "Le chat chasse la souris"

**Impact** : Page de référence complète pour les 34 atomes, disponible en FR et EN.

### 3. Mise à jour des pages `research/overview.md` (FR + EN)

**Constat** : Les pages `overview.md` existantes étaient des stubs sans métriques ni
liens vers les nouvelles pages de résultats.

**Décision** : Réécrire avec :
- Tableau synthétique des résultats clés (6 métriques)
- Structure par axe de recherche avec liens internes
- Sommaire des universaux sémantiques (catégories + correspondances théoriques)
- Liens vers les nouvelles pages

### 4. Mise à jour de la navigation `mkdocs.yml`

**Constat** : Les nouvelles pages n'étaient pas dans le nav → orphelines.

**Décision** : Réorganiser la section "Recherche" dans le nav :
- Vue d'ensemble
- Quoi de neuf
- **Résultats de couverture** ← nouveau
- **Atomes universaux (34)** ← nouveau
- Universaux sémantiques
- Expériences Dhātu v0.1 (déplacé dans la section Recherche)
- Inventaire Dhātu v0.1 (déplacé)
- Langage humain
- Compression sémantique

## Fichiers modifiés

| Fichier | Action | Raison |
|---------|--------|--------|
| `docs/research/resultats-couverture.md` | **CRÉÉ** | Tableaux détaillés de couverture |
| `docs/en/research/coverage-results.md` | **CRÉÉ** | English version |
| `docs/research/atomes-universaux.md` | **CRÉÉ** | Table complète des 34 atomes |
| `docs/en/research/universal-atoms.md` | **CRÉÉ** | English version |
| `docs/research/overview.md` | Réécrit | Liens vers nouvelles pages, métriques |
| `docs/en/research/overview.md` | Réécrit | English version |
| `mkdocs.yml` | Modifié | Nav section Recherche réorganisée |

## Tests effectués

### Build MkDocs local
```
mkdocs build --clean
Documentation built in 3.48 seconds
```

Aucune erreur. Pages générées :
- `site/research/atomes-universaux/`
- `site/research/resultats-couverture/`
- `site/en/research/coverage-results/`
- `site/en/research/universal-atoms/`

### Vérification contenu

Les pages EN utilisent le fallback FR pour :
- `en/research/atomes-universaux/` → fallback FR (normal, pas de page EN spécifique pour cet URL)
- `en/research/universal-atoms/` → page EN explicite ✓
- `en/research/coverage-results/` → page EN explicite ✓

## Prochaines étapes

1. Ajouter un tableau de **couverture Wikipedia par article** (liens vers CHILDES, UD)
2. Créer une page de **comparaison inter-corpus** (Gutenberg vs Wikipedia vs child-directed)
3. Valider les encodages Dhātu avec le corpus jouet `experiments/dhatu/`
4. Documenter les cas d'usage concrets de compression sémantique
