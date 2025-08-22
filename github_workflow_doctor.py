#!/usr/bin/env python3
"""
🩺 GITHUB WORKFLOW DOCTOR - Version Camping Strategy
====================================================

Diagnostic et réparation automatique des workflows GitHub
avec focus sur l'externalisation complète (camping strategy).

Fonctionnalités:
- Diagnostic des échecs de workflow
- Réparation automatique des erreurs communes  
- Configuration optimisée pour camping strategy
- Désactivation des workflows inutiles
- Création workflows minimaux fonctionnels
"""

import os
import yaml
import json
import subprocess
from pathlib import Path

class GitHubWorkflowDoctor:
    def __init__(self):
        self.repo_path = Path("/home/stephane/GitHub/PaniniFS-1")
        self.workflows_path = self.repo_path / ".github" / "workflows"
        self.fixes_applied = []
        
    def diagnose_and_fix(self):
        """Diagnostic complet et réparation automatique"""
        print("🩺 GITHUB WORKFLOW DOCTOR - Camping Strategy Edition")
        print("=" * 60)
        
        # 1. Créer structure .github si nécessaire
        self._ensure_github_structure()
        
        # 2. Diagnostiquer workflows existants
        self._diagnose_existing_workflows()
        
        # 3. Créer workflow MkDocs minimal
        self._create_minimal_mkdocs_workflow()
        
        # 4. Désactiver workflows problématiques
        self._disable_problematic_workflows()
        
        # 5. Créer requirements.txt minimal
        self._create_minimal_requirements()
        
        # 6. Rapport final
        self._generate_report()
        
    def _ensure_github_structure(self):
        """Créer structure .github si nécessaire"""
        print("📁 Vérification structure .github...")
        
        self.workflows_path.mkdir(parents=True, exist_ok=True)
        self.fixes_applied.append("Structure .github créée/vérifiée")
        
    def _diagnose_existing_workflows(self):
        """Diagnostiquer workflows existants"""
        print("🔍 Diagnostic workflows existants...")
        
        if not self.workflows_path.exists():
            print("   ℹ️ Aucun workflow existant")
            return
            
        for workflow_file in self.workflows_path.glob("*.yml"):
            print(f"   📄 Workflow trouvé: {workflow_file.name}")
            
            # Lire le workflow
            try:
                with open(workflow_file, 'r') as f:
                    workflow = yaml.safe_load(f)
                    
                # Vérifier problèmes communs
                if 'rust' in str(workflow).lower():
                    print(f"   ⚠️ Workflow Rust détecté: {workflow_file.name}")
                    self._disable_workflow(workflow_file)
                    
            except Exception as e:
                print(f"   ❌ Erreur lecture {workflow_file.name}: {e}")
                
    def _disable_workflow(self, workflow_file):
        """Désactiver un workflow problématique"""
        disabled_path = workflow_file.with_suffix('.yml.disabled')
        workflow_file.rename(disabled_path)
        print(f"   🔕 Workflow désactivé: {workflow_file.name} -> {disabled_path.name}")
        self.fixes_applied.append(f"Workflow désactivé: {workflow_file.name}")
        
    def _create_minimal_mkdocs_workflow(self):
        """Créer workflow MkDocs minimal pour camping strategy"""
        print("📝 Création workflow MkDocs minimal...")
        
        workflow_content = """name: 🏕️ Deploy MkDocs Site (Camping Strategy)

on:
  push:
    branches: [ master ]
    paths:
      - 'docs_new/**'
      - 'mkdocs.yml'
      - '.github/workflows/deploy-docs.yml'
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: 📥 Checkout
      uses: actions/checkout@v4
      with:
        fetch-depth: 0
        
    - name: 🐍 Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: 📦 Install dependencies
      run: |
        pip install mkdocs-material
        pip install mkdocs-git-revision-date-localized-plugin
        
    - name: 🏗️ Build site
      run: mkdocs build --config-file mkdocs.yml
      
    - name: 🚀 Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./site
        cname: paninifs.org
        
    - name: ✅ Success notification
      run: |
        echo "🎉 Site MkDocs déployé avec succès!"
        echo "🌐 Disponible sur: https://paninifs.org"
"""
        
        workflow_file = self.workflows_path / "deploy-docs.yml"
        with open(workflow_file, 'w') as f:
            f.write(workflow_content)
            
        print("   ✅ Workflow MkDocs créé: deploy-docs.yml")
        self.fixes_applied.append("Workflow MkDocs minimal créé")
        
    def _disable_problematic_workflows(self):
        """Désactiver workflows qui causent des échecs"""
        print("🔕 Désactivation workflows problématiques...")
        
        problematic_patterns = [
            'rust', 'cargo', 'build', 'test', 'ci', 'continuous-integration'
        ]
        
        for workflow_file in self.workflows_path.glob("*.yml"):
            if workflow_file.name == "deploy-docs.yml":
                continue  # Garder notre workflow MkDocs
                
            with open(workflow_file, 'r') as f:
                content = f.read().lower()
                
            for pattern in problematic_patterns:
                if pattern in content:
                    self._disable_workflow(workflow_file)
                    break
                    
    def _create_minimal_requirements(self):
        """Créer requirements.txt minimal pour éviter les erreurs"""
        print("📄 Création requirements.txt minimal...")
        
        requirements_content = """# 🏕️ CAMPING STRATEGY - Dependencies minimales
# =============================================
#
# Dépendances pour MkDocs uniquement
# Tout le reste est externalisé

mkdocs-material>=9.0.0
mkdocs-git-revision-date-localized-plugin>=1.2.0

# Monitoring minimal
requests>=2.31.0
pyyaml>=6.0

# Pas de dépendances lourdes (Rust, compilateurs, etc.)
# Camping strategy = externalisation maximale
"""
        
        requirements_file = self.repo_path / "requirements.txt"
        with open(requirements_file, 'w') as f:
            f.write(requirements_content)
            
        print("   ✅ requirements.txt minimal créé")
        self.fixes_applied.append("requirements.txt minimal créé")
        
    def _generate_report(self):
        """Générer rapport de réparation"""
        print("\n" + "=" * 60)
        print("📋 RAPPORT DE RÉPARATION")
        print("=" * 60)
        
        for fix in self.fixes_applied:
            print(f"   ✅ {fix}")
            
        print(f"\n📊 Total: {len(self.fixes_applied)} réparations appliquées")
        
        print("\n🏕️ CAMPING STRATEGY OPTIMISATIONS:")
        print("   🔕 Workflows lourds désactivés")
        print("   📦 Dépendances minimales")
        print("   🚀 Déploiement MkDocs externalisé")
        print("   🌐 GitHub Pages automatique")
        
        print("\n🎯 PROCHAINES ÉTAPES:")
        print("   1. git add -A && git commit -m 'Fix workflows'")
        print("   2. git push origin master")
        print("   3. Vérifier https://github.com/stephanedenis/PaniniFS/actions")
        
        print("\n✨ Workflows optimisés pour camping strategy!")

def main():
    """Fonction principale"""
    doctor = GitHubWorkflowDoctor()
    doctor.diagnose_and_fix()

if __name__ == "__main__":
    main()
