#!/usr/bin/env python3
"""
🔬 DHĀTU DETECTOR - Outil de Recherche et Validation des Atomes Conceptuels

Détecte les patterns dhātu (racines conceptuelles primitives) dans différents
types de contenu pour valider l'universalité des concepts atomiques.
"""

import re
import json
from typing import Dict, List, Set, Any
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Dhatu:
    """Racine conceptuelle primitive"""
    root: str                    # Nom du dhātu (ex: 'ITER')
    concept: str                 # Concept primitif (ex: 'répéter, parcourir')
    patterns: List[str]          # Patterns de reconnaissance
    manifestations: Dict[str, List[str]]  # Par domaine (code, text, etc.)
    universality_score: float = 0.0      # Score d'universalité validé

# Catalogue des Dhātu Informationnels Universels
DHATU_CATALOG = [
    Dhatu(
        root="ITER",
        concept="Répéter, parcourir, traverser séquentiellement",
        patterns=[
            r'\bfor\b.*\bin\b',           # for loops
            r'\bwhile\b',                 # while loops  
            r'\brepeat\b',                # repeat patterns
            r'\beach\b',                  # iteration methods
            r'\bmap\b',                   # functional iteration
            r'\bforeach\b',               # foreach patterns
            r'\.forEach\(',               # JavaScript forEach
            r'range\(',                   # Python range
            r'enumerate\(',               # Python enumerate
        ],
        manifestations={
            'programming': ['for loops', 'while loops', 'iterators', 'map/reduce'],
            'natural_language': ['again', 'repeat', 'each', 'every', 'all'],
            'baby_sign': ['MORE gesture', 'AGAIN gesture'],
            'cognition': ['repetition', 'enumeration', 'scanning']
        }
    ),
    
    Dhatu(
        root="TRANS",
        concept="Transformer, changer d'état, convertir",
        patterns=[
            r'\btransform\b',
            r'\bconvert\b',
            r'\bmap\b',
            r'\bfilter\b',
            r'\bmutate\b',
            r'\.map\(',
            r'\.filter\(',
            r'\.transform\(',
            r'=>',                        # Arrow functions (transformation)
            r'\bprocess\b',
            r'\bparse\b',
        ],
        manifestations={
            'programming': ['map', 'filter', 'transform', 'parse', 'convert'],
            'natural_language': ['change', 'transform', 'become', 'turn into'],
            'baby_sign': ['CHANGE gesture', 'DIFFERENT gesture'],
            'cognition': ['transformation', 'conversion', 'modification']
        }
    ),
    
    Dhatu(
        root="ACCUM",
        concept="Accumuler, rassembler, construire progressivement",
        patterns=[
            r'\baccumulate\b',
            r'\bcollect\b',
            r'\baggregate\b',
            r'\breduce\b',
            r'\bsum\b',
            r'\bbuild\b',
            r'\.reduce\(',
            r'\.collect\(',
            r'\bappend\b',
            r'\badd\b',
            r'\+=',
        ],
        manifestations={
            'programming': ['reduce', 'aggregate', 'collect', 'append', 'accumulate'],
            'natural_language': ['gather', 'collect', 'accumulate', 'build up'],
            'baby_sign': ['GATHER gesture', 'PILE UP gesture'],
            'cognition': ['accumulation', 'aggregation', 'synthesis']
        }
    ),
    
    Dhatu(
        root="DECIDE",
        concept="Choisir entre alternatives, prendre décision",
        patterns=[
            r'\bif\b',
            r'\belse\b',
            r'\bswitch\b',
            r'\bcase\b',
            r'\bmatch\b',
            r'\bchoose\b',
            r'\bselect\b',
            r'\bdecide\b',
            r'\?.*:',                     # Ternary operator
            r'\|\|',                      # Logical OR (choice)
            r'\&\&',                      # Logical AND (condition)
        ],
        manifestations={
            'programming': ['if/else', 'switch', 'pattern matching', 'conditionals'],
            'natural_language': ['if', 'choose', 'decide', 'either', 'or'],
            'baby_sign': ['CHOOSE gesture', 'WHICH gesture'],
            'cognition': ['decision', 'choice', 'selection', 'discrimination']
        }
    ),
    
    Dhatu(
        root="COMM",
        concept="Communiquer, échanger, transmettre",
        patterns=[
            r'\bprint\b',
            r'\bconsole\.log\b',
            r'\bsend\b',
            r'\breceive\b',
            r'\bemit\b',
            r'\bmessage\b',
            r'\bpost\b',
            r'\bget\b',
            r'\bput\b',
            r'\bapi\b',
            r'\bhttp\b',
            r'\bsocket\b',
        ],
        manifestations={
            'programming': ['print', 'log', 'API calls', 'messaging', 'I/O'],
            'natural_language': ['say', 'tell', 'communicate', 'send', 'receive'],
            'baby_sign': ['TALK gesture', 'GIVE gesture', 'SHOW gesture'],
            'cognition': ['communication', 'expression', 'transmission']
        }
    ),
    
    Dhatu(
        root="LOCATE",
        concept="Localiser, situer, retrouver, naviguer",
        patterns=[
            r'\bfind\b',
            r'\bsearch\b',
            r'\blocate\b',
            r'\bget\b',
            r'\bfetch\b',
            r'\bquery\b',
            r'\.find\(',
            r'\.search\(',
            r'\.indexOf\(',
            r'\bwhere\b',
            r'\bselect\b.*\bwhere\b',
        ],
        manifestations={
            'programming': ['find', 'search', 'query', 'get', 'locate'],
            'natural_language': ['where', 'find', 'search', 'locate', 'look for'],
            'baby_sign': ['WHERE gesture', 'FIND gesture'],
            'cognition': ['search', 'location', 'navigation', 'retrieval']
        }
    ),
    
    Dhatu(
        root="GROUP",
        concept="Grouper, rassembler par affinité, classer",
        patterns=[
            r'\bgroup\b',
            r'\bcluster\b',
            r'\bclass\b',
            r'\bcategory\b',
            r'\barray\b',
            r'\blist\b',
            r'\bset\b',
            r'\bcollection\b',
            r'\.groupBy\(',
            r'\bpartition\b',
        ],
        manifestations={
            'programming': ['arrays', 'lists', 'sets', 'classes', 'groupBy'],
            'natural_language': ['group', 'class', 'category', 'type', 'kind'],
            'baby_sign': ['SAME gesture', 'TOGETHER gesture'],
            'cognition': ['categorization', 'classification', 'grouping']
        }
    ),
    
    Dhatu(
        root="SEQ",
        concept="Séquencer, ordonner dans temps/espace",
        patterns=[
            r'\bsequence\b',
            r'\border\b',
            r'\bsort\b',
            r'\bfirst\b',
            r'\blast\b',
            r'\bnext\b',
            r'\bprevious\b',
            r'\.sort\(',
            r'\bstep\b',
            r'\bphase\b',
        ],
        manifestations={
            'programming': ['arrays', 'sequences', 'sorting', 'ordering'],
            'natural_language': ['first', 'then', 'next', 'sequence', 'order'],
            'baby_sign': ['FIRST gesture', 'NEXT gesture'],
            'cognition': ['sequencing', 'ordering', 'temporal organization']
        }
    ),
]

class DhatuDetector:
    """Détecteur de patterns dhātu dans différents types de contenu"""
    
    def __init__(self):
        self.dhatu_catalog = {d.root: d for d in DHATU_CATALOG}
        self.detection_results = defaultdict(list)
        
    def detect_in_text(self, text: str, content_type: str = "general") -> Dict[str, Any]:
        """Détecte les dhātu dans un texte"""
        results = {
            'detected_dhatus': [],
            'dhatu_composition': {},
            'universality_indicators': [],
            'content_type': content_type
        }
        
        text_lower = text.lower()
        
        for dhatu_name, dhatu in self.dhatu_catalog.items():
            matches = []
            
            # Test patterns avec regex
            for pattern in dhatu.patterns:
                pattern_matches = re.finditer(pattern, text, re.IGNORECASE)
                matches.extend([m.group() for m in pattern_matches])
            
            # Test manifestations pour le type de contenu
            if content_type in dhatu.manifestations:
                for manifestation in dhatu.manifestations[content_type]:
                    if manifestation.lower() in text_lower:
                        matches.append(manifestation)
            
            if matches:
                results['detected_dhatus'].append({
                    'dhatu': dhatu_name,
                    'concept': dhatu.concept,
                    'matches': list(set(matches)),  # Dédupliquer
                    'count': len(matches)
                })
                results['dhatu_composition'][dhatu_name] = len(matches)
        
        return results
    
    def detect_in_file(self, filepath: Path) -> Dict[str, Any]:
        """Détecte les dhātu dans un fichier"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Détermine le type de contenu selon l'extension
            content_type = self._determine_content_type(filepath)
            
            results = self.detect_in_text(content, content_type)
            results['filepath'] = str(filepath)
            results['file_extension'] = filepath.suffix
            
            return results
            
        except Exception as e:
            return {'error': str(e), 'filepath': str(filepath)}
    
    def _determine_content_type(self, filepath: Path) -> str:
        """Détermine le type de contenu selon l'extension"""
        ext = filepath.suffix.lower()
        
        programming_exts = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.rs', '.go'}
        text_exts = {'.txt', '.md', '.rst', '.doc'}
        
        if ext in programming_exts:
            return 'programming'
        elif ext in text_exts:
            return 'natural_language'
        else:
            return 'general'
    
    def analyze_corpus(self, directory: Path) -> Dict[str, Any]:
        """Analyse un corpus entier pour valider universalité des dhātu"""
        corpus_results = {
            'total_files': 0,
            'files_analyzed': 0,
            'dhatu_universality': {},
            'cross_language_patterns': {},
            'content_type_distribution': defaultdict(int),
            'detailed_results': []
        }
        
        # Analyse tous les fichiers
        for filepath in directory.rglob('*'):
            if filepath.is_file() and self._is_analyzable_file(filepath):
                corpus_results['total_files'] += 1
                
                file_results = self.detect_in_file(filepath)
                
                if 'error' not in file_results:
                    corpus_results['files_analyzed'] += 1
                    corpus_results['detailed_results'].append(file_results)
                    corpus_results['content_type_distribution'][file_results['content_type']] += 1
        
        # Calcule l'universalité des dhātu
        self._compute_universality_metrics(corpus_results)
        
        return corpus_results
    
    def _is_analyzable_file(self, filepath: Path) -> bool:
        """Vérifie si un fichier peut être analysé"""
        analyzable_exts = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.rs', '.go',
            '.txt', '.md', '.rst', '.html', '.css', '.json', '.yaml'
        }
        return filepath.suffix.lower() in analyzable_exts
    
    def _compute_universality_metrics(self, corpus_results: Dict[str, Any]):
        """Calcule les métriques d'universalité des dhātu"""
        dhatu_counts = defaultdict(int)
        content_type_counts = defaultdict(lambda: defaultdict(int))
        
        # Compte les occurrences par dhātu et type de contenu
        for result in corpus_results['detailed_results']:
            content_type = result['content_type']
            for dhatu_info in result['detected_dhatus']:
                dhatu_name = dhatu_info['dhatu']
                dhatu_counts[dhatu_name] += dhatu_info['count']
                content_type_counts[content_type][dhatu_name] += dhatu_info['count']
        
        # Calcule scores d'universalité
        total_files = corpus_results['files_analyzed']
        for dhatu_name in self.dhatu_catalog.keys():
            files_with_dhatu = sum(1 for result in corpus_results['detailed_results'] 
                                 if any(d['dhatu'] == dhatu_name for d in result['detected_dhatus']))
            
            universality_score = files_with_dhatu / total_files if total_files > 0 else 0
            
            corpus_results['dhatu_universality'][dhatu_name] = {
                'universality_score': universality_score,
                'total_occurrences': dhatu_counts[dhatu_name],
                'files_containing': files_with_dhatu,
                'content_type_distribution': dict(content_type_counts)
            }
    
    def generate_report(self, corpus_results: Dict[str, Any]) -> str:
        """Génère un rapport d'analyse des dhātu"""
        report = []
        report.append("# 🔬 RAPPORT D'ANALYSE DHĀTU")
        report.append(f"## 📊 Statistiques Générales")
        report.append(f"- **Fichiers analysés**: {corpus_results['files_analyzed']}/{corpus_results['total_files']}")
        report.append(f"- **Types de contenu**: {dict(corpus_results['content_type_distribution'])}")
        report.append("")
        
        report.append("## 🌟 Universalité des Dhātu")
        dhatu_by_universality = sorted(
            corpus_results['dhatu_universality'].items(),
            key=lambda x: x[1]['universality_score'],
            reverse=True
        )
        
        for dhatu_name, metrics in dhatu_by_universality:
            dhatu = self.dhatu_catalog[dhatu_name]
            score = metrics['universality_score']
            
            report.append(f"### **{dhatu_name}** - {dhatu.concept}")
            report.append(f"- **Score d'universalité**: {score:.2%}")
            report.append(f"- **Occurrences totales**: {metrics['total_occurrences']}")
            report.append(f"- **Fichiers contenant**: {metrics['files_containing']}")
            
            # Indicateur visuel
            if score > 0.7:
                report.append("- **Status**: ✅ UNIVERSEL (>70%)")
            elif score > 0.4:
                report.append("- **Status**: ⚠️ FRÉQUENT (40-70%)")
            else:
                report.append("- **Status**: ❌ RARE (<40%)")
            report.append("")
        
        report.append("## 🎯 Recommandations")
        universal_dhatus = [name for name, metrics in dhatu_by_universality 
                          if metrics['universality_score'] > 0.7]
        
        if universal_dhatus:
            report.append(f"**Dhātu Universels Validés**: {', '.join(universal_dhatus)}")
            report.append("→ Ces dhātu peuvent être considérés comme atomiques universels")
        else:
            report.append("**Aucun dhātu universel détecté** - Révision du catalogue nécessaire")
        
        return "\n".join(report)

def main():
    """Fonction principale pour test et démonstration"""
    detector = DhatuDetector()
    
    # Test sur quelques exemples
    test_codes = [
        ("for i in range(10): print(i)", "programming"),
        ("if condition: do_something() else: do_other()", "programming"),
        ("items.map(x => x.transform()).filter(x => x.valid)", "programming"),
        ("I want to find where the files are located", "natural_language"),
        ("First, we need to group all similar items together", "natural_language")
    ]
    
    print("🔬 Test de Détection des Dhātu\n")
    
    for text, content_type in test_codes:
        print(f"**Texte**: {text}")
        print(f"**Type**: {content_type}")
        
        results = detector.detect_in_text(text, content_type)
        
        if results['detected_dhatus']:
            print("**Dhātu détectés**:")
            for dhatu_info in results['detected_dhatus']:
                print(f"  - {dhatu_info['dhatu']}: {dhatu_info['matches']}")
        else:
            print("  - Aucun dhātu détecté")
        print()

if __name__ == "__main__":
    main()
