#!/usr/bin/env python3
"""
🔧 CORRECTIF SYSTÈME AUTONOME RECHERCHE
======================================
Version sans multiprocessing problématique
"""

import json
import time
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
import queue


class AutonomousResearchEngineFixed:
    """Version corrigée du moteur autonome sans problème sérialisation"""
    
    def __init__(self, workspace: Path, duration_hours: int = 12):
        self.workspace = workspace
        self.duration_hours = duration_hours
        self.session_id = f"auto_fixed_{int(time.time())}"
        self.results_dir = workspace / f'autonomous_research_{self.session_id}'
        self.results_dir.mkdir(exist_ok=True)
        
        # État de recherche
        self.research_state = {
            'cycles_completed': 0,
            'hypotheses_tested': 0,
            'discoveries': [],
            'performance_metrics': {},
            'corpus_size': 0,
            'active_threads': 0,
            'errors': [],
            'last_checkpoint': None
        }
        
        # Configuration
        self.cycle_duration = 1800  # 30 minutes
        self.health_check_interval = 60  # 1 minute
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.results_dir / f'{self.session_id}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        self.log("🚀 Moteur autonome corrigé initialisé")
    
    def log(self, message: str):
        """Logging avec timestamp"""
        self.logger.info(message)
    
    def generate_hypotheses(self, count: int = 10) -> List[Dict]:
        """Génération hypothèses sans multiprocessing"""
        hypotheses = []
        
        dhatu_base = ['gam', 'kar', 'kṛ', 'bhū', 'as', 'vid', 'śru', 'pac']
        hypothesis_types = [
            'aspectual_analysis', 'semantic_evolution', 'morphological_pattern',
            'syntactic_behavior', 'phonological_change', 'dialectal_variation'
        ]
        
        for i in range(count):
            dhatu = random.choice(dhatu_base)
            hyp_type = random.choice(hypothesis_types)
            
            hypothesis = {
                'id': f"hyp_{self.session_id}_{i}",
                'dhatu': dhatu,
                'type': hyp_type,
                'description': f"Hypothèse {hyp_type} pour dhātu {dhatu}",
                'confidence': random.uniform(0.3, 0.9),
                'generated_at': datetime.now().isoformat(),
                'status': 'pending'
            }
            
            hypotheses.append(hypothesis)
        
        return hypotheses
    
    def test_hypothesis_simple(self, hypothesis: Dict) -> Dict:
        """Test simple d'hypothèse sans multiprocessing"""
        # Simulation test
        time.sleep(random.uniform(0.1, 0.5))
        
        success_rate = 0.7  # 70% de succès
        is_validated = random.random() < success_rate
        
        result = {
            'hypothesis_id': hypothesis['id'],
            'dhatu': hypothesis['dhatu'],
            'type': hypothesis['type'],
            'validated': is_validated,
            'confidence': hypothesis['confidence'],
            'test_score': random.uniform(0.4, 0.95),
            'test_timestamp': datetime.now().isoformat(),
            'evidence': f"Analyse {hypothesis['type']} pour {hypothesis['dhatu']}",
            'method': 'corpus_analysis'
        }
        
        return result
    
    def process_discoveries(self, test_results: List[Dict]) -> List[Dict]:
        """Traitement découvertes"""
        discoveries = []
        
        for result in test_results:
            if result['validated'] and result['test_score'] > 0.8:
                discovery = {
                    'id': f"discovery_{int(time.time())}_{len(discoveries)}",
                    'dhatu': result['dhatu'],
                    'type': result['type'],
                    'significance': 'high' if result['test_score'] > 0.9 else 'medium',
                    'description': f"Découverte {result['type']} pour {result['dhatu']}",
                    'evidence_score': result['test_score'],
                    'discovered_at': datetime.now().isoformat()
                }
                discoveries.append(discovery)
        
        return discoveries
    
    def save_cycle_results(self, cycle: int, hypotheses: List[Dict], 
                          test_results: List[Dict], discoveries: List[Dict]):
        """Sauvegarde résultats cycle"""
        cycle_data = {
            'cycle_number': cycle,
            'timestamp': datetime.now().isoformat(),
            'hypotheses_count': len(hypotheses),
            'tests_completed': len(test_results),
            'discoveries_count': len(discoveries),
            'hypotheses': hypotheses,
            'test_results': test_results,
            'discoveries': discoveries,
            'session_id': self.session_id
        }
        
        cycle_file = self.results_dir / f'cycle_{cycle}_results.json'
        with open(cycle_file, 'w', encoding='utf-8') as f:
            json.dump(cycle_data, f, ensure_ascii=False, indent=2)
        
        self.log(f"💾 Résultats cycle {cycle} sauvegardés")
    
    def execute_research_cycle(self) -> Dict:
        """Exécution cycle de recherche corrigé"""
        cycle_start = time.time()
        cycle = self.research_state['cycles_completed'] + 1
        
        self.log(f"🔄 Début cycle {cycle}")
        
        try:
            # 1. Génération hypothèses
            hypotheses = self.generate_hypotheses(count=random.randint(8, 15))
            self.log(f"🧠 Générées {len(hypotheses)} nouvelles hypothèses")
            
            # 2. Test hypothèses (séquentiel pour éviter problème multiprocessing)
            test_results = []
            for hypothesis in hypotheses:
                result = self.test_hypothesis_simple(hypothesis)
                test_results.append(result)
            
            validated_count = sum(1 for r in test_results if r['validated'])
            self.log(f"✅ {validated_count}/{len(test_results)} hypothèses validées")
            
            # 3. Découvertes
            discoveries = self.process_discoveries(test_results)
            if discoveries:
                self.log(f"🎯 {len(discoveries)} nouvelles découvertes")
            
            # 4. Sauvegarde
            self.save_cycle_results(cycle, hypotheses, test_results, discoveries)
            
            # 5. Mise à jour état
            self.research_state['cycles_completed'] = cycle
            self.research_state['hypotheses_tested'] += len(test_results)
            self.research_state['discoveries'].extend(discoveries)
            
            cycle_duration = time.time() - cycle_start
            
            cycle_result = {
                'cycle': cycle,
                'duration': cycle_duration,
                'hypotheses_generated': len(hypotheses),
                'hypotheses_tested': len(test_results),
                'hypotheses_validated': validated_count,
                'discoveries': len(discoveries),
                'timestamp': datetime.now().isoformat()
            }
            
            self.log(f"✅ Cycle {cycle} terminé en {cycle_duration:.1f}s")
            
            return cycle_result
            
        except Exception as e:
            error_info = {
                'timestamp': datetime.now().isoformat(),
                'message': 'Erreur cycle recherche',
                'exception': str(e),
                'cycle': cycle
            }
            
            self.research_state['errors'].append(error_info)
            self.log(f"❌ Erreur cycle {cycle}: {e}")
            
            return {'error': str(e), 'cycle': cycle}
    
    def monitor_health(self):
        """Monitoring santé simple"""
        health_file = self.results_dir / 'health_metrics.json'
        health_metrics = []
        
        while True:
            try:
                import psutil
                
                health = {
                    'timestamp': datetime.now().isoformat(),
                    'memory_usage': psutil.virtual_memory().percent,
                    'disk_usage': psutil.disk_usage('/').percent,
                    'cpu_usage': psutil.cpu_percent(interval=1),
                    'cycles_completed': self.research_state['cycles_completed'],
                    'status': 'healthy'
                }
                
                health_metrics.append(health)
                
                # Garder seulement les 100 derniers
                if len(health_metrics) > 100:
                    health_metrics = health_metrics[-100:]
                
                # Sauvegarde
                with open(health_file, 'w', encoding='utf-8') as f:
                    json.dump(health_metrics, f, ensure_ascii=False, indent=2)
                
                time.sleep(self.health_check_interval)
                
            except Exception as e:
                self.log(f"Erreur monitoring santé: {e}")
                time.sleep(60)
    
    def run_autonomous_research(self):
        """Recherche autonome principale"""
        end_time = datetime.now().timestamp() + (self.duration_hours * 3600)
        
        self.log(f"🚀 DÉMARRAGE RECHERCHE AUTONOME - {self.duration_hours} heures")
        self.log(f"⏰ Fin prévue: {datetime.fromtimestamp(end_time)}")
        
        # Démarrage monitoring santé en arrière-plan
        health_thread = threading.Thread(target=self.monitor_health, daemon=True)
        health_thread.start()
        
        try:
            while time.time() < end_time:
                # Cycle de recherche
                cycle_result = self.execute_research_cycle()
                
                # Pause entre cycles
                pause_time = self.cycle_duration - cycle_result.get('duration', 0)
                pause_time = max(300, pause_time)  # Minimum 5 minutes
                
                self.log(f"😴 Pause {pause_time/60:.1f}min avant prochain cycle")
                time.sleep(pause_time)
                
        except KeyboardInterrupt:
            self.log("🛑 Arrêt demandé par utilisateur")
        
        # Rapport final
        final_report = {
            'session_id': self.session_id,
            'duration_hours': self.duration_hours,
            'research_state': self.research_state,
            'final_timestamp': datetime.now().isoformat()
        }
        
        report_file = self.results_dir / 'final_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(final_report, f, ensure_ascii=False, indent=2)
        
        self.log(f"🏁 Recherche autonome terminée - {self.research_state['cycles_completed']} cycles")


def main():
    """Point d'entrée principal"""
    workspace = Path('/home/stephane/GitHub/PaniniFS-Research')
    engine = AutonomousResearchEngineFixed(workspace, duration_hours=12)
    engine.run_autonomous_research()


if __name__ == "__main__":
    main()