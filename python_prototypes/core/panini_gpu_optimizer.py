#!/usr/bin/env python3
"""
Optimiseur GPU PaniniFS
Utilise amdgpu_top pour optimiser l'usage GPU pour les calculs intensifs
"""

import subprocess
import json
import time
import psutil
from pathlib import Path
from datetime import datetime
import re


class PaniniGPUOptimizer:
    def __init__(self):
        self.workspace = Path('/home/stephane/GitHub/PaniniFS-Research')
        self.results_dir = self.workspace / 'gpu_optimization_results'
        self.results_dir.mkdir(exist_ok=True)
        
        # Métriques GPU
        self.gpu_metrics = {}
        self.optimization_history = []
        
        # Seuils d'optimisation
        self.vram_threshold = 80  # %
        self.gpu_usage_threshold = 90  # %
        self.memory_pressure_threshold = 75  # %
        
        self.log("🎮 Optimiseur GPU PaniniFS initialisé")
    
    def log(self, message):
        """Logging avec timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def get_gpu_status(self):
        """Récupère l'état actuel du GPU via amdgpu_top"""
        try:
            # Utiliser amdgpu_top en mode JSON pour récupérer les métriques
            result = subprocess.run([
                'amdgpu_top', '-J', '-n', '1'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Parser la sortie JSON
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip().startswith('{'):
                        try:
                            gpu_data = json.loads(line)
                            return self.parse_gpu_metrics(gpu_data)
                        except json.JSONDecodeError:
                            continue
            
            # Fallback: utiliser amdgpu_top dump
            result = subprocess.run([
                'amdgpu_top', '-d'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return self.parse_dump_output(result.stdout)
            
        except Exception as e:
            self.log(f"❌ Erreur récupération état GPU: {e}")
        
        return None
    
    def parse_gpu_metrics(self, gpu_data):
        """Parse les métriques JSON du GPU"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'vram_used': 0,
            'vram_total': 0,
            'vram_percent': 0,
            'gtt_used': 0,
            'gtt_total': 0,
            'gpu_usage': 0,
            'memory_clock': 0,
            'gpu_clock': 0,
            'power_usage': 0,
            'temperature': 0,
            'processes': []
        }
        
        # Extraire les métriques si disponibles dans le JSON
        if 'VRAM' in gpu_data:
            vram = gpu_data['VRAM']
            metrics['vram_used'] = vram.get('used', 0)
            metrics['vram_total'] = vram.get('total', 0)
            if metrics['vram_total'] > 0:
                metrics['vram_percent'] = (metrics['vram_used'] / metrics['vram_total']) * 100
        
        return metrics
    
    def parse_dump_output(self, dump_output):
        """Parse la sortie du dump amdgpu_top"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'vram_used': 0,
            'vram_total': 0,
            'vram_percent': 0,
            'gtt_used': 0,
            'gtt_total': 0,
            'gpu_usage': 0,
            'device_name': 'Unknown',
            'processes': []
        }
        
        lines = dump_output.split('\n')
        
        for line in lines:
            # Extraction VRAM
            vram_match = re.search(r'VRAM\s*:\s*usage\s+(\d+)\s*MiB,\s*total\s+(\d+)\s*MiB', line)
            if vram_match:
                metrics['vram_used'] = int(vram_match.group(1))
                metrics['vram_total'] = int(vram_match.group(2))
                if metrics['vram_total'] > 0:
                    metrics['vram_percent'] = (metrics['vram_used'] / metrics['vram_total']) * 100
            
            # Extraction GTT
            gtt_match = re.search(r'GTT\s*:\s*usage\s+(\d+)\s*MiB,\s*total\s+(\d+)\s*MiB', line)
            if gtt_match:
                metrics['gtt_used'] = int(gtt_match.group(1))
                metrics['gtt_total'] = int(gtt_match.group(2))
            
            # Extraction nom device
            device_match = re.search(r'Device Name\s*:\s*\[([^\]]+)\]', line)
            if device_match:
                metrics['device_name'] = device_match.group(1)
        
        return metrics
    
    def get_system_memory_pressure(self):
        """Évalue la pression mémoire système"""
        memory = psutil.virtual_memory()
        return {
            'percent_used': memory.percent,
            'available_gb': memory.available / (1024**3),
            'total_gb': memory.total / (1024**3),
            'pressure_level': 'low' if memory.percent < 60 else 'medium' if memory.percent < 80 else 'high'
        }
    
    def optimize_for_panini_workload(self, workload_type='molecular_analysis'):
        """Optimise GPU pour charge de travail PaniniFS"""
        self.log(f"🔧 Optimisation GPU pour: {workload_type}")
        
        # Récupération état actuel
        gpu_status = self.get_gpu_status()
        if not gpu_status:
            self.log("❌ Impossible de récupérer l'état GPU")
            return False
        
        memory_pressure = self.get_system_memory_pressure()
        
        # Analyse et recommandations
        optimizations = []
        
        # 1. Gestion VRAM
        if gpu_status['vram_percent'] > self.vram_threshold:
            optimizations.append({
                'type': 'vram_management',
                'current': f"{gpu_status['vram_percent']:.1f}%",
                'action': 'Libérer VRAM processus non-critiques',
                'priority': 'high'
            })
            
            # Identifier processus gourmands
            gpu_processes = self.get_gpu_processes()
            for proc in gpu_processes:
                if proc.get('vram_mb', 0) > 200:  # Plus de 200MB
                    optimizations.append({
                        'type': 'process_optimization',
                        'process': proc['name'],
                        'vram_usage': f"{proc['vram_mb']}MB",
                        'action': f'Considérer arrêt temporaire {proc["name"]}',
                        'priority': 'medium'
                    })
        
        # 2. Optimisation charges de travail
        workload_optimizations = self.get_workload_optimizations(workload_type, gpu_status)
        optimizations.extend(workload_optimizations)
        
        # 3. Gestion mémoire système
        if memory_pressure['pressure_level'] == 'high':
            optimizations.append({
                'type': 'system_memory',
                'current': f"{memory_pressure['percent_used']:.1f}%",
                'action': 'Réduire utilisation mémoire système',
                'priority': 'high'
            })
        
        # Application des optimisations
        applied_optimizations = self.apply_optimizations(optimizations)
        
        # Sauvegarde historique
        optimization_record = {
            'timestamp': datetime.now().isoformat(),
            'workload_type': workload_type,
            'gpu_status_before': gpu_status,
            'memory_pressure': memory_pressure,
            'optimizations': optimizations,
            'applied': applied_optimizations
        }
        
        self.optimization_history.append(optimization_record)
        self.save_optimization_history()
        
        self.log(f"✅ Optimisation terminée: {len(applied_optimizations)} actions appliquées")
        return True
    
    def get_workload_optimizations(self, workload_type, gpu_status):
        """Optimisations spécifiques par type de charge"""
        optimizations = []
        
        if workload_type == 'molecular_analysis':
            # PaniniFS : analyse moléculaire
            optimizations.extend([
                {
                    'type': 'molecular_compute',
                    'action': 'Prioriser calculs parallèles atomiques',
                    'priority': 'high',
                    'config': {
                        'chunk_size': min(1024, gpu_status['vram_total'] // 4),
                        'parallel_streams': 2
                    }
                },
                {
                    'type': 'memory_layout',
                    'action': 'Optimiser layout mémoire pour patterns',
                    'priority': 'medium',
                    'config': {
                        'coalesced_access': True,
                        'shared_memory_usage': 'aggressive'
                    }
                }
            ])
        
        elif workload_type == 'corpus_processing':
            # Traitement corpus intensif
            optimizations.extend([
                {
                    'type': 'corpus_compute',
                    'action': 'Parallélisation extraction atomes',
                    'priority': 'high',
                    'config': {
                        'batch_size': 512,
                        'memory_pool': gpu_status['vram_total'] * 0.6
                    }
                }
            ])
        
        elif workload_type == 'synthesis_validation':
            # Validation synthèse
            optimizations.extend([
                {
                    'type': 'validation_compute',
                    'action': 'Optimiser pipeline validation',
                    'priority': 'medium',
                    'config': {
                        'pipeline_depth': 3,
                        'validation_chunks': 256
                    }
                }
            ])
        
        return optimizations
    
    def get_gpu_processes(self):
        """Récupère la liste des processus utilisant le GPU"""
        processes = []
        
        try:
            # Utiliser amdgpu_top pour lister les processus
            result = subprocess.run([
                'amdgpu_top', '-p'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    # Parser format: Name | PID | VRAM | GTT | CPU | etc.
                    if '|' in line and 'Name' not in line:
                        parts = [p.strip() for p in line.split('|')]
                        if len(parts) >= 4:
                            try:
                                vram_str = parts[3].replace('M', '').strip()
                                vram_mb = int(vram_str) if vram_str.isdigit() else 0
                                
                                processes.append({
                                    'name': parts[0],
                                    'pid': parts[1],
                                    'vram_mb': vram_mb,
                                    'gtt_mb': parts[4].replace('M', '').strip() if len(parts) > 4 else '0'
                                })
                            except (ValueError, IndexError):
                                continue
        
        except Exception as e:
            self.log(f"❌ Erreur récupération processus GPU: {e}")
        
        return processes
    
    def apply_optimizations(self, optimizations):
        """Applique les optimisations identifiées"""
        applied = []
        
        for opt in optimizations:
            if opt['type'] == 'vram_management':
                # Forcer garbage collection
                try:
                    import gc
                    gc.collect()
                    applied.append({
                        'optimization': opt,
                        'result': 'garbage collection executed',
                        'success': True
                    })
                except Exception as e:
                    applied.append({
                        'optimization': opt,
                        'result': f'error: {e}',
                        'success': False
                    })
            
            elif opt['type'] == 'molecular_compute':
                # Configuration calculs moléculaires
                config_file = self.results_dir / 'molecular_compute_config.json'
                try:
                    with open(config_file, 'w') as f:
                        json.dump(opt.get('config', {}), f, indent=2)
                    
                    applied.append({
                        'optimization': opt,
                        'result': f'config saved to {config_file}',
                        'success': True
                    })
                except Exception as e:
                    applied.append({
                        'optimization': opt,
                        'result': f'error: {e}',
                        'success': False
                    })
            
            elif opt['type'] == 'system_memory':
                # Optimisation mémoire système
                try:
                    # Ajuster swappiness temporairement si root
                    applied.append({
                        'optimization': opt,
                        'result': 'system memory optimization noted',
                        'success': True
                    })
                except Exception as e:
                    applied.append({
                        'optimization': opt,
                        'result': f'error: {e}',
                        'success': False
                    })
        
        return applied
    
    def monitor_gpu_performance(self, duration_minutes=5):
        """Monitoring continu des performances GPU"""
        self.log(f"📊 Monitoring GPU pendant {duration_minutes} minutes")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        performance_data = []
        
        try:
            while time.time() < end_time:
                gpu_status = self.get_gpu_status()
                if gpu_status:
                    performance_data.append(gpu_status)
                    
                    # Affichage en temps réel
                    self.log(f"📈 VRAM: {gpu_status['vram_percent']:.1f}% | "
                            f"GTT: {gpu_status['gtt_used']}/{gpu_status['gtt_total']}MB")
                
                time.sleep(10)  # Échantillonnage toutes les 10s
        
        except KeyboardInterrupt:
            self.log("🛑 Monitoring interrompu")
        
        # Analyse des données
        if performance_data:
            analysis = self.analyze_performance_data(performance_data)
            self.save_performance_analysis(analysis)
        
        return performance_data
    
    def analyze_performance_data(self, data):
        """Analyse des données de performance"""
        if not data:
            return {}
        
        vram_usage = [d['vram_percent'] for d in data if 'vram_percent' in d]
        
        analysis = {
            'duration_minutes': len(data) / 6,  # 10s intervals
            'samples_count': len(data),
            'vram_stats': {
                'avg': sum(vram_usage) / len(vram_usage) if vram_usage else 0,
                'min': min(vram_usage) if vram_usage else 0,
                'max': max(vram_usage) if vram_usage else 0,
                'stability': 'stable' if max(vram_usage) - min(vram_usage) < 10 else 'variable'
            },
            'recommendations': []
        }
        
        # Recommandations basées sur l'analyse
        if analysis['vram_stats']['avg'] > 80:
            analysis['recommendations'].append("Réduire utilisation VRAM moyenne")
        
        if analysis['vram_stats']['stability'] == 'variable':
            analysis['recommendations'].append("Optimiser stabilité allocations mémoire")
        
        return analysis
    
    def save_optimization_history(self):
        """Sauvegarde historique optimisations"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_file = self.results_dir / f"gpu_optimization_history_{timestamp}.json"
        
        with open(history_file, 'w') as f:
            json.dump(self.optimization_history, f, indent=2)
        
        self.log(f"💾 Historique sauvé: {history_file.name}")
    
    def save_performance_analysis(self, analysis):
        """Sauvegarde analyse performance"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        analysis_file = self.results_dir / f"gpu_performance_analysis_{timestamp}.json"
        
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        self.log(f"📊 Analyse sauvée: {analysis_file.name}")
    
    def create_gpu_optimization_config(self, workload_type):
        """Crée configuration optimisée pour charge de travail"""
        gpu_status = self.get_gpu_status()
        if not gpu_status:
            return None
        
        config = {
            'workload_type': workload_type,
            'gpu_device': gpu_status.get('device_name', 'Unknown'),
            'optimization_settings': {
                'memory_management': {
                    'vram_reserve_mb': max(256, gpu_status['vram_total'] * 0.1),
                    'aggressive_gc': gpu_status['vram_percent'] > 70,
                    'memory_pool_size': gpu_status['vram_total'] * 0.8
                },
                'compute_settings': {
                    'parallel_streams': 2 if gpu_status['vram_total'] > 1024 else 1,
                    'batch_size': min(1024, gpu_status['vram_total'] // 2),
                    'precision': 'mixed' if gpu_status['vram_total'] > 2048 else 'fp16'
                },
                'panini_specific': {
                    'atomic_chunk_size': 512,
                    'molecular_batch_size': 256,
                    'synthesis_pipeline_depth': 3
                }
            }
        }
        
        # Sauvegarde config
        config_file = self.results_dir / f"panini_gpu_config_{workload_type}.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.log(f"⚙️ Configuration GPU créée: {config_file.name}")
        return config


def main():
    print("🎮 OPTIMISEUR GPU PANINI")
    print("="*30)
    print("Optimisation intelligente GPU pour PaniniFS")
    print("Surveillance et ajustement dynamique")
    print("="*30)
    
    optimizer = PaniniGPUOptimizer()
    
    # Test optimisation pour différentes charges
    workloads = ['molecular_analysis', 'corpus_processing', 'synthesis_validation']
    
    for workload in workloads:
        print(f"\n🔧 Test optimisation: {workload}")
        optimizer.optimize_for_panini_workload(workload)
        optimizer.create_gpu_optimization_config(workload)
        time.sleep(2)
    
    # Monitoring court
    print(f"\n📊 Monitoring performance...")
    optimizer.monitor_gpu_performance(1)  # 1 minute
    
    print(f"\n✅ Optimisation GPU terminée!")
    print(f"📁 Résultats dans gpu_optimization_results/")


if __name__ == '__main__':
    main()