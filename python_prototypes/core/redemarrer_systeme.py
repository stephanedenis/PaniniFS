#!/usr/bin/env python3

import subprocess
import time
import os

def redemarrer_systeme():
    """Redémarre le système depuis les nouveaux emplacements"""
    
    print("🚀 REDÉMARRAGE SYSTÈME DEPUIS NOUVELLE ORGANISATION")
    print("=" * 55)
    
    # Vérifier que les fichiers existent
    files_to_check = [
        'systeme_evenementiel/systeme_evenementiel_cpu.py',
        'systeme_evenementiel/dashboard_evenementiel.py'
    ]
    
    missing_files = []
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Fichiers manquants:")
        for f in missing_files:
            print(f"   {f}")
        return False
    
    print("✅ Tous les fichiers trouvés")
    
    # Lancer le système événementiel
    print("\n🎯 Lancement système événementiel...")
    try:
        proc1 = subprocess.Popen([
            'python3', 'systeme_evenementiel/systeme_evenementiel_cpu.py'
        ])
        print(f"✅ Système événementiel lancé (PID {proc1.pid})")
    except Exception as e:
        print(f"❌ Erreur lancement système: {e}")
        return False
    
    # Attendre un peu
    time.sleep(3)
    
    # Lancer le dashboard
    print("📊 Lancement dashboard...")
    try:
        proc2 = subprocess.Popen([
            'python3', 'systeme_evenementiel/dashboard_evenementiel.py'
        ])
        print(f"✅ Dashboard lancé (PID {proc2.pid})")
    except Exception as e:
        print(f"❌ Erreur lancement dashboard: {e}")
        return False
    
    # Attendre stabilisation
    time.sleep(2)
    
    print(f"\n🎯 SYSTÈME REDÉMARRÉ")
    print("📡 Dashboard: http://localhost:8892")
    print("🔧 Architecture: Événementielle avec affinité CPU")
    print("⚡ Cores dédiés: 1-2, 3-4, 5-7, 8")
    
    print(f"\n💡 Pour vérifier:")
    print("   python3 systeme_evenementiel/verifier_statut.py")
    print("   python3 systeme_evenementiel/ouvrir_dashboard.py")
    
    return True

if __name__ == "__main__":
    redemarrer_systeme()