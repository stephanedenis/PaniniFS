"""
Système événementiel avec affinité CPU - Module principal
"""

import threading
import queue
import time
import json
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Callable
import logging

from .system_base import CPUAffinityManager, setup_logging


class EventType(Enum):
    """Types d'événements du système"""
    CORPUS_DATA_READY = "corpus_data_ready"
    RESEARCH_HYPOTHESIS_GENERATED = "research_hypothesis_generated"
    OPTIMIZATION_REQUEST = "optimization_request"
    VALIDATION_REQUIRED = "validation_required"
    SYSTEM_HEALTH_CHECK = "system_health_check"
    METRICS_UPDATE = "metrics_update"


@dataclass
class SystemEvent:
    """Événement système"""
    event_type: EventType
    data: Dict[str, Any]
    timestamp: float = None
    priority: int = 1
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class EventProcessor:
    """Processeur d'événements générique"""
    
    def __init__(self, name: str, cores: List[int]):
        self.name = name
        self.cores = cores
        self.event_queue = queue.PriorityQueue()
        self.is_running = False
        self.thread = None
        self.stats = {
            'events_processed': 0,
            'total_processing_time': 0,
            'average_processing_time': 0
        }
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self.handlers = {}
    
    def register_handler(self, event_type: EventType, handler: Callable):
        """Enregistre un gestionnaire pour un type d'événement"""
        self.handlers[event_type] = handler
    
    def start(self, affinity_manager: CPUAffinityManager):
        """Démarre le processeur"""
        if self.is_running:
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._run, args=(affinity_manager,))
        self.thread.daemon = True
        self.thread.start()
        self.logger.info(f"🚀 {self.name} démarré sur cores {self.cores}")
    
    def stop(self):
        """Arrête le processeur"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def add_event(self, event: SystemEvent):
        """Ajoute un événement à traiter"""
        self.event_queue.put((event.priority, event.timestamp, event))
    
    def _run(self, affinity_manager: CPUAffinityManager):
        """Boucle principale du processeur"""
        # Applique l'affinité CPU
        import os
        current_pid = os.getpid()
        affinity_manager.apply_affinity(current_pid, self.cores)
        
        while self.is_running:
            try:
                # Récupère l'événement avec timeout
                priority, timestamp, event = self.event_queue.get(timeout=1)
                
                # Traite l'événement
                start_time = time.time()
                self._process_event(event)
                processing_time = time.time() - start_time
                
                # Met à jour les statistiques
                self.stats['events_processed'] += 1
                self.stats['total_processing_time'] += processing_time
                self.stats['average_processing_time'] = (
                    self.stats['total_processing_time'] / self.stats['events_processed']
                )
                
                self.event_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Erreur traitement événement: {e}")
    
    def _process_event(self, event: SystemEvent):
        """Traite un événement"""
        handler = self.handlers.get(event.event_type)
        if handler:
            handler(event)
        else:
            self.logger.warning(f"Pas de gestionnaire pour {event.event_type}")
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques"""
        return {
            'name': self.name,
            'cores': self.cores,
            'queue_size': self.event_queue.qsize(),
            **self.stats
        }


class EventCoordinator:
    """Coordinateur principal du système événementiel"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.processors = {}
        self.affinity_manager = CPUAffinityManager()
        self.is_running = False
        self.metrics_thread = None
    
    def add_processor(self, processor: EventProcessor):
        """Ajoute un processeur"""
        self.processors[processor.name] = processor
        self.affinity_manager.allocate_cores(processor.name, processor.cores)
    
    def start(self):
        """Démarre le coordinateur"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Démarre tous les processeurs
        for processor in self.processors.values():
            processor.start(self.affinity_manager)
        
        # Démarre le thread de métriques
        self.metrics_thread = threading.Thread(target=self._metrics_loop)
        self.metrics_thread.daemon = True
        self.metrics_thread.start()
        
        self.logger.info("🚀 Système événementiel démarré avec affinité CPU optimisée")
    
    def stop(self):
        """Arrête le coordinateur"""
        self.is_running = False
        
        for processor in self.processors.values():
            processor.stop()
        
        if self.metrics_thread:
            self.metrics_thread.join(timeout=5)
    
    def send_event(self, processor_name: str, event: SystemEvent):
        """Envoie un événement à un processeur"""
        processor = self.processors.get(processor_name)
        if processor:
            processor.add_event(event)
        else:
            self.logger.warning(f"⚠️ Pas de processeur pour {processor_name}")
    
    def broadcast_event(self, event: SystemEvent):
        """Diffuse un événement à tous les processeurs"""
        for processor in self.processors.values():
            processor.add_event(event)
    
    def get_metrics(self) -> Dict:
        """Retourne les métriques du système"""
        return {
            'timestamp': time.time(),
            'total_events': sum(p.stats['events_processed'] for p in self.processors.values()),
            'cpu_allocation': self.affinity_manager.get_allocations(),
            'processors': [p.get_stats() for p in self.processors.values()]
        }
    
    def _metrics_loop(self):
        """Boucle de métriques"""
        while self.is_running:
            try:
                metrics = self.get_metrics()
                
                # Affiche les métriques
                print(f"\n📊 MÉTRIQUES SYSTÈME - {time.strftime('%H:%M:%S')}")
                print(f"📈 Événements traités: {metrics['total_events']}")
                print(f"🔧 Allocation CPU: {metrics['cpu_allocation']}")
                
                for proc_stats in metrics['processors']:
                    avg_time = proc_stats['average_processing_time']
                    print(f"   ⚡ {proc_stats['name']}: cores{proc_stats['cores']}, "
                          f"{proc_stats['events_processed']} événements, "
                          f"queue:{proc_stats['queue_size']}, avg:{avg_time:.3f}s")
                
                # Sauvegarde les métriques
                with open('event_system_metrics.json', 'w') as f:
                    json.dump(metrics, f, indent=2)
                
                time.sleep(30)  # Métriques toutes les 30 secondes
                
            except Exception as e:
                self.logger.error(f"Erreur métriques: {e}")
                time.sleep(5)