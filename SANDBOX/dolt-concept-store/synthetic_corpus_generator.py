#!/usr/bin/env python3
"""
Générateur de corpus synthétique multilingue basé sur des templates.

Au lieu de télécharger Wikipedia (dumps très lourds et URLs changeantes),
ce script génère un corpus synthétique de phrases avec variations
pour tester la déduplication sémantique.

Usage:
    python3 synthetic_corpus_generator.py [--count 1000] [--languages fr,en,es]
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List
from collections import defaultdict


# Templates de phrases par concept avec variations
CONCEPT_TEMPLATES = {
    "greeting": {
        "dhatu": {"COMM": 0.9, "ITER": 0.0, "TRANS": 0.1, "DECIDE": 0.0, "LOCATE": 0.0, "GROUP": 0.0, "SEQ": 0.0},
        "variations": {
            "fr": [
                "Bonjour {name}",
                "Salut {name}",
                "Bienvenue {name}",
                "Enchanté {name}",
                "Ravi de vous rencontrer {name}",
            ],
            "en": [
                "Hello {name}",
                "Hi {name}",
                "Welcome {name}",
                "Nice to meet you {name}",
                "Greetings {name}",
            ],
            "es": [
                "Hola {name}",
                "Bienvenido {name}",
                "Saludos {name}",
                "Encantado de conocerte {name}",
                "Mucho gusto {name}",
            ],
        }
    },
    "iterate_collection": {
        "dhatu": {"COMM": 0.1, "ITER": 0.7, "TRANS": 0.1, "DECIDE": 0.05, "LOCATE": 0.0, "GROUP": 0.05, "SEQ": 0.0},
        "variations": {
            "fr": [
                "Parcourir tous les {items}",
                "Itérer sur chaque {item}",
                "Traiter chaque {item} de la collection",
                "Pour chaque {item} dans {items}",
                "Boucler sur les {items}",
            ],
            "en": [
                "Iterate over all {items}",
                "Loop through each {item}",
                "Process every {item} in the collection",
                "For each {item} in {items}",
                "Traverse all {items}",
            ],
            "es": [
                "Iterar sobre todos los {items}",
                "Recorrer cada {item}",
                "Procesar cada {item} de la colección",
                "Para cada {item} en {items}",
                "Bucle sobre los {items}",
            ],
        }
    },
    "transform_data": {
        "dhatu": {"COMM": 0.1, "ITER": 0.05, "TRANS": 0.7, "DECIDE": 0.05, "LOCATE": 0.0, "GROUP": 0.1, "SEQ": 0.0},
        "variations": {
            "fr": [
                "Convertir {source} en {target}",
                "Transformer {source} vers {target}",
                "Changer {source} en {target}",
                "Adapter {source} au format {target}",
                "Mapper {source} en {target}",
            ],
            "en": [
                "Convert {source} to {target}",
                "Transform {source} into {target}",
                "Change {source} to {target}",
                "Map {source} to {target}",
                "Adapt {source} to {target} format",
            ],
            "es": [
                "Convertir {source} a {target}",
                "Transformar {source} en {target}",
                "Cambiar {source} a {target}",
                "Mapear {source} a {target}",
                "Adaptar {source} al formato {target}",
            ],
        }
    },
    "conditional_check": {
        "dhatu": {"COMM": 0.05, "ITER": 0.0, "TRANS": 0.1, "DECIDE": 0.7, "LOCATE": 0.05, "GROUP": 0.05, "SEQ": 0.05},
        "variations": {
            "fr": [
                "Si {condition} alors {action}",
                "Vérifier si {condition}",
                "Quand {condition}, faire {action}",
                "En cas de {condition}",
                "Lorsque {condition} est vrai",
            ],
            "en": [
                "If {condition} then {action}",
                "Check if {condition}",
                "When {condition}, do {action}",
                "In case of {condition}",
                "Whenever {condition} is true",
            ],
            "es": [
                "Si {condition} entonces {action}",
                "Verificar si {condition}",
                "Cuando {condition}, hacer {action}",
                "En caso de {condition}",
                "Siempre que {condition} sea verdadero",
            ],
        }
    },
    "locate_position": {
        "dhatu": {"COMM": 0.1, "ITER": 0.0, "TRANS": 0.0, "DECIDE": 0.0, "LOCATE": 0.7, "GROUP": 0.1, "SEQ": 0.1},
        "variations": {
            "fr": [
                "Le {object} se trouve dans {location}",
                "Localiser {object} à {location}",
                "{object} est situé dans {location}",
                "Trouver {object} dans {location}",
                "Position de {object}: {location}",
            ],
            "en": [
                "The {object} is in {location}",
                "Locate {object} at {location}",
                "{object} is located in {location}",
                "Find {object} in {location}",
                "Position of {object}: {location}",
            ],
            "es": [
                "El {object} está en {location}",
                "Localizar {object} en {location}",
                "{object} está ubicado en {location}",
                "Encontrar {object} en {location}",
                "Posición de {object}: {location}",
            ],
        }
    },
}

# Valeurs pour remplir les templates
SUBSTITUTIONS = {
    "name": ["monde", "world", "mundo", "utilisateur", "user", "usuario"],
    "items": ["éléments", "items", "elementos", "fichiers", "files", "archivos"],
    "item": ["élément", "item", "elemento", "fichier", "file", "archivo"],
    "source": ["données", "data", "datos", "XML", "JSON", "CSV"],
    "target": ["JSON", "XML", "texte", "text", "formato"],
    "condition": ["valeur > 10", "value > 10", "valor > 10", "erreur", "error", "liste vide", "empty list"],
    "action": ["continuer", "continue", "continuar", "arrêter", "stop", "parar"],
    "object": ["fichier", "file", "archivo", "document", "image"],
    "location": ["serveur", "server", "servidor", "dossier", "folder", "base de données", "database"],
}


class SyntheticCorpusGenerator:
    """Générateur de corpus synthétique"""
    
    def __init__(self, db_path: str = "./panini-concepts-db"):
        self.db_path = db_path
        self.stats = defaultdict(int)
    
    def generate_phrases(self, languages: List[str], count: int) -> Dict[str, List[Dict]]:
        """Génère des phrases pour chaque langue"""
        corpus = defaultdict(list)
        
        phrases_per_concept = count // len(CONCEPT_TEMPLATES)
        
        for concept_name, concept_data in CONCEPT_TEMPLATES.items():
            dhatu = concept_data["dhatu"]
            
            generated = 0
            while generated < phrases_per_concept:
                for lang in languages:
                    if lang not in concept_data["variations"]:
                        continue
                    
                    for template in concept_data["variations"][lang]:
                        # Identifier les placeholders
                        placeholders = [key for key in SUBSTITUTIONS.keys() if f"{{{key}}}" in template]
                        
                        if not placeholders:
                            # Pas de placeholder, utiliser tel quel
                            text = template
                        else:
                            # Substituer chaque placeholder
                            text = template
                            for placeholder in placeholders:
                                # Choisir une valeur au hasard mais déterministement
                                idx = (generated + hash(lang + placeholder)) % len(SUBSTITUTIONS[placeholder])
                                value = SUBSTITUTIONS[placeholder][idx]
                                text = text.replace(f"{{{placeholder}}}", value)
                        
                        corpus[lang].append({
                            "text": text,
                            "dhatu": dhatu,
                            "concept": concept_name
                        })
                        
                        generated += 1
                        if generated >= phrases_per_concept:
                            break
                    
                    if generated >= phrases_per_concept:
                        break
                
                if generated >= phrases_per_concept:
                    break
        
        return corpus
    
    def compute_semantic_hash(self, dhatu_signature: Dict[str, float]) -> str:
        """Calcule le hash sémantique"""
        quantized = {k: round(v * 4) / 4 for k, v in dhatu_signature.items()}
        signature_str = json.dumps(quantized, sort_keys=True)
        return hashlib.sha256(signature_str.encode()).hexdigest()
    
    def insert_into_dolt(self, language: str, text: str, dhatu_sig: Dict[str, float]):
        """Insère dans Dolt"""
        content_hash = hashlib.sha256(text.encode()).hexdigest()
        semantic_hash = self.compute_semantic_hash(dhatu_sig)
        dhatu_json = json.dumps(dhatu_sig)
        
        # Échappement SQL
        text_escaped = text.replace("'", "''").replace("\\", "\\\\")
        
        sql = f"""INSERT INTO semantic_mappings 
(content_hash, source_text, language, dhatu_signature, semantic_hash)
VALUES ('{content_hash}', '{text_escaped}', '{language}', '{dhatu_json}', '{semantic_hash}');
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
        except subprocess.CalledProcessError:
            # Ignorer les doublons
            self.stats[f"{language}_duplicates"] += 1
    
    def process_corpus(self, corpus: Dict[str, List[Dict]]):
        """Traite et insère le corpus"""
        for lang, phrases in corpus.items():
            print(f"\n🌍 Langue: {lang.upper()}")
            print(f"  📝 {len(phrases)} phrases à insérer...")
            
            for i, phrase in enumerate(phrases, 1):
                self.insert_into_dolt(lang, phrase["text"], phrase["dhatu"])
                
                if i % 100 == 0:
                    print(f"     {i}/{len(phrases)} phrases traitées...")
            
            print(f"  ✅ {lang}: {self.stats[f'{lang}_inserted']} insérées, "
                  f"{self.stats[f'{lang}_duplicates']} doublons")
    
    def commit_changes(self, message: str):
        """Commit Dolt"""
        print(f"\n💾 Commit: {message}")
        subprocess.run(["dolt", "add", "."], cwd=self.db_path, check=True)
        subprocess.run(["dolt", "commit", "-m", message], cwd=self.db_path, check=True)
    
    def show_stats(self):
        """Affiche les statistiques"""
        print("\n" + "=" * 70)
        print("📊 STATISTIQUES FINALES")
        print("=" * 70)
        
        result = subprocess.run(
            ["dolt", "sql", "-q", 
             "SELECT COUNT(*) as total, COUNT(DISTINCT semantic_hash) as concepts, "
             "COUNT(DISTINCT language) as languages FROM semantic_mappings"],
            cwd=self.db_path,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        
        print("\nTop 10 concepts par nombre de langues:")
        result = subprocess.run(
            ["dolt", "sql", "-q",
             "SELECT semantic_hash, COUNT(DISTINCT language) as langs, "
             "GROUP_CONCAT(DISTINCT language) as languages "
             "FROM semantic_mappings GROUP BY semantic_hash "
             "ORDER BY langs DESC LIMIT 10"],
            cwd=self.db_path,
            capture_output=True,
            text=True
        )
        print(result.stdout)


def main():
    parser = argparse.ArgumentParser(description="Génère un corpus synthétique multilingue")
    parser.add_argument("--count", type=int, default=1000, help="Nombre total de phrases")
    parser.add_argument("--languages", default="fr,en,es", help="Langues (séparées par virgules)")
    parser.add_argument("--db-path", default="./panini-concepts-db", help="Chemin base Dolt")
    
    args = parser.parse_args()
    languages = [lang.strip() for lang in args.languages.split(",")]
    
    print("=" * 80)
    print("🚀 GÉNÉRATEUR DE CORPUS SYNTHÉTIQUE MULTILINGUE")
    print("=" * 80)
    print(f"  Langues: {', '.join(languages)}")
    print(f"  Total phrases: {args.count}")
    print(f"  Base: {args.db_path}")
    print()
    
    # Notification
    notify_script = Path(__file__).parent / "notify_user.sh"
    if notify_script.exists():
        subprocess.run([str(notify_script), "Génération corpus démarrée"], check=False)
    
    generator = SyntheticCorpusGenerator(args.db_path)
    
    try:
        # Génération
        print("📝 Génération des phrases...")
        corpus = generator.generate_phrases(languages, args.count)
        
        total = sum(len(phrases) for phrases in corpus.values())
        print(f"✅ {total} phrases générées")
        
        # Insertion
        generator.process_corpus(corpus)
        generator.commit_changes(f"Add synthetic corpus: {total} phrases in {len(languages)} languages")
        
        # Stats
        generator.show_stats()
        
        print("\n" + "=" * 80)
        print("✅ CORPUS GÉNÉRÉ AVEC SUCCÈS!")
        print("=" * 80)
        
        if notify_script.exists():
            subprocess.run([str(notify_script), f"Corpus généré: {total} phrases!"], check=False)
    
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        if notify_script.exists():
            subprocess.run([str(notify_script), f"Erreur: {e}"], check=False)
        sys.exit(1)


if __name__ == "__main__":
    main()
