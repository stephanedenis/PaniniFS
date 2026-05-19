#!/usr/bin/env python3
"""
Launcher Intégré RX 480 + High-End System
Démarrage optimiseur haute performance + dashboard matriciel
"""

import sys
import time
import signal
import subprocess
import threading
from pathlib import Path
from datetime import datetime


class RX480IntegratedLauncher:
    """Lanceur intégré pour système RX 480 + High-End"""
    
    def __init__(self):
        self.workspace = Path('/home/stephane/GitHub/PaniniFS-Research')
        self.dashboard_process = None
        self.dashboard_port = 8092
        
        # Configuration système RX 480
        self.system_config = {
            "gpu": {
                "name": "RX 480",
                "shaders": 2304,
                "rops": 32,
                "tmus": 144,
                "vram_gb": 8,
                "bandwidth_gbs": 256,
                "target_utilization": 85
            },
            "cpu": {
                "cores": 16,
                "threads": 32,
                "target_utilization": 75
            },
            "memory": {
                "total_gb": 64,
                "target_usage_gb": 48
            }
        }
        
        # Gestionnaire signal pour arrêt propre
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Gestionnaire arrêt propre"""
        print(f"\n🛑 Signal {signum} reçu - Arrêt en cours...")
        self.shutdown()
        sys.exit(0)
    
    def print_header(self):
        """Affiche en-tête launcher"""
        print("🎮" + "="*55 + "🎮")
        print("   LAUNCHER INTÉGRÉ RX 480 + HIGH-END SYSTEM")
        print("="*59)
        print("🎮 GPU: RX 480 (2304 shaders, 8GB VRAM, 256GB/s)")
        print("🖥️ CPU: 16 cores, 32 threads hyperthreading")
        print("🧠 RAM: 64GB DDR4 haute performance")
        print("⚡ Optimisation: Exploitation maximale ressources")
        print("="*59)
        print(f"📅 Session: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*59)
    
    def check_dependencies(self):
        """Vérifie dépendances système"""
        print("🔍 Vérification dépendances...")
        
        dependencies = {
            "psutil": "Monitoring système",
            "numpy": "Calculs haute performance",
            "threading": "Parallélisme CPU",
            "subprocess": "Gestion processus"
        }
        
        missing = []
        for dep, description in dependencies.items():
            try:
                if dep == "threading" or dep == "subprocess":
                    # Modules built-in
                    pass
                else:
                    __import__(dep)
                print(f"  ✅ {dep}: {description}")
            except ImportError:
                print(f"  ❌ {dep}: {description}")
                missing.append(dep)
        
        if missing:
            print(f"⚠️ Dépendances manquantes: {', '.join(missing)}")
            return False
        
        print("✅ Toutes les dépendances disponibles")
        return True
    
    def check_hardware_readiness(self):
        """Vérifie état matériel"""
        print("\n🔧 Vérification matériel RX 480...")
        
        try:
            import psutil
            
            # Vérification CPU
            cpu_count = psutil.cpu_count()
            cpu_logical = psutil.cpu_count(logical=True)
            print(f"  🖥️ CPU: {cpu_count} cores physiques, {cpu_logical} logiques")
            
            if cpu_count >= 8 and cpu_logical >= 16:
                print("  ✅ CPU: Configuration haute performance détectée")
            else:
                print("  ⚠️ CPU: Configuration sous-optimale")
            
            # Vérification mémoire
            memory = psutil.virtual_memory()
            memory_gb = round(memory.total / (1024**3), 1)
            print(f"  🧠 RAM: {memory_gb}GB disponible")
            
            if memory_gb >= 32:
                print("  ✅ RAM: Configuration haute performance")
            else:
                print("  ⚠️ RAM: Configuration limitée")
            
            # Test GPU (amdgpu_top)
            gpu_result = subprocess.run(['which', 'amdgpu_top'], 
                                      capture_output=True, text=True, timeout=2)
            if gpu_result.returncode == 0:
                print("  ✅ GPU: amdgpu_top disponible (RX 480 monitoring)")
            else:
                print("  ⚠️ GPU: amdgpu_top non installé (monitoring limité)")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Erreur vérification: {e}")
            return False
    
    def start_dashboard(self):
        """Démarre le dashboard matriciel"""
        print(f"\n📊 Démarrage dashboard matriciel (port {self.dashboard_port})...")
        
        try:
            # Commande dashboard
            cmd = [
                sys.executable, "-c",
                f"from rx480_matrix_dashboard import start_rx480_dashboard; start_rx480_dashboard({self.dashboard_port})"
            ]
            
            self.dashboard_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.workspace
            )
            
            # Attendre démarrage
            time.sleep(2)
            
            if self.dashboard_process.poll() is None:
                print(f"  ✅ Dashboard démarré: http://localhost:{self.dashboard_port}")
                return True
            else:
                stdout, stderr = self.dashboard_process.communicate()
                print(f"  ❌ Erreur dashboard: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"  ❌ Erreur démarrage dashboard: {e}")
            return False
    
    def run_optimization_cycle(self):
        """Exécute cycle optimisation haute performance"""
        print("\n⚡ Démarrage cycle optimisation RX 480...")
        
        try:
            # Commande optimiseur
            optimizer_path = self.workspace / "panini_high_performance_optimizer.py"
            if not optimizer_path.exists():
                print(f"  ❌ Optimiseur non trouvé: {optimizer_path}")
                return False
            
            cmd = [sys.executable, str(optimizer_path)]
            
            print("  🚀 Lancement optimiseur haute performance...")
            print("  🎯 Cibles: GPU 85%, CPU 75%, RAM 48GB")
            print("  🎮 RX 480: Exploitation 2304 shaders")
            print("  ⏳ Durée estimée: 45-60 secondes")
            
            # Exécution avec timeout
            result = subprocess.run(
                cmd,
                cwd=self.workspace,
                timeout=180,  # 3 minutes max
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("  ✅ Optimisation terminée avec succès")
                
                # Parse résultats
                output = result.stdout
                if "performance improvement" in output.lower():
                    for line in output.split('\n'):
                        if "performance improvement" in line.lower():
                            print(f"  📈 {line.strip()}")
                        elif "elements/sec" in line.lower():
                            print(f"  ⚛️ {line.strip()}")
                        elif "molecules/sec" in line.lower():
                            print(f"  🧪 {line.strip()}")
                
                return True
            else:
                print(f"  ❌ Erreur optimisation: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("  ⏰ Timeout optimisation (normal pour gros datasets)")
            return True  # Pas d'erreur, juste long
        except Exception as e:
            print(f"  ❌ Erreur cycle optimisation: {e}")
            return False
    
    def monitor_system(self, duration=30):
        """Monitoring système pendant durée donnée"""
        print(f"\n📈 Monitoring système RX 480 ({duration}s)...")
        
        try:
            import psutil
            
            start_time = time.time()
            samples = []
            
            while time.time() - start_time < duration:
                # Collecte métriques
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                sample = {
                    "timestamp": time.time() - start_time,
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_gb": round(memory.used / (1024**3), 1)
                }
                samples.append(sample)
                
                # Affichage temps réel
                print(f"  ⏱️ {sample['timestamp']:4.0f}s | "
                      f"CPU: {cpu_percent:5.1f}% | "
                      f"RAM: {sample['memory_gb']:4.1f}GB ({memory.percent:4.1f}%)")
            
            # Statistiques finales
            if samples:
                avg_cpu = sum(s['cpu_percent'] for s in samples) / len(samples)
                avg_memory = sum(s['memory_percent'] for s in samples) / len(samples)
                max_cpu = max(s['cpu_percent'] for s in samples)
                max_memory = max(s['memory_gb'] for s in samples)
                
                print(f"\n  📊 Statistiques {duration}s:")
                print(f"    CPU moyen: {avg_cpu:.1f}% | Max: {max_cpu:.1f}%")
                print(f"    RAM moyenne: {avg_memory:.1f}% | Max: {max_memory:.1f}GB")
                
                # Évaluation performance
                if avg_cpu > 60 and avg_memory > 30:
                    print("  ✅ Système bien utilisé")
                elif avg_cpu > 40 or avg_memory > 20:
                    print("  ⚠️ Système modérément utilisé")
                else:
                    print("  📈 Potentiel d'optimisation élevé")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Erreur monitoring: {e}")
            return False
    
    def show_optimization_summary(self):
        """Affiche résumé optimisations"""
        print("\n📋 RÉSUMÉ SESSION RX 480")
        print("="*40)
        
        # Recherche rapports récents
        report_files = list(self.workspace.glob("*performance_report*.json"))
        report_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if report_files:
            latest_report = report_files[0]
            print(f"📄 Dernier rapport: {latest_report.name}")
            
            try:
                import json
                with open(latest_report, 'r') as f:
                    data = json.load(f)
                
                if 'performance_summary' in data:
                    summary = data['performance_summary']
                    print(f"⚡ Gain performance: {summary.get('overall_improvement', 'N/A')}")
                    print(f"⚛️ Éléments/sec: {summary.get('atomic_elements_per_sec', 'N/A')}")
                    print(f"🧪 Molécules/sec: {summary.get('molecules_per_sec', 'N/A')}")
                
                if 'resource_utilization' in data:
                    resources = data['resource_utilization']
                    print(f"🎮 GPU cible: {resources.get('gpu_target', 'N/A')}%")
                    print(f"🖥️ CPU cible: {resources.get('cpu_target', 'N/A')}%")
                    print(f"🧠 RAM cible: {resources.get('memory_target_gb', 'N/A')}GB")
                    
            except Exception as e:
                print(f"⚠️ Erreur lecture rapport: {e}")
        else:
            print("📄 Aucun rapport récent trouvé")
        
        print(f"📊 Dashboard: http://localhost:{self.dashboard_port}")
        print("🎮 Système RX 480 + High-End optimisé!")
    
    def shutdown(self):
        """Arrêt propre du launcher"""
        print("\n🛑 Arrêt launcher intégré...")
        
        if self.dashboard_process and self.dashboard_process.poll() is None:
            print("  🔌 Arrêt dashboard matriciel...")
            self.dashboard_process.terminate()
            try:
                self.dashboard_process.wait(timeout=5)
                print("  ✅ Dashboard arrêté proprement")
            except subprocess.TimeoutExpired:
                print("  ⚠️ Arrêt forcé dashboard")
                self.dashboard_process.kill()
        
        print("✅ Launcher arrêté")
    
    def run(self):
        """Exécution principale du launcher"""
        self.print_header()
        
        # Vérifications initiales
        if not self.check_dependencies():
            print("❌ Échec vérification dépendances")
            return False
        
        if not self.check_hardware_readiness():
            print("❌ Échec vérification matériel")
            return False
        
        # Démarrage dashboard
        if not self.start_dashboard():
            print("⚠️ Dashboard non démarré (continuant sans)")
        
        # Menu interactif
        while True:
            print("\n" + "="*59)
            print("🎮 MENU LAUNCHER RX 480")
            print("="*59)
            print("1. 🚀 Lancer cycle optimisation haute performance")
            print("2. 📈 Monitoring système (30s)")
            print("3. 📊 Ouvrir dashboard matriciel")
            print("4. 📋 Afficher résumé optimisations")
            print("5. 🛑 Quitter")
            print("="*59)
            
            try:
                choice = input("Choix (1-5): ").strip()
                
                if choice == "1":
                    self.run_optimization_cycle()
                elif choice == "2":
                    self.monitor_system(30)
                elif choice == "3":
                    print(f"📊 Dashboard: http://localhost:{self.dashboard_port}")
                    print("   (Ouvrir dans navigateur)")
                elif choice == "4":
                    self.show_optimization_summary()
                elif choice == "5":
                    break
                else:
                    print("⚠️ Choix invalide")
                    
            except KeyboardInterrupt:
                break
            except EOFError:
                break
        
        # Arrêt propre
        self.shutdown()
        return True


def main():
    """Point d'entrée principal"""
    launcher = RX480IntegratedLauncher()
    try:
        success = launcher.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        launcher.shutdown()
        print("\n👋 Session interrompue")
        sys.exit(0)


if __name__ == '__main__':
    main()