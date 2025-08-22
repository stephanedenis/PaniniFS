#!/usr/bin/env python3
"""
🤖 GitHub Workflow Doctor Autonome
=================================

Surveillance continue 24/7 des workflows GitHub
Intervention automatique en cas de défaillance
"""

import subprocess
import json
import datetime
import time
import sys
import os
import logging
from pathlib import Path

class AutonomousWorkflowDoctor:
    def __init__(self):
        self.repo = "stephanedenis/PaniniFS"
        self.check_interval = 300  # 5 minutes
        self.emergency_threshold = 3  # 3 échecs = intervention
        self.max_interventions_per_hour = 2  # Limite pour éviter le spam
        
        # Configuration des logs
        self.setup_logging()
        
        # État interne
        self.last_interventions = []
        self.monitored_workflows = set()
        self.status_file = Path("doctor_status.json")
        
        self.logger.info("🤖 Doctor Autonome initialisé")
        
    def setup_logging(self):
        """Configure le système de logs"""
        log_dir = Path("OPERATIONS/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"workflow_doctor_{datetime.date.today()}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger("WorkflowDoctor")
    
    def check_rate_limit(self):
        """Vérifie si on peut faire une intervention (rate limiting)"""
        now = datetime.datetime.now()
        one_hour_ago = now - datetime.timedelta(hours=1)
        
        # Nettoie les interventions anciennes
        self.last_interventions = [
            intervention for intervention in self.last_interventions
            if intervention > one_hour_ago
        ]
        
        return len(self.last_interventions) < self.max_interventions_per_hour
    
    def get_workflow_runs(self):
        """Récupère les runs récents de tous les workflows"""
        try:
            cmd = [
                "gh", "run", "list",
                "--limit", "100",
                "--json", "status,conclusion,name,workflowName,createdAt,databaseId,url"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                self.logger.error(f"Erreur récupération runs: {result.stderr}")
                return []
                
        except Exception as e:
            self.logger.error(f"Exception get_workflow_runs: {e}")
            return []
    
    def analyze_workflow_health(self, runs):
        """Analyse la santé des workflows"""
        now = datetime.datetime.now()
        last_hour = now - datetime.timedelta(hours=1)
        
        workflow_stats = {}
        
        for run in runs:
            workflow_name = run.get('workflowName', 'unknown')
            
            # Parse la date de création
            try:
                created_at = datetime.datetime.fromisoformat(
                    run['createdAt'].replace('Z', '+00:00')
                ).replace(tzinfo=None)
            except:
                continue
            
            # Focus sur la dernière heure
            if created_at < last_hour:
                continue
            
            if workflow_name not in workflow_stats:
                workflow_stats[workflow_name] = {
                    'total': 0,
                    'failures': 0,
                    'successes': 0,
                    'in_progress': 0,
                    'recent_runs': []
                }
            
            stats = workflow_stats[workflow_name]
            stats['total'] += 1
            stats['recent_runs'].append(run)
            
            conclusion = run.get('conclusion')
            status = run.get('status')
            
            if conclusion == 'failure':
                stats['failures'] += 1
            elif conclusion == 'success':
                stats['successes'] += 1
            elif status == 'in_progress':
                stats['in_progress'] += 1
        
        return workflow_stats
    
    def detect_critical_workflows(self, workflow_stats):
        """Détecte les workflows en état critique"""
        critical_workflows = {}
        
        for workflow_name, stats in workflow_stats.items():
            # Ignore les workflows GitHub internes (non modifiables)
            if workflow_name in ['pages-build-deployment', 'Dependabot Updates']:
                continue
                
            failure_rate = stats['failures'] / max(stats['total'], 1)
            
            # Critères de criticité
            is_critical = (
                stats['failures'] >= self.emergency_threshold or
                (stats['total'] >= 5 and failure_rate > 0.8)
            )
            
            if is_critical:
                critical_workflows[workflow_name] = {
                    'stats': stats,
                    'failure_rate': failure_rate,
                    'severity': 'high' if stats['failures'] >= 5 else 'medium'
                }
                
                self.logger.warning(
                    f"🚨 Workflow critique: {workflow_name} "
                    f"({stats['failures']} échecs, {failure_rate:.1%} taux)"
                )
        
        return critical_workflows
    
    def disable_workflow(self, workflow_name, recent_runs):
        """Désactive un workflow problématique"""
        self.logger.info(f"🛑 Tentative désactivation: {workflow_name}")
        
        # Essaie de trouver le path du workflow
        workflow_path = None
        
        # Méthode 1: Chercher dans les runs récents
        for run in recent_runs:
            if 'path' in run:
                workflow_path = run['path']
                break
        
        # Méthode 2: Devine basé sur le nom
        if not workflow_path:
            safe_name = workflow_name.lower().replace(' ', '-').replace('🏕️', '').strip()
            possible_paths = [
                f".github/workflows/{safe_name}.yml",
                f".github/workflows/{workflow_name.lower()}.yml",
                f".github/workflows/deploy-docs.yml",  # Cas spécifique
                f".github/workflows/camping-status.yml"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    workflow_path = path
                    break
        
        if not workflow_path:
            self.logger.error(f"❌ Path non trouvé pour {workflow_name}")
            return False
        
        try:
            # Désactive le workflow
            cmd = ["gh", "workflow", "disable", workflow_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info(f"✅ Workflow désactivé: {workflow_path}")
                
                # Renomme en .disabled
                if os.path.exists(workflow_path):
                    disabled_path = f"{workflow_path}.disabled"
                    os.rename(workflow_path, disabled_path)
                    self.logger.info(f"📁 Renommé: {workflow_path} → {disabled_path}")
                
                return True
            else:
                self.logger.error(f"❌ Échec désactivation {workflow_path}: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Exception désactivation {workflow_name}: {e}")
            return False
    
    def create_intervention_issue(self, disabled_workflows):
        """Crée une issue pour documenter l'intervention"""
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        
        title = f"🤖 AUTO: Doctor désactivation workflows - {timestamp}"
        
        body = f"""# 🤖 Intervention Automatique du Doctor

## ⏰ Timestamp
{datetime.datetime.now().isoformat()}

## 🚨 Workflows désactivés automatiquement ({len(disabled_workflows)})

"""
        
        for workflow_name, info in disabled_workflows.items():
            stats = info['stats']
            body += f"""### {workflow_name}
- **Échecs récents**: {stats['failures']} 
- **Taux d'échec**: {info['failure_rate']:.1%}
- **Sévérité**: {info['severity']}
- **Total runs (1h)**: {stats['total']}

"""
        
        body += f"""
## 🎯 Actions effectuées
- [x] Détection automatique des workflows critiques
- [x] Désactivation immédiate 
- [x] Renommage en .disabled
- [x] Documentation de l'intervention

## 🔄 Monitoring continu
Le Doctor continue sa surveillance toutes les 5 minutes.

## 📋 Linked Issues
- Epic #9: Camping Strategy
- Issue #15: Workflows défectueux précédents

## 🤖 Autonomie
Cette intervention est **100% automatique** - aucune action manuelle requise.
"""
        
        try:
            cmd = [
                "gh", "issue", "create",
                "--title", title,
                "--body", body,
                "--label", "camping-strategy,workflow-failure,automated"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                issue_url = result.stdout.strip()
                self.logger.info(f"📋 Issue créée: {issue_url}")
                return issue_url
            else:
                self.logger.error(f"❌ Erreur création issue: {result.stderr}")
                
        except Exception as e:
            self.logger.error(f"❌ Exception création issue: {e}")
        
        return None
    
    def save_status(self, status_data):
        """Sauvegarde l'état du doctor"""
        try:
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde status: {e}")
    
    def load_status(self):
        """Charge l'état précédent du doctor"""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Erreur chargement status: {e}")
        
        return {}
    
    def monitoring_cycle(self):
        """Un cycle complet de monitoring"""
        self.logger.info("🔍 Début cycle monitoring")
        
        # 1. Récupère les runs
        runs = self.get_workflow_runs()
        if not runs:
            self.logger.warning("⚠️ Aucun run récupéré")
            return
        
        # 2. Analyse la santé
        workflow_stats = self.analyze_workflow_health(runs)
        self.logger.info(f"📊 {len(workflow_stats)} workflows analysés")
        
        # 3. Détecte les workflows critiques
        critical_workflows = self.detect_critical_workflows(workflow_stats)
        
        if not critical_workflows:
            self.logger.info("✅ Aucun workflow critique détecté")
            return
        
        # 4. Vérifie le rate limiting
        if not self.check_rate_limit():
            self.logger.warning("⏸️ Rate limit atteint - intervention différée")
            return
        
        # 5. Intervention
        self.logger.warning(f"🚨 {len(critical_workflows)} workflows critiques - INTERVENTION")
        
        disabled_workflows = {}
        for workflow_name, info in critical_workflows.items():
            if self.disable_workflow(workflow_name, info['stats']['recent_runs']):
                disabled_workflows[workflow_name] = info
                
        # 6. Documentation
        if disabled_workflows:
            self.last_interventions.append(datetime.datetime.now())
            self.create_intervention_issue(disabled_workflows)
            
            # Sauvegarde l'état
            status_data = {
                'last_intervention': datetime.datetime.now(),
                'disabled_workflows': list(disabled_workflows.keys()),
                'total_interventions': len(self.last_interventions)
            }
            self.save_status(status_data)
            
            self.logger.info(f"✅ Intervention terminée - {len(disabled_workflows)} workflows désactivés")
    
    def run_autonomous_monitoring(self):
        """Lance la surveillance autonome continue"""
        self.logger.info("🚀 DÉMARRAGE DOCTOR AUTONOME")
        self.logger.info(f"⏱️ Intervalle: {self.check_interval}s")
        self.logger.info(f"🎯 Seuil critique: {self.emergency_threshold} échecs")
        
        try:
            cycle_count = 0
            while True:
                cycle_count += 1
                self.logger.info(f"📊 Cycle #{cycle_count}")
                
                try:
                    self.monitoring_cycle()
                except Exception as e:
                    self.logger.error(f"❌ Erreur cycle: {e}")
                
                self.logger.info(f"⏸️ Pause {self.check_interval}s...")
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Arrêt demandé par l'utilisateur")
        except Exception as e:
            self.logger.error(f"💥 Erreur fatale: {e}")
            raise

def main():
    """Point d'entrée principal"""
    print("🤖 GitHub Workflow Doctor Autonome")
    print("===================================")
    
    doctor = AutonomousWorkflowDoctor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("🧪 Mode test - un seul cycle")
        doctor.monitoring_cycle()
    else:
        print("🔄 Mode autonome - surveillance continue")
        doctor.run_autonomous_monitoring()

if __name__ == "__main__":
    main()
