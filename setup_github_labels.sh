#!/bin/bash

# 🏷️ CONFIGURATION LABELS GITHUB - PaniniFS
# Basé sur GOVERNANCE/roadmap/GITHUB_PROJECT_PLAN.md

echo "🚀 Configuration labels GitHub pour PaniniFS..."

# 🔬 RECHERCHE & VALIDATION
gh label create "research:dhatu-validation" --color "8B5CF6" --description "Validation des 7 dhātu informationnels"
gh label create "research:compression" --color "8B5CF6" --description "Recherche compression sémantique"
gh label create "research:linguistics" --color "8B5CF6" --description "Analyses linguistiques et expérimentations"
gh label create "research:publications" --color "8B5CF6" --description "Publications académiques et articles"

# 💻 DÉVELOPPEMENT TECHNIQUE
gh label create "core:rust" --color "F97316" --description "Engine Rust compression"
gh label create "core:performance" --color "F97316" --description "Optimisations et benchmarks"
gh label create "core:api" --color "F97316" --description "APIs et interfaces"
gh label create "core:tests" --color "F97316" --description "Tests unitaires et intégration"

# 🌐 ÉCOSYSTÈME & INTÉGRATIONS
gh label create "ecosystem:python" --color "10B981" --description "Outils Python et intégrations"
gh label create "ecosystem:cloud" --color "10B981" --description "Intégrations cloud (Azure, Google Drive)"
gh label create "ecosystem:automation" --color "10B981" --description "Outils automation et workflows"
gh label create "ecosystem:integrations" --color "10B981" --description "Extensions et plugins externes"

# 🚀 OPÉRATIONS & INFRASTRUCTURE
gh label create "ops:deployment" --color "EF4444" --description "Déploiement et infrastructure"
gh label create "ops:monitoring" --color "EF4444" --description "Monitoring et observabilité"
gh label create "ops:security" --color "EF4444" --description "Sécurité et audit"
gh label create "ops:project-management" --color "EF4444" --description "Gestion projet et coordination"

# 📖 DOCUMENTATION
gh label create "docs:api" --color "3B82F6" --description "Documentation API"
gh label create "docs:user-guides" --color "3B82F6" --description "Guides utilisateurs"
gh label create "docs:architecture" --color "3B82F6" --description "Documentation architecture"
gh label create "docs:tutorials" --color "3B82F6" --description "Tutoriels et exemples"

# ⚙️ WORKFLOW & PROCESS
gh label create "workflow:triage" --color "6B7280" --description "Nouveau, besoin évaluation"
gh label create "workflow:blocked" --color "6B7280" --description "Bloqué, attend dépendance"
gh label create "workflow:ready" --color "6B7280" --description "Prêt pour développement"
gh label create "workflow:in-progress" --color "6B7280" --description "En cours développement"
gh label create "workflow:review" --color "6B7280" --description "En revue/validation"
gh label create "workflow:testing" --color "6B7280" --description "En phase de test"

# 🎯 PRIORITÉS
gh label create "priority:critical" --color "DC2626" --description "Critique, bloque le projet"
gh label create "priority:high" --color "EA580C" --description "Haute priorité"
gh label create "priority:medium" --color "D97706" --description "Priorité moyenne"
gh label create "priority:low" --color "65A30D" --description "Peut attendre"

# 👥 INTERVENANTS
gh label create "human:required" --color "8B5CF6" --description "Validation humaine requise"
gh label create "human:preferred" --color "A855F7" --description "Input humain préférable"
gh label create "ai:autonomous" --color "06B6D4" --description "IA peut gérer en autonomie"
gh label create "ai:assisted" --color "0891B2" --description "IA assistée par humain"

# 🏷️ TYPES GÉNÉRIQUES
gh label create "bug" --color "DC2626" --description "Quelque chose ne fonctionne pas"
gh label create "enhancement" --color "10B981" --description "Nouvelle fonctionnalité ou amélioration"
gh label create "question" --color "3B82F6" --description "Question ou demande d'information"
gh label create "duplicate" --color "6B7280" --description "Issue ou PR duplicate"
gh label create "good first issue" --color "22C55E" --description "Bon pour nouveaux contributeurs"
gh label create "help wanted" --color "0EA5E9" --description "Aide communautaire souhaitée"
gh label create "setup" --color "F59E0B" --description "Configuration initiale et setup"

echo "✅ Labels GitHub configurés avec succès !"
echo "🔍 Vérifiez sur: https://github.com/stephanedenis/PaniniFS/labels"
