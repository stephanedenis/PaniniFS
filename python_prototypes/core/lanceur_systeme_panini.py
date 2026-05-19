#!/usr/bin/env python3
"""
Lanceur Système PaniniFS Research
Lance tout le système de recherche autonome en arrière-plan
avec traitement itératif par niveaux de complexité
"""

import subprocess
import sys
import time
import json
from pathlib import Path
import signal
import os

def afficher_banniere():
    """Affiche la bannière de démarrage"""
    print("🚀" + "="*60 + "🚀")
    print("   PANINIFS RESEARCH - SYSTÈME AUTONOME")
    print("   Traitement itératif par niveaux de complexité")
    print("   Préscolaire → Primaire → Secondaire → Universitaire → Expert")
    print("🚀" + "="*60 + "🚀")
    print()

def verifier_prerequis():
    """Vérifie les prérequis avant démarrage"""
    print("🔍 Vérification des prérequis...")
    
    # Vérifier Python
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ requis")
        return False
    
    # Vérifier environnement virtuel
    venv_python = Path('.venv/bin/python')
    if venv_python.exists():
        print("✅ Environnement virtuel détecté")
        python_cmd = str(venv_python)
    else:
        print("⚠️ Pas d'environnement virtuel, utilisation Python système")
        python_cmd = 'python3'
    
    # Vérifier corpus de base
    corpus_files = ['corpus_multilingue_dev.json', 'panini/references/references_database.json']
    corpus_ok = 0
    for corpus_file in corpus_files:
        if Path(corpus_file).exists():
            print(f"✅ Corpus trouvé: {corpus_file}")
            corpus_ok += 1
        else:
            print(f"⚠️ Corpus manquant: {corpus_file}")
    
    print(f"📊 Corpus disponibles: {corpus_ok}/{len(corpus_files)}")
    print("✅ Prérequis vérifiés")
    
    return python_cmd

def demarrer_systeme_arriere_plan(python_cmd):
    """Démarre le système en arrière-plan"""
    print("🚀 Démarrage système arrière-plan...")
    
    try:
        # Démarrer gestionnaire arrière-plan
        cmd = [python_cmd, 'gestionnaire_arriere_plan.py']
        
        print(f"📡 Commande: {' '.join(cmd)}")
        
        # Démarrer en arrière-plan
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print(f"✅ Gestionnaire démarré (PID: {process.pid})")
        
        # Sauvegarder PID pour contrôle
        with open('systeme_pid.txt', 'w') as f:
            f.write(str(process.pid))
        
        # Afficher premières lignes de sortie
        print("📋 Sortie initiale:")
        try:
            for i in range(10):  # Premières 10 lignes
                line = process.stdout.readline()
                if line:
                    print(f"   {line.strip()}")
                else:
                    break
                time.sleep(0.1)
        except:
            pass
        
        return process
        
    except Exception as e:
        print(f"❌ Erreur démarrage: {e}")
        return None

def afficher_statut_systeme():
    """Affiche le statut du système"""
    print("\n📊 STATUT SYSTÈME:")
    print("-" * 40)
    
    # Lire état gestionnaire
    if Path('etat_gestionnaire_arriere_plan.json').exists():
        try:
            with open('etat_gestionnaire_arriere_plan.json', 'r') as f:
                etat = json.load(f)
            
            processus_actifs = etat.get('processus_actifs', 0)
            redemarrages = etat.get('redemarrages_totaux', 0)
            erreurs = etat.get('erreurs_totales', 0)
            
            print(f"   Processus actifs: {processus_actifs}")
            print(f"   Redémarrages: {redemarrages}")
            print(f"   Erreurs: {erreurs}")
            
        except Exception as e:
            print(f"   ⚠️ Erreur lecture état: {e}")
    else:
        print("   ⏳ Système en cours de démarrage...")
    
    # Lire état pipeline
    if Path('pipeline_iteratif_resultats/etat_pipeline.json').exists():
        try:
            with open('pipeline_iteratif_resultats/etat_pipeline.json', 'r') as f:
                etat_pipeline = json.load(f)
            
            niveau = etat_pipeline.get('niveau_actuel', 0)
            qualite = etat_pipeline.get('modele_qualite', 0.0)
            cycles = etat_pipeline.get('cycles_completes', 0)
            
            niveaux = ['préscolaire', 'primaire', 'secondaire', 'universitaire', 'expert']
            niveau_nom = niveaux[min(niveau, len(niveaux)-1)]
            
            print(f"   Niveau actuel: {niveau_nom}")
            print(f"   Qualité modèle: {qualite:.3f}")
            print(f"   Cycles complétés: {cycles}")
            
        except Exception as e:
            print(f"   ⚠️ Erreur lecture pipeline: {e}")
    else:
        print("   ⏳ Pipeline en cours d'initialisation...")

def arreter_systeme():
    """Arrête le système"""
    print("\n🛑 Arrêt du système...")
    
    # Lire PID
    if Path('systeme_pid.txt').exists():
        try:
            with open('systeme_pid.txt', 'r') as f:
                pid = int(f.read().strip())
            
            # Envoyer signal d'arrêt
            os.kill(pid, signal.SIGTERM)
            print(f"✅ Signal d'arrêt envoyé (PID: {pid})")
            
            # Attendre arrêt
            time.sleep(3)
            
            # Vérifier si arrêté
            try:
                os.kill(pid, 0)  # Test si processus existe
                print("⚠️ Processus encore actif, forçage arrêt...")
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                print("✅ Système arrêté")
            
            # Nettoyer fichier PID
            Path('systeme_pid.txt').unlink()
            
        except Exception as e:
            print(f"❌ Erreur arrêt: {e}")
    else:
        print("⚠️ Aucun PID trouvé")

def menu_principal():
    """Menu principal interactif"""
    while True:
        print("\n" + "="*50)
        print("PANINIFS RESEARCH - CONTRÔLE SYSTÈME")
        print("="*50)
        print("1. 🚀 Démarrer système complet")
        print("2. 📊 Voir statut")
        print("3. 🛑 Arrêter système")
        print("4. 📋 Voir logs")
        print("5. ❌ Quitter")
        print("-"*50)
        
        choix = input("Choix (1-5): ").strip()
        
        if choix == '1':
            python_cmd = verifier_prerequis()
            if python_cmd:
                process = demarrer_systeme_arriere_plan(python_cmd)
                if process:
                    print("\n✅ Système démarré en arrière-plan")
                    print("💡 Utilisez option 2 pour voir le statut")
                    print("💡 Utilisez option 3 pour arrêter")
        
        elif choix == '2':
            afficher_statut_systeme()
        
        elif choix == '3':
            arreter_systeme()
        
        elif choix == '4':
            print("\n📋 Logs récents:")
            if Path('gestionnaire_arriere_plan.log').exists():
                try:
                    with open('gestionnaire_arriere_plan.log', 'r') as f:
                        lignes = f.readlines()
                        for ligne in lignes[-20:]:  # 20 dernières lignes
                            print(f"   {ligne.strip()}")
                except Exception as e:
                    print(f"❌ Erreur lecture logs: {e}")
            else:
                print("   ⚠️ Aucun log trouvé")
        
        elif choix == '5':
            print("👋 Au revoir!")
            break
        
        else:
            print("❌ Choix invalide")

def main():
    """Point d'entrée principal"""
    afficher_banniere()
    
    # Vérifier si argument en ligne de commande
    if len(sys.argv) > 1:
        action = sys.argv[1].lower()
        
        if action == 'start':
            python_cmd = verifier_prerequis()
            if python_cmd:
                demarrer_systeme_arriere_plan(python_cmd)
        
        elif action == 'stop':
            arreter_systeme()
        
        elif action == 'status':
            afficher_statut_systeme()
        
        else:
            print(f"❌ Action inconnue: {action}")
            print("💡 Actions disponibles: start, stop, status")
    
    else:
        # Mode interactif
        menu_principal()

if __name__ == "__main__":
    main()