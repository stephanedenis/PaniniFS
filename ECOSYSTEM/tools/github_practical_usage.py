#!/usr/bin/env python3
"""
🎭 GUIDE D'UTILISATION PRATIQUE - GITHUB SESSION MANAGER
Automatisation complète des tâches GitHub sans re-connexion
"""

import asyncio
from github_session_client import GitHubSessionClient

# Labels pour PaniniFS-1 (configuration complète)
PANINI_LABELS_COMPLETE = [
    # Priorité et urgence
    {"name": "🔥 Critical", "description": "Problème critique nécessitant une action immédiate", "color": "ff0000"},
    {"name": "🎯 Priority", "description": "Tâche prioritaire du projet", "color": "ff4757"},
    {"name": "⚡ Urgent", "description": "Nécessite une attention rapide", "color": "ff6b35"},
    
    # Types de tâches
    {"name": "🚀 Enhancement", "description": "Amélioration du système", "color": "2ecc71"},
    {"name": "🐛 Bug", "description": "Problème à corriger", "color": "e74c3c"},
    {"name": "🆕 Feature", "description": "Nouvelle fonctionnalité", "color": "3498db"},
    {"name": "🔧 Maintenance", "description": "Tâche de maintenance", "color": "95a5a6"},
    {"name": "🏗️ Infrastructure", "description": "Infrastructure et DevOps", "color": "34495e"},
    
    # Documentation et communication
    {"name": "📚 Documentation", "description": "Mise à jour documentation", "color": "f39c12"},
    {"name": "📝 Content", "description": "Création de contenu", "color": "f1c40f"},
    {"name": "🎓 Tutorial", "description": "Guide ou tutoriel", "color": "e67e22"},
    {"name": "📖 User Guide", "description": "Guide utilisateur", "color": "d35400"},
    
    # Tests et validation
    {"name": "🧪 Testing", "description": "Tests et validation", "color": "9b59b6"},
    {"name": "✅ QA", "description": "Assurance qualité", "color": "8e44ad"},
    {"name": "🔍 Review", "description": "Révision nécessaire", "color": "2c3e50"},
    {"name": "🎯 Validation", "description": "Validation requise", "color": "16a085"},
    
    # Domaines techniques
    {"name": "🦀 Rust", "description": "Code Rust Core", "color": "ce422b"},
    {"name": "🐍 Python", "description": "Code Python", "color": "306998"},
    {"name": "🌐 Web", "description": "Interface web", "color": "61dafb"},
    {"name": "🤖 AI", "description": "Intelligence artificielle", "color": "ff6b6b"},
    {"name": "☁️ Cloud", "description": "Services cloud", "color": "0ea5e9"},
    {"name": "🔐 Security", "description": "Sécurité", "color": "dc2626"},
    
    # État et workflow
    {"name": "🚧 In Progress", "description": "En cours de développement", "color": "f97316"},
    {"name": "⏸️ On Hold", "description": "En attente", "color": "6b7280"},
    {"name": "✅ Ready", "description": "Prêt pour déploiement", "color": "10b981"},
    {"name": "🔄 Needs Update", "description": "Nécessite une mise à jour", "color": "eab308"},
    {"name": "❓ Question", "description": "Question ou clarification", "color": "06b6d4"},
    {"name": "💬 Discussion", "description": "Discussion en cours", "color": "8b5cf6"},
    
    # Composants PaniniFS
    {"name": "🍳 Core", "description": "Système core PaniniFS", "color": "b91c1c"},
    {"name": "🔗 Protocols", "description": "Protocoles et API", "color": "059669"},
    {"name": "🧠 Semantic", "description": "Analyse sémantique", "color": "7c3aed"},
    {"name": "🔄 Validation", "description": "Système de validation", "color": "0891b2"},
    {"name": "📊 Ecosystem", "description": "Écosystème et intégrations", "color": "dc2626"},
    {"name": "⚙️ Operations", "description": "Opérations et DevOps", "color": "374151"},
    {"name": "🔬 Research", "description": "Recherche et développement", "color": "7c2d12"},
    
    # Automatisation et AI
    {"name": "🤖 AI-Generated", "description": "Généré par IA", "color": "ff6b6b"},
    {"name": "🎭 Playwright", "description": "Automation Playwright", "color": "2563eb"},
    {"name": "🔧 Automation", "description": "Automatisation", "color": "059669"},
    {"name": "🚀 Auto-Deploy", "description": "Déploiement automatique", "color": "7c3aed"},
    
    # Collaboration
    {"name": "👥 Team", "description": "Travail d'équipe", "color": "6366f1"},
    {"name": "🎯 Copilotage", "description": "Système de copilotage", "color": "ec4899"},
    {"name": "📈 Metrics", "description": "Métriques et analytics", "color": "0891b2"},
    {"name": "🔗 Dependencies", "description": "Dépendances externes", "color": "6b7280"},
]

async def setup_complete_github_project():
    """Configuration complète du projet GitHub"""
    client = GitHubSessionClient()
    
    print("🎭 SETUP COMPLET PROJET GITHUB PANINI-FS")
    print("=" * 50)
    
    # Connexion
    if not await client.connect():
        print("❌ Impossible de se connecter au Session Manager")
        print("💡 Démarrez d'abord: ./ECOSYSTEM/tools/github_session_control.sh start")
        return
    
    # Vérifier l'état
    status = await client.get_status()
    print(f"📊 État session: {status.get('url', 'N/A')}")
    print(f"🔐 Connecté: {status.get('logged_in', False)}")
    
    if not status.get("logged_in", False):
        print("\n⚠️  Session non connectée!")
        print("💡 Utilisez: ./ECOSYSTEM/tools/github_session_control.sh demo")
        print("   pour faire la connexion initiale")
        await client.disconnect()
        return
    
    try:
        # Navigation vers les labels
        print("\n📍 Navigation vers les labels...")
        result = await client.goto_url("https://github.com/stephanedenis/PaniniFS/labels")
        print(f"   ✅ {result.get('url', 'N/A')}")
        
        # Création des labels
        print(f"\n🏷️  Création de {len(PANINI_LABELS_COMPLETE)} labels...")
        created_count = 0
        failed_count = 0
        
        for i, label in enumerate(PANINI_LABELS_COMPLETE, 1):
            print(f"\n[{i:2d}/{len(PANINI_LABELS_COMPLETE)}] {label['name']}")
            
            result = await client.create_label(**label)
            if result.get("success"):
                print(f"    ✅ {result.get('message', 'Créé')}")
                created_count += 1
            else:
                error = result.get('error', 'Erreur inconnue')
                if "already exists" in error.lower():
                    print(f"    ⚠️  Existe déjà")
                else:
                    print(f"    ❌ {error}")
                    failed_count += 1
            
            # Pause entre créations
            await asyncio.sleep(1.5)
        
        # Résumé
        print(f"\n📊 RÉSUMÉ:")
        print(f"   ✅ Créés: {created_count}")
        print(f"   ⚠️  Existants: {len(PANINI_LABELS_COMPLETE) - created_count - failed_count}")
        print(f"   ❌ Échecs: {failed_count}")
        
        # Screenshot final
        print("\n📸 Screenshot final...")
        result = await client.take_screenshot("/tmp/github_labels_complete.png")
        if result.get("success"):
            print(f"   ✅ Sauvé: {result.get('screenshot_path')}")
        
        print("\n🎉 Configuration GitHub terminée!")
        print("🔗 Voir: https://github.com/stephanedenis/PaniniFS/labels")
        
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé...")
    except Exception as e:
        print(f"\n🚨 Erreur: {e}")
    
    finally:
        await client.disconnect()

async def quick_issue_management():
    """Gestion rapide des issues"""
    client = GitHubSessionClient()
    
    if not await client.connect():
        return
    
    print("📝 GESTION RAPIDE DES ISSUES")
    print("=" * 30)
    
    # Navigation vers les issues
    await client.goto_url("https://github.com/stephanedenis/PaniniFS/issues")
    
    # Screenshot
    await client.take_screenshot("/tmp/github_issues.png")
    print("📸 Screenshot: /tmp/github_issues.png")
    
    await client.disconnect()

async def monitoring_session():
    """Monitoring de la session"""
    client = GitHubSessionClient()
    
    if not await client.connect():
        return
    
    print("📊 MONITORING SESSION GITHUB")
    print("=" * 30)
    
    status = await client.get_status()
    print(f"🌐 URL actuelle: {status.get('url', 'N/A')}")
    print(f"📰 Titre: {status.get('title', 'N/A')}")
    print(f"🔐 Connecté: {status.get('logged_in', False)}")
    print(f"⏱️  Durée session: {status.get('session_duration', 'N/A')}")
    
    await client.disconnect()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "setup":
            asyncio.run(setup_complete_github_project())
        elif command == "issues":
            asyncio.run(quick_issue_management())
        elif command == "monitor":
            asyncio.run(monitoring_session())
        else:
            print(f"❌ Commande inconnue: {command}")
    else:
        print("🎭 UTILISATION PRATIQUE GITHUB SESSION")
        print("Usage:")
        print("  python3 github_practical_usage.py setup    # Configuration complète")
        print("  python3 github_practical_usage.py issues   # Gestion issues")
        print("  python3 github_practical_usage.py monitor  # Monitoring session")
        print("")
        print("Prérequis:")
        print("  1. ./ECOSYSTEM/tools/github_session_control.sh start")
        print("  2. ./ECOSYSTEM/tools/github_session_control.sh demo  (première fois)")
        print("  3. python3 github_practical_usage.py setup")
