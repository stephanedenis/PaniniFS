# Instructions Copilot - Panini-FS

📍 **CONTEXTE LOCAL :** Tu te trouves actuellement dans le sous-module `modules/core/filesystem`.
**Mission stricte :** Stockage bit-perfect et intégration FUSE3.

⚠️ **RÈGLES D'ANTI-DÉBORDEMENT :**
- Gère uniquement les I/O fichier. Pas d'analyse sémantique.
- Ne recrée jamais une logique qui appartient à un autre module de l'écosystème.
- Ce module interagit avec le reste de l'écosystème via des interfaces claires.

🗺️ **CARTOGRAPHIE DE L'ÉCOSYSTÈME PANINI :**
1. **Hub/Orchestrateur** (Racine) : Lien entre les modules. Ne contient que l'orchestration (`src/panini_colabmcp`).
2. **Panini-FS** (`modules/core/filesystem`) : Stockage FUSE3.
3. **Panini-SemanticCore** (`modules/core/semantic`) : Extraction dhātu.
4. **OntoWave** (`modules/ontowave`) : UX et UI.
5. **Panini-AttributionRegistry** (`modules/data/attribution`) : Traçabilité et provenance.
6. **Panini-AutonomousMissions** (`modules/missions/autonomous`) : Workflows IA.
7. **Panini-PublicationEngine** (`modules/publication/engine`) : Formatage/Export.
8. **Panini-UltraReactive** (`modules/reactive/ultra-reactive`) : Streaming temps réel.
9. **Panini-CloudOrchestrator** (`modules/orchestration/cloud`) : Infra et Déploiement.
10. **Panini-Research** (`research`) : Brouillons et laboratoire.

🔗 **RÈGLES GLOBALES :**
Pour les conventions de code, la journalisation OBLIGATOIRE (`docs/journal-de-bord`) et l'autonomie, **réfère-toi impérativement aux directives globales présentes dans le Hub parent**.
