#!/usr/bin/env python3
"""
🎯 CRÉATION LABELS PANINI-FS - VERSION PRODUCTION
Optimisé pour rapidité et fiabilité
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from github_session_client import GitHubSessionClient

# Labels PaniniFS complets - Version optimisée
PANINI_LABELS_FINAL = [
    # Priorité et urgence
    {"name": "🔥 Critical", "description": "Problème critique", "color": "ff0000"},
    {"name": "🎯 Priority", "description": "Tâche prioritaire", "color": "ff4757"},
    {"name": "⚡ Urgent", "description": "Action rapide", "color": "ff6b35"},
    
    # Types principaux
    {"name": "🚀 Enhancement", "description": "Amélioration système", "color": "2ecc71"},
    {"name": "🐛 Bug", "description": "Problème à corriger", "color": "e74c3c"},
    {"name": "🆕 Feature", "description": "Nouvelle fonctionnalité", "color": "3498db"},
    {"name": "🔧 Maintenance", "description": "Tâche maintenance", "color": "95a5a6"},
    {"name": "🏗️ Infrastructure", "description": "Infrastructure DevOps", "color": "34495e"},
    
    # Documentation
    {"name": "📚 Documentation", "description": "Mise à jour docs", "color": "f39c12"},
    {"name": "📝 Content", "description": "Création contenu", "color": "f1c40f"},
    {"name": "🎓 Tutorial", "description": "Guide tutoriel", "color": "e67e22"},
    
    # Tests et validation
    {"name": "🧪 Testing", "description": "Tests validation", "color": "9b59b6"},
    {"name": "✅ QA", "description": "Assurance qualité", "color": "8e44ad"},
    {"name": "🔍 Review", "description": "Révision nécessaire", "color": "2c3e50"},
    
    # Technologies
    {"name": "🦀 Rust", "description": "Code Rust Core", "color": "ce422b"},
    {"name": "🐍 Python", "description": "Code Python", "color": "306998"},
    {"name": "🌐 Web", "description": "Interface web", "color": "61dafb"},
    {"name": "🤖 AI", "description": "Intelligence artificielle", "color": "ff6b6b"},
    {"name": "☁️ Cloud", "description": "Services cloud", "color": "0ea5e9"},
    {"name": "🔐 Security", "description": "Sécurité", "color": "dc2626"},
    
    # État workflow
    {"name": "🚧 In Progress", "description": "En développement", "color": "f97316"},
    {"name": "⏸️ On Hold", "description": "En attente", "color": "6b7280"},
    {"name": "✅ Ready", "description": "Prêt déploiement", "color": "10b981"},
    {"name": "🔄 Needs Update", "description": "Mise à jour requise", "color": "eab308"},
    {"name": "❓ Question", "description": "Question clarification", "color": "06b6d4"},
    
    # Composants PaniniFS
    {"name": "🍳 Core", "description": "Système core PaniniFS", "color": "b91c1c"},
    {"name": "🔗 Protocols", "description": "Protocoles API", "color": "059669"},
    {"name": "🧠 Semantic", "description": "Analyse sémantique", "color": "7c3aed"},
    {"name": "🔄 Validation", "description": "Système validation", "color": "0891b2"},
    {"name": "📊 Ecosystem", "description": "Écosystème intégrations", "color": "dc2626"},
    {"name": "⚙️ Operations", "description": "Opérations DevOps", "color": "374151"},
    
    # Automatisation
    {"name": "🤖 AI-Generated", "description": "Généré par IA", "color": "ff6b6b"},
    {"name": "🎭 Playwright", "description": "Automation Playwright", "color": "2563eb"},
    {"name": "🔧 Automation", "description": "Automatisation", "color": "059669"},
    {"name": "🎯 Copilotage", "description": "Système copilotage", "color": "ec4899"},
]

async def create_all_labels():
    """Création de tous les labels PaniniFS"""
    client = GitHubSessionClient()
    
    print("🎯 CRÉATION LABELS PANINI-FS - VERSION FINALE")
    print("=" * 50)
    
    if not await client.connect():
        print("❌ Serveur WebSocket non disponible")
        print("💡 Démarrez: ./ECOSYSTEM/tools/github_session_control.sh start")
        return
    
    # Vérifier si on a une session active
    status = await client.get_status()
    print(f"📊 Session actuelle: {status}")
    
    # Si pas de session, demander connexion
    if not status.get('logged_in') and 'github.com' not in str(status.get('url', '')):
        print("🔐 Pas de session GitHub active")
        print("💡 Connectez-vous d'abord avec:")
        print("   ./ECOSYSTEM/tools/github_session_control.sh demo")
        await client.disconnect()
        return
    
    # Confirmer la session
    await client.confirm_login()
    
    # Navigation vers les labels
    print("📍 Navigation vers les labels GitHub...")
    result = await client.goto_url("https://github.com/stephanedenis/PaniniFS/labels")
    print(f"   Navigation: {result.get('success', False)}")
    
    # Création des labels
    print(f"\\n🏷️  Création de {len(PANINI_LABELS_FINAL)} labels...")
    print("   (Pauses optimisées pour rapidité)")
    
    created = 0
    existing = 0
    failed = 0
    start_time = asyncio.get_event_loop().time()
    
    for i, label in enumerate(PANINI_LABELS_FINAL, 1):
        print(f"[{i:2d}/{len(PANINI_LABELS_FINAL)}] {label['name'][:25]:<25} ", end="")
        
        try:
            result = await client.create_label(**label)
            
            if result.get("success"):
                print("✅ Créé")
                created += 1
            else:
                error = result.get("error", "").lower()
                if "already exists" in error or "existe" in error:
                    print("⚠️  Existe")
                    existing += 1
                else:
                    print(f"❌ {result.get('error', 'Erreur')[:30]}")
                    failed += 1
            
            # Pause très courte entre créations
            await asyncio.sleep(0.3)
            
        except Exception as e:
            print(f"❌ Exception: {str(e)[:30]}")
            failed += 1
    
    end_time = asyncio.get_event_loop().time()
    total_time = end_time - start_time
    
    # Résumé final
    print(f"\\n📊 RÉSUMÉ FINAL:")
    print(f"   ✅ Créés:     {created}")
    print(f"   ⚠️  Existants: {existing}")
    print(f"   ❌ Échecs:    {failed}")
    print(f"   ⏱️  Durée:     {total_time:.1f}s")
    print(f"   🚀 Vitesse:   {len(PANINI_LABELS_FINAL)/total_time:.1f} labels/s")
    
    # Screenshot final
    print("\\n📸 Screenshot final...")
    screenshot_result = await client.take_screenshot("/tmp/panini_labels_final.png")
    if screenshot_result.get("success"):
        print(f"   Sauvé: {screenshot_result.get('screenshot_path')}")
    
    print("\\n🎉 CONFIGURATION GITHUB TERMINÉE!")
    print("🔗 Voir: https://github.com/stephanedenis/PaniniFS/labels")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(create_all_labels())
