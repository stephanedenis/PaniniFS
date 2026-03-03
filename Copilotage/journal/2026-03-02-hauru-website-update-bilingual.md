## Contexte

Mise à jour du site https://paninifs.org/ (dossier `docs/`) pour refléter les travaux de février 2026 et corriger le fonctionnement bilingue FR/EN.

Le site utilisait `mkdocs-static-i18n` en mode `suffix` (par défaut) ce qui ne permettait pas d'utiliser la structure `docs/en/` pour les traductions anglaises. Les pages anglaises dans `docs/en/` étaient traitées comme des pages orphelines non reliées à la navigation.

## Décisions clés

### 1. Activation du mode `folder` dans mkdocs-static-i18n

**Constat** : La config `mkdocs.yml` utilisait `mkdocs-static-i18n` v1.3.1 sans `docs_structure: folder`, donc le plugin cherchait des fichiers `.fr.md`/`.en.md` et ignorait `docs/en/`. Les pages `docs/en/` apparaissaient dans le build comme "not in nav".

**Décision** : Ajouter `docs_structure: folder` dans le bloc `i18n` du `mkdocs.yml`. Avec cette option, le plugin construit `/` depuis `docs/` et `/en/` depuis `docs/en/`, avec fallback sur la langue par défaut si un fichier anglais est absent.

**Impact** : La navigation bilingue fonctionne correctement. Les 34 pages anglaises existantes dans `docs/en/` sont maintenant servies à `/en/<page>/`.

### 2. Correction du bug YAML LinkedIn

**Constat** : `link: https://www.linkedin.com/in/neuronspikes` était mal indenté dans `extra.social` — placé au niveau `extra` au lieu d'être sous l'item LinkedIn.

**Décision** : Corriger l'indentation.

**Impact** : L'icône LinkedIn dans le footer est maintenant correctement liée.

### 3. Correction de l'erreur de build `cloud-free-compute.md`

**Constat** : `docs/research/cloud-free-compute.md` utilisait `{% include-markdown "../../RESEARCH/cloud-processing/FREE_COMPUTE_STRATEGY.md" %}` mais le sous-module RESEARCH n'est pas initialisé → erreur BUILD bloquante.

**Décision** : Remplacer l'include par un contenu autonome résumant la stratégie de calcul gratuit.

**Impact** : Build passe sans erreur.

### 4. Correction des liens inter-langue cassés

**Constat** : Plusieurs fichiers dans `docs/` et `docs/en/` utilisaient des liens relatifs vers `../en/livre/...` qui ne fonctionnent plus avec le mode `folder`.

**Décision** : Remplacer par des liens absolus (`/en/livre/lecture-integrale/`) ou des liens relatifs corrects (`../livre/lecture-integrale.md`).

**Fichiers corrigés** :
- `docs/livre/index.md`
- `docs/publications.md`
- `docs/en/research/whats-new.md`
- `docs/en/research/overview.md`
- `docs/en/index.md` (lien `../modules/index.md` → `modules/index.md`)

### 5. Mise à jour du contenu avec les travaux de février 2026

**Constat** : Les pages clés (`index.md`, `avancement.md`, `research/whats-new.md`, `dhatu-framework.md`) étaient figées à septembre 2025 et ne reflétaient pas les avancées majeures de février 2026.

**Décision** : Mettre à jour les 8 pages clés (FR + EN) avec les résultats validés :
- 34 atomes universels sur 14 langues, 7/7 EU ≥ 90%
- Percées ja (+55pp), zh (+40pp), ru (+40pp), nl (+28pp)
- Couverture globale 76.8% sur ~8M mots
- PaniniWeb Rust v0.1 (4 crates, 71 tests, P2P libp2p)
- Roadmap 6 phases

### 6. Création des pages anglaises manquantes

**Constat** : `docs/en/livre/index.md` et `docs/en/dashboard.md` manquaient → les URLs `/en/livre/` et `/en/dashboard/` retombaient sur le français (comportement de fallback OK mais non optimal).

**Décision** : Créer ces deux pages avec contenu anglais adapté.

## Fichiers modifiés

| Fichier | Action | Raison |
|---------|--------|--------|
| `mkdocs.yml` | Modifié | `docs_structure: folder` + fix LinkedIn YAML |
| `docs/research/cloud-free-compute.md` | Remplacé | Suppression de l'include RESEARCH cassé |
| `docs/index.md` | Mis à jour | Résultats Feb 2026 dans "Actualités" |
| `docs/en/index.md` | Mis à jour | English home + fix lien modules |
| `docs/avancement.md` | Reécrit | Métriques Feb 2026, tableau percées, roadmap 6 phases |
| `docs/en/avancement.md` | Reécrit | English version |
| `docs/research/whats-new.md` | Reécrit | Percées multilingues, état global v4.8.16 |
| `docs/en/research/whats-new.md` | Reécrit | English version |
| `docs/dhatu-framework.md` | Reécrit | 7 dhātu + 34 atomes + couverture validée |
| `docs/en/dhatu-framework.md` | Reécrit | English version |
| `docs/livre/index.md` | Corrigé | Lien EN cassé → lien absolu |
| `docs/publications.md` | Corrigé | Lien EN cassé → lien absolu |
| `docs/en/research/whats-new.md` | Corrigé | Lien livre relatif cassé |
| `docs/en/research/overview.md` | Corrigé | Lien livre relatif cassé |
| `docs/en/livre/index.md` | Créé | Page index anglaise manquante |
| `docs/en/dashboard.md` | Créé | Dashboard anglais manquant |

## Tests effectués

### Build MkDocs local

```
mkdocs build --clean
```

Résultat : **Documentation built in 2.84 seconds** — aucune erreur.

Warnings restants (acceptables) :
- Avertissement MkDocs 2.0 générique (non bloquant, pas actionnable)
- git-revision-date pour les 2 nouveaux fichiers (normal avant commit)

### Vérification du site généré

- `site/index.html` : contient "Français" et "English" dans le sélecteur de langue ✓
- `site/en/index.html` : contient "Français" et "English" ✓
- `site/en/avancement/index.html` : contient "74.1%" et "Multilingual breakthroughs" ✓
- `site/en/` : 34+ pages servies correctement ✓

## Prochaines étapes

1. **Réactiver le workflow CI** `deploy-pages-mkdocs.yml.disabled` → `.yml` (ou déclencher manuellement le déploiement)
2. **Sanskrit (sa)** : 10.7% de couverture — problème structurel IAST non résolu
3. **Russe/Néerlandais** : 56%/56% — marge de progression avec 3ème vague de vocabulaire
4. **Emballage Python** : `panini/` package + `pyproject.toml` + CLI (Phase 0-1 de la roadmap)
5. **Mettre à jour INDEX.md** dans Copilotage/journal/
