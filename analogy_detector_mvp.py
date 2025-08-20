#!/usr/bin/env python3
"""
🔬 PaniniFS MVP - DÉTECTEUR D'ANALOGIES AVANCÉ
Test spécialisé pour validation concept analogies Pāṇini
"""

import time
import json
from pathlib import Path
from collections import Counter
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class AnalogySemantic:
    """Structure sémantique pour détection analogies"""
    core_concepts: List[str]
    structural_patterns: List[str]
    semantic_density: float
    narrative_flow: List[str]
    conceptual_signature: str

class PaniniFSAnalogyDetector:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.start_time = time.time()
        self.results = {}
        
    def extract_narrative_structure(self, text):
        """Extraction structure narrative à la Pāṇini"""
        # Normalisation
        text = text.lower()
        
        # Détection patterns narratifs
        narrative_markers = {
            'character_intro': r'(enter|romeo|juliet|hamlet)',
            'dialogue': r'(\w+:|\w+ says|\w+ speaks)',
            'action': r'(dies?|love|kill|marry|fight)',
            'emotion': r'(sad|happy|angry|love|hate|fear)',
            'transition': r'(then|next|after|before|when)'
        }
        
        patterns = []
        for pattern_type, regex in narrative_markers.items():
            matches = len(re.findall(regex, text))
            if matches > 0:
                patterns.append(f"{pattern_type}:{matches}")
                
        return patterns
    
    def extract_algorithmic_structure(self, code):
        """Extraction structure algorithmique universelle"""
        # Patterns algorithmiques universels
        algo_patterns = {
            'conditional': r'(if|elif|else|\?|switch|case)',
            'loop': r'(for|while|foreach|map|filter)',
            'function': r'(def|function|func|\w+\s*\()',
            'variable': r'(\w+\s*=|\w+\s*:)',
            'return': r'(return|yield|\w+\s*;)',
            'validation': r'(check|valid|test|assert|verify)'
        }
        
        patterns = []
        for pattern_type, regex in algo_patterns.items():
            matches = len(re.findall(regex, code, re.IGNORECASE))
            if matches > 0:
                patterns.append(f"{pattern_type}:{matches}")
                
        return patterns
    
    def calculate_structural_analogy(self, struct1, struct2):
        """Calcul analogie structurelle pure"""
        if not struct1 or not struct2:
            return 0.0
            
        # Extraction types de patterns
        types1 = set(p.split(':')[0] for p in struct1)
        types2 = set(p.split(':')[0] for p in struct2)
        
        # Intersection patterns
        common_types = types1.intersection(types2)
        total_types = types1.union(types2)
        
        if not total_types:
            return 0.0
            
        structural_similarity = len(common_types) / len(total_types)
        
        # Bonus pour proportions similaires
        proportion_bonus = 0.0
        for pattern_type in common_types:
            count1 = next((int(p.split(':')[1]) for p in struct1 if p.startswith(pattern_type)), 0)
            count2 = next((int(p.split(':')[1]) for p in struct2 if p.startswith(pattern_type)), 0)
            
            if count1 > 0 and count2 > 0:
                ratio = min(count1, count2) / max(count1, count2)
                proportion_bonus += ratio
                
        if common_types:
            proportion_bonus /= len(common_types)
        
        return structural_similarity * 0.6 + proportion_bonus * 0.4
    
    def test_narrative_analogy(self):
        """Test analogie narrative : Romeo EN vs Romeo FR"""
        print("📖 Testing narrative analogy (Romeo EN/FR)...")
        
        romeo_en = (self.base_dir / 'gutenberg' / 'romeo_en.txt').read_text()
        romeo_fr = (self.base_dir / 'gutenberg' / 'romeo_fr.txt').read_text()
        
        struct_en = self.extract_narrative_structure(romeo_en)
        struct_fr = self.extract_narrative_structure(romeo_fr)
        
        analogy_score = self.calculate_structural_analogy(struct_en, struct_fr)
        
        self.results['narrative_analogy'] = {
            'romeo_en_fr_analogy': analogy_score,
            'target': 0.70,
            'status': 'PASS' if analogy_score >= 0.70 else 'FAIL',
            'structure_en': struct_en,
            'structure_fr': struct_fr,
            'insight': 'Même structure narrative, langues différentes'
        }
        
        print(f"  Narrative analogy score: {analogy_score:.1%}")
        print(f"  Common patterns: {len(set(p.split(':')[0] for p in struct_en).intersection(set(p.split(':')[0] for p in struct_fr)))}")
        return analogy_score
    
    def test_algorithmic_analogy(self):
        """Test analogie algorithmique : Python vs JavaScript"""
        print("⚙️  Testing algorithmic analogy (Python/JS)...")
        
        py_code = (self.base_dir / 'formats' / 'demo_algo.py').read_text()
        js_code = (self.base_dir / 'formats' / 'demo_algo.js').read_text()
        
        struct_py = self.extract_algorithmic_structure(py_code)
        struct_js = self.extract_algorithmic_structure(js_code)
        
        analogy_score = self.calculate_structural_analogy(struct_py, struct_js)
        
        self.results['algorithmic_analogy'] = {
            'python_js_analogy': analogy_score,
            'target': 0.80,
            'status': 'PASS' if analogy_score >= 0.80 else 'FAIL',
            'structure_py': struct_py,
            'structure_js': struct_js,
            'insight': 'Même algorithme, syntaxes différentes'
        }
        
        print(f"  Algorithmic analogy score: {analogy_score:.1%}")
        print(f"  Structural patterns: {struct_py} vs {struct_js}")
        return analogy_score
    
    def test_format_analogy(self):
        """Test analogie format : YAML vs JSON"""
        print("📋 Testing format analogy (YAML/JSON)...")
        
        yaml_content = (self.base_dir / 'formats' / 'demo_config.yml').read_text()
        json_content = (self.base_dir / 'formats' / 'demo_config.json').read_text()
        
        # Extraction structure de données
        yaml_structure = self.extract_data_structure(yaml_content)
        json_structure = self.extract_data_structure(json_content)
        
        analogy_score = self.calculate_structural_analogy(yaml_structure, json_structure)
        
        self.results['format_analogy'] = {
            'yaml_json_analogy': analogy_score,
            'target': 0.90,
            'status': 'PASS' if analogy_score >= 0.90 else 'FAIL',
            'structure_yaml': yaml_structure,
            'structure_json': json_structure,
            'insight': 'Mêmes données, formats différents'
        }
        
        print(f"  Format analogy score: {analogy_score:.1%}")
        return analogy_score
    
    def extract_data_structure(self, config_text):
        """Extraction structure données universelle"""
        patterns = []
        
        # Patterns structure données
        if re.search(r'\w+:\s*\w+', config_text):
            patterns.append('key_value:' + str(len(re.findall(r'\w+:\s*\w+', config_text))))
        
        if re.search(r'[{\[]', config_text):
            patterns.append('nested:' + str(len(re.findall(r'[{\[]', config_text))))
            
        if re.search(r'[\d.]+', config_text):
            patterns.append('numeric:' + str(len(re.findall(r'[\d.]+', config_text))))
            
        if re.search(r'"[^"]*"', config_text):
            patterns.append('string:' + str(len(re.findall(r'"[^"]*"', config_text))))
            
        return patterns
    
    def test_cross_domain_analogy(self):
        """Test analogie cross-domaine : littérature vs algorithme"""
        print("🌊 Testing cross-domain analogy (narrative/algorithm)...")
        
        # Romeo (narrative structure)
        romeo_en = (self.base_dir / 'gutenberg' / 'romeo_en.txt').read_text()
        narrative_struct = self.extract_narrative_structure(romeo_en)
        
        # Algorithm (logical structure)  
        py_code = (self.base_dir / 'formats' / 'demo_algo.py').read_text()
        algo_struct = self.extract_algorithmic_structure(py_code)
        
        # Recherche patterns universels
        universal_patterns = self.find_universal_patterns(narrative_struct, algo_struct)
        
        analogy_score = len(universal_patterns) / max(len(narrative_struct), len(algo_struct)) if narrative_struct or algo_struct else 0
        
        self.results['cross_domain_analogy'] = {
            'narrative_algorithm_analogy': analogy_score,
            'target': 0.30,
            'status': 'PASS' if analogy_score >= 0.30 else 'FAIL',
            'universal_patterns': universal_patterns,
            'insight': 'Patterns universels cross-domaines'
        }
        
        print(f"  Cross-domain analogy score: {analogy_score:.1%}")
        print(f"  Universal patterns found: {universal_patterns}")
        return analogy_score
    
    def find_universal_patterns(self, struct1, struct2):
        """Recherche patterns universels entre domaines"""
        # Mapping concepts universels
        universal_mappings = {
            'conditional': ['if', 'choice', 'decision'],
            'sequence': ['then', 'next', 'after'],
            'character': ['function', 'actor', 'agent'],
            'action': ['execution', 'verb', 'process']
        }
        
        patterns1 = [p.split(':')[0] for p in struct1]
        patterns2 = [p.split(':')[0] for p in struct2]
        
        universal_found = []
        for universal, concepts in universal_mappings.items():
            if any(c in patterns1 for c in concepts) and any(c in patterns2 for c in concepts):
                universal_found.append(universal)
                
        return universal_found
    
    def generate_analogy_report(self):
        """Rapport spécialisé détection analogies"""
        elapsed = time.time() - self.start_time
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r['status'] == 'PASS')
        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        # Calcul score analogie globale
        analogy_scores = []
        for test_name, result in self.results.items():
            score_key = next((k for k in result.keys() if k.endswith('_analogy')), None)
            if score_key:
                analogy_scores.append(result[score_key])
        
        avg_analogy_score = sum(analogy_scores) / len(analogy_scores) if analogy_scores else 0
        
        print(f"\n🔬 PANINIFS ANALOGY DETECTION REPORT")
        print(f"=" * 55)
        print(f"⏱️  Processing Time: {elapsed:.1f}s")
        print(f"🎯 Average Analogy Score: {avg_analogy_score:.1%}")
        print(f"📊 Tests Passed: {passed_tests}/{total_tests}")
        print(f"🌟 Overall Status: {'✅ ANALOGIES DETECTED' if success_rate >= 0.75 else '⚠️ PARTIAL DETECTION' if success_rate >= 0.5 else '❌ DETECTION FAILED'}")
        
        print(f"\n📋 Analogy Test Details:")
        for test_name, result in self.results.items():
            status_emoji = "✅" if result['status'] == 'PASS' else "❌"
            score_key = next((k for k in result.keys() if k.endswith('_analogy')), None)
            score = result[score_key] if score_key else 0
            insight = result.get('insight', 'No insight')
            print(f"   {status_emoji} {test_name}: {score:.1%} - {insight}")
        
        print(f"\n💡 Insights:")
        if avg_analogy_score >= 0.70:
            print("   🚀 Strong analogy detection capability")
            print("   📈 Ready for complex semantic patterns")
        elif avg_analogy_score >= 0.50:
            print("   🔧 Good foundation, needs refinement")
            print("   📊 Focus on cross-domain pattern detection")
        else:
            print("   ⚠️  Core analogy detection needs work")
            print("   🔍 Review structural pattern extraction")
        
        # Sauvegarde rapport analogies
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'elapsed_seconds': round(elapsed, 2),
            'average_analogy_score': avg_analogy_score,
            'success_rate': success_rate,
            'analogy_results': self.results
        }
        
        with open(self.base_dir / 'results' / 'analogy_detection.json', 'w') as f:
            json.dump(report, f, indent=2)
            
        return report

def main():
    detector = PaniniFSAnalogyDetector('/tmp/paninifs_mvp')
    
    print("🔬 Starting PaniniFS Analogy Detection Tests...")
    print("=" * 50)
    
    # Tests analogies spécialisés
    detector.test_narrative_analogy()
    detector.test_algorithmic_analogy() 
    detector.test_format_analogy()
    detector.test_cross_domain_analogy()
    
    # Rapport final
    report = detector.generate_analogy_report()
    
    print(f"\n📄 Analogy report saved: /tmp/paninifs_mvp/results/analogy_detection.json")
    
    return report

if __name__ == "__main__":
    main()
