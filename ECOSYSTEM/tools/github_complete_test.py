#!/usr/bin/env python3
"""
🎭 TEST COMPLET - Initialisation + Création Labels
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from github_session_client import GitHubSessionClient

async def complete_test():
    client = GitHubSessionClient()
    
    print("🎭 TEST COMPLET GITHUB SESSION")
    print("=" * 35)
    
    if not await client.connect():
        print("❌ Impossible de se connecter au serveur")
        print("💡 Démarrez: ./ECOSYSTEM/tools/github_session_control.sh start")
        return
    
    # 1. Initialiser le navigateur
    print("🚀 Initialisation du navigateur...")
    result = await client.initialize_session()
    print(f"   Résultat: {result.get('success', False)}")
    
    if not result.get('success'):
        print("❌ Échec initialisation")
        await client.disconnect()
        return
    
    # 2. Démarrer le login (ouvre Firefox)
    print("🔐 Ouverture de Firefox pour login...")
    result = await client.start_login()
    print("   👆 CONNECTEZ-VOUS DANS FIREFOX (vous avez 30 secondes)")
    
    # Attendre que l'utilisateur se connecte
    await asyncio.sleep(30)
    
    # 3. Confirmer le login
    print("✅ Confirmation du login...")
    await client.confirm_login()
    
    # 4. Vérifier l'état
    status = await client.get_status()
    print(f"📊 État: {status}")
    
    # 5. Test de création d'un label simple
    print("🏷️  Test création label...")
    test_label = {
        "name": "🧪 Test-Rapide",
        "description": "Label de test optimisé",
        "color": "00ff00"
    }
    
    result = await client.create_label(**test_label)
    print(f"   Résultat: {result}")
    
    # 6. Screenshot final
    print("📸 Screenshot...")
    await client.take_screenshot("/tmp/github_test_final.png")
    
    await client.disconnect()
    print("🎉 Test terminé!")

if __name__ == "__main__":
    asyncio.run(complete_test())
