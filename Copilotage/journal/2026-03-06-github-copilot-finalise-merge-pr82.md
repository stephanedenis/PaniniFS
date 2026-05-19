# Finalisation du merge de PR #82 — Ajout sous-module RESEARCH

**Session** : 2026-03-06 · agent: github-copilot · branche: copilot/finalise-merge-de

## Contexte

La PR #82 (`chore/add-research-submodule`) visait à ajouter le sous-module RESEARCH en tant que sous-module Git propre (PaniniFS-Research). La branche avait divergé de `master` (30+ commits d'écart), la rendant « dirty » et non fusionnable directement. Cette session finalise le merge en extrayant les apports uniques de la PR #82 et en les appliquant à master.

## Décisions clés

| Constat | Décision | Impact |
|---------|----------|--------|
| PR #82 branch divergée de master (30+ commits) | Extraire les apports uniques et les appliquer sur master | Évite le conflit, apporte la valeur de la PR |
| Entrée `.gitmodules` RESEARCH déjà présente dans master | Réordonner seulement (RESEARCH après `modules/ontowave-app`) | Cohérence chronologique des sous-modules |
| 27 workflows `.yml.disabled` dans master | Les renommer en `.yml` comme prévu par la PR | Réactive les workflows CI/CD |
| `deploy-pages-mkdocs.yml` : version master corrigée, PR bugguée | Conserver la version master (correcte) | Pas de régression |
| `experiments/dhatu/` absent de master | Extraire de la branche PR et ajouter à master | Nouveau contenu de recherche dhātu |
| `governance/copilotage/knowledge/ESSENCE_PANINIFS.md` absent | Extraire de la branche PR et ajouter à master | Documentation de l'essence du projet |
| `cleanup/manifest.txt` absent de master | Extraire de la branche PR et ajouter | Traçabilité des chemins à nettoyer |
| `.gitignore` : patterns manquants | Ajouter `cleanup/local_untracked_backup_*/`, `cleanup/**/*.tgz`, `artifacts/`, `*.pid` | Meilleure exclusion des artefacts locaux |
| `data/ecosystem.yml` RESEARCH : description et tags incomplets | Mettre à jour description et tags | Meilleure documentation de l'écosystème |

## Fichiers modifiés

| Fichier | Raison |
|---------|--------|
| `.github/workflows/*.yml.disabled` → `*.yml` (×26) | Réactivation des workflows CI/CD selon l'intention de la PR #82 |
| `.github/workflows/copilotage-journal-check.yml` | Mise à jour avec version complète (trigger PR réactivé) |
| `.github/workflows/deploy-pages-mkdocs.yml.disabled` | Suppression (doublon, version active conservée) |
| `.gitmodules` | Réordonnancement : RESEARCH déplacé après `modules/ontowave-app` |
| `.gitignore` | Ajout de patterns manquants : `cleanup/local_untracked_backup_*/`, `cleanup/**/*.tgz`, `artifacts/`, `*.pid` |
| `data/ecosystem.yml` | Mise à jour description et tags du sous-module RESEARCH |
| `experiments/dhatu/` (28 fichiers) | Ajout du harness d'expérimentation dhātu (validator.py, report.py, JSON) |
| `governance/copilotage/knowledge/ESSENCE_PANINIFS.md` | Ajout du fichier de connaissance sur l'essence de PaniniFS |
| `cleanup/manifest.txt` | Ajout du manifeste de nettoyage (chemins candidats à suppression) |
| `Copilotage/journal/INDEX.md` | Mise à jour de l'index |

## Tests effectués

- Vérification manuelle des fichiers extraits de la branche `chore/add-research-submodule`
- Vérification que `deploy-pages-mkdocs.yml` (version corrigée) est conservé
- Vérification de la cohérence du `.gitmodules` après réordonnancement
- Vérification du `.gitignore` (patterns ajoutés sans supprimer les existants)

## Prochaines étapes

- Fusionner la PR `copilot/finalise-merge-de` dans master
- Fermer la PR #82 comme obsolète (ses apports ont été intégrés)
- Vérifier que les workflows nouvellement activés ne causent pas de problèmes CI
