# Copilot Instructions — PaniniFS

## Règle n°1 : Journal de bord obligatoire

**Chaque session de travail DOIT produire une entrée dans `Copilotage/journal/`.**

### Procédure

1. **En début de session** : Lire `Copilotage/journal/INDEX.md` et les dernières
   entrées pour connaître le contexte récent du projet.
2. **Pendant la session** : Accumuler les décisions prises, fichiers modifiés,
   tests effectués.
3. **Avant tout commit** : Créer (ou mettre à jour) un fichier journal du jour :
   - **Nom** : `YYYY-MM-DD-<host>-<description-courte>.md`
   - **Emplacement** : `Copilotage/journal/`
   - **Sections obligatoires** :
     - `## Contexte` — Pourquoi cette session
     - `## Décisions clés` — Chaque décision avec constat → décision → impact
     - `## Fichiers modifiés` — Liste et raison
     - `## Tests effectués` — Résultats des validations
     - `## Prochaines étapes` — Ce qui reste à faire
4. **Inclure le journal dans le commit** : `git add Copilotage/journal/YYYY-MM-DD*.md`
5. **Mettre à jour INDEX.md** si c'est une nouvelle entrée.

### Pourquoi

Un hook `pre-commit` **bloquera le commit** si aucun fichier
`Copilotage/journal/<date-du-jour>*.md` n'est stagé. Cette règle assure la traçabilité
de toutes les décisions architecturales et évite les trous de documentation.

## Règle n°2 : Identification des agents

Suivre les conventions de `Copilotage/AGENT_CONVENTION.md` pour l'identification
(label de provenance, hostname, PID, modèle).

## Règle n°3 : Base Dolt = cache calculé

La base de données Dolt (`panini-unified-db`, `panini-concepts-db`) est un
**cache calculé**, pas du capital accumulé. Elle est entièrement reconstructible
via le pipeline déterministe. Ne pas traiter les fichiers `.dolt/` comme précieux.

## Règle n°4 : Ontologie à 4 catégories

Le système d'atomes couvre 4 catégories ontologiques :
- **ENT** (entités) — objets, substances
- **PROC** (processus) — actions, événements, émotions
- **QUAL** (qualités) — propriétés, attributs
- **ABS** (abstraits) — relations, structures, mesures

Tout nouvel atome doit être mappé dans les 6 dictionnaires de
`import_panlang_v2.py` : ATOM_DIMENSIONS, ATOM_NSM, ATOM_JACKENDOFF,
ATOM_PUSTEJOVSKY, ATOM_DHATU, et ATOM_KEYWORDS dans
`gutenberg_multilingual_validator.py`.
