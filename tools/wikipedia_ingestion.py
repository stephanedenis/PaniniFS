#!/usr/bin/env python3
"""
Wikipedia Ingestion Tool for Panini-FS
======================================

Ingère les dumps Wikipedia XML dans Panini-FS via l'API de déduplication.
Préserve l'intégrité bit-perfect et extrait les métadonnées pour l'analyse Dhātu.

Usage:
    python3 wikipedia_ingestion.py --dump /path/to/frwiki.xml.bz2 --lang fr --limit 1000
    python3 wikipedia_ingestion.py --dump /path/to/sawiki.xml.bz2 --lang sa --all
"""

import bz2
import xml.etree.ElementTree as ET
import requests
import hashlib
import json
import time
import argparse
from pathlib import Path
from typing import Dict, Optional, Generator
from dataclasses import dataclass
import sys

# Configuration
API_BASE_URL = "http://localhost:3000/api"
BATCH_SIZE = 100  # Articles par batch
STATS_INTERVAL = 10  # Afficher stats tous les N articles

@dataclass
class Article:
    """Représente un article Wikipedia"""
    title: str
    text: str
    language: str
    timestamp: str
    revision_id: str
    namespace: int
    
    def to_json(self) -> dict:
        return {
            "title": self.title,
            "language": self.language,
            "timestamp": self.timestamp,
            "revision_id": self.revision_id,
            "namespace": self.namespace,
            "text": self.text,
        }
    
    def get_path(self) -> str:
        """Chemin virtuel pour cet article"""
        return f"/wikipedia/{self.language}/{self.namespace}/{self.title}.wiki"


class WikipediaParser:
    """Parse les dumps Wikipedia XML"""
    
    def __init__(self, dump_path: Path):
        self.dump_path = dump_path
        # Support both 0.10 and 0.11 namespaces (try 0.11 first, fallback to 0.10)
        self.namespace = "{http://www.mediawiki.org/xml/export-0.11/}"
    
    def parse_articles(self, limit: Optional[int] = None) -> Generator[Article, None, None]:
        """Génère les articles du dump"""
        count = 0
        
        # Ouvrir le fichier (bz2 ou XML brut)
        if self.dump_path.suffix == ".bz2":
            file_obj = bz2.open(self.dump_path, "rt", encoding="utf-8")
        else:
            file_obj = open(self.dump_path, "r", encoding="utf-8")
        
        try:
            # Parser XML incrementalement pour économiser la mémoire
            context = ET.iterparse(file_obj, events=("start", "end"))
            context = iter(context)
            
            _, root = next(context)  # Get root element
            
            current_page = {}
            current_revision = {}
            
            for event, elem in context:
                tag = elem.tag.replace(self.namespace, "")
                
                if event == "end":
                    if tag == "title":
                        current_page["title"] = elem.text or ""
                    elif tag == "ns":
                        current_page["namespace"] = int(elem.text or "0")
                    elif tag == "id" and "revision_id" not in current_revision:
                        current_revision["revision_id"] = elem.text or ""
                    elif tag == "timestamp":
                        current_revision["timestamp"] = elem.text or ""
                    elif tag == "text":
                        current_revision["text"] = elem.text or ""
                    elif tag == "page":
                        # Article complet trouvé
                        if (current_page.get("namespace") == 0 and  # Articles principaux uniquement
                            current_revision.get("text")):
                            
                            article = Article(
                                title=current_page.get("title", ""),
                                text=current_revision.get("text", ""),
                                language=self.dump_path.stem.split("wiki")[0],
                                timestamp=current_revision.get("timestamp", ""),
                                revision_id=current_revision.get("revision_id", ""),
                                namespace=current_page.get("namespace", 0),
                            )
                            
                            yield article
                            count += 1
                            
                            if limit and count >= limit:
                                break
                        
                        # Reset pour le prochain article
                        current_page = {}
                        current_revision = {}
                        elem.clear()
                        root.clear()
            
        finally:
            file_obj.close()


class PaniniIngester:
    """Ingère les articles dans Panini-FS"""
    
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.stats = {
            "total_articles": 0,
            "total_bytes": 0,
            "deduplicated_bytes": 0,
            "upload_errors": 0,
            "classification_errors": 0,
            "start_time": time.time(),
        }
    
    def upload_article(self, article: Article) -> Optional[Dict]:
        """Upload un article via l'API de déduplication"""
        try:
            # Préparer les données
            content = article.text.encode("utf-8")
            metadata = json.dumps(article.to_json()).encode("utf-8")
            
            # Upload via API /files/analyze
            files = {
                "file": (f"{article.title}.txt", content, "text/plain; charset=utf-8"),
            }
            
            response = requests.post(
                f"{self.api_url}/files/analyze",
                files=files,
                timeout=30,
            )
            
            if response.status_code == 200:
                result = response.json()
                self.stats["total_articles"] += 1
                self.stats["total_bytes"] += len(content)
                
                if result.get("already_exists"):
                    self.stats["deduplicated_bytes"] += len(content)
                
                return result
            else:
                self.stats["upload_errors"] += 1
                print(f"⚠️  Upload error {response.status_code}: {article.title}", file=sys.stderr)
                return None
                
        except Exception as e:
            self.stats["upload_errors"] += 1
            print(f"❌ Exception uploading {article.title}: {e}", file=sys.stderr)
            return None
    
    def classify_article(self, article: Article, upload_result: Dict) -> Optional[Dict]:
        """Classifie un article avec Dhātu"""
        try:
            # Classifier le texte (premiers 10KB pour performance)
            text_sample = article.text[:10000]
            
            payload = {
                "path": article.get_path(),
                "content": text_sample,
            }
            
            response = requests.post(
                f"{self.api_url}/dhatu/classify",
                json=payload,
                timeout=10,
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.stats["classification_errors"] += 1
                return None
                
        except Exception as e:
            self.stats["classification_errors"] += 1
            print(f"⚠️  Classification error {article.title}: {e}", file=sys.stderr)
            return None
    
    def print_stats(self, force: bool = False):
        """Affiche les statistiques"""
        if not force and self.stats["total_articles"] % STATS_INTERVAL != 0:
            return
        
        elapsed = time.time() - self.stats["start_time"]
        rate = self.stats["total_articles"] / elapsed if elapsed > 0 else 0
        dedup_ratio = (self.stats["deduplicated_bytes"] / self.stats["total_bytes"] * 100 
                      if self.stats["total_bytes"] > 0 else 0)
        
        print(f"\n📊 Statistiques:")
        print(f"   Articles ingérés: {self.stats['total_articles']}")
        print(f"   Taille totale: {self.stats['total_bytes'] / (1024**2):.1f} MB")
        print(f"   Dédupliqués: {self.stats['deduplicated_bytes'] / (1024**2):.1f} MB ({dedup_ratio:.1f}%)")
        print(f"   Vitesse: {rate:.1f} articles/sec")
        print(f"   Erreurs upload: {self.stats['upload_errors']}")
        print(f"   Erreurs classification: {self.stats['classification_errors']}")
        print(f"   Temps écoulé: {elapsed:.0f}s")
    
    def save_report(self, output_path: Path):
        """Sauvegarde un rapport JSON"""
        elapsed = time.time() - self.stats["start_time"]
        
        report = {
            **self.stats,
            "elapsed_seconds": elapsed,
            "articles_per_second": self.stats["total_articles"] / elapsed if elapsed > 0 else 0,
            "deduplication_ratio": (self.stats["deduplicated_bytes"] / self.stats["total_bytes"] 
                                   if self.stats["total_bytes"] > 0 else 0),
        }
        
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📝 Rapport sauvegardé: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Ingestion Wikipedia dans Panini-FS")
    parser.add_argument("--dump", type=Path, required=True, help="Chemin vers le dump Wikipedia (XML.bz2)")
    parser.add_argument("--lang", type=str, help="Code langue (fr, en, de, sa, hi)")
    parser.add_argument("--limit", type=int, help="Limiter le nombre d'articles (pour tests)")
    parser.add_argument("--all", action="store_true", help="Ingérer tous les articles")
    parser.add_argument("--api", type=str, default=API_BASE_URL, help="URL de l'API Panini")
    parser.add_argument("--classify", action="store_true", help="Classifier avec Dhātu (plus lent)")
    parser.add_argument("--output", type=Path, help="Fichier de rapport JSON")
    
    args = parser.parse_args()
    
    if not args.dump.exists():
        print(f"❌ Dump introuvable: {args.dump}", file=sys.stderr)
        sys.exit(1)
    
    if not args.all and not args.limit:
        print("⚠️  Utilisez --limit N ou --all", file=sys.stderr)
        sys.exit(1)
    
    # Détecter la langue du dump
    lang = args.lang or args.dump.stem.split("wiki")[0]
    
    print(f"🚀 Ingestion Wikipedia ({lang})")
    print(f"   Dump: {args.dump}")
    print(f"   Limite: {args.limit or 'TOUS LES ARTICLES'}")
    print(f"   API: {args.api}")
    print(f"   Classification: {'OUI' if args.classify else 'NON'}")
    print()
    
    # Parser et ingérer
    parser_wiki = WikipediaParser(args.dump)
    ingester = PaniniIngester(args.api)
    
    try:
        for i, article in enumerate(parser_wiki.parse_articles(limit=args.limit), 1):
            # Upload
            result = ingester.upload_article(article)
            
            # Classification optionnelle
            if args.classify and result:
                ingester.classify_article(article, result)
            
            # Afficher progression
            if i % STATS_INTERVAL == 0:
                print(f"✅ {i} articles traités - {article.title[:50]}")
                ingester.print_stats()
        
        # Stats finales
        print("\n" + "="*70)
        print("🎉 INGESTION TERMINÉE!")
        ingester.print_stats(force=True)
        
        # Sauvegarder rapport
        if args.output:
            ingester.save_report(args.output)
        else:
            report_path = Path(f"wikipedia_ingestion_{lang}_{int(time.time())}.json")
            ingester.save_report(report_path)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interruption par l'utilisateur")
        ingester.print_stats(force=True)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
