#!/usr/bin/env python3
"""
🚨 GitHub Workflow Emergency Doctor
===================================

Détecte et arrête automatiquement les workflows défectueux
Crée des issues GitHub pour traitement différé
"""

import subprocess
import json
import datetime
import sys
import os

class GitHubWorkflowEmergencyDoctor:
    def __init__(self):
        self.repo = "stephanedenis/PaniniFS"
        self.emergency_threshold = 3  # 3 échecs = urgence
        self.disabled_workflows = []
        self.failed_runs = []
        
    def get_failed_runs(self):
        """Récupère les runs en échec récents"""
        try:
            cmd = [
                "gh", "run", "list", 
                "--limit", "50",
                "--json", "status,conclusion,name,workflowName,createdAt,id"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                runs = json.loads(result.stdout)
                
                # Filtre les échecs récents (dernières 24h)
                now = datetime.datetime.now()
                failed_runs = []
                
                for run in runs:
                    if run.get('conclusion') == 'failure':
                        created = datetime.datetime.fromisoformat(
                            run['createdAt'].replace('Z', '+00:00')
                        )
                        
                        # Si échec dans les dernières 24h
                        if (now - created.replace(tzinfo=None)).days < 1:
                            failed_runs.append(run)
                
                return failed_runs
            
        except Exception as e:
            print(f"❌ Erreur récupération runs: {e}")
            return []
    
    def analyze_failure_patterns(self, failed_runs):
        """Analyse les patterns d'échec par workflow"""
        workflow_failures = {}
        
        for run in failed_runs:
            workflow = run.get('workflowName', 'unknown')
            
            if workflow not in workflow_failures:
                workflow_failures[workflow] = []
            
            workflow_failures[workflow].append(run)
        
        # Identifie les workflows critiques (≥3 échecs)
        critical_workflows = {}
        for workflow, runs in workflow_failures.items():
            if len(runs) >= self.emergency_threshold:
                critical_workflows[workflow] = runs
        
        return critical_workflows
    
    def disable_critical_workflows(self, critical_workflows):
        """Désactive les workflows critiques"""
        for workflow_name, runs in critical_workflows.items():
            print(f"🛑 Workflow critique détecté: {workflow_name}")
            print(f"   {len(runs)} échecs récents")
            
            # Tente de désactiver le workflow
            try:
                # Recherche le fichier workflow
                for run in runs:
                    if 'path' in run:
                        workflow_path = run['path']
                        break
                else:
                    # Devine le path basé sur le nom
                    workflow_path = f".github/workflows/{workflow_name.lower().replace(' ', '-')}.yml"
                
                # Désactive le workflow
                cmd = ["gh", "workflow", "disable", workflow_path]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ Workflow désactivé: {workflow_path}")
                    self.disabled_workflows.append({
                        'name': workflow_name,
                        'path': workflow_path,
                        'failures': len(runs),
                        'disabled_at': datetime.datetime.now().isoformat()
                    })
                else:
                    print(f"⚠️ Échec désactivation {workflow_path}: {result.stderr}")
                    
            except Exception as e:
                print(f"❌ Erreur désactivation {workflow_name}: {e}")
    
    def create_github_issue(self):
        """Crée une issue GitHub pour le traitement différé"""
        if not self.disabled_workflows:
            return
            
        title = f"🚨 URGENT: Workflows désactivés automatiquement - {datetime.date.today()}"
        
        body = f"""# 🚨 Intervention d'urgence - Workflows défectueux

## 📊 Résumé
Le GitHub Workflow Emergency Doctor a détecté et désactivé automatiquement des workflows défectueux.

## 🛑 Workflows désactivés ({len(self.disabled_workflows)})

"""
        
        for workflow in self.disabled_workflows:
            body += f"""### {workflow['name']}
- **Path**: `{workflow['path']}`
- **Échecs**: {workflow['failures']} en 24h
- **Désactivé**: {workflow['disabled_at']}

"""
        
        body += f"""
## 🎯 Actions requises

### 1. Diagnostic immédiat
- [ ] Analyser les logs d'échec de chaque workflow
- [ ] Identifier la cause racine (configuration, dépendances, etc.)
- [ ] Vérifier l'état des services externes (GitHub Pages, DNS, etc.)

### 2. Réparation
- [ ] Corriger les configurations défectueuses
- [ ] Tester les workflows en local si possible
- [ ] Mettre à jour les dépendances si nécessaire

### 3. Réactivation
- [ ] Réactiver les workflows corrigés
- [ ] Surveiller les nouveaux runs
- [ ] Ajuster le seuil d'urgence si nécessaire

## 🏕️ Impact Camping Strategy
Ces échecs bloquent le déploiement automatique. Priority absolue pour la deadline du 30 août.

## 🤖 Automatisation
- **Seuil d'urgence**: {self.emergency_threshold} échecs/24h
- **Doctor script**: `github_workflow_emergency_doctor.py`
- **Intervention**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📋 Linked Issues
- Epic #9: Camping Strategy - Externalisation Complète
- Issue #10: Colab Deployment Center (requis pour monitoring)
"""
        
        # Crée l'issue
        try:
            cmd = [
                "gh", "issue", "create",
                "--title", title,
                "--body", body,
                "--label", "camping-strategy,priority-critical,workflow-failure"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                issue_url = result.stdout.strip()
                print(f"✅ Issue créée: {issue_url}")
                return issue_url
            else:
                print(f"❌ Erreur création issue: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Erreur création issue: {e}")
    
    def run_emergency_intervention(self):
        """Lance l'intervention d'urgence complète"""
        print("🚨 GITHUB WORKFLOW EMERGENCY DOCTOR")
        print("===================================")
        print(f"⏰ {datetime.datetime.now()}")
        print("")
        
        # 1. Récupère les échecs récents
        print("🔍 Analyse des échecs récents...")
        failed_runs = self.get_failed_runs()
        if not failed_runs:
            print("✅ Aucun échec récent détecté")
            return
        
        print(f"📊 {len(failed_runs)} runs en échec trouvés")
        
        # 2. Analyse les patterns
        print("\n🔬 Analyse des patterns d'échec...")
        critical_workflows = self.analyze_failure_patterns(failed_runs)
        
        if not critical_workflows:
            print("✅ Aucun workflow critique détecté")
            return
        
        print(f"🚨 {len(critical_workflows)} workflows critiques identifiés")
        
        # 3. Désactive les workflows critiques
        print("\n🛑 Désactivation des workflows critiques...")
        self.disable_critical_workflows(critical_workflows)
        
        # 4. Crée l'issue GitHub
        print("\n📋 Création issue GitHub...")
        issue_url = self.create_github_issue()
        
        # 5. Résumé final
        print("\n🎯 INTERVENTION TERMINÉE")
        print("======================")
        print(f"🛑 Workflows désactivés: {len(self.disabled_workflows)}")
        if issue_url:
            print(f"📋 Issue GitHub: {issue_url}")
        print("")
        print("🏕️ Les workflows sont stabilisés pour la Camping Strategy")
        print("⚠️ Traitement différé requis via l'issue créée")

def main():
    doctor = GitHubWorkflowEmergencyDoctor()
    doctor.run_emergency_intervention()

if __name__ == "__main__":
    main()
