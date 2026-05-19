"""
Module de base pour la gestion des processus et monitoring système
"""

import psutil
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class ProcessManager:
    """Gestionnaire de processus réutilisable"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def find_processes_by_keywords(self, keywords: List[str]) -> List[Dict]:
        """Trouve les processus contenant les mots-clés"""
        found_processes = []
        
        for proc in psutil.process_iter(['pid', 'cmdline', 'cpu_percent', 'memory_info']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                
                for keyword in keywords:
                    if keyword in cmdline:
                        cpu_pct = proc.cpu_percent(interval=0.1)
                        memory_mb = proc.info['memory_info'].rss / 1024 / 1024
                        
                        try:
                            affinity = proc.cpu_affinity()
                        except (AttributeError, psutil.AccessDenied):
                            affinity = []
                        
                        found_processes.append({
                            'pid': proc.info['pid'],
                            'name': keyword,
                            'cmdline': cmdline,
                            'cpu_percent': cpu_pct,
                            'memory_mb': memory_mb,
                            'affinity': affinity,
                            'process': proc
                        })
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return found_processes
    
    def stop_processes(self, processes: List[Dict], timeout: int = 5) -> Tuple[int, int]:
        """Arrête les processus proprement"""
        if not processes:
            return 0, 0
        
        # Arrêt propre avec SIGTERM
        terminated = []
        for proc_info in processes:
            try:
                proc_info['process'].terminate()
                self.logger.info(f"SIGTERM envoyé à {proc_info['name']} (PID {proc_info['pid']})")
                terminated.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Attente
        time.sleep(timeout)
        
        # Force l'arrêt des récalcitrants
        still_running = []
        for proc_info in terminated:
            try:
                if proc_info['process'].is_running():
                    still_running.append(proc_info)
                    proc_info['process'].kill()
                    self.logger.info(f"SIGKILL envoyé à {proc_info['name']}")
            except psutil.NoSuchProcess:
                pass
        
        return len(terminated), len(still_running)


class SystemMonitor:
    """Moniteur système réutilisable"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_cpu_metrics(self) -> Dict:
        """Récupère les métriques CPU"""
        cpu_usage = psutil.cpu_percent(interval=0.5, percpu=True)
        
        return {
            'total_cores': len(cpu_usage),
            'average_usage': sum(cpu_usage) / len(cpu_usage),
            'per_core_usage': [
                {
                    'core': i,
                    'usage': usage,
                    'status': '🔥' if usage > 30 else '⚡' if usage > 10 else '💤'
                }
                for i, usage in enumerate(cpu_usage)
            ]
        }
    
    def get_memory_metrics(self) -> Dict:
        """Récupère les métriques mémoire"""
        memory = psutil.virtual_memory()
        
        return {
            'total_gb': memory.total / (1024**3),
            'available_gb': memory.available / (1024**3),
            'used_percent': memory.percent,
            'status': '🔥' if memory.percent > 80 else '⚡' if memory.percent > 60 else '✅'
        }
    
    def get_network_ports(self, ports: List[int]) -> Dict:
        """Vérifie l'état des ports réseau"""
        ports_status = {}
        
        for conn in psutil.net_connections():
            if conn.laddr and conn.laddr.port in ports:
                ports_status[conn.laddr.port] = {
                    'status': 'LISTEN' if conn.status == 'LISTEN' else conn.status,
                    'pid': conn.pid
                }
        
        return ports_status


class CPUAffinityManager:
    """Gestionnaire d'affinité CPU réutilisable"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.allocations = {}
    
    def allocate_cores(self, process_name: str, cores: List[int]) -> bool:
        """Alloue des cores à un processus"""
        try:
            total_cores = psutil.cpu_count()
            if max(cores) >= total_cores:
                self.logger.warning(f"Core {max(cores)} dépasse le nombre disponible ({total_cores})")
                return False
            
            self.allocations[process_name] = cores
            self.logger.info(f"Cores {cores} alloués à {process_name}")
            return True
        except Exception as e:
            self.logger.error(f"Erreur allocation cores pour {process_name}: {e}")
            return False
    
    def apply_affinity(self, pid: int, cores: List[int]) -> bool:
        """Applique l'affinité CPU à un processus"""
        try:
            proc = psutil.Process(pid)
            proc.cpu_affinity(cores)
            self.logger.info(f"Affinité appliquée au PID {pid}: cores {cores}")
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            self.logger.error(f"Impossible d'appliquer l'affinité au PID {pid}: {e}")
            return False
    
    def get_allocations(self) -> Dict:
        """Retourne les allocations actuelles"""
        return self.allocations.copy()


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure le logging pour les modules"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('panini_system.log')
        ]
    )
    return logging.getLogger(__name__)


def get_timestamp() -> str:
    """Retourne un timestamp formaté"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')