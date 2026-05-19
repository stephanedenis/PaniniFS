# Convention d’identification des agents

Objectif: distinguer les PRs par agent pour permettre des validations croisées.

## Comment marquer une PR
- Ajoutez un label unique de provenance: `provenance:host=<HOST>,pid=<PID>,agent=GitHubCopilot,model=<MODELE>,owner=<human|agent>`.
- Optionnel: ajoutez `[model:NOM]` (ex: `[model:gpt-4o]`, `[model:claude-3.5]`).
- Optionnel: pour lever toute ambiguïté d’attribution, ajoutez `[owner:human]` si la PR est portée par un humain (sinon propriétaire inféré côté automatisation quand `journal`/`model` présents).
- À défaut, utilisez un nom de branche: `agents/HOST/ma-feature` (moins précis; ne remplace pas le PID).

## Automatisation
- Le workflow `.github/workflows/label-agent.yml` peut ajouter des labels complémentaires (`agent:<host>`, `model:<nom>`).
- Le workflow `validate-agent-provenance.yml` échoue si le label `provenance:...` est absent ou incomplet.
- Exception: ajoutez le label `copilotage-exempt` pour bypass (cas rares).

## Bonnes pratiques
- HOST = hostname court (ex: `totoro`). PID = PID du process VS Code (ex: `17771`).
- `model` = type d’agent IA utilisé (ex: `gpt-4o`, `claude-3.5`, `mistral-large`).
- Garder le même ID sur toute la durée d’une session.
## Journal de bord obligatoire

**Règle absolue** : Toute session de travail (humaine ou IA) DOIT produire une
entrée dans `Copilotage/journal/` avant de pouvoir committer.

### Pour les agents IA

1. **En début de session** : Lire `Copilotage/journal/INDEX.md` pour connaître le contexte récent.
2. **Pendant la session** : Documenter les décisions au fur et à mesure.
3. **Avant le commit** : Créer ou mettre à jour un fichier journal du jour :
   - Nom : `YYYY-MM-DD-<host>-<description-courte>.md`
   - Emplacement : `Copilotage/journal/`
   - Sections obligatoires : **Contexte**, **Décisions clés**, **Fichiers modifiés**,
     **Tests effectués**, **Prochaines étapes**
4. **Mettre à jour INDEX.md** : Ajouter une ligne pointant vers la nouvelle entrée.
5. **Inclure le journal dans le commit** : Le fichier journal DOIT faire partie des
   fichiers stagés (`git add`) avec les autres changements.

### Contenu minimal d'une entrée

```markdown
# 📓 Journal de session — YYYY-MM-DD

**Host**: <hostname>
**Agent**: <nom et modèle>
**Humain**: <nom>

## Contexte
<Pourquoi cette session, quel objectif>

## Décisions clés
<Chaque décision avec constat → décision → impact>

## Fichiers modifiés
<Liste des fichiers touchés et pourquoi>

## Tests effectués
<Résultats des validations>

## Prochaines étapes
<Ce qui reste à faire>
```

### Enforcement

Un hook `pre-commit` vérifie qu'au moins un fichier `Copilotage/journal/YYYY-MM-DD*.md`
(avec la date du jour) est présent dans les fichiers stagés. Le commit est **refusé**
si aucune entrée journal n'est trouvée.

Pour bypass exceptionnel (ex: hotfix urgent) : `git commit --no-verify`