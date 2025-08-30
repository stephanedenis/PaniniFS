# Vue d’ensemble des modules et projet parent Panini

Constat: PaniniFS = sous-projet filesystem. Un projet parent "Panini" devrait regrouper vision, recherche, outils et PaniniFS.

Parent Panini (proposé)
- Repos parent: Panini (vision, gouvernance globale, publications, roadmaps)
- Subprojects: PaniniFS (filesystem), SemanticCore, PublicationEngine, CloudOrchestrator, UltraReactive, CoLabController, etc.
- Docs: site unifié (mkdocs), pages par sous-projet.

Sous-modules actuels (rappel)
- autonomous-missions — orchestration d’actions
- semantic-core — noyau sémantique (dhātu, indexation)
- publication-engine — pipelines éditoriaux (Medium/Leanpub)
- cloud-orchestrator — déploiements/infra
- ultra-reactive — monitoring/doctor
- colab-controller — automatisation Colab

À faire
- Spécifier les interfaces minimales entre modules (contrats, types, événements).
- Créer le repo parent et déplacer/mirroir docs générales.
