#!/usr/bin/env python3
"""
Validation Bit-Perfect pour Wikipedia dans Panini-FS
====================================================

Vérifie que les articles récupérés depuis Panini-FS sont identiques
byte-par-byte aux originaux Wikipedia.

Usage:
    python3 validate_bitperfect.py --dump frwiki.xml.bz2 --sample 100
"""

import bz2
import xml.etree.ElementTree as ET
import requests
import hashlib
import argparse
from pathlib import Path
from typing import Optional
import sys
import random

API_BASE_URL = "http://localhost:3000/api"


class BitPerfectValidator:
    """Valide l'intégrité bit-perfect des articles"""
    
    def __init__(self, api_url: str, dump_path: Path):
        self.api_url = api_url
        self.dump_path = dump_path
        self.stats = {
            "total_checked": 0,
            "perfect_matches": 0,
            "hash_matches": 0,
            "content_mismatches": 0,
            "not_found": 0,
        }
    
    def get_article_from_panini(self, path: str) -> Optional[bytes]:
        """Récupère un article depuis Panini-FS"""
        try:
            response = requests.get(
                f"{self.api_url}/dedup/search",
                params={"path": path},
                timeout=10,
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("found") and result.get("atoms"):
                    # Reconstruire le contenu depuis les atoms
                    # TODO: Implémenter la reconstruction complète
                    return result.get("content", "").encode("utf-8")
            
            return None
            
        except Exception as e:
            print(f"⚠️  Erreur récupération: {e}", file=sys.stderr)
            return None
    
    def compute_hash(self, content: bytes) -> str:
        """Calcule le hash SHA-256"""
        return hashlib.sha256(content).hexdigest()
    
    def validate_article(self, title: str, original_content: bytes, lang: str) -> bool:
        """Valide un article"""
        path = f"/wikipedia/{lang}/0/{title}.wiki"
        
        # Récupérer depuis Panini
        retrieved_content = self.get_article_from_panini(path)
        
        if retrieved_content is None:
            print(f"❌ {title}: NOT FOUND in Panini-FS")
            self.stats["not_found"] += 1
            return False
        
        # Comparer les hash
        original_hash = self.compute_hash(original_content)
        retrieved_hash = self.compute_hash(retrieved_content)
        
        if original_hash == retrieved_hash:
            print(f"✅ {title}: BIT-PERFECT MATCH (SHA-256: {original_hash[:16]}...)")
            self.stats["perfect_matches"] += 1
            self.stats["hash_matches"] += 1
            return True
        
        # Hash différent - vérifier le contenu
        if original_content == retrieved_content:
            print(f"✅ {title}: CONTENT MATCH (hash diff shouldn't happen!)")
            self.stats["perfect_matches"] += 1
            return True
        
        # Mismatch
        print(f"❌ {title}: CONTENT MISMATCH")
        print(f"   Original hash:  {original_hash}")
        print(f"   Retrieved hash: {retrieved_hash}")
        print(f"   Original size:  {len(original_content)} bytes")
        print(f"   Retrieved size: {len(retrieved_content)} bytes")
        self.stats["content_mismatches"] += 1
        return False
    
    def print_stats(self):
        """Affiche les statistiques finales"""
        print("\n" + "="*70)
        print("📊 RÉSULTATS DE VALIDATION BIT-PERFECT")
        print("="*70)
        print(f"   Articles vérifiés: {self.stats['total_checked']}")
        print(f"   ✅ Correspondances parfaites: {self.stats['perfect_matches']}")
        print(f"   🔐 Hash SHA-256 identiques: {self.stats['hash_matches']}")
        print(f"   ❌ Différences de contenu: {self.stats['content_mismatches']}")
        print(f"   ❓ Articles introuvables: {self.stats['not_found']}")
        
        if self.stats['total_checked'] > 0:
            success_rate = (self.stats['perfect_matches'] / self.stats['total_checked']) * 100
            print(f"\n   🎯 Taux de réussite: {success_rate:.2f}%")
            
            if success_rate == 100:
                print("\n   🎉 VALIDATION BIT-PERFECT RÉUSSIE! 🎉")
            elif success_rate >= 95:
                print("\n   ⚠️  Validation quasi-parfaite (quelques erreurs)")
            else:
                print("\n   ❌ Validation échouée (trop d'erreurs)")


def parse_sample_articles(dump_path: Path, sample_size: int, random_sample: bool = True):
    """Parse un échantillon d'articles du dump"""
    namespace = "{http://www.mediawiki.org/xml/export-0.10/}"
    articles = []
    
    # Ouvrir le dump
    if dump_path.suffix == ".bz2":
        file_obj = bz2.open(dump_path, "rt", encoding="utf-8")
    else:
        file_obj = open(dump_path, "r", encoding="utf-8")
    
    try:
        context = ET.iterparse(file_obj, events=("start", "end"))
        context = iter(context)
        _, root = next(context)
        
        current_page = {}
        current_revision = {}
        
        for event, elem in context:
            tag = elem.tag.replace(namespace, "")
            
            if event == "end":
                if tag == "title":
                    current_page["title"] = elem.text or ""
                elif tag == "ns":
                    current_page["namespace"] = int(elem.text or "0")
                elif tag == "text":
                    current_revision["text"] = elem.text or ""
                elif tag == "page":
                    if (current_page.get("namespace") == 0 and 
                        current_revision.get("text")):
                        
                        articles.append({
                            "title": current_page["title"],
                            "content": current_revision["text"].encode("utf-8"),
                        })
                        
                        if len(articles) >= sample_size * 2:  # Buffer pour random sample
                            break
                    
                    current_page = {}
                    current_revision = {}
                    elem.clear()
                    root.clear()
    
    finally:
        file_obj.close()
    
    # Échantillonnage aléatoire ou séquentiel
    if random_sample and len(articles) > sample_size:
        return random.sample(articles, sample_size)
    else:
        return articles[:sample_size]


def main():
    parser = argparse.ArgumentParser(description="Validation bit-perfect Wikipedia")
    parser.add_argument("--dump", type=Path, required=True, help="Dump Wikipedia")
    parser.add_argument("--sample", type=int, default=10, help="Nombre d'articles à vérifier")
    parser.add_argument("--lang", type=str, help="Code langue")
    parser.add_argument("--api", type=str, default=API_BASE_URL, help="URL API")
    parser.add_argument("--sequential", action="store_true", help="Échantillon séquentiel (pas aléatoire)")
    
    args = parser.parse_args()
    
    if not args.dump.exists():
        print(f"❌ Dump introuvable: {args.dump}", file=sys.stderr)
        sys.exit(1)
    
    lang = args.lang or args.dump.stem.split("wiki")[0]
    
    print(f"🔍 Validation Bit-Perfect Wikipedia ({lang})")
    print(f"   Dump: {args.dump}")
    print(f"   Échantillon: {args.sample} articles")
    print(f"   Mode: {'séquentiel' if args.sequential else 'aléatoire'}")
    print(f"   API: {args.api}")
    print()
    
    # Parser échantillon
    print("📖 Extraction des articles du dump...")
    articles = parse_sample_articles(args.dump, args.sample, not args.sequential)
    print(f"   {len(articles)} articles extraits\n")
    
    # Valider
    validator = BitPerfectValidator(args.api, args.dump)
    
    for article in articles:
        validator.stats["total_checked"] += 1
        validator.validate_article(article["title"], article["content"], lang)
    
    # Stats finales
    validator.print_stats()


if __name__ == "__main__":
    main()
