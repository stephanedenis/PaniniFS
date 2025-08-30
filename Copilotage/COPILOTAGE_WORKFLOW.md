# Flux de travail standard pour agents IA

Objectif: garantir que chaque travail suit une discipline traçable via GitHub.

Règles obligatoires:
- Chaque travail démarre par une tâche (issue) GitHub.
- Une branche dédiée est créée: `<type>/issue-<num>-<slug>` (ex: `feat/issue-42-vision-agent`).
- Tous les commits référencent l’issue: `... (#<num>)` ou `Refs #<num>`.
- Une Pull Request relie la branche à `master/main` et ferme l’issue (`Closes #<num>`).
- Quality gates dans la PR: build/lint/tests, checklist "Done".

Pratiques recommandées:
- Petites PRs, descriptions concises, changelog clair.
- CI minimale dans sous-modules; lint (ruff/black) à venir.

Automatisation:
- Utiliser `Copilotage/scripts/devops/gh_task_init.sh` pour ouvrir une issue et créer la branche.

Journalisation Copilotage (obligatoire):
- À chaque session, ajouter un fichier `Copilotage/journal/<date>-<host>-pid<pid>-<session>.md`.
- Contenu minimal: Contexte, Décisions & actions clés, Liens (issues/PR), Tests/quality gates, Prochaines étapes.
- Nommage: `YYYY-MM-DD-<host>-pid<pid>-<slug>.md` (host: ex. Hauru; pid: pid VSCode si dispo, sinon shell).

Cheatsheet:
- Issue types: feat | fix | docs | chore | refactor | perf | test | ci
- Slug court, kebab-case.

---

Mainteneur: consigner tout écart dans l’issue.
