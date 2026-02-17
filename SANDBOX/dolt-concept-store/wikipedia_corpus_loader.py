#!/usr/bin/env python3
"""
Téléchargement et traitement de dumps Wikipedia multilingues
pour tester le Dolt Concept Store à grande échelle.

Ce script:
1. Télécharge des extraits Wikipedia (abstracts) dans plusieurs langues
2. Extrait les phrases
3. Les analyse avec des signatures dhātu (simulées pour l'instant)
4. Les insère dans Dolt pour déduplication sémantique

Usage:
    python3 wikipedia_corpus_loader.py [--languages fr,en,es] [--limit 1000]
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


# URLs des dumps Wikipedia (cirrussearch - includes extracts, plus disponible que abstracts)
# Format: cirrussearch content dumps contiennent les extracts textuels
WIKIPEDIA_ABSTRACT_URLS = {
    "en": "https://dumps.wikimedia.org/other/cirrussearch/current/enwiki-20250217-cirrussearch-content.json.gz",
    "fr": "https://dumps.wikimedia.org/other/cirrussearch/current/frwiki-20250217-cirrussearch-content.json.gz",
    "es": "https://dumps.wikimedia.org/other/cirrussearch/current/eswiki-20250217-cirrussearch-content.json.gz",
    "de": "https://dumps.wikimedia.org/other/cirrussearch/current/dewiki-20250217-cirrussearch-content.json.gz",
    "ar": "https://dumps.wikimedia.org/other/cirrussearch/current/arwiki-20250217-cirrussearch-content.json.gz",
    "zh": "https://dumps.wikimedia.org/other/cirrussearch/current/zhwiki-20250217-cirrussearch-content.json.gz",
    "ja": "https://dumps.wikimedia.org/other/cirrussearch/current/jawiki-20250217-cirrussearch-content.json.gz",
}

# Alternative: utiliser des samples Wikipedia pré-extraits
# Pour l'instant on va créer un corpus synthétique plus large basé sur notre test

CACHE_DIR = Path("./wikipedia_cache")


class WikipediaCorpusLoader:
    """Chargeur de corpus Wikipedia pour tests Dolt"""
    
    def __init__(self, db_path: str = "./dolt_concepts"):
        self.db_path = db_path
        self.stats = defaultdict(int)
        CACHE_DIR.mkdir(exist_ok=True)
    
    def download_wikipedia_abstracts(self, language: str) -> Path:
        """Télécharge les abstracts Wikipedia pour une langue"""
        if language not in WIKIPEDIA_ABSTRACT_URLS:
            raise ValueError(f"Langue non supportée: {language}")
        
        url = WIKIPEDIA_ABSTRACT_URLS[language]
        filename = CACHE_DIR / f"{language}wiki-abstracts.xml.gz"
        
        if filename.exists():
            print(f"  ✅ Cache existant: {filename}")
            return filename
        
        print(f"  📥 Téléchargement: {url}")
        print(f"     → {filename}")
        
        urllib.request.urlretrieve(url, filename)
        print(f"  ✅ Téléchargé: {filename.stat().st_size / 1024 / 1024:.1f} MB")
        
        return filename
    
    def extract_sentences(self, xml_file: Path, limit: int = 1000) -> List[str]:
        """Extrait les phrases du fichier XML Wikipedia"""
        import gzip
        
        print(f"  📖 Extraction des phrases (limit={limit})...")
        
        sentences = []
        with gzip.open(xml_file, 'rt', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # Parse XML
            try:
                # Le XML Wikipedia est dans un namespace
                root = ET.fromstring(f'<root xmlns:wiki="http://www.mediawiki.org/xml/export-0.10/">{content}</root>')
                
                # Extraire les abstracts
                for doc in root.findall('.//doc'):
                    abstract = doc.find('abstract')
                    if abstract is not None and abstract.text:
                        # Split en phrases (simple)
                        text = abstract.text.strip()
                        # Split par . ! ? mais pas dans les abréviations communes
                        text = re.sub(r'\s+', ' ', text)
                        phrases = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
                        
                        for phrase in phrases:
                            phrase = phrase.strip()
                            if 10 < len(phrase) < 200:  # Filtre longueur raisonnable
                                sentences.append(phrase)
                                if len(sentences) >= limit:
                                    return sentences
            except ET.ParseError:
                # Fallback: extraction brutale
                print("  ⚠️  XML invalide, extraction brute...")
                abstracts = re.findall(r'<abstract>(.*?)</abstract>', content, re.DOTALL)
                for abstract in abstracts[:limit]:
                    text = re.sub(r'<[^>]+>', '', abstract)  # Strip HTML
                    text = re.sub(r'\s+', ' ', text).strip()
                    if 10 < len(text) < 200:
                        sentences.append(text)
                        if len(sentences) >= limit:
                            break
        
        print(f"  ✅ {len(sentences)} phrases extraites")
        return sentences
    
    def simulate_dhatu_analysis(self, text: str) -> Dict[str, float]:
        """
        Simulation de l'analyse dhātu (en attendant le vrai analyzer Rust).
        
        Détecte des mots-clés pour estimer la signature dhātu.
        """
        text_lower = text.lower()
        
        dhatu = {
            "COMM": 0.0,
            "ITER": 0.0,
            "TRANS": 0.0,
            "DECIDE": 0.0,
            "LOCATE": 0.0,
            "GROUP": 0.0,
            "SEQ": 0.0,
        }
        
        # COMM (communication, speak, say, tell)
        comm_keywords = ['say', 'speak', 'tell', 'communicate', 'dit', 'parle', 'communique', 
                         'dice', 'habla', 'يقول', 'يتحدث', '说', '話す']
        dhatu["COMM"] = sum(0.15 for kw in comm_keywords if kw in text_lower)
        
        # ITER (iterate, repeat, each, every, loop)
        iter_keywords = ['each', 'every', 'all', 'repeat', 'loop', 'iterate', 
                         'chaque', 'tous', 'répète', 'cada', 'todos', 'repite',
                         'كل', '每个', '全て', '各']
        dhatu["ITER"] = sum(0.15 for kw in iter_keywords if kw in text_lower)
        
        # TRANS (transform, convert, change, become)
        trans_keywords = ['transform', 'convert', 'change', 'become', 'make',
                          'transformer', 'convertir', 'changer', 'transformar', 'cambiar',
                          'تحويل', 'يتغير', '转换', '变化', '変換']
        dhatu["TRANS"] = sum(0.15 for kw in trans_keywords if kw in text_lower)
        
        # DECIDE (decide, if, whether, choice, select)
        decide_keywords = ['if', 'decide', 'choice', 'select', 'whether', 'choose',
                           'si', 'décide', 'choix', 'sélectionne', 'إذا', 'يختار',
                           '如果', '选择', 'もし', '選択']
        dhatu["DECIDE"] = sum(0.15 for kw in decide_keywords if kw in text_lower)
        
        # LOCATE (where, location, place, position, at, in)
        locate_keywords = ['where', 'location', 'place', 'position', 'at', 'in', 'on',
                           'où', 'lieu', 'place', 'dans', 'sur', 'donde', 'lugar', 'en',
                           'أين', 'مكان', 'في', '在', '哪里', '場所', 'どこ']
        dhatu["LOCATE"] = sum(0.15 for kw in locate_keywords if kw in text_lower)
        
        # GROUP (group, collection, set, together, organize)
        group_keywords = ['group', 'collection', 'set', 'together', 'organize', 'gather',
                          'groupe', 'ensemble', 'collection', 'grupo', 'conjunto',
                          'مجموعة', 'ينظم', '组', '集合', 'グループ', 'セット']
        dhatu["GROUP"] = sum(0.15 for kw in group_keywords if kw in text_lower)
        
        # SEQ (sequence, order, first, next, then, after, before)
        seq_keywords = ['first', 'next', 'then', 'after', 'before', 'sequence', 'order',
                        'premier', 'ensuite', 'après', 'avant', 'primero', 'luego', 'después',
                        'أولا', 'ثم', 'بعد', '首先', '然后', '最初', '次', 'その後']
        dhatu["SEQ"] = sum(0.15 for kw in seq_keywords if kw in text_lower)
        
        # Normalisation
        total = sum(dhatu.values())
        if total > 0:
            dhatu = {k: round(v / total, 3) for k, v in dhatu.items()}
        else:
            # Pas de mots-clés détectés, distribution uniforme faible
            dhatu = {k: round(1.0 / 7, 3) for k in dhatu.keys()}
        
        return dhatu
    
    def compute_semantic_hash(self, dhatu_signature: Dict[str, float]) -> str:
        """Calcule le hash sémantique à partir de la signature dhātu"""
        # Quantification grossière pour regrouper les signatures similaires
        quantized = {
            k: round(v * 4) / 4  # Quantification par 0.25
            for k, v in dhatu_signature.items()
        }
        
        signature_str = json.dumps(quantized, sort_keys=True)
        return hashlib.sha256(signature_str.encode()).hexdigest()
    
    def insert_into_dolt(self, language: str, text: str, dhatu_sig: Dict[str, float]):
        """Insère un mapping dans Dolt"""
        content_hash = hashlib.sha256(text.encode()).hexdigest()
        semantic_hash = self.compute_semantic_hash(dhatu_sig)
        
        # Construction de la requête SQL
        dhatu_json = json.dumps(dhatu_sig)
        
        sql = f"""
        INSERT INTO semantic_mappings 
        (content_hash, source_text, language, dhatu_signature, semantic_hash)
        VALUES (
            '{content_hash}',
            {self._escape_sql_string(text)},
            '{language}',
            '{dhatu_json}',
            '{semantic_hash}'
        );
        """
        
        try:
            subprocess.run(
                ["dolt", "sql", "-q", sql],
                cwd=self.db_path,
                check=True,
                capture_output=True,
                text=True
            )
            self.stats[f"{language}_inserted"] += 1
        except subprocess.CalledProcessError as e:
            # Ignorer les doublons (content_hash unique)
            if "duplicate" not in e.stderr.lower():
                print(f"  ⚠️  Erreur insertion: {e.stderr[:100]}")
    
    def _escape_sql_string(self, s: str) -> str:
        """Échappe une chaîne pour SQL"""
        s = s.replace("'", "''")
        s = s.replace("\\", "\\\\")
        return f"'{s}'"
    
    def process_language(self, language: str, limit: int = 1000):
        """Traite une langue complète"""
        print(f"\n{'=' * 70}")
        print(f"🌍 Langue: {language.upper()}")
        print(f"{'=' * 70}")
        
        # 1. Téléchargement
        xml_file = self.download_wikipedia_abstracts(language)
        
        # 2. Extraction
        sentences = self.extract_sentences(xml_file, limit)
        
        # 3. Analyse et insertion
        print(f"  🔍 Analyse et insertion dans Dolt...")
        for i, text in enumerate(sentences, 1):
            dhatu_sig = self.simulate_dhatu_analysis(text)
            self.insert_into_dolt(language, text, dhatu_sig)
            
            if i % 100 == 0:
                print(f"     {i}/{len(sentences)} phrases traitées...")
        
        print(f"  ✅ {len(sentences)} phrases traitées pour {language}")
    
    def commit_changes(self, message: str):
        """Commit Dolt"""
        print(f"\n  💾 Commit Dolt: {message}")
        subprocess.run(
            ["dolt", "add", "."],
            cwd=self.db_path,
            check=True
        )
        subprocess.run(
            ["dolt", "commit", "-m", message],
            cwd=self.db_path,
            check=True
        )
    
    def show_deduplication_stats(self):
        """Affiche les statistiques de déduplication"""
        print(f"\n{'=' * 70}")
        print("📊 STATISTIQUES DE DÉDUPLICATION")
        print(f"{'=' * 70}")
        
        # Requête sur la vue semantic_deduplication
        result = subprocess.run(
            ["dolt", "sql", "-q", "SELECT * FROM semantic_deduplication LIMIT 20"],
            cwd=self.db_path,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        
        # Comptage total
        result = subprocess.run(
            ["dolt", "sql", "-q", 
             "SELECT COUNT(*) as total_mappings, COUNT(DISTINCT semantic_hash) as unique_concepts FROM semantic_mappings"],
            cwd=self.db_path,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)


def main():
    parser = argparse.ArgumentParser(description="Charge un corpus Wikipedia dans Dolt")
    parser.add_argument(
        "--languages",
        default="fr,en,es",
        help="Langues à traiter (séparées par virgules)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1000,
        help="Nombre max de phrases par langue"
    )
    parser.add_argument(
        "--db-path",
        default="./dolt_concepts",
        help="Chemin de la base Dolt"
    )
    
    args = parser.parse_args()
    
    languages = [lang.strip() for lang in args.languages.split(",")]
    
    print("=" * 80)
    print("🚀 CHARGEMENT CORPUS WIKIPEDIA → DOLT CONCEPT STORE")
    print("=" * 80)
    print(f"  Langues: {', '.join(languages)}")
    print(f"  Limite: {args.limit} phrases/langue")
    print(f"  Base: {args.db_path}")
    print()
    
    # Notification utilisateur
    notify_script = Path(__file__).parent / "notify_user.sh"
    if notify_script.exists():
        subprocess.run([str(notify_script), "Chargement Wikipedia démarré"], check=False)
    
    loader = WikipediaCorpusLoader(args.db_path)
    
    try:
        for language in languages:
            loader.process_language(language, args.limit)
            loader.commit_changes(f"Add {language} Wikipedia corpus")
        
        loader.show_deduplication_stats()
        
        print("\n" + "=" * 80)
        print("✅ CORPUS CHARGÉ AVEC SUCCÈS!")
        print("=" * 80)
        print(f"\n📊 Statistiques:")
        for key, value in sorted(loader.stats.items()):
            print(f"  • {key}: {value}")
        
        if notify_script.exists():
            subprocess.run([str(notify_script), "Corpus Wikipedia chargé avec succès!"], check=False)
    
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        if notify_script.exists():
            subprocess.run([str(notify_script), f"Erreur: {e}"], check=False)
        sys.exit(1)


if __name__ == "__main__":
    main()
