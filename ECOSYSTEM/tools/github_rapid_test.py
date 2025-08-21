#!/usr/bin/env python3
"""
🚀 TEST RAPIDE CRÉATION LABELS - Version optimisée
Pauses réduites et sélecteurs précis
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from github_session_client import GitHubSessionClient

# Labels de test avec descriptions courtes
TEST_LABELS = [
    {"name": "🔥 Critical", "description": "Problème critique", "color": "ff0000"},
    {"name": "🎯 Priority", "description": "Tâche prioritaire", "color": "ff4757"},
    {"name": "🚀 Enhancement", "description": "Amélioration système", "color": "2ecc71"},
    {"name": "🐛 Bug", "description": "Problème à corriger", "color": "e74c3c"},
    {"name": "📚 Documentation", "description": "Docs à jour", "color": "f39c12"},
]

async def rapid_test():
    client = GitHubSessionClient()
    
    print("🚀 TEST RAPIDE - CRÉATION LABELS OPTIMISÉE")
    print("=" * 45)
    
    if not await client.connect():
        print("❌ Serveur non disponible")
        return
    
    # Confirmer session (la session Firefox devrait être active)
    await client.confirm_login()
    
    # Navigation directe
    print("📍 Navigation vers labels...")
    await client.goto_url("https://github.com/stephanedenis/PaniniFS/labels")
    
    # Test de création rapide
    print(f"\n🏷️  Création de {len(TEST_LABELS)} labels...")
    start_time = asyncio.get_event_loop().time()
    
    created = 0
    for i, label in enumerate(TEST_LABELS, 1):
        print(f"[{i}/{len(TEST_LABELS)}] {label['name']}", end=" ")
        
        result = await client.create_label(**label)
        if result.get("success"):
            print("✅")
            created += 1
        else:
            error = result.get("error", "")
            if "already exists" in error.lower():
                print("⚠️")
            else:
                print(f"❌ {error}")
        
        # Pause très courte
        await asyncio.sleep(0.2)
    
    end_time = asyncio.get_event_loop().time()
    duration = end_time - start_time
    
    print(f"\n📊 RÉSULTATS:")
    print(f"   ✅ Créés: {created}/{len(TEST_LABELS)}")
    print(f"   ⏱️  Durée: {duration:.1f}s")
    print(f"   🚀 Vitesse: {len(TEST_LABELS)/duration:.1f} labels/seconde")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(rapid_test())
