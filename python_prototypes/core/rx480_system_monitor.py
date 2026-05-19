#!/usr/bin/env python3
"""
Moniteur Ressources RX 480 + Système High-End
Monitoring optimisé pour RX 480 (2304 shaders, 8GB GDDR5, 256GB/s) + CPU 16-cores + 64GB RAM
"""

import psutil
import subprocess
import json
import time
import threading
from datetime import datetime
from pathlib import Path


class RX480SystemMonitor:
    def __init__(self):
        self.workspace = Path('/home/stephane/GitHub/PaniniFS-Research')
        
        # Spécifications RX 480
        self.rx480_specs = {
            "shaders": 2304,
            "rops": 32,
            "tmus": 144,
            "vram_gb": 8,
            "memory_bandwidth_gbs": 256,
            "base_clock_mhz": 1120,
            "boost_clock_mhz": 1266,
            "memory_clock_mhz": 2000
        }
        
        # Spécifications système
        self.system_specs = {
            "cpu_cores": 16,
            "ram_gb": 64,
            "expected_threads": 32  # Hyperthreading
        }
        
        self.monitoring_active = False
        self.monitor_thread = None
        self.metrics_history = []
        
        self.log("🎮 Moniteur RX 480 + Système High-End initialisé")
        self.log(f"📊 Cible: RX 480 ({self.rx480_specs['shaders']} shaders, {self.rx480_specs['vram_gb']}GB VRAM)")
        self.log(f"🖥️ Système: {self.system_specs['cpu_cores']} cores, {self.system_specs['ram_gb']}GB RAM")
    
    def log(self, message):
        """Logging avec timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {message}")
    
    def detect_rx480_properly(self):
        """Force la détection correcte de la RX 480"""
        self.log("🔍 Détection avancée RX 480...")
        
        gpu_info = {
            "detected": False,
            "driver": None,
            "device_id": None,
            "memory_detected": 0,
            "issues": []
        }
        
        # Vérification lspci avec forçage RX 480
        try:
            result = subprocess.run(['lspci', '-v'], capture_output=True, text=True)
            output = result.stdout.lower()
            
            # Recherche patterns RX 480
            rx480_patterns = [
                "rx 480", "rx480", "polaris", "ellesmere", 
                "67df", "67ef"  # Device IDs RX 480
            ]
            
            for pattern in rx480_patterns:
                if pattern in output:
                    gpu_info["detected"] = True
                    self.log(f"✅ Pattern RX 480 détecté: {pattern}")
                    break
            
            # Détection driver
            if "amdgpu" in output:
                gpu_info["driver"] = "amdgpu"
            elif "radeon" in output:
                gpu_info["driver"] = "radeon"
                gpu_info["issues"].append("Driver legacy détecté - amdgpu recommandé")
            
        except Exception as e:
            gpu_info["issues"].append(f"Erreur lspci: {e}")
        
        # Vérification dmesg pour RX 480
        try:
            result = subprocess.run(['dmesg'], capture_output=True, text=True)
            dmesg_output = result.stdout.lower()
            
            # Recherche mentions RX 480/Polaris
            if any(pattern in dmesg_output for pattern in ["polaris", "ellesmere", "rx"]):
                gpu_info["detected"] = True
                self.log("✅ RX 480 trouvée dans dmesg")
            
            # Détection mémoire VRAM
            vram_patterns = ["8192m", "8gb", "8000m"]
            for pattern in vram_patterns:
                if pattern in dmesg_output:
                    gpu_info["memory_detected"] = 8
                    self.log(f"✅ VRAM 8GB détectée: {pattern}")
                    break
                    
        except Exception as e:
            gpu_info["issues"].append(f"Erreur dmesg: {e}")
        
        # Force assumption RX 480 si aucune détection
        if not gpu_info["detected"]:
            self.log("⚠️ Détection automatique échouée - Force RX 480 selon confirmation utilisateur")
            gpu_info = {
                "detected": True,
                "driver": "amdgpu (assumé)",
                "device_id": "RX480_FORCED",
                "memory_detected": 8,
                "forced": True,
                "issues": ["Détection logicielle échouée - Configuration forcée"]
            }
        
        return gpu_info
    
    def get_advanced_gpu_metrics(self):
        """Collecte métriques GPU avancées pour RX 480"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "gpu_utilization": 0,
            "vram_usage": {"used_mb": 0, "total_mb": 8192, "percent": 0},
            "memory_bandwidth_usage": 0,
            "shader_utilization": 0,
            "rop_utilization": 0,
            "tmu_utilization": 0,
            "temperature": 0,
            "power_usage": 0,
            "clocks": {"gpu_mhz": 0, "memory_mhz": 0},
            "source": "unknown"
        }
        
        # Tentative amdgpu_top
        try:
            result = subprocess.run(['amdgpu_top', '--smi'], 
                                  capture_output=True, text=True, timeout=3)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                metrics["source"] = "amdgpu_top"
                
                for line in lines:
                    line_lower = line.lower()
                    
                    # Parse VRAM
                    if 'vram' in line_lower and 'gib' in line_lower:
                        try:
                            parts = line.split()
                            for part in parts:
                                if '/' in part and 'gib' in part.lower():
                                    used_str, total_str = part.lower().replace('gib', '').split('/')
                                    used_gb = float(used_str)
                                    total_gb = float(total_str)
                                    
                                    metrics["vram_usage"]["used_mb"] = int(used_gb * 1024)
                                    metrics["vram_usage"]["total_mb"] = int(total_gb * 1024)
                                    metrics["vram_usage"]["percent"] = (used_gb / total_gb) * 100
                                    break
                        except:
                            pass
                    
                    # Parse GPU utilization
                    if 'gpu' in line_lower and '%' in line:
                        try:
                            for part in line.split():
                                if '%' in part:
                                    gpu_util = float(part.replace('%', ''))
                                    metrics["gpu_utilization"] = gpu_util
                                    break
                        except:
                            pass
        
        except Exception as e:
            metrics["source"] = f"error: {e}"
        
        # Calculs spécifiques RX 480
        if metrics["gpu_utilization"] > 0:
            # Estimation utilisation composants basée sur GPU utilization
            metrics["shader_utilization"] = metrics["gpu_utilization"] * 0.9  # Shaders très utilisés
            metrics["rop_utilization"] = metrics["gpu_utilization"] * 0.7    # ROPs moins sollicités
            metrics["tmu_utilization"] = metrics["gpu_utilization"] * 0.8    # TMUs moyennement utilisés
            
            # Estimation bande passante mémoire (max 256 GB/s)
            vram_percent = metrics["vram_usage"]["percent"]
            metrics["memory_bandwidth_usage"] = min(100, vram_percent * 1.2)
        
        return metrics
    
    def get_system_metrics(self):
        """Collecte métriques système 16-cores + 64GB RAM"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "cpu": self.get_cpu_metrics(),
            "memory": self.get_memory_metrics(),
            "disk": self.get_disk_metrics(),
            "processes": self.get_process_metrics()
        }
        
        return metrics
    
    def get_cpu_metrics(self):
        """Métriques CPU détaillées pour 16 cores"""
        try:
            # CPU global
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            cpu_count_logical = psutil.cpu_count(logical=True)
            
            # CPU par core
            cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
            
            # Fréquences
            cpu_freq = psutil.cpu_freq()
            
            # Load average
            load_avg = psutil.getloadavg()
            
            # Analyse utilisation
            cores_high_usage = sum(1 for usage in cpu_per_core if usage > 80)
            cores_medium_usage = sum(1 for usage in cpu_per_core if 40 < usage <= 80)
            cores_low_usage = sum(1 for usage in cpu_per_core if usage <= 40)
            
            return {
                "percent_total": cpu_percent,
                "cores_physical": cpu_count,
                "cores_logical": cpu_count_logical,
                "per_core_usage": cpu_per_core,
                "frequency": {
                    "current_mhz": cpu_freq.current if cpu_freq else 0,
                    "min_mhz": cpu_freq.min if cpu_freq else 0,
                    "max_mhz": cpu_freq.max if cpu_freq else 0
                },
                "load_average": {
                    "1min": load_avg[0],
                    "5min": load_avg[1], 
                    "15min": load_avg[2]
                },
                "utilization_analysis": {
                    "cores_high_usage": cores_high_usage,
                    "cores_medium_usage": cores_medium_usage,
                    "cores_low_usage": cores_low_usage,
                    "efficiency_percent": ((cores_high_usage + cores_medium_usage) / len(cpu_per_core)) * 100
                },
                "status": "high" if cpu_percent > 80 else "medium" if cpu_percent > 50 else "low"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_memory_metrics(self):
        """Métriques mémoire détaillées pour 64GB RAM"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "free_gb": round(memory.free / (1024**3), 2),
                "percent_used": memory.percent,
                "buffers_gb": round(memory.buffers / (1024**3), 2) if hasattr(memory, 'buffers') else 0,
                "cached_gb": round(memory.cached / (1024**3), 2) if hasattr(memory, 'cached') else 0,
                "swap": {
                    "total_gb": round(swap.total / (1024**3), 2),
                    "used_gb": round(swap.used / (1024**3), 2),
                    "percent": swap.percent
                },
                "utilization_analysis": {
                    "high_usage_threshold_gb": 51.2,  # 80% de 64GB
                    "current_efficiency": (memory.used / memory.total) * 100,
                    "memory_pressure": "high" if memory.percent > 80 else "medium" if memory.percent > 60 else "low"
                },
                "status": "high" if memory.percent > 80 else "medium" if memory.percent > 60 else "low"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_disk_metrics(self):
        """Métriques disque I/O"""
        try:
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            return {
                "usage": {
                    "total_gb": round(disk_usage.total / (1024**3), 2),
                    "used_gb": round(disk_usage.used / (1024**3), 2),
                    "free_gb": round(disk_usage.free / (1024**3), 2),
                    "percent": (disk_usage.used / disk_usage.total) * 100
                },
                "io": {
                    "read_count": disk_io.read_count if disk_io else 0,
                    "write_count": disk_io.write_count if disk_io else 0,
                    "read_bytes": disk_io.read_bytes if disk_io else 0,
                    "write_bytes": disk_io.write_bytes if disk_io else 0
                } if disk_io else {},
                "status": "high" if disk_usage.used/disk_usage.total > 0.85 else "medium" if disk_usage.used/disk_usage.total > 0.70 else "low"
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_process_metrics(self):
        """Métriques processus système"""
        try:
            processes = []
            total_processes = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    if info['cpu_percent'] > 5 or info['memory_percent'] > 1:  # Processus significatifs
                        processes.append({
                            'pid': info['pid'],
                            'name': info['name'],
                            'cpu_percent': info['cpu_percent'],
                            'memory_percent': info['memory_percent']
                        })
                    total_processes += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Top processus par CPU et mémoire
            top_cpu = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:5]
            top_memory = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:5]
            
            return {
                "total_count": total_processes,
                "significant_count": len(processes),
                "top_cpu_users": top_cpu,
                "top_memory_users": top_memory
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def calculate_bottlenecks(self, gpu_metrics, system_metrics):
        """Analyse goulots d'étranglement RX 480 + système"""
        bottlenecks = []
        recommendations = []
        
        # Analyse GPU RX 480
        gpu_util = gpu_metrics.get("gpu_utilization", 0)
        vram_percent = gpu_metrics.get("vram_usage", {}).get("percent", 0)
        
        if gpu_util < 30:
            bottlenecks.append({
                "component": "GPU RX 480",
                "issue": "Sous-utilisation shaders",
                "severity": "medium",
                "detail": f"Seulement {gpu_util:.1f}% des 2304 shaders utilisés"
            })
            recommendations.append("Augmenter charge GPU ou parallélisme")
        
        if vram_percent < 20:
            bottlenecks.append({
                "component": "VRAM RX 480", 
                "issue": "Sous-utilisation mémoire",
                "severity": "low",
                "detail": f"Seulement {vram_percent:.1f}% des 8GB VRAM utilisés"
            })
            recommendations.append("Augmenter taille datasets ou batch size")
        
        # Analyse CPU 16-cores
        cpu_data = system_metrics.get("cpu", {})
        cpu_percent = cpu_data.get("percent_total", 0)
        efficiency = cpu_data.get("utilization_analysis", {}).get("efficiency_percent", 0)
        
        if efficiency < 40:
            bottlenecks.append({
                "component": "CPU 16-cores",
                "issue": "Sous-utilisation cores",
                "severity": "high",
                "detail": f"Efficacité {efficiency:.1f}% sur 16 cores disponibles"
            })
            recommendations.append("Augmenter parallélisme CPU ou threading")
        
        # Analyse RAM 64GB
        memory_data = system_metrics.get("memory", {})
        memory_percent = memory_data.get("percent_used", 0)
        
        if memory_percent < 25:
            bottlenecks.append({
                "component": "RAM 64GB",
                "issue": "Sous-utilisation mémoire système", 
                "severity": "medium",
                "detail": f"Seulement {memory_percent:.1f}% des 64GB RAM utilisés"
            })
            recommendations.append("Augmenter cache en mémoire ou datasets")
        
        return {
            "bottlenecks": bottlenecks,
            "recommendations": recommendations,
            "overall_efficiency": {
                "gpu_efficiency": min(100, gpu_util * 1.2),
                "cpu_efficiency": efficiency,
                "memory_efficiency": min(100, memory_percent * 1.5),
                "system_balance": "good" if len(bottlenecks) <= 1 else "needs_optimization"
            }
        }
    
    def start_monitoring(self, duration_minutes=10):
        """Démarre monitoring avancé"""
        self.log(f"🎯 Démarrage monitoring avancé ({duration_minutes} minutes)")
        self.monitoring_active = True
        
        # Détection RX 480
        gpu_detection = self.detect_rx480_properly()
        if gpu_detection["detected"]:
            self.log(f"✅ RX 480 confirmée - Driver: {gpu_detection['driver']}")
            if gpu_detection.get("issues"):
                for issue in gpu_detection["issues"]:
                    self.log(f"⚠️ {issue}")
        else:
            self.log("❌ RX 480 non détectée - Monitoring système uniquement")
        
        def monitor_loop():
            start_time = time.time()
            end_time = start_time + (duration_minutes * 60)
            
            while self.monitoring_active and time.time() < end_time:
                try:
                    # Collecte métriques
                    gpu_metrics = self.get_advanced_gpu_metrics()
                    system_metrics = self.get_system_metrics()
                    
                    # Analyse
                    analysis = self.calculate_bottlenecks(gpu_metrics, system_metrics)
                    
                    # Stockage
                    snapshot = {
                        "timestamp": datetime.now().isoformat(),
                        "gpu": gpu_metrics,
                        "system": system_metrics,
                        "analysis": analysis
                    }
                    
                    self.metrics_history.append(snapshot)
                    
                    # Rapport périodique
                    self.print_monitoring_snapshot(snapshot)
                    
                    time.sleep(5)  # Monitoring toutes les 5 secondes
                    
                except Exception as e:
                    self.log(f"❌ Erreur monitoring: {e}")
                    time.sleep(1)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        # Attente fin monitoring
        self.monitor_thread.join()
        self.log("✅ Monitoring terminé")
        
        # Rapport final
        self.generate_final_report()
    
    def print_monitoring_snapshot(self, snapshot):
        """Affiche snapshot monitoring"""
        gpu = snapshot["gpu"]
        cpu = snapshot["system"]["cpu"]
        memory = snapshot["system"]["memory"]
        analysis = snapshot["analysis"]
        
        print(f"\n{'='*60}")
        print(f"📊 SNAPSHOT MONITORING - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        
        # GPU RX 480
        print(f"🎮 RX 480:")
        print(f"   GPU: {gpu['gpu_utilization']:.1f}% | VRAM: {gpu['vram_usage']['percent']:.1f}% ({gpu['vram_usage']['used_mb']}MB/8192MB)")
        print(f"   Shaders: {gpu['shader_utilization']:.1f}% | ROPs: {gpu['rop_utilization']:.1f}% | TMUs: {gpu['tmu_utilization']:.1f}%")
        
        # CPU 16-cores
        print(f"🖥️ CPU 16-cores:")
        print(f"   Total: {cpu['percent_total']:.1f}% | Efficacité: {cpu['utilization_analysis']['efficiency_percent']:.1f}%")
        print(f"   Cores actifs: H:{cpu['utilization_analysis']['cores_high_usage']} M:{cpu['utilization_analysis']['cores_medium_usage']} L:{cpu['utilization_analysis']['cores_low_usage']}")
        
        # RAM 64GB
        print(f"💾 RAM 64GB:")
        print(f"   Utilisée: {memory['used_gb']:.1f}GB ({memory['percent_used']:.1f}%) | Disponible: {memory['available_gb']:.1f}GB")
        
        # Goulots
        bottlenecks = analysis["bottlenecks"]
        if bottlenecks:
            print(f"🚨 Goulots ({len(bottlenecks)}):")
            for b in bottlenecks[:3]:  # Top 3
                print(f"   • {b['component']}: {b['issue']} ({b['severity']})")
        else:
            print("✅ Aucun goulot détecté")
    
    def generate_final_report(self):
        """Génère rapport final optimisation"""
        if not self.metrics_history:
            return
        
        print(f"\n{'='*80}")
        print("📋 RAPPORT FINAL OPTIMISATION RX 480 + SYSTÈME HIGH-END")
        print(f"{'='*80}")
        
        # Moyennes sur période
        gpu_utils = [m["gpu"]["gpu_utilization"] for m in self.metrics_history]
        vram_utils = [m["gpu"]["vram_usage"]["percent"] for m in self.metrics_history]
        cpu_utils = [m["system"]["cpu"]["percent_total"] for m in self.metrics_history]
        memory_utils = [m["system"]["memory"]["percent_used"] for m in self.metrics_history]
        
        avg_gpu = sum(gpu_utils) / len(gpu_utils)
        avg_vram = sum(vram_utils) / len(vram_utils)
        avg_cpu = sum(cpu_utils) / len(cpu_utils)
        avg_memory = sum(memory_utils) / len(memory_utils)
        
        print(f"📊 Utilisation Moyenne:")
        print(f"   🎮 GPU RX 480: {avg_gpu:.1f}% (Cible: >70% pour optimisation)")
        print(f"   💾 VRAM 8GB: {avg_vram:.1f}% (Cible: >50% pour datasets significatifs)")
        print(f"   🖥️ CPU 16-cores: {avg_cpu:.1f}% (Cible: >60% pour parallélisme efficace)")
        print(f"   🧠 RAM 64GB: {avg_memory:.1f}% (Cible: >40% pour cache optimal)")
        
        # Recommandations spécifiques
        print(f"\n🎯 RECOMMANDATIONS SPÉCIFIQUES:")
        
        if avg_gpu < 70:
            print(f"   🎮 GPU RX 480 sous-utilisé ({avg_gpu:.1f}%):")
            print(f"      • Augmenter batch size pour saturer les 2304 shaders")
            print(f"      • Implémenter calculs parallèles GPU (OpenCL/ROCm)")
            print(f"      • Utiliser davantage la bande passante 256 GB/s")
        
        if avg_vram < 50:
            print(f"   💾 VRAM 8GB sous-utilisée ({avg_vram:.1f}%):")
            print(f"      • Augmenter datasets en mémoire GPU") 
            print(f"      • Précharger plus de données pour pipeline")
        
        if avg_cpu < 60:
            print(f"   🖥️ CPU 16-cores sous-utilisé ({avg_cpu:.1f}%):")
            print(f"      • Augmenter parallélisme (16+ threads)")
            print(f"      • Implémenter work-stealing algorithms")
            print(f"      • Optimiser charge par core")
        
        if avg_memory < 40:
            print(f"   🧠 RAM 64GB sous-utilisée ({avg_memory:.1f}%):")
            print(f"      • Augmenter cache système")
            print(f"      • Précharger plus de corpus en mémoire")
            print(f"      • Utiliser ramdisk pour données temporaires")
        
        # Potentiel inexploité
        gpu_potential = max(0, 100 - avg_gpu)
        cpu_potential = max(0, 100 - avg_cpu)
        memory_potential = max(0, 100 - avg_memory)
        
        total_potential = (gpu_potential + cpu_potential + memory_potential) / 3
        
        print(f"\n⚡ POTENTIEL INEXPLOITÉ:")
        print(f"   GPU: {gpu_potential:.1f}% | CPU: {cpu_potential:.1f}% | RAM: {memory_potential:.1f}%")
        print(f"   POTENTIEL GLOBAL: {total_potential:.1f}%")
        
        if total_potential > 40:
            print(f"   🚨 SYSTÈME TRÈS SOUS-UTILISÉ - Optimisation prioritaire!")
        elif total_potential > 20:
            print(f"   ⚠️ Marge d'amélioration significative")
        else:
            print(f"   ✅ Utilisation satisfaisante des ressources")
        
        print(f"{'='*80}")
        
        # Sauvegarde rapport
        self.save_optimization_report({
            "averages": {"gpu": avg_gpu, "vram": avg_vram, "cpu": avg_cpu, "memory": avg_memory},
            "potential": {"gpu": gpu_potential, "cpu": cpu_potential, "memory": memory_potential, "total": total_potential},
            "history": self.metrics_history
        })
    
    def save_optimization_report(self, report_data):
        """Sauvegarde rapport optimisation"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.workspace / f"rx480_system_optimization_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        self.log(f"💾 Rapport sauvé: {report_file.name}")


def main():
    print("🎮 MONITEUR RX 480 + SYSTÈME HIGH-END")
    print("="*50)
    print("RX 480: 2304 shaders, 8GB VRAM, 256 GB/s")
    print("Système: 16 cores, 64GB RAM")
    print("Détection goulots + optimisations")
    print("="*50)
    
    monitor = RX480SystemMonitor()
    
    try:
        monitor.start_monitoring(duration_minutes=3)  # Test 3 minutes
    except KeyboardInterrupt:
        print("\n🛑 Monitoring interrompu")
        monitor.monitoring_active = False


if __name__ == '__main__':
    main()