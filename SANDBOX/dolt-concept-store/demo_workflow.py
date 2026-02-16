#!/usr/bin/env python3
"""
Démonstration du workflow Dolt complet pour PaniniFS

Ce script démontre:
1. Insertion de semantic_mappings avec déduplication cross-langue
2. Insertion de analysis_results pour fichiers simulés
3. Création de branches expérimentales
4. Commits versionnés
5. Diff entre branches
6. Historique et audit trail
7. Déduplication sémantique ("Hello world" = "Bonjour monde")

Usage:
    python demo_workflow.py

Prérequis:
    - Avoir exécuté init_dolt.py d'abord
"""

import subprocess
import json
import hashlib
import sys
from datetime import datetime

DB_DIR = "./panini-concepts-db"


def run_dolt_cmd(args):
    """Execute une commande dolt"""
    try:
        result = subprocess.run(
            ["dolt"] + args,
            cwd=DB_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur dolt: {e.stderr}")
        raise
    except FileNotFoundError:
        print("❌ Erreur: 'dolt' n'est pas installé")
        sys.exit(1)


def compute_semantic_hash(text):
    """
    Calcule le hash sémantique d'un texte
    
    Dans un vrai système, ceci utiliserait l'analyseur Rust pour:
    1. Extraire la signature dhātu du texte
    2. Normaliser cette signature (invariante à la langue)
    3. Hash de la signature normalisée
    
    Pour la démo, on simule: textes avec même sens → même hash
    """
    # Normalisation simplifiée pour la démo
    # "Hello world" et "Bonjour monde" → concept de salutation
    normalized = text.lower().strip()
    
    # Mapping simplifié pour démonstration
    semantic_clusters = {
        "hello": "greeting_world",
        "bonjour": "greeting_world",
        "hola": "greeting_world",
        "iterate": "concept_iteration",
        "itérer": "concept_iteration",
        "loop": "concept_iteration",
        "transform": "concept_transformation",
        "transformer": "concept_transformation",
    }
    
    # Chercher un cluster sémantique connu
    for key, cluster in semantic_clusters.items():
        if key in normalized:
            # Hash du cluster sémantique
            return hashlib.sha256(cluster.encode()).hexdigest()
    
    # Fallback: hash du texte normalisé
    return hashlib.sha256(normalized.encode()).hexdigest()


def insert_semantic_mapping(text, language, dhatu_signature):
    """Insère un mapping sémantique"""
    content_hash = hashlib.sha256(text.encode()).hexdigest()
    semantic_hash = compute_semantic_hash(text)
    
    sql = f"""
    INSERT INTO semantic_mappings 
    (content_hash, source_text, language, dhatu_signature, semantic_hash)
    VALUES ('{content_hash}', '{text}', '{language}', 
            '{json.dumps(dhatu_signature)}', '{semantic_hash}');
    """
    run_dolt_cmd(["sql", "-q", sql])
    return semantic_hash


def insert_analysis_result(file_path, dhatu_vector, dominant_dhatu):
    """Insère un résultat d'analyse"""
    file_hash = hashlib.sha256(file_path.encode()).hexdigest()
    
    sql = f"""
    INSERT INTO analysis_results 
    (file_path, file_hash, dhatu_vector, dominant_dhatu, analysis_version)
    VALUES ('{file_path}', '{file_hash}', '{json.dumps(dhatu_vector)}', 
            '{dominant_dhatu}', 'v0.1.0-demo');
    """
    run_dolt_cmd(["sql", "-q", sql])


def demo_cross_language_deduplication():
    """Démontre la déduplication cross-langue"""
    print("=" * 60)
    print("📝 DÉMO 1: Déduplication sémantique cross-langue")
    print("=" * 60)
    print()
    
    # Insérer "Hello world" en anglais
    print("Insertion: 'Hello world' (en)")
    hash_en = insert_semantic_mapping(
        "Hello world",
        "en",
        {"COMM": 0.9, "ITER": 0.0, "TRANS": 0.1, "DECIDE": 0.0, 
         "LOCATE": 0.0, "GROUP": 0.0, "SEQ": 0.0}
    )
    print(f"  → semantic_hash: {hash_en[:16]}...")
    
    # Insérer "Bonjour monde" en français
    print("\nInsertion: 'Bonjour monde' (fr)")
    hash_fr = insert_semantic_mapping(
        "Bonjour monde",
        "fr",
        {"COMM": 0.9, "ITER": 0.0, "TRANS": 0.1, "DECIDE": 0.0,
         "LOCATE": 0.0, "GROUP": 0.0, "SEQ": 0.0}
    )
    print(f"  → semantic_hash: {hash_fr[:16]}...")
    
    # Insérer "Hola mundo" en espagnol
    print("\nInsertion: 'Hola mundo' (es)")
    hash_es = insert_semantic_mapping(
        "Hola mundo",
        "es",
        {"COMM": 0.9, "ITER": 0.0, "TRANS": 0.1, "DECIDE": 0.0,
         "LOCATE": 0.0, "GROUP": 0.0, "SEQ": 0.0}
    )
    print(f"  → semantic_hash: {hash_es[:16]}...")
    
    # Vérifier la déduplication
    print("\n🔍 Vérification de la déduplication:")
    if hash_en == hash_fr == hash_es:
        print("✅ SUCCÈS! Les 3 textes partagent le même semantic_hash")
        print("   → Concept identique détecté malgré langues différentes")
    else:
        print("⚠️  Les hashes diffèrent (attendu dans cette démo simplifiée)")
        print(f"   EN: {hash_en[:16]}...")
        print(f"   FR: {hash_fr[:16]}...")
        print(f"   ES: {hash_es[:16]}...")
    
    # Afficher les mappings
    print("\n📊 Table semantic_mappings:")
    result = run_dolt_cmd(["sql", "-q", 
        "SELECT language, source_text, semantic_hash FROM semantic_mappings ORDER BY id;"])
    print(result)


def demo_file_analysis():
    """Démontre l'analyse de fichiers"""
    print()
    print("=" * 60)
    print("📊 DÉMO 2: Analyse de fichiers")
    print("=" * 60)
    print()
    
    # Fichier 1: API REST (COMM dominant)
    print("Analyse: src/api/server.rs (API REST)")
    insert_analysis_result(
        "src/api/server.rs",
        {"COMM": 0.6, "ITER": 0.1, "TRANS": 0.2, "DECIDE": 0.05,
         "LOCATE": 0.0, "GROUP": 0.05, "SEQ": 0.0},
        "COMM"
    )
    print("  → Dhātu dominant: COMM")
    
    # Fichier 2: Loop processor (ITER dominant)
    print("\nAnalyse: src/processor/loop.rs (Traitement itératif)")
    insert_analysis_result(
        "src/processor/loop.rs",
        {"COMM": 0.05, "ITER": 0.7, "TRANS": 0.15, "DECIDE": 0.05,
         "LOCATE": 0.0, "GROUP": 0.05, "SEQ": 0.0},
        "ITER"
    )
    print("  → Dhātu dominant: ITER")
    
    # Fichier 3: Data transformer (TRANS dominant)
    print("\nAnalyse: src/transform/pipeline.rs (Pipeline de transformation)")
    insert_analysis_result(
        "src/transform/pipeline.rs",
        {"COMM": 0.1, "ITER": 0.15, "TRANS": 0.6, "DECIDE": 0.05,
         "LOCATE": 0.0, "GROUP": 0.1, "SEQ": 0.0},
        "TRANS"
    )
    print("  → Dhātu dominant: TRANS")
    
    # Afficher les résultats
    print("\n📊 Table analysis_results:")
    result = run_dolt_cmd(["sql", "-q",
        "SELECT file_path, dominant_dhatu FROM analysis_results ORDER BY id;"])
    print(result)


def demo_branching():
    """Démontre le branching et expérimentation"""
    print()
    print("=" * 60)
    print("🌿 DÉMO 3: Branches et expérimentation")
    print("=" * 60)
    print()
    
    # Commit sur main
    print("Commit sur branche main:")
    run_dolt_cmd(["add", "."])
    run_dolt_cmd(["commit", "-m", "Add initial semantic mappings and analysis results"])
    print("✅ Commit effectué")
    
    # Créer une branche expérimentale
    print("\nCréation de la branche experiment/extended-dhatu:")
    run_dolt_cmd(["branch", "experiment/extended-dhatu"])
    run_dolt_cmd(["checkout", "experiment/extended-dhatu"])
    print("✅ Branche créée et checked out")
    
    # Ajouter un dhātu expérimental
    print("\nAjout d'un dhātu expérimental: COMPOSE (composer/combiner)")
    sql = """
    INSERT INTO dhatu_definitions (id, code, name_fr, name_en, description, components)
    VALUES ('dhatu_compose', 'COMPOSE', 'Composer/Combiner', 'Compose/Combine',
            'Composition de plusieurs éléments en un tout', '["éléments", "composition", "résultat"]');
    """
    run_dolt_cmd(["sql", "-q", sql])
    print("✅ Dhātu expérimental ajouté")
    
    # Commit sur la branche expérimentale
    run_dolt_cmd(["add", "."])
    run_dolt_cmd(["commit", "-m", "experiment: Add COMPOSE dhatu candidate"])
    print("✅ Commit expérimental effectué")
    
    # Retour à main
    run_dolt_cmd(["checkout", "main"])
    print("\n✅ Retour sur branche main")


def demo_diff():
    """Démontre le diff entre branches"""
    print()
    print("=" * 60)
    print("🔍 DÉMO 4: Diff entre branches")
    print("=" * 60)
    print()
    
    print("Différences entre main et experiment/extended-dhatu:")
    print()
    
    # Diff des tables
    try:
        result = run_dolt_cmd(["diff", "main", "experiment/extended-dhatu"])
        print(result)
    except subprocess.CalledProcessError:
        # Alternative: comparer les tables
        print("Dhātu sur main:")
        result = run_dolt_cmd(["sql", "-q", "SELECT code FROM dhatu_definitions ORDER BY code;"])
        print(result)
        
        run_dolt_cmd(["checkout", "experiment/extended-dhatu"])
        print("\nDhātu sur experiment/extended-dhatu:")
        result = run_dolt_cmd(["sql", "-q", "SELECT code FROM dhatu_definitions ORDER BY code;"])
        print(result)
        
        run_dolt_cmd(["checkout", "main"])


def demo_history():
    """Démontre l'historique et audit trail"""
    print()
    print("=" * 60)
    print("📜 DÉMO 5: Historique et audit trail")
    print("=" * 60)
    print()
    
    print("Historique des commits:")
    result = run_dolt_cmd(["log", "--oneline"])
    print(result)
    
    print("\nDétails du dernier commit:")
    result = run_dolt_cmd(["log", "-n", "1"])
    print(result)
    
    print("\nListe des branches:")
    result = run_dolt_cmd(["branch", "-a"])
    print(result)


def demo_semantic_query():
    """Démontre les requêtes sémantiques avancées"""
    print()
    print("=" * 60)
    print("🔎 DÉMO 6: Requêtes sémantiques avancées")
    print("=" * 60)
    print()
    
    # Vue de déduplication
    print("Vue semantic_deduplication (concepts partagés entre langues):")
    result = run_dolt_cmd(["sql", "-q",
        "SELECT * FROM semantic_deduplication;"])
    print(result)
    
    # Statistiques par dhātu
    print("\nVue dhatu_statistics (distribution des dhātu):")
    result = run_dolt_cmd(["sql", "-q",
        "SELECT * FROM dhatu_statistics;"])
    print(result)
    
    # Requête custom: fichiers par dhātu dominant
    print("\nFichiers groupés par dhātu dominant:")
    result = run_dolt_cmd(["sql", "-q", """
        SELECT dominant_dhatu, COUNT(*) as count, GROUP_CONCAT(file_path SEPARATOR ', ') as files
        FROM analysis_results
        GROUP BY dominant_dhatu
        ORDER BY count DESC;
    """])
    print(result)


def main():
    """Point d'entrée principal"""
    print()
    print("=" * 80)
    print("🚀 Démonstration du workflow Dolt pour PaniniFS Concept Store")
    print("=" * 80)
    print()
    
    try:
        demo_cross_language_deduplication()
        demo_file_analysis()
        demo_branching()
        demo_diff()
        demo_history()
        demo_semantic_query()
        
        print()
        print("=" * 80)
        print("✅ Démonstration terminée avec succès!")
        print("=" * 80)
        print()
        print("Points clés démontrés:")
        print("  ✅ Déduplication sémantique cross-langue")
        print("  ✅ Versioning des concepts avec Git workflow")
        print("  ✅ Branches pour expérimentation")
        print("  ✅ Diff entre versions du modèle")
        print("  ✅ Audit trail complet")
        print("  ✅ Requêtes sémantiques sur les dhātu")
        print()
        print("Architecture Rust ↔ Dolt:")
        print("  • Rust: analyse fichiers → extraction dhātu → JSON")
        print("  • Dolt: stockage concepts → versioning → querying")
        print("  • Bridge: subprocess, named pipe, ou MySQL protocol")
        print()
        
    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ Erreur: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
