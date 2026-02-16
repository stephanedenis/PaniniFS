#!/usr/bin/env python3
"""
Script d'initialisation du concept store Dolt pour PaniniFS

Ce script :
1. Initialise un repo Dolt local dans ./panini-concepts-db/
2. Crée les tables depuis schema.sql
3. Peuple dhatu_definitions avec les 7 dhātu
4. Peuple dhatu_inventory avec les primitives v0.1
5. Fait un commit initial "seed: 7 dhātu + inventory v0.1"

Usage:
    python init_dolt.py

Architecture:
    - Utilise subprocess pour appeler la CLI dolt (plus fiable que doltpy)
    - Alternative: doltpy si installé et compatible
"""

import subprocess
import json
import os
import sys
from pathlib import Path

# Configuration
DB_DIR = "./panini-concepts-db"
SCHEMA_FILE = "./schema.sql"

# Les 7 dhātu informationnels (depuis Copilotage/knowledge/SEMANTIC_UNIVERSALS_DHATU.md)
DHATU_DEFINITIONS = [
    {
        "id": "dhatu_comm",
        "code": "COMM",
        "name_fr": "Communiquer/Partager",
        "name_en": "Communicate/Share",
        "description": "Transmission d'information, canal de communication, échange source-cible",
        "components": json.dumps(["canal", "source", "cible"])
    },
    {
        "id": "dhatu_iter",
        "code": "ITER",
        "name_fr": "Itérer/Répéter",
        "name_en": "Iterate/Repeat",
        "description": "Boucle, répétition, cumul, fréquence",
        "components": json.dumps(["boucle", "fréquence", "cumul"])
    },
    {
        "id": "dhatu_trans",
        "code": "TRANS",
        "name_fr": "Transformer",
        "name_en": "Transform",
        "description": "Transformation entrée-opération-sortie",
        "components": json.dumps(["entrée", "opération", "sortie"])
    },
    {
        "id": "dhatu_decide",
        "code": "DECIDE",
        "name_fr": "Choisir/Régler",
        "name_en": "Decide/Choose",
        "description": "Décision, choix, critères, seuils, branches conditionnelles",
        "components": json.dumps(["critères", "seuils", "branches"])
    },
    {
        "id": "dhatu_locate",
        "code": "LOCATE",
        "name_fr": "Localiser/Ancrer",
        "name_en": "Locate/Anchor",
        "description": "Localisation, position, contexte spatial ou conceptuel, repères",
        "components": json.dumps(["position", "contexte", "repères"])
    },
    {
        "id": "dhatu_group",
        "code": "GROUP",
        "name_fr": "Regrouper/Structurer",
        "name_en": "Group/Structure",
        "description": "Collection, regroupement, appartenance, structure",
        "components": json.dumps(["collection", "appartenance"])
    },
    {
        "id": "dhatu_seq",
        "code": "SEQ",
        "name_fr": "Séquencer/Ordonner",
        "name_en": "Sequence/Order",
        "description": "Ordre, séquence, dépendances, timeline",
        "components": json.dumps(["ordre", "dépendances", "timeline"])
    }
]

# Inventaire dhātu v0.1 (depuis docs/en/research/dhatu-inventory-v0-1.md)
DHATU_INVENTORY = [
    # Core primitives
    {"id": "inv_agent", "category": "AGENT", "symbol": "AGENT", "stable_id": "primitive:agent", "description": "Agent de l'action"},
    {"id": "inv_action", "category": "ACTION", "symbol": "ACTION", "stable_id": "primitive:action", "description": "Action effectuée"},
    {"id": "inv_patient", "category": "PATIENT", "symbol": "PATIENT", "stable_id": "primitive:patient", "description": "Patient/objet de l'action"},
    {"id": "inv_place", "category": "PLACE", "symbol": "PLACE", "stable_id": "primitive:place", "description": "Lieu de l'action"},
    {"id": "inv_time", "category": "TIME", "symbol": "TIME", "stable_id": "primitive:time", "description": "Temps de l'action"},
    {"id": "inv_rel", "category": "REL", "symbol": "REL", "stable_id": "primitive:rel", "description": "Relation générique"},
    {"id": "inv_possession", "category": "POSSESSION", "symbol": "POSSESSION", "stable_id": "primitive:possession", "description": "Possession, appartenance"},
    {"id": "inv_negation", "category": "NEGATION", "symbol": "NEGATION", "stable_id": "primitive:negation", "description": "Négation"},
    {"id": "inv_quant", "category": "QUANT", "symbol": "QUANT", "stable_id": "primitive:quant", "description": "Quantification"},
    {"id": "inv_modality", "category": "MODALITY", "symbol": "MODALITY", "stable_id": "primitive:modality", "description": "Modalité (can, must, etc.)"},
    {"id": "inv_aspect", "category": "ASPECT", "symbol": "ASPECT", "stable_id": "primitive:aspect", "description": "Aspect (habitual, perfective, etc.)"},
    {"id": "inv_coref", "category": "COREF", "symbol": "COREF", "stable_id": "primitive:coref", "description": "Coréférence"},
    {"id": "inv_interrogative", "category": "INTERROGATIVE", "symbol": "INTERROGATIVE", "stable_id": "primitive:interrogative", "description": "Interrogation"},
    {"id": "inv_state", "category": "STATE", "symbol": "STATE", "stable_id": "primitive:state", "description": "État"},
    
    # Lexicon - Relations
    {"id": "inv_rel_on", "category": "REL", "symbol": "ON", "stable_id": "rel:on", "description": "Relation: sur", "lexicon_alias": "ON"},
    {"id": "inv_rel_in", "category": "REL", "symbol": "IN", "stable_id": "rel:in", "description": "Relation: dans", "lexicon_alias": "IN"},
    {"id": "inv_rel_of", "category": "REL", "symbol": "OF", "stable_id": "rel:of", "description": "Relation: de", "lexicon_alias": "OF"},
    
    # Lexicon - Modalité
    {"id": "inv_modal_can", "category": "MODALITY", "symbol": "CAN", "stable_id": "modal:can", "description": "Modalité: pouvoir", "lexicon_alias": "CAN"},
    {"id": "inv_modal_must", "category": "MODALITY", "symbol": "MUST", "stable_id": "modal:must", "description": "Modalité: devoir", "lexicon_alias": "MUST"},
    
    # Lexicon - Aspect
    {"id": "inv_aspect_hab", "category": "ASPECT", "symbol": "HABITUAL", "stable_id": "aspect:habitual", "description": "Aspect: habituel", "lexicon_alias": "HABITUAL"},
    {"id": "inv_aspect_perf", "category": "ASPECT", "symbol": "PERFECTIVE", "stable_id": "aspect:perfective", "description": "Aspect: perfectif", "lexicon_alias": "PERFECTIVE"},
]


def run_dolt_cmd(args, cwd=None):
    """Execute une commande dolt via subprocess"""
    try:
        result = subprocess.run(
            ["dolt"] + args,
            cwd=cwd or DB_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur dolt: {e.stderr}")
        raise
    except FileNotFoundError:
        print("❌ Erreur: 'dolt' n'est pas installé ou n'est pas dans le PATH")
        print("Installation: https://docs.dolthub.com/introduction/installation")
        sys.exit(1)


def init_dolt_repo():
    """Initialise le repo Dolt"""
    print("🔧 Initialisation du repo Dolt...")
    
    # Créer le répertoire s'il n'existe pas
    os.makedirs(DB_DIR, exist_ok=True)
    
    # Vérifier si déjà initialisé
    if os.path.exists(os.path.join(DB_DIR, ".dolt")):
        print("ℹ️  Repo Dolt déjà initialisé")
        return
    
    # Initialiser
    run_dolt_cmd(["init"], cwd=DB_DIR)
    print("✅ Repo Dolt initialisé dans", DB_DIR)
    
    # Configurer l'utilisateur
    run_dolt_cmd(["config", "--local", "user.name", "PaniniFS System"])
    run_dolt_cmd(["config", "--local", "user.email", "panini@localhost"])


def create_schema():
    """Crée les tables depuis schema.sql"""
    print("🔧 Création du schéma...")
    
    if not os.path.exists(SCHEMA_FILE):
        print(f"❌ Fichier {SCHEMA_FILE} introuvable")
        sys.exit(1)
    
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # Exécuter le schéma (Dolt supporte < pour redirection)
    run_dolt_cmd(["sql", "-q", schema_sql])
    print("✅ Schéma créé")


def populate_dhatu_definitions():
    """Peuple la table dhatu_definitions"""
    print("🔧 Peuplement des 7 dhātu...")
    
    for dhatu in DHATU_DEFINITIONS:
        sql = f"""
        INSERT INTO dhatu_definitions (id, code, name_fr, name_en, description, components)
        VALUES ('{dhatu['id']}', '{dhatu['code']}', '{dhatu['name_fr']}', 
                '{dhatu['name_en']}', '{dhatu['description']}', '{dhatu['components']}');
        """
        run_dolt_cmd(["sql", "-q", sql])
    
    print(f"✅ {len(DHATU_DEFINITIONS)} dhātu insérés")


def populate_dhatu_inventory():
    """Peuple la table dhatu_inventory"""
    print("🔧 Peuplement de l'inventaire v0.1...")
    
    for item in DHATU_INVENTORY:
        lexicon = item.get('lexicon_alias', '')
        sql = f"""
        INSERT INTO dhatu_inventory (id, category, symbol, stable_id, description, lexicon_alias)
        VALUES ('{item['id']}', '{item['category']}', '{item['symbol']}', 
                '{item['stable_id']}', '{item.get('description', '')}', '{lexicon}');
        """
        run_dolt_cmd(["sql", "-q", sql])
    
    print(f"✅ {len(DHATU_INVENTORY)} primitives insérées")


def initial_commit():
    """Fait le commit initial"""
    print("🔧 Commit initial...")
    
    # Ajouter toutes les tables
    run_dolt_cmd(["add", "."])
    
    # Commit
    run_dolt_cmd(["commit", "-m", "seed: 7 dhātu + inventory v0.1"])
    
    print("✅ Commit initial effectué")


def verify_installation():
    """Vérifie l'installation"""
    print("🔍 Vérification de l'installation...")
    
    # Compter les dhātu
    result = run_dolt_cmd(["sql", "-q", "SELECT COUNT(*) FROM dhatu_definitions;"])
    print(f"   - dhatu_definitions: {result.strip()}")
    
    result = run_dolt_cmd(["sql", "-q", "SELECT COUNT(*) FROM dhatu_inventory;"])
    print(f"   - dhatu_inventory: {result.strip()}")
    
    # Afficher les dhātu
    print("\n📊 Les 7 dhātu:")
    result = run_dolt_cmd(["sql", "-q", "SELECT code, name_fr, name_en FROM dhatu_definitions ORDER BY id;"])
    print(result)
    
    # Historique
    print("📜 Historique:")
    result = run_dolt_cmd(["log"])
    print(result)


def main():
    """Point d'entrée principal"""
    print("=" * 60)
    print("🚀 Initialisation du Dolt Concept Store PaniniFS")
    print("=" * 60)
    print()
    
    try:
        init_dolt_repo()
        create_schema()
        populate_dhatu_definitions()
        populate_dhatu_inventory()
        initial_commit()
        verify_installation()
        
        print()
        print("=" * 60)
        print("✅ Initialisation terminée avec succès!")
        print("=" * 60)
        print()
        print("Prochaines étapes:")
        print("  1. Exécuter demo_workflow.py pour voir le workflow complet")
        print("  2. Exécuter rust_bridge_stub.py pour voir l'interface Rust")
        print()
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Erreur lors de l'initialisation: {e}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
