#!/usr/bin/env python3
"""
🎯 INTÉGRATEUR CORPUS TRIPARTITE ULTIME
=======================================

Intégration finale de tous les corpus avec le système tripartite dhātu
pour atteindre la restitution 100% parfaite sur l'ensemble des données.

Mode autonome - Traitement complet sans intervention
"""

import json
import logging
from pathlib import Path
from datetime import datetime
import time
from typing import Dict, List, Any
import sys

# Ajout du chemin pour imports
sys.path.append(str(Path(__file__).parent.parent))

from compression.dhatu_tripartite_system import DhatuTripartiteSystem

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('integration_corpus_tripartite_ultimate.log'),
        logging.StreamHandler()
    ]
)

class CorpusTripartiteIntegrator:
    """Intégrateur corpus avec système tripartite dhātu"""
    
    def __init__(self):
        self.tripartite_system = DhatuTripartiteSystem()
        self.processed_files = []
        self.integration_results = {}
        self.total_original_size = 0
        self.total_compressed_size = 0
        self.session_start = time.time()
    
    def find_all_corpus_files(self) -> List[Path]:
        """Trouve tous les fichiers corpus dans le workspace"""
        corpus_files = []
        root_path = Path.cwd()
        
        # Motifs de fichiers corpus
        patterns = [
            '**/corpus*.json',
            '**/gutenberg*.json', 
            '**/multilingual*.json',
            '**/molecules*.json',
            '**/dhatu*.json',
            '**/integration*.json'
        ]
        
        for pattern in patterns:
            files = list(root_path.glob(pattern))
            corpus_files.extend(files)
        
        # Déduplication
        unique_files = list(set(corpus_files))
        logging.info(f"🔍 Trouvés {len(unique_files)} fichiers corpus uniques")
        
        return unique_files
    
    def load_corpus_content(self, file_path: Path) -> Dict[str, Any]:
        """Charge contenu d'un fichier corpus"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logging.info(f"📁 Chargé: {file_path.name} ({len(str(data))} caractères)")
            return data
            
        except Exception as e:
            logging.error(f"❌ Erreur lecture {file_path}: {e}")
            return {}
    
    def extract_texts_from_corpus(self, corpus_data: Dict[str, Any], source_file: str) -> List[Dict[str, str]]:
        """Extrait textes analysables du corpus"""
        texts = []
        
        def extract_recursive(obj, path="root"):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}"
                    
                    if isinstance(value, str) and len(value.strip()) > 20:
                        # Texte analysable trouvé
                        texts.append({
                            'text': value.strip(),
                            'source_file': source_file,
                            'path': current_path,
                            'length': len(value.strip())
                        })
                    elif isinstance(value, (dict, list)):
                        extract_recursive(value, current_path)
                        
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]"
                    extract_recursive(item, current_path)
        
        extract_recursive(corpus_data)
        logging.info(f"   📄 Extraits {len(texts)} textes analysables")
        return texts
    
    def process_corpus_file_tripartite(self, file_path: Path) -> Dict[str, Any]:
        """Traite un fichier corpus avec système tripartite"""
        corpus_data = self.load_corpus_content(file_path)
        if not corpus_data:
            return {'error': 'Chargement échoué'}
        
        texts = self.extract_texts_from_corpus(corpus_data, file_path.name)
        if not texts:
            return {'error': 'Aucun texte analysable'}
        
        # Traitement tripartite de chaque texte
        processed_texts = []
        total_compression_ratio = 0
        total_fidelity = 0
        perfect_reconstructions = 0
        
        for i, text_info in enumerate(texts[:50]):  # Limite pour performance
            try:
                text = text_info['text']
                context = f"{text_info['source_file']}:{text_info['path']}"
                
                # Compression tripartite
                compressed_data, metadata = self.tripartite_system.compress_tripartite(text, context)
                
                # Décompression et validation
                reconstructed_text, metrics = self.tripartite_system.decompress_tripartite(compressed_data, metadata)
                
                # Métriques
                total_compression_ratio += metrics.compression_ratio
                total_fidelity += metrics.reconstruction_fidelity
                if metrics.is_perfect_reconstruction():
                    perfect_reconstructions += 1
                
                # Statistiques tailles
                self.total_original_size += len(text)
                self.total_compressed_size += len(compressed_data)
                
                processed_texts.append({
                    'original_length': len(text),
                    'compressed_length': len(compressed_data),
                    'reconstructed_length': len(reconstructed_text),
                    'compression_ratio': metrics.compression_ratio,
                    'reconstruction_fidelity': metrics.reconstruction_fidelity,
                    'is_perfect': metrics.is_perfect_reconstruction(),
                    'processing_time': metrics.processing_time,
                    'source_path': text_info['path']
                })
                
            except Exception as e:
                logging.error(f"   ❌ Erreur texte {i}: {e}")
                continue
        
        # Résultats agrégés
        num_processed = len(processed_texts)
        results = {
            'source_file': file_path.name,
            'texts_extracted': len(texts),
            'texts_processed': num_processed,
            'average_compression_ratio': total_compression_ratio / max(num_processed, 1),
            'average_fidelity': total_fidelity / max(num_processed, 1),
            'perfect_reconstructions': perfect_reconstructions,
            'perfect_reconstruction_rate': perfect_reconstructions / max(num_processed, 1),
            'processed_texts_details': processed_texts
        }
        
        logging.info(f"   ✅ Traité {num_processed} textes - Perfection: {perfect_reconstructions}/{num_processed}")
        return results
    
    def integrate_all_corpus_tripartite(self):
        """Intégration complète de tous les corpus avec tripartite"""
        logging.info("🚀 INTÉGRATION CORPUS TRIPARTITE ULTIMATE - DÉMARRAGE")
        logging.info("=" * 70)
        
        corpus_files = self.find_all_corpus_files()
        
        for i, file_path in enumerate(corpus_files):
            logging.info(f"🔄 Traitement {i+1}/{len(corpus_files)}: {file_path.name}")
            
            try:
                results = self.process_corpus_file_tripartite(file_path)
                self.integration_results[file_path.name] = results
                self.processed_files.append(str(file_path))
                
            except Exception as e:
                logging.error(f"❌ Erreur traitement {file_path}: {e}")
                self.integration_results[file_path.name] = {'error': str(e)}
        
        # Génération rapport final
        self.generate_integration_report()
    
    def generate_integration_report(self):
        """Génère rapport final intégration"""
        successful_files = [r for r in self.integration_results.values() if 'error' not in r]
        
        # Calculs agrégés
        total_texts_processed = sum(r.get('texts_processed', 0) for r in successful_files)
        total_perfect_reconstructions = sum(r.get('perfect_reconstructions', 0) for r in successful_files)
        
        avg_fidelity = 0
        avg_compression_ratio = 0
        if successful_files:
            avg_fidelity = sum(r.get('average_fidelity', 0) for r in successful_files) / len(successful_files)
            avg_compression_ratio = sum(r.get('average_compression_ratio', 0) for r in successful_files) / len(successful_files)
        
        # Rapport final
        final_report = {
            'integration_summary': {
                'files_found': len(self.integration_results),
                'files_processed_successfully': len(successful_files),
                'total_texts_processed': total_texts_processed,
                'total_perfect_reconstructions': total_perfect_reconstructions,
                'overall_perfect_rate': total_perfect_reconstructions / max(total_texts_processed, 1),
                'average_fidelity': avg_fidelity,
                'average_compression_ratio': avg_compression_ratio,
                'total_original_size_bytes': self.total_original_size,
                'total_compressed_size_bytes': self.total_compressed_size,
                'overall_compression_ratio': self.total_original_size / max(self.total_compressed_size, 1),
                'processing_time_seconds': time.time() - self.session_start
            },
            'detailed_results': self.integration_results,
            'tripartite_performance': self.tripartite_system.get_performance_summary(),
            'timestamp': datetime.now().isoformat(),
            'status': 'INTEGRATION_TRIPARTITE_COMPLETED'
        }
        
        # Sauvegarde rapport
        report_file = Path("integration_corpus_tripartite_ultimate_final.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)
        
        # Affichage résumé
        logging.info("📊 RÉSULTATS INTÉGRATION TRIPARTITE ULTIMATE:")
        logging.info(f"   Fichiers traités: {len(successful_files)}/{len(self.integration_results)}")
        logging.info(f"   Textes traités: {total_texts_processed}")
        logging.info(f"   Reconstructions parfaites: {total_perfect_reconstructions}")
        logging.info(f"   Taux perfection global: {total_perfect_reconstructions/max(total_texts_processed,1):.1%}")
        logging.info(f"   Fidélité moyenne: {avg_fidelity:.1%}")
        logging.info(f"   Compression moyenne: {avg_compression_ratio:.3f}x")
        logging.info(f"   Temps total: {time.time() - self.session_start:.1f}s")
        logging.info(f"   Rapport sauvegardé: {report_file}")
        
        return final_report

def main():
    """Point d'entrée principal"""
    try:
        integrator = CorpusTripartiteIntegrator()
        integrator.integrate_all_corpus_tripartite()
        
        logging.info("🎉 INTÉGRATION TRIPARTITE ULTIMATE TERMINÉE AVEC SUCCÈS")
        return True
        
    except Exception as e:
        logging.error(f"❌ Erreur intégration: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)