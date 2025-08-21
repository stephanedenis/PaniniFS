#!/usr/bin/env python3
"""
🎭 CLIENT GITHUB SESSION - COMMUNICATION WEBSOCKET
Contrôle le processus Playwright autonome via WebSocket
"""

import asyncio
import websockets
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class GitHubSessionClient:
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.websocket = None
        self.connected = False
    
    async def connect(self):
        """Se connecter au serveur WebSocket"""
        try:
            self.websocket = await websockets.connect(f"ws://{self.host}:{self.port}")
            self.connected = True
            logger.info("✅ Connecté au GitHub Session Manager")
            return True
        except Exception as e:
            logger.error(f"🚨 Erreur connexion: {e}")
            return False
    
    async def disconnect(self):
        """Se déconnecter du serveur"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            logger.info("🔌 Déconnecté du serveur")
    
    async def send_command(self, command: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Envoyer une commande au serveur"""
        if not self.connected:
            return {"success": False, "error": "Not connected to server"}
        
        message = {"command": command}
        if data:
            message["data"] = data
        
        try:
            await self.websocket.send(json.dumps(message))
            response = await self.websocket.recv()
            return json.loads(response)
        except Exception as e:
            logger.error(f"🚨 Erreur envoi commande: {e}")
            return {"success": False, "error": str(e)}
    
    async def initialize_session(self):
        """Initialiser la session browser"""
        return await self.send_command("initialize")
    
    async def start_login(self):
        """Démarrer le processus de login"""
        return await self.send_command("login")
    
    async def confirm_login(self):
        """Confirmer que le login est terminé"""
        return await self.send_command("login_complete")
    
    async def check_login_status(self):
        """Vérifier l'état du login"""
        return await self.send_command("check_login")
    
    async def get_status(self):
        """Obtenir l'état de la session"""
        return await self.send_command("status")
    
    async def create_label(self, name: str, description: str = "", color: str = "65c7a0"):
        """Créer un label GitHub"""
        label_data = {
            "name": name,
            "description": description,
            "color": color
        }
        return await self.send_command("action", {
            "type": "create_label",
            "label": label_data
        })
    
    async def goto_url(self, url: str):
        """Naviguer vers une URL"""
        return await self.send_command("action", {
            "type": "goto_url",
            "url": url
        })
    
    async def take_screenshot(self, path: str = "/tmp/github_session.png"):
        """Prendre un screenshot"""
        return await self.send_command("action", {
            "type": "take_screenshot",
            "path": path
        })
    
    async def shutdown_session(self):
        """Fermer la session"""
        return await self.send_command("shutdown")

# Labels PaniniFS pour test
PANINI_LABELS = [
    {"name": "🎯 Priority", "description": "Tâche prioritaire du projet", "color": "ff4757"},
    {"name": "🚀 Enhancement", "description": "Amélioration du système", "color": "2ecc71"},
    {"name": "🐛 Bug", "description": "Problème à corriger", "color": "e74c3c"},
    {"name": "📚 Documentation", "description": "Mise à jour documentation", "color": "3498db"},
    {"name": "🧪 Testing", "description": "Tests et validation", "color": "9b59b6"},
]

async def demo_session():
    """Démonstration d'utilisation du client"""
    client = GitHubSessionClient()
    
    print("🎭 DÉMONSTRATION GITHUB SESSION CLIENT")
    print("=====================================")
    
    # Connexion
    if not await client.connect():
        print("❌ Impossible de se connecter au serveur")
        return
    
    try:
        # Initialiser le navigateur
        print("\n🚀 Initialisation du navigateur...")
        result = await client.initialize_session()
        print(f"   Résultat: {result}")
        
        # Démarrer le login
        print("\n🔐 Démarrage du processus de login...")
        result = await client.start_login()
        print(f"   Résultat: {result}")
        print("   👆 VEUILLEZ VOUS CONNECTER DANS LE NAVIGATEUR FIREFOX")
        
        # Attendre confirmation
        input("\n⏳ Appuyez sur ENTRÉE après vous être connecté...")
        
        # Confirmer le login
        print("\n✅ Confirmation du login...")
        result = await client.confirm_login()
        print(f"   Résultat: {result}")
        
        # Vérifier l'état
        print("\n📊 État de la session...")
        status = await client.get_status()
        print(f"   URL: {status.get('url', 'N/A')}")
        print(f"   Connecté: {status.get('logged_in', False)}")
        print(f"   Durée: {status.get('session_duration', 'N/A')}")
        
        # Test création d'un label
        print("\n🏷️  Test création label...")
        result = await client.create_label(
            name="🤖 AI-Generated",
            description="Label créé par l'agent AI",
            color="ff6b6b"
        )
        print(f"   Résultat: {result}")
        
        # Screenshot
        print("\n📸 Screenshot de la session...")
        result = await client.take_screenshot("/tmp/github_session_demo.png")
        print(f"   Résultat: {result}")
        
        print("\n✨ Session maintenue en arrière-plan!")
        print("   Vous pouvez maintenant utiliser le client sans re-login")
        
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé...")
    
    finally:
        await client.disconnect()

async def quick_label_creation():
    """Création rapide de labels sans re-login"""
    client = GitHubSessionClient()
    
    if not await client.connect():
        print("❌ Serveur non disponible. Démarrez github_session_manager.py d'abord")
        return
    
    print("🏷️  CRÉATION RAPIDE DE LABELS")
    print("============================")
    
    # Vérifier l'état
    status = await client.get_status()
    if not status.get("logged_in", False):
        print("⚠️  Session non connectée. Utilisez demo_session() d'abord")
        await client.disconnect()
        return
    
    print(f"✅ Session active: {status.get('url', 'N/A')}")
    
    # Créer les labels PaniniFS
    for label in PANINI_LABELS:
        print(f"\n🏷️  Création: {label['name']}")
        result = await client.create_label(**label)
        if result.get("success"):
            print(f"   ✅ {result.get('message', 'Créé')}")
        else:
            print(f"   ❌ {result.get('error', 'Erreur')}")
        
        await asyncio.sleep(2)  # Pause entre labels
    
    await client.disconnect()
    print("\n🎉 Création terminée!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        asyncio.run(quick_label_creation())
    else:
        asyncio.run(demo_session())
