# 🌐 Panini-FS Web Interface

Interface web moderne pour explorer et analyser le système de fichiers Panini-FS.

## 🚀 Démarrage Rapide

### 1. Lancer l'API Panini

```bash
# Depuis la racine du projet
export PANINI_STORAGE=/home/stephane/panini-wikipedia-full
cargo run --release --bin panini-api
```

L'API sera disponible sur `http://localhost:3000`

### 2. Lancer l'interface Web

```bash
# Depuis la racine du projet
./start-web.sh
```

Le site sera disponible sur `http://localhost:5173`

## 📊 Pages Disponibles

### 🏠 Dashboard (`/`)
Vue d'ensemble générale du système avec statistiques en temps réel.

### 📄 Concepts (`/concepts`)
Exploration des concepts et fichiers stockés.

### ⏱️ Timeline (`/timeline`)
Visualisation temporelle des modifications.

### 📸 Snapshots (`/snapshots`)
Gestion des snapshots du système.

### 🔥 Dhātu (`/dhatu`)
Dashboard émotionnel basé sur les 7 émotions primaires de Panksepp.

### 🌐 **Graph Explorer** (`/graph`) ⭐ **NOUVEAU**

**La page principale pour naviguer dans tout le graphe Panini !**

#### Fonctionnalités

##### 📊 Vue Statistiques
- **Total Files**: Nombre total de fichiers ingérés
- **Unique Atoms**: Nombre d'atoms uniques (déduplication)
- **Deduplication Ratio**: Pourcentage d'économie d'espace
- **Storage Saved**: Espace disque économisé

##### 🔍 3 Modes de Visualisation

1. **Atoms Mode** (Par défaut)
   - Liste des atoms les plus partagés
   - Affichage du hash, taille, et nombre d'utilisations
   - Classification "Hot/Warm/Cold" selon la réutilisation
   - Clic sur un atom pour voir les détails

2. **Files Mode**
   - Liste de tous les fichiers ingérés
   - Métadonnées complètes
   - Liens vers les atoms composants
   - Classification émotionnelle (Dhātu)

3. **Network Mode**
   - Visualisation interactive du graphe
   - Connexions atoms ↔ files
   - Navigation par zoom/pan
   - Mise en évidence des clusters

##### 🔎 Recherche Intelligente
- Recherche par hash d'atom
- Recherche par nom de fichier
- Recherche par contenu
- Filtrage en temps réel

##### 📝 Panneau de Détails
Sélection d'un nœud affiche:
- Hash complet
- Taille exacte
- Nombre d'utilisations
- Actions disponibles:
  - **View Content**: Afficher le contenu
  - **Show Connections**: Voir les connexions
  - **Export Data**: Exporter les données

##### 📈 Métriques du Graphe
- **Average Reuse Factor**: Combien de fois chaque atom est réutilisé
- **Total Graph Size**: Taille totale estimée du graphe
- **Efficiency Gain**: Gain d'efficacité par déduplication

## 🎯 Use Cases

### 1. Analyse de Déduplication
Utilisez Graph Explorer pour:
- Identifier les atoms les plus réutilisés
- Comprendre les patterns de duplication
- Optimiser le stockage

### 2. Exploration de Données Wikipedia
Après ingestion Wikipedia:
- Voir quels contenus sont partagés entre langues
- Analyser les concepts universels
- Explorer les profils émotionnels culturels

### 3. Debugging
- Vérifier l'intégrité des atoms
- Tracer les connexions entre fichiers
- Identifier les anomalies

## 🛠️ Développement

### Structure du Projet

```
web-ui/
├── src/
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── ConceptsPage.tsx
│   │   ├── TimelinePage.tsx
│   │   ├── SnapshotsPage.tsx
│   │   ├── DhatuDashboard.tsx
│   │   └── GraphExplorer.tsx    ⭐ NOUVEAU
│   ├── components/
│   │   └── Layout.tsx
│   ├── api/
│   ├── types/
│   └── utils/
├── package.json
└── vite.config.ts
```

### Développement Local

```bash
cd web-ui
npm install
npm run dev
```

### Technologies Utilisées

- **React 18** - Framework UI
- **TypeScript** - Type safety
- **Vite** - Build tool ultra-rapide
- **React Router** - Navigation
- **Tailwind CSS** - Styling
- **Lucide Icons** - Icônes modernes

## 📡 API Endpoints Utilisés

### Deduplication Stats
```
GET http://localhost:3000/api/dedup/stats
```

Retourne:
```json
{
  "total_files": 1470,
  "total_size": 52883058,
  "unique_atoms": 1458,
  "dedup_ratio": 0.008163,
  "storage_saved": 428174,
  "avg_reuse": 1.008,
  "top_atoms": [...]
}
```

### Dhātu Stats
```
GET http://localhost:3000/api/dhatu/stats
```

Retourne:
```json
{
  "total_profiles": 1469,
  "emotion_distribution": {
    "Rage": 590,
    "Play": 393,
    ...
  },
  "average_arousal": 0.173,
  "top_emotions": [...]
}
```

## 🔜 Fonctionnalités Futures

### Graph Explorer Enhancements
- [ ] Visualisation 3D interactive du graphe
- [ ] Export du graphe en GraphML/Neo4j
- [ ] Filtres avancés par taille/usage
- [ ] Timeline de création des atoms
- [ ] Comparaison de plusieurs nœuds
- [ ] Recherche par expression régulière
- [ ] Clustering automatique
- [ ] Heatmap de réutilisation

### Nouvelles Pages
- [ ] Settings (configuration)
- [ ] Analytics (rapports détaillés)
- [ ] Comparisons (diff entre snapshots)
- [ ] Search (recherche globale)

## 📚 Ressources

- [Documentation Panini-FS](../README.md)
- [API Documentation](../docs/API.md)
- [Dhātu Theory](../docs/DHATU.md)
- [Wikipedia Ingestion Guide](../docs/WIKIPEDIA_COMPLETE_GUIDE.md)

## 🤝 Contribution

Pour contribuer au développement de l'interface web:

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 License

MIT License - Voir [LICENSE](../LICENSE) pour plus de détails.

---

**Note**: Cette interface web est optimisée pour les navigateurs modernes (Chrome, Firefox, Safari, Edge).

Pour toute question ou problème, ouvrir une issue sur GitHub.
