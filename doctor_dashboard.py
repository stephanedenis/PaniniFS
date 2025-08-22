#!/usr/bin/env python3
"""
📊 Doctor Dashboard
==================

Dashboard temps réel du Doctor Autonome
Monitoring des interventions et état des workflows
"""

import subprocess
import json
import datetime
import time
import os
from pathlib import Path

def clear_screen():
    """Efface l'écran"""
    os.system('clear' if os.name == 'posix' else 'cls')

def get_doctor_status():
    """Récupère le status du doctor"""
    try:
        result = subprocess.run(
            ["python3", "doctor_control.py", "status"],
            capture_output=True, text=True
        )
        return result.returncode == 0
    except:
        return False

def get_workflow_health():
    """Récupère l'état de santé des workflows"""
    try:
        result = subprocess.run(
            ["gh", "run", "list", "--limit", "20", "--json", "conclusion,workflowName,createdAt"],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            runs = json.loads(result.stdout)
            
            # Analyse rapide
            workflows = {}
            for run in runs:
                name = run.get('workflowName', 'unknown')
                conclusion = run.get('conclusion')
                
                if name not in workflows:
                    workflows[name] = {'success': 0, 'failure': 0, 'total': 0}
                
                workflows[name]['total'] += 1
                if conclusion == 'success':
                    workflows[name]['success'] += 1
                elif conclusion == 'failure':
                    workflows[name]['failure'] += 1
            
            return workflows
    except:
        pass
    
    return {}

def display_dashboard():
    """Affiche le dashboard principal"""
    clear_screen()
    
    print("🤖 DOCTOR AUTONOMOUS DASHBOARD")
    print("==============================")
    print(f"📅 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Status du doctor
    doctor_running = get_doctor_status()
    status_icon = "🟢 ACTIF" if doctor_running else "🔴 ARRÊTÉ"
    print(f"🤖 Doctor Status: {status_icon}")
    
    # État des workflows
    print()
    print("📊 WORKFLOW HEALTH (20 derniers runs):")
    print("─" * 50)
    
    workflows = get_workflow_health()
    
    if workflows:
        for name, stats in workflows.items():
            total = stats['total']
            success = stats['success']
            failure = stats['failure']
            
            if total > 0:
                success_rate = (success / total) * 100
                
                # Détermine l'icône de santé
                if success_rate >= 80:
                    health_icon = "🟢"
                elif success_rate >= 50:
                    health_icon = "🟡"
                else:
                    health_icon = "🔴"
                
                print(f"{health_icon} {name[:40]:<40} | ✅{success:2d} ❌{failure:2d} | {success_rate:5.1f}%")
    else:
        print("⚠️ Aucune donnée workflow disponible")
    
    print()
    print("─" * 50)
    print("🔄 Actualisation auto toutes les 30s")
    print("⌨️  Ctrl+C pour quitter")
    print()
    
    # Instructions
    if not doctor_running:
        print("💡 Pour démarrer le doctor:")
        print("   python3 doctor_control.py start")
    else:
        print("✅ Doctor en surveillance continue")
        print("   Intervention auto si ≥3 échecs détectés")

def main():
    """Boucle principale du dashboard"""
    try:
        print("🚀 Démarrage Doctor Dashboard...")
        print("⏱️ Actualisation toutes les 30s")
        print("⌨️ Ctrl+C pour quitter")
        print()
        time.sleep(2)
        
        while True:
            display_dashboard()
            time.sleep(30)
            
    except KeyboardInterrupt:
        clear_screen()
        print("👋 Dashboard fermé")
        print("🤖 Doctor continue en arrière-plan")
        print()
        print("💡 Pour vérifier le status:")
        print("   python3 doctor_control.py status")

if __name__ == "__main__":
    main()
