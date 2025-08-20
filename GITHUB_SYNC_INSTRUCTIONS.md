# 🔐 CONFIGURATION TOKEN GITHUB POUR SYNCHRONISATION

Pour synchroniser tous vos projets PaniniFS vers GitHub :

## 1. Créer un Personal Access Token GitHub

1. Allez sur : https://github.com/settings/tokens
2. Cliquez "Generate new token (classic)"
3. Nom : "PaniniFS Ecosystem Sync"
4. Scopes requis :
   - ✅ `repo` (accès complet aux repos)
   - ✅ `workflow` (pour les GitHub Actions)
   - ✅ `admin:repo_hook` (webhooks si nécessaire)

## 2. Configurer le token en local

```bash
# Ajouter au trousseau (sécurisé)
export GITHUB_TOKEN="ghp_votre_token_ici"

# Ou créer un fichier de config temporaire
echo "export GITHUB_TOKEN=ghp_votre_token_ici" > ~/.github_token
source ~/.github_token
```

## 3. Exécuter la synchronisation

```bash
cd ~/GitHub/PaniniFS-1
./sync_paninifs_ecosystem.sh
```

## 4. Nettoyer après usage

```bash
unset GITHUB_TOKEN
rm -f ~/.github_token
```

## Alternative : Synchronisation manuelle

Si vous préférez contrôler repo par repo :

```bash
cd ~/GitHub/PaniniFS-AutonomousMissions
git remote add origin https://github.com/stephanedenis/PaniniFS-AutonomousMissions.git
git push -u origin main
```

---

🎯 **Une fois synchronisé, vous aurez tout l'écosystème PaniniFS visible sur GitHub !**
