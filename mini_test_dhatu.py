#!/usr/bin/env python3
"""
🔬 MINI TEST DHĀTU - Validation sur échantillon restreint

Test ciblé sur 2-3 fichiers pour valider le concept avant extension.
"""

import sys
from pathlib import Path
sys.path.append('.')
from dhatu_detector import DhatuDetector

def mini_test_dhatu():
    """Test minimal sur quelques fichiers sélectionnés"""
    
    detector = DhatuDetector()
    
    # Sélection de fichiers tests
    test_files = [
        'analogy_detector_mvp.py',
        'BABY_SIGN_LANGUAGE_FOUNDATION.md', 
        'setup_mvp_dataset.sh'
    ]
    
    print("🎯 MINI TEST DHĀTU - Échantillon Restreint")
    print("=" * 50)
    
    for filename in test_files:
        filepath = Path(filename)
        if not filepath.exists():
            print(f"❌ Fichier non trouvé: {filename}")
            continue
            
        print(f"\n📄 Analyse: {filename}")
        print("-" * 30)
        
        result = detector.detect_in_file(filepath)
        
        if 'error' in result:
            print(f"❌ Erreur: {result['error']}")
            continue
            
        if result['detected_dhatus']:
            print("✅ Dhātu détectés:")
            for dhatu_info in result['detected_dhatus']:
                dhatu = dhatu_info['dhatu']
                count = dhatu_info['count']
                matches = dhatu_info['matches'][:3]  # Premiers 3 exemples
                print(f"  🔹 {dhatu} ({count}x): {matches}")
        else:
            print("  ➖ Aucun dhātu détecté")
    
    print("\n" + "=" * 50)
    print("🎯 CONCLUSIONS MINI TEST:")
    print("1. Le détecteur fonctionne-t-il sur nos fichiers ?")
    print("2. Les dhātu détectés sont-ils pertinents ?") 
    print("3. Y a-t-il des patterns cross-fichiers ?")
    print("4. Faut-il ajuster le catalogue de dhātu ?")

if __name__ == "__main__":
    mini_test_dhatu()
