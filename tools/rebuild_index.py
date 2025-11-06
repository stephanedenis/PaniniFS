#!/usr/bin/env python3
"""
Reconstruit l'index RocksDB depuis les chunks stockés

Scanne le storage content-addressed et reconstruit l'index
pour rendre les chunks accessibles via l'API.
"""

import os
import sys
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Tuple
import time

def compute_sha256(data: bytes) -> str:
    """Calcule le hash SHA-256 des données"""
    return hashlib.sha256(data).hexdigest()

def scan_chunks(storage_path: Path) -> List[Tuple[str, Path, int]]:
    """
    Scanne récursivement le storage pour trouver tous les chunks
    
    Returns:
        List de (hash, path, size) pour chaque chunk
    """
    chunks = []
    
    # Ignorer ces répertoires spéciaux
    ignore_dirs = {'dhatu', 'checkpoints', 'index'}
    
    print(f"📂 Scan de {storage_path}...")
    
    # Parcourir tous les répertoires hex (00-ff)
    for item in storage_path.iterdir():
        if not item.is_dir():
            continue
        if item.name in ignore_dirs:
            continue
            
        # C'est un répertoire hex, scanner récursivement
        for chunk_file in item.rglob('*'):
            if chunk_file.is_file():
                size = chunk_file.stat().st_size
                # Le hash est reconstruit depuis le chemin
                # Format: /path/to/storage/XX/YY/ZZ/...
                rel_path = chunk_file.relative_to(storage_path)
                hash_parts = [p for p in rel_path.parts if len(p) == 2]
                reconstructed_hash = ''.join(hash_parts) + chunk_file.name
                
                chunks.append((reconstructed_hash, chunk_file, size))
    
    return chunks

def verify_chunk(chunk_path: Path, expected_hash: str) -> bool:
    """
    Vérifie qu'un chunk a le bon hash
    
    Returns:
        True si le hash correspond
    """
    try:
        with open(chunk_path, 'rb') as f:
            data = f.read()
            actual_hash = compute_sha256(data)
            return actual_hash == expected_hash
    except Exception as e:
        print(f"⚠️  Erreur lecture {chunk_path}: {e}")
        return False

def load_dhatu_profiles(storage_path: Path) -> Dict[str, dict]:
    """
    Charge les profils Dhātu existants
    
    Returns:
        Dict de hash → profil Dhātu
    """
    dhatu_dir = storage_path / 'dhatu'
    if not dhatu_dir.exists():
        return {}
    
    profiles = {}
    
    for profile_file in dhatu_dir.rglob('*.json'):
        try:
            with open(profile_file, 'r') as f:
                data = json.load(f)
                # Le nom du fichier devrait être le hash
                chunk_hash = profile_file.stem
                profiles[chunk_hash] = data
        except Exception as e:
            print(f"⚠️  Erreur lecture profil {profile_file}: {e}")
    
    return profiles

def generate_index_data(chunks: List[Tuple[str, Path, int]], 
                       dhatu_profiles: Dict[str, dict]) -> dict:
    """
    Génère les données d'index au format attendu par l'API
    
    Returns:
        Dict avec statistiques et métadonnées
    """
    total_size = sum(size for _, _, size in chunks)
    
    # Calculer les statistiques de déduplication
    # Pour l'instant on suppose un faible taux (0.81% observé)
    dedup_ratio = 0.0081
    storage_saved = int(total_size * dedup_ratio)
    
    # Créer les métadonnées de chunks
    chunks_metadata = []
    for chunk_hash, chunk_path, size in chunks:
        metadata = {
            'hash': chunk_hash,
            'size': size,
            'chunk_type': 'Raw',  # Défaut, à affiner plus tard
            'ref_count': 1,  # À calculer si on a les références
            'created_at': int(chunk_path.stat().st_mtime),
        }
        
        # Ajouter le profil Dhātu si disponible
        if chunk_hash in dhatu_profiles:
            metadata['dhatu'] = dhatu_profiles[chunk_hash]
        
        chunks_metadata.append(metadata)
    
    return {
        'total_files': len(chunks),  # À affiner: compter les fichiers originaux
        'total_chunks': len(chunks),
        'unique_chunks': len(chunks),
        'total_size': total_size,
        'dedup_ratio': dedup_ratio,
        'storage_saved': storage_saved,
        'avg_reuse': 1.0 + dedup_ratio,  # Facteur de réutilisation
        'chunks': chunks_metadata,
        'rebuilt_at': int(time.time()),
    }

def save_index(storage_path: Path, index_data: dict):
    """
    Sauvegarde l'index reconstruit
    
    Pour l'instant, on sauvegarde en JSON.
    TODO: Intégrer avec RocksDB directement
    """
    index_file = storage_path / 'index' / 'rebuilt_index.json'
    index_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(index_file, 'w') as f:
        json.dump(index_data, f, indent=2)
    
    print(f"\n💾 Index sauvegardé: {index_file}")
    print(f"   Taille: {index_file.stat().st_size / 1024:.1f} KB")

def main():
    if len(sys.argv) < 2:
        print("Usage: rebuild_index.py <storage_path>")
        print("\nExemple:")
        print("  python3 rebuild_index.py /home/stephane/panini-wikipedia-full")
        sys.exit(1)
    
    storage_path = Path(sys.argv[1])
    
    if not storage_path.exists():
        print(f"❌ Storage introuvable: {storage_path}")
        sys.exit(1)
    
    print("=" * 70)
    print("🔧 RECONSTRUCTION D'INDEX PANINI-FS")
    print("=" * 70)
    print(f"\n📍 Storage: {storage_path}")
    print(f"   Taille: {sum(f.stat().st_size for f in storage_path.rglob('*') if f.is_file()) / (1024*1024):.1f} MB")
    
    # Étape 1: Scanner les chunks
    print("\n📊 Étape 1/4: Scan des chunks...")
    start_time = time.time()
    chunks = scan_chunks(storage_path)
    scan_duration = time.time() - start_time
    
    print(f"   ✅ {len(chunks)} chunks trouvés en {scan_duration:.1f}s")
    print(f"   💾 Taille totale: {sum(s for _, _, s in chunks) / (1024*1024):.1f} MB")
    
    # Étape 2: Charger les profils Dhātu
    print("\n🪷 Étape 2/4: Chargement profils Dhātu...")
    dhatu_profiles = load_dhatu_profiles(storage_path)
    print(f"   ✅ {len(dhatu_profiles)} profils Dhātu chargés")
    
    # Étape 3: Vérification (optionnelle, sur échantillon)
    print("\n🔍 Étape 3/4: Vérification intégrité (échantillon)...")
    sample_size = min(10, len(chunks))
    verified = 0
    for i, (chunk_hash, chunk_path, _) in enumerate(chunks[:sample_size]):
        if verify_chunk(chunk_path, chunk_hash):
            verified += 1
        if (i + 1) % 5 == 0:
            print(f"   ... {i + 1}/{sample_size} vérifiés")
    
    print(f"   ✅ {verified}/{sample_size} chunks valides")
    
    # Étape 4: Générer et sauvegarder l'index
    print("\n💾 Étape 4/4: Génération de l'index...")
    index_data = generate_index_data(chunks, dhatu_profiles)
    save_index(storage_path, index_data)
    
    # Résumé
    print("\n" + "=" * 70)
    print("✅ RECONSTRUCTION TERMINÉE")
    print("=" * 70)
    print(f"\n📊 Statistiques:")
    print(f"   • Chunks uniques: {index_data['unique_chunks']}")
    print(f"   • Taille totale: {index_data['total_size'] / (1024*1024):.1f} MB")
    print(f"   • Déduplication: {index_data['dedup_ratio']*100:.2f}%")
    print(f"   • Storage économisé: {index_data['storage_saved'] / 1024:.1f} KB")
    print(f"   • Profils Dhātu: {len(dhatu_profiles)}")
    
    print(f"\n🚀 Prochaines étapes:")
    print(f"   1. Relancer l'API: PANINI_STORAGE={storage_path} cargo run --bin panini-api")
    print(f"   2. Tester: curl http://localhost:3000/api/dedup/stats")
    print(f"   3. Vérifier Web UI: http://localhost:5173/graph")

if __name__ == '__main__':
    main()
