#!/usr/bin/env python3
"""
🎭 PLAYWRIGHT SESSION MANAGER - PROCESSUS AUTONOME
Maintient une session GitHub ouverte en permanence
Communication via WebSocket pour éviter les re-connexions
"""

import asyncio
import websockets
import json
import logging
from playwright.async_api import async_playwright
from datetime import datetime

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubSessionManager:
    def __init__(self):
        self.browser = None
        self.page = None
        self.context = None
        self.playwright = None
        self.is_logged_in = False
        self.session_start_time = None
        
    async def initialize_browser(self):
        """Initialiser le navigateur et la session GitHub"""
        logger.info("🚀 Initialisation du navigateur...")
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.firefox.launch(
            headless=False, 
            slow_mo=500,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        
        self.page = await self.context.new_page()
        self.session_start_time = datetime.now()
        
        logger.info("✅ Navigateur initialisé")
        return True
    
    async def login_to_github(self):
        """Se connecter à GitHub (interaction manuelle requise)"""
        if self.is_logged_in:
            logger.info("✅ Déjà connecté à GitHub")
            return True
        
        logger.info("🔐 Connexion à GitHub...")
        await self.page.goto("https://github.com/login")
        await self.page.wait_for_load_state('networkidle', timeout=30000)
        
        logger.info("👤 VEUILLEZ VOUS CONNECTER À GITHUB")
        logger.info("   - Utilisez le navigateur ouvert")
        logger.info("   - Faites votre 2FA si nécessaire")
        logger.info("   - Une fois connecté, envoyez 'login_complete' via WebSocket")
        
        return False  # Sera mis à True via WebSocket
    
    async def check_github_login(self):
        """Vérifier si on est toujours connecté"""
        try:
            await self.page.goto("https://github.com/settings", timeout=10000)
            await self.page.wait_for_load_state('networkidle', timeout=10000)
            
            # Si on arrive sur les settings, on est connecté
            current_url = self.page.url
            if "settings" in current_url:
                self.is_logged_in = True
                logger.info("✅ Session GitHub active")
                return True
            else:
                self.is_logged_in = False
                logger.warning("⚠️  Session GitHub expirée")
                return False
                
        except Exception as e:
            logger.error(f"🚨 Erreur vérification login: {e}")
            self.is_logged_in = False
            return False
    
    async def execute_github_action(self, action_data):
        """Exécuter une action GitHub"""
        if not self.is_logged_in:
            return {"success": False, "error": "Not logged in to GitHub"}
        
        action_type = action_data.get("type")
        
        try:
            if action_type == "create_label":
                return await self.create_label(action_data["label"])
            elif action_type == "goto_url":
                return await self.goto_url(action_data["url"])
            elif action_type == "get_page_info":
                return await self.get_page_info()
            elif action_type == "take_screenshot":
                return await self.take_screenshot(action_data.get("path", "/tmp/github_session.png"))
            else:
                return {"success": False, "error": f"Unknown action: {action_type}"}
                
        except Exception as e:
            logger.error(f"🚨 Erreur action {action_type}: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_label(self, label):
        """Créer un label GitHub"""
        logger.info(f"🏷️  Création label: {label['name']}")
        
        # Navigation vers les labels
        await self.page.goto("https://github.com/stephanedenis/PaniniFS/labels")
        await self.page.wait_for_load_state('networkidle', timeout=15000)
        
        # Cliquer New label
        await self.page.click("text=New label")
        await self.page.wait_for_load_state('networkidle', timeout=10000)
        
        # Remplir nom
        name_input = await self.page.wait_for_selector("input[placeholder='Label name']", timeout=5000)
        await name_input.fill(label['name'])
        await asyncio.sleep(0.1)  # Pause réduite
        
        # Remplir description avec le bon placeholder
        description_input = await self.page.wait_for_selector("input[placeholder*='optionally add a description']", timeout=5000)
        if description_input and label.get('description'):
            await description_input.fill(label['description'])
            await asyncio.sleep(0.1)  # Pause réduite
        
        # Remplir couleur - chercher l'input avec # préfixé
        color = label.get('color', '65c7a0').replace('#', '')
        color_input = await self.page.query_selector("input[value^='#']")
        if color_input:
            await color_input.clear()
            await color_input.fill(f"#{color}")
            await asyncio.sleep(0.1)  # Pause réduite
        
        # Sauvegarder
        await self.page.click("button:has-text('Create label')")
        await self.page.wait_for_load_state('networkidle', timeout=10000)
        
        logger.info(f"✅ Label '{label['name']}' créé")
        return {"success": True, "message": f"Label '{label['name']}' créé"}
    
    async def goto_url(self, url):
        """Naviguer vers une URL"""
        await self.page.goto(url)
        await self.page.wait_for_load_state('networkidle', timeout=30000)
        return {"success": True, "url": self.page.url}
    
    async def get_page_info(self):
        """Récupérer infos de la page actuelle"""
        if not self.page:
            return {
                "success": True,
                "url": "Not initialized",
                "title": "Not initialized",
                "logged_in": self.is_logged_in,
                "session_duration": str(datetime.now() - self.session_start_time) if self.session_start_time else None
            }
        
        return {
            "success": True,
            "url": self.page.url,
            "title": await self.page.title(),
            "logged_in": self.is_logged_in,
            "session_duration": str(datetime.now() - self.session_start_time) if self.session_start_time else None
        }
    
    async def take_screenshot(self, path):
        """Prendre un screenshot"""
        await self.page.screenshot(path=path)
        return {"success": True, "screenshot_path": path}
    
    async def cleanup(self):
        """Nettoyer les ressources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("🔚 Session fermée")

# WebSocket Server pour communiquer avec le session manager
class GitHubSessionServer:
    def __init__(self):
        self.session_manager = GitHubSessionManager()
        self.connected_clients = set()
    
    async def register_client(self, websocket):
        """Enregistrer un nouveau client"""
        self.connected_clients.add(websocket)
        logger.info(f"📱 Client connecté: {websocket.remote_address}")
        
        # Envoyer l'état actuel
        status = await self.session_manager.get_page_info()
        await websocket.send(json.dumps({
            "type": "status_update",
            "data": status
        }))
    
    async def unregister_client(self, websocket):
        """Désenregistrer un client"""
        self.connected_clients.discard(websocket)
        logger.info(f"📱 Client déconnecté: {websocket.remote_address}")
    
    async def handle_message(self, websocket, message):
        """Traiter un message reçu"""
        try:
            data = json.loads(message)
            command = data.get("command")
            
            logger.info(f"📨 Commande reçue: {command}")
            
            if command == "initialize":
                await self.session_manager.initialize_browser()
                response = {"success": True, "message": "Browser initialized"}
                
            elif command == "login":
                await self.session_manager.login_to_github()
                response = {"success": True, "message": "Login process started"}
                
            elif command == "login_complete":
                self.session_manager.is_logged_in = True
                logger.info("✅ Login confirmé par l'utilisateur")
                response = {"success": True, "message": "Login confirmed"}
                
            elif command == "check_login":
                result = await self.session_manager.check_github_login()
                response = {"success": True, "logged_in": result}
                
            elif command == "action":
                result = await self.session_manager.execute_github_action(data.get("data", {}))
                response = result
                
            elif command == "status":
                result = await self.session_manager.get_page_info()
                response = result
                
            elif command == "shutdown":
                await self.session_manager.cleanup()
                response = {"success": True, "message": "Session closed"}
                
            else:
                response = {"success": False, "error": f"Unknown command: {command}"}
            
            await websocket.send(json.dumps(response))
            
        except Exception as e:
            logger.error(f"🚨 Erreur traitement message: {e}")
            await websocket.send(json.dumps({
                "success": False, 
                "error": str(e)
            }))
    
    async def handle_client(self, websocket):
        """Gérer une connexion client"""
        await self.register_client(websocket)
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister_client(websocket)

async def main():
    """Démarrer le serveur WebSocket"""
    server = GitHubSessionServer()
    
    logger.info("🚀 DÉMARRAGE GITHUB SESSION MANAGER")
    logger.info("📡 WebSocket Server sur ws://localhost:8765")
    logger.info("🎭 Prêt à maintenir la session GitHub")
    
    start_server = websockets.serve(
        server.handle_client, 
        "localhost", 
        8765,
        ping_interval=30,
        ping_timeout=10
    )
    
    try:
        await start_server
        logger.info("✅ Serveur WebSocket démarré")
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt du serveur...")
        await server.session_manager.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
