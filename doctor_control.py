#!/usr/bin/env python3
"""
🎛️ Doctor Control Panel
=======================

Interface de contrôle pour le Doctor Autonome
Status, démarrage, arrêt, configuration
"""

import subprocess
import json
import datetime
import os
import sys
from pathlib import Path

class DoctorControlPanel:
    def __init__(self):
        self.pid_file = Path("doctor.pid")
        self.status_file = Path("doctor_status.json")
        self.log_dir = Path("OPERATIONS/logs")
        
    def is_running(self):
        """Vérifie si le doctor est en cours d'exécution"""
        if not self.pid_file.exists():
            return False, None
            
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
                
            # Vérifie si le processus existe
            try:
                os.kill(pid, 0)  # Signal 0 = test existence
                return True, pid
            except OSError:
                # Processus n'existe plus, nettoie le PID file
                self.pid_file.unlink()
                return False, None
                
        except (ValueError, FileNotFoundError):
            return False, None
    
    def get_status(self):
        """Récupère le status détaillé du doctor"""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def get_recent_logs(self, lines=20):
        """Récupère les logs récents"""
        log_file = self.log_dir / f"workflow_doctor_{datetime.date.today()}.log"
        
        if not log_file.exists():
            return []
            
        try:
            with open(log_file, 'r') as f:
                all_lines = f.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
        except Exception:
            return []
    
    def start_doctor(self):
        """Démarre le doctor en arrière-plan"""
        is_running, pid = self.is_running()
        
        if is_running:
            return False, f"Doctor déjà en cours (PID: {pid})"
        
        try:
            # Lance le launcher
            process = subprocess.Popen(
                ["bash", "launch_autonomous_doctor.sh"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Attend un peu pour vérifier le démarrage
            import time
            time.sleep(2)
            
            is_running, pid = self.is_running()
            if is_running:
                return True, f"Doctor démarré (PID: {pid})"
            else:
                return False, "Échec démarrage doctor"
                
        except Exception as e:
            return False, f"Erreur démarrage: {e}"
    
    def stop_doctor(self):
        """Arrête le doctor"""
        is_running, pid = self.is_running()
        
        if not is_running:
            return False, "Doctor pas en cours d'exécution"
        
        try:
            os.kill(pid, 15)  # SIGTERM
            
            # Nettoie le PID file après un délai
            import time
            time.sleep(1)
            
            if self.pid_file.exists():
                self.pid_file.unlink()
                
            return True, f"Doctor arrêté (PID: {pid})"
            
        except Exception as e:
            return False, f"Erreur arrêt: {e}"
    
    def display_status(self):
        """Affiche le status complet"""
        print("🤖 DOCTOR CONTROL PANEL")
        print("========================")
        print(f"📅 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # État de fonctionnement
        is_running, pid = self.is_running()
        if is_running:
            print(f"🟢 STATUS: ACTIF (PID: {pid})")
        else:
            print("🔴 STATUS: ARRÊTÉ")
        
        print()
        
        # Statistiques
        status = self.get_status()
        if status:
            print("📊 STATISTIQUES:")
            if 'last_intervention' in status:
                print(f"• Dernière intervention: {status['last_intervention']}")
            if 'total_interventions' in status:
                print(f"• Total interventions: {status['total_interventions']}")
            if 'disabled_workflows' in status:
                print(f"• Workflows désactivés: {len(status['disabled_workflows'])}")
                for workflow in status['disabled_workflows']:
                    print(f"  - {workflow}")
        else:
            print("📊 STATISTIQUES: Aucune donnée")
        
        print()
        
        # Logs récents
        print("📝 LOGS RÉCENTS (10 dernières lignes):")
        logs = self.get_recent_logs(10)
        if logs:
            for line in logs:
                print(f"  {line.strip()}")
        else:
            print("  Aucun log disponible")
        
        print()
        
        # Instructions
        print("🎛️ COMMANDES:")
        print("• python3 doctor_control.py start   - Démarre le doctor")
        print("• python3 doctor_control.py stop    - Arrête le doctor")
        print("• python3 doctor_control.py status  - Affiche ce status")
        print("• python3 doctor_control.py logs    - Logs complets")

def main():
    control = DoctorControlPanel()
    
    if len(sys.argv) < 2:
        control.display_status()
        return
    
    command = sys.argv[1].lower()
    
    if command == "start":
        success, message = control.start_doctor()
        print(f"{'✅' if success else '❌'} {message}")
        
    elif command == "stop":
        success, message = control.stop_doctor()
        print(f"{'✅' if success else '❌'} {message}")
        
    elif command == "status":
        control.display_status()
        
    elif command == "logs":
        logs = control.get_recent_logs(50)
        print("📝 LOGS COMPLETS:")
        print("================")
        for line in logs:
            print(line.strip())
            
    else:
        print("❌ Commande inconnue. Usage:")
        print("  python3 doctor_control.py [start|stop|status|logs]")

if __name__ == "__main__":
    main()
