#!/usr/bin/env python3
"""
Analyseur du Modèle Panini Wikipedia Complet
============================================

Analyse approfondie du corpus Wikipedia multilingue ingéré:
- Déduplication inter-langues
- Profils émotionnels culturels
- Concepts universels
- Graphe de connaissances

Usage:
    python3 analyze_panini_model.py --storage /mnt/data/panini-wikipedia-full
"""

import argparse
import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple
import requests

API_URL = "http://localhost:3000/api"


class PaniniModelAnalyzer:
    """Analyse le modèle Panini complet"""
    
    def __init__(self, storage_path: Path, api_url: str):
        self.storage_path = storage_path
        self.api_url = api_url
        self.reports_dir = storage_path.parent / "panini-wikipedia-full" / "reports" / "wikipedia_full"
        
    def load_language_reports(self) -> Dict[str, dict]:
        """Charge tous les rapports par langue"""
        reports = {}
        
        if not self.reports_dir.exists():
            print(f"⚠️  Répertoire de rapports introuvable: {self.reports_dir}")
            return reports
        
        for report_file in self.reports_dir.glob("*_report.json"):
            lang = report_file.stem.replace("_report", "")
            try:
                with open(report_file) as f:
                    reports[lang] = json.load(f)
            except Exception as e:
                print(f"⚠️  Erreur lecture {lang}: {e}")
        
        return reports
    
    def get_api_stats(self) -> Tuple[dict, dict]:
        """Récupère les stats depuis l'API"""
        try:
            dedup = requests.get(f"{self.api_url}/dedup/stats", timeout=10).json()
            dhatu = requests.get(f"{self.api_url}/dhatu/stats", timeout=10).json()
            return dedup, dhatu
        except Exception as e:
            print(f"⚠️  Erreur API: {e}")
            return {}, {}
    
    def analyze_global_deduplication(self, reports: Dict[str, dict], dedup_stats: dict):
        """Analyse la déduplication globale"""
        print("\n" + "="*70)
        print("📊 ANALYSE DE LA DÉDUPLICATION GLOBALE")
        print("="*70)
        
        total_files = dedup_stats.get("total_files", 0)
        total_atoms = dedup_stats.get("total_atoms", 0)
        unique_atoms = dedup_stats.get("unique_atoms", 0)
        total_size = dedup_stats.get("total_size", 0)
        dedup_ratio = dedup_stats.get("dedup_ratio", 0)
        storage_saved = dedup_stats.get("storage_saved", 0)
        
        print(f"\n📁 Fichiers/Articles:")
        print(f"   Total: {total_files:,}")
        print(f"\n🧩 Atoms:")
        print(f"   Total créés: {total_atoms:,}")
        print(f"   Uniques: {unique_atoms:,}")
        print(f"   Réutilisés: {total_atoms - unique_atoms:,}")
        print(f"   Ratio de réutilisation: {total_atoms / unique_atoms if unique_atoms > 0 else 0:.2f}x")
        print(f"\n💾 Stockage:")
        print(f"   Taille brute: {total_size / (1024**3):.2f} GB")
        print(f"   Économie: {storage_saved / (1024**3):.2f} GB ({dedup_ratio * 100:.1f}%)")
        
        # Top atoms réutilisés
        top_atoms = dedup_stats.get("top_atoms", [])
        if top_atoms:
            print(f"\n🔝 Top 10 Atoms les Plus Réutilisés:")
            for i, atom in enumerate(top_atoms[:10], 1):
                hash_short = atom["hash"][:16]
                usage = atom["usage_count"]
                size = atom["size"]
                print(f"   {i}. {hash_short}... → {usage}x ({size} bytes)")
    
    def analyze_cultural_emotions(self, reports: Dict[str, dict], dhatu_stats: dict):
        """Analyse les profils émotionnels par culture"""
        print("\n" + "="*70)
        print("🧠 ANALYSE DES PROFILS ÉMOTIONNELS CULTURELS")
        print("="*70)
        
        total_profiles = dhatu_stats.get("total_profiles", 0)
        emotion_dist = dhatu_stats.get("emotion_distribution", {})
        avg_arousal = dhatu_stats.get("average_arousal", 0)
        top_emotions = dhatu_stats.get("top_emotions", [])
        
        print(f"\n📊 Statistiques Globales:")
        print(f"   Profils classifiés: {total_profiles:,}")
        print(f"   Arousal moyen: {avg_arousal:.4f}")
        
        print(f"\n🎭 Distribution Émotionnelle Globale:")
        
        emotion_symbols = {
            "Seeking": "🟡",
            "Fear": "🟣",
            "Rage": "🔴",
            "Lust": "🌸",
            "Care": "🟢",
            "Panic": "🔵",
            "Play": "🟠",
        }
        
        total_emotions = sum(emotion_dist.values())
        for emotion, count in sorted(emotion_dist.items(), key=lambda x: x[1], reverse=True):
            symbol = emotion_symbols.get(emotion, "⚪")
            pct = (count / total_emotions * 100) if total_emotions > 0 else 0
            bar = "█" * int(pct / 2)
            print(f"   {symbol} {emotion:12} {count:6,} ({pct:5.1f}%) {bar}")
        
        # TODO: Analyser par langue (nécessite API étendue)
        print(f"\n🌍 Analyse Par Langue:")
        print("   (Nécessite API étendue pour statistiques Dhātu par langue)")
        print("   À implémenter: Comparer profiles émotionnels fr vs en vs de vs sa vs hi")
    
    def analyze_interlanguage_concepts(self, reports: Dict[str, dict]):
        """Identifie les concepts universels présents dans plusieurs langues"""
        print("\n" + "="*70)
        print("🌐 CONCEPTS UNIVERSELS INTER-LANGUES")
        print("="*70)
        
        print("\n🔍 Recherche de concepts communs...")
        print("   (Analyse basée sur les titres d'articles similaires)")
        
        # Concepts candidats (noms propres, termes techniques universels)
        universal_concepts = [
            "Wikipedia", "Pāṇini", "Sanskrit", "India", "France", 
            "Mathematics", "Physics", "Earth", "Moon", "Sun",
            "Computer", "Internet", "Science", "Philosophy",
        ]
        
        print(f"\n📋 Concepts Universels Candidats (présence par langue):")
        
        for concept in universal_concepts:
            langs_present = []
            # TODO: Requête API pour chercher ce concept dans chaque langue
            print(f"   • {concept}: (analyse à implémenter)")
        
        print(f"\n💡 Recommandation:")
        print("   Implémenter endpoint API: GET /api/concepts/search?title=X&langs=all")
        print("   Pour identifier automatiquement les articles présents dans N+ langues")
    
    def analyze_atom_sharing(self, dedup_stats: dict):
        """Analyse le partage d'atoms entre langues"""
        print("\n" + "="*70)
        print("🔗 ANALYSE DU PARTAGE D'ATOMS INTER-LANGUES")
        print("="*70)
        
        top_atoms = dedup_stats.get("top_atoms", [])
        
        print(f"\n🧩 Atoms Partagés (usage > 1):")
        print(f"   Total atoms avec réutilisation: {len([a for a in top_atoms if a['usage_count'] > 1])}")
        
        # Analyser les tailles d'atoms les plus réutilisés
        if top_atoms:
            shared_atoms = [a for a in top_atoms if a["usage_count"] > 1]
            
            size_distribution = Counter()
            for atom in shared_atoms:
                size_bucket = (atom["size"] // 100) * 100
                size_distribution[size_bucket] += 1
            
            print(f"\n📏 Distribution de Taille (atoms partagés):")
            for size, count in sorted(size_distribution.items()):
                print(f"   {size}-{size+99} bytes: {count} atoms")
            
            print(f"\n💡 Interprétation:")
            print("   Petits atoms (<100B): Probablement structures répétitives, dates, nombres")
            print("   Moyens atoms (100-1KB): Phrases communes, paragraphes standards")
            print("   Grands atoms (>1KB): Sections entières copiées entre langues")
    
    def generate_knowledge_graph(self, reports: Dict[str, dict]):
        """Génère un graphe de connaissances (structure de base)"""
        print("\n" + "="*70)
        print("🕸️  GRAPHE DE CONNAISSANCES MULTILINGUE")
        print("="*70)
        
        print(f"\n📐 Structure du Graphe:")
        print(f"   Nœuds: Articles Wikipedia (un par langue)")
        print(f"   Arêtes: Liens inter-langues, atoms partagés, concepts communs")
        
        total_articles = sum(r.get("total_articles", 0) for r in reports.values())
        total_langs = len(reports)
        
        print(f"\n📊 Dimensions:")
        print(f"   Langues: {total_langs}")
        print(f"   Articles: {total_articles:,}")
        print(f"   Nœuds estimés: {total_articles:,}")
        print(f"   Arêtes potentielles: (à calculer)")
        
        print(f"\n💾 Export:")
        print(f"   Format GraphML: (à implémenter)")
        print(f"   Format Neo4j: (à implémenter)")
        print(f"   Format RDF: (à implémenter)")
        
        print(f"\n🔬 Analyses Possibles:")
        print("   • Centralité: Identifier les concepts les plus connectés")
        print("   • Communautés: Détecter les clusters thématiques")
        print("   • Chemins: Trouver les routes conceptuelles entre langues")
        print("   • PageRank: Calculer l'importance relative des concepts")
    
    def analyze(self):
        """Analyse complète du modèle"""
        print(f"\n🕉️  ANALYSE DU MODÈLE PANINI WIKIPEDIA COMPLET")
        print(f"   Storage: {self.storage_path}")
        print(f"   API: {self.api_url}")
        
        # Charger les rapports
        print(f"\n📖 Chargement des rapports par langue...")
        reports = self.load_language_reports()
        print(f"   {len(reports)} rapports chargés")
        
        # Stats API
        print(f"\n📡 Récupération des statistiques API...")
        dedup_stats, dhatu_stats = self.get_api_stats()
        
        # Analyses
        self.analyze_global_deduplication(reports, dedup_stats)
        self.analyze_cultural_emotions(reports, dhatu_stats)
        self.analyze_interlanguage_concepts(reports)
        self.analyze_atom_sharing(dedup_stats)
        self.generate_knowledge_graph(reports)
        
        print("\n" + "="*70)
        print("✅ ANALYSE TERMINÉE")
        print("="*70)
        
        print(f"\n📝 Prochaines Étapes:")
        print("   1. Exporter le graphe de connaissances (GraphML, Neo4j)")
        print("   2. Visualiser les profils émotionnels (dashboard interactif)")
        print("   3. Analyser l'évolution temporelle (timestamps Wikipedia)")
        print("   4. Identifier les concepts émergents (nouveaux articles)")
        print("   5. Comparer avec d'autres corpus (arXiv, PubMed, etc.)")


def main():
    parser = argparse.ArgumentParser(description="Analyse du modèle Panini Wikipedia")
    parser.add_argument("--storage", type=Path, required=True, help="Chemin du storage Panini")
    parser.add_argument("--api", type=str, default=API_URL, help="URL de l'API Panini")
    parser.add_argument("--export-graph", type=Path, help="Export du graphe (GraphML)")
    
    args = parser.parse_args()
    
    if not args.storage.exists():
        print(f"❌ Storage introuvable: {args.storage}", file=sys.stderr)
        sys.exit(1)
    
    analyzer = PaniniModelAnalyzer(args.storage, args.api)
    analyzer.analyze()
    
    if args.export_graph:
        print(f"\n📊 Export du graphe vers {args.export_graph}...")
        print("   (À implémenter)")


if __name__ == "__main__":
    main()
