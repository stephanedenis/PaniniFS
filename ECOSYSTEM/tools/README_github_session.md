# 🎭 GitHub Session Manager - Processus Autonome

Un système de gestion de session GitHub persistante utilisant Playwright et WebSocket, permettant de maintenir une session authentifiée en arrière-plan et d'éviter les re-connexions avec 2FA.

## 🏗️ Architecture

```
┌─────────────────────┐    WebSocket     ┌──────────────────────┐
│  Client Python      │ ◄──────────────► │  Session Manager     │
│  (Votre script)     │   ws://8765      │  (Processus daemon)  │
└─────────────────────┘                  └──────────────────────┘
                                                    │
                                                    ▼
                                         ┌──────────────────────┐
                                         │  Firefox Browser     │
                                         │  (Session GitHub)    │
                                         └──────────────────────┘
```

## 🚀 Démarrage Rapide

### 1. Démarrer le Session Manager

```bash
# Démarrer en arrière-plan
./ECOSYSTEM/tools/github_session_control.sh start

# Vérifier l'état
./ECOSYSTEM/tools/github_session_control.sh status
```

### 2. Première connexion (une seule fois)

```bash
# Lancer la démo pour setup initial
./ECOSYSTEM/tools/github_session_control.sh demo
```

**Processus de connexion :**
1. Firefox s'ouvre automatiquement sur GitHub
2. Connectez-vous manuellement (avec 2FA si nécessaire)
3. Appuyez sur ENTRÉE dans le terminal après connexion
4. La session reste active en permanence !

### 3. Utilisation sans re-connexion

```bash
# Créer des labels rapidement
./ECOSYSTEM/tools/github_session_control.sh labels

# Ou utiliser le client Python directement
python3 ECOSYSTEM/tools/github_session_client.py quick
```

## 📋 Commandes Disponibles

```bash
# Gestion du serveur
./github_session_control.sh start     # Démarrer
./github_session_control.sh stop      # Arrêter  
./github_session_control.sh restart   # Redémarrer
./github_session_control.sh status    # État
./github_session_control.sh logs      # Logs temps réel

# Utilisation
./github_session_control.sh demo      # Première connexion
./github_session_control.sh labels    # Création labels rapide
```

## 🔧 API Client Python

```python
from github_session_client import GitHubSessionClient

async def main():
    client = GitHubSessionClient()
    await client.connect()
    
    # Créer un label
    result = await client.create_label(
        name="🚀 Feature",
        description="Nouvelle fonctionnalité",
        color="2ecc71"
    )
    
    # Naviguer
    await client.goto_url("https://github.com/stephanedenis/PaniniFS/issues")
    
    # Screenshot
    await client.take_screenshot("/tmp/github.png")
    
    await client.disconnect()
```

## 🎯 Avantages

✅ **Session Persistante** : Plus de re-connexion 2FA  
✅ **Processus Autonome** : Fonctionne en arrière-plan  
✅ **API Simple** : Communication WebSocket facile  
✅ **Multi-clients** : Plusieurs scripts peuvent utiliser la même session  
✅ **État Partagé** : Connaît l'URL actuelle et l'état de connexion  
✅ **Robuste** : Gestion d'erreurs et reconnexion automatique  

## 📊 Surveillance

```bash
# État détaillé
./github_session_control.sh status

# Logs en temps réel
./github_session_control.sh logs

# Test de connexion
python3 -c "
import asyncio
import websockets
import json

async def test():
    async with websockets.connect('ws://localhost:8765') as ws:
        await ws.send(json.dumps({'command': 'status'}))
        response = await ws.recv()
        print(json.loads(response))

asyncio.run(test())
"
```

## 🔍 Debugging

### Logs du serveur
```bash
tail -f /tmp/github_session_manager.log
```

### Test de connexion WebSocket
```bash
python3 -c "
import websockets
import asyncio
import json

async def test():
    uri = 'ws://localhost:8765'
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({'command': 'get_page_info'}))
        response = await ws.recv()
        print(json.loads(response))

asyncio.run(test())
"
```

### Vérifier processus
```bash
ps aux | grep github_session_manager
netstat -tlnp | grep 8765
```

## 🛡️ Sécurité

- La session reste locale (localhost:8765)
- Pas de stockage de mots de passe
- Session expiration automatique avec GitHub
- Possibilité d'arrêt immédiat (`./github_session_control.sh stop`)

## 🔄 Workflow Typique

1. **Setup initial** (une fois) :
   ```bash
   ./github_session_control.sh start
   ./github_session_control.sh demo  # Connexion manuelle
   ```

2. **Utilisation quotidienne** :
   ```bash
   ./github_session_control.sh status  # Vérifier
   ./github_session_control.sh labels  # Créer labels
   # Ou votre propre script Python
   ```

3. **Maintenance** :
   ```bash
   ./github_session_control.sh restart  # Si problème
   ./github_session_control.sh logs     # Debugging
   ```

## 📝 Personnalisation

### Ajouter des actions personnalisées

Modifiez `github_session_manager.py` dans la méthode `execute_github_action()` :

```python
elif action_type == "create_issue":
    return await self.create_issue(action_data["issue"])
elif action_type == "assign_labels":
    return await self.assign_labels_to_issue(action_data)
```

### Configuration

Variables dans `github_session_manager.py` :
- `port = 8765` : Port WebSocket
- `slow_mo = 500` : Vitesse Playwright
- `timeout = 30000` : Timeouts par défaut

## 🚨 Dépannage

**Serveur ne démarre pas :**
```bash
source venv_playwright/bin/activate
pip install websockets playwright
```

**Session expirée :**
```bash
./github_session_control.sh restart
./github_session_control.sh demo  # Re-connexion
```

**Port occupé :**
```bash
lsof -ti:8765 | xargs kill -9
./github_session_control.sh start
```

Ce système permet de maintenir une session GitHub active en permanence, éliminant le besoin de re-saisir les codes 2FA à chaque opération ! 🎉
