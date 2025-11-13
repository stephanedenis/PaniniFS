# 🎨 Panini-FS Web UI - Phase 7 Améliorations

## 📋 Vue d'ensemble

Cette phase ajoute des fonctionnalités avancées à l'interface Web pour visualiser et interagir avec la déduplication de contenu en temps réel.

## 🆕 Nouvelles Pages

### 1. 🔍 Deduplication Dashboard (`/dedup`)

**Objectif** : Visualiser les métriques de déduplication en temps réel

**Fonctionnalités** :
- ✅ KPI Cards avec métriques clés
  - Fichiers totaux
  - Taux de déduplication
  - Nombre d'atomes
  - Réutilisation moyenne
- ✅ Graphiques interactifs
  - Bar chart : Comparaison stockage brut vs dédupliqué
  - Pie chart : Distribution atomes uniques vs réutilisés
  - Bar chart : Top 10 atomes les plus réutilisés
- ✅ Table des top atomes
  - Hash, utilisations, taille, économie totale
- ✅ Rafraîchissement automatique (5 secondes)

**Technologies** :
- React + TypeScript
- Recharts pour les graphiques
- Tailwind CSS pour le style
- Lucide React pour les icônes

**Endpoints API requis** :
```
GET /api/dedup/stats
Response:
{
  "total_files": 400360,
  "total_size": 9624887296,
  "total_atoms": 491240,
  "unique_atoms": 126177,
  "dedup_ratio": 0.743,
  "storage_saved": 7149823488,
  "avg_reuse": 3.96,
  "top_atoms": [
    {
      "hash": "63e1de009344...",
      "usage_count": 380,
      "size": 65536
    }
  ]
}
```

---

### 2. 🔬 Atom Explorer (`/atoms`)

**Objectif** : Explorer et rechercher les atomes individuels

**Fonctionnalités** :
- ✅ Recherche par hash (auto-complete)
- ✅ Résultats de recherche avec preview
- ✅ Détails complets de l'atome sélectionné
  - Hash SHA256 complet
  - Statistiques (taille, utilisations, économie)
  - Type d'atome
  - Date de création
  - Liste des fichiers utilisant l'atome
- ✅ Analyse d'impact
  - Économie totale
  - Ratio d'économie
  - Comparaison avec/sans dédup

**Technologies** :
- React + TypeScript
- Lucide React pour les icônes
- Tailwind CSS

**Endpoints API requis** :
```
GET /api/atoms/search?q=<query>
Response:
{
  "atoms": [
    {
      "hash": "63e1de009344...",
      "size": 65536,
      "type": "Container",
      "created_at": "2025-10-31T10:30:00Z",
      "usage_count": 380
    }
  ],
  "total": 1
}

GET /api/atoms/<hash>
Response:
{
  "hash": "63e1de009344...",
  "size": 65536,
  "type": "Container",
  "created_at": "2025-10-31T10:30:00Z",
  "usage_count": 380,
  "files": [
    "/path/to/file1.html",
    "/path/to/file2.html"
  ]
}
```

---

### 3. 📤 File Upload & Analysis (`/upload`)

**Objectif** : Uploader et analyser la décomposition de fichiers

**Fonctionnalités** :
- ✅ Drag & drop interface
- ✅ Sélection multiple de fichiers
- ✅ Preview avant upload
- ✅ Upload et analyse en temps réel
- ✅ Résultats détaillés par fichier
  - Atomes créés vs réutilisés
  - Ratio de déduplication
  - Économie de stockage
  - Temps de traitement
- ✅ Détails des atomes
  - Liste complète des atomes
  - Indication nouveau/réutilisé
  - Nombre de réutilisations
- ✅ Statistiques agrégées
  - Économie totale
  - Déduplication moyenne

**Technologies** :
- React + TypeScript
- File API (drag & drop)
- FormData pour upload
- Lucide React

**Endpoints API requis** :
```
POST /api/files/analyze
Content-Type: multipart/form-data
Body: file=<binary>

Response:
{
  "filename": "example.html",
  "size": 102400,
  "atoms_created": 5,
  "atoms_reused": 8,
  "dedup_ratio": 0.615,
  "storage_saved": 63488,
  "hash": "abc123...",
  "processing_time_ms": 42
}

GET /api/files/<hash>/atoms
Response:
{
  "atoms": [
    {
      "hash": "63e1de009344...",
      "size": 65536,
      "is_new": false,
      "reuse_count": 380
    }
  ]
}
```

---

## 🛠️ Installation des dépendances

### Bibliothèques requises

```bash
cd panini-fs-web-ui

# Recharts pour les graphiques
npm install recharts

# Lucide React pour les icônes
npm install lucide-react

# Types
npm install --save-dev @types/recharts
```

### Packages déjà installés
- React 18
- TypeScript
- Tailwind CSS
- Vite

---

## 🔌 Intégration avec l'API Backend

### 1. Ajouter les nouveaux endpoints dans `crates/panini-api/src/routes.rs`

```rust
use axum::{
    routing::{get, post},
    Router,
};

pub fn create_routes() -> Router {
    Router::new()
        // Endpoints existants...
        
        // Nouveaux endpoints Phase 7
        .route("/api/dedup/stats", get(handlers::get_dedup_stats))
        .route("/api/atoms/search", get(handlers::search_atoms))
        .route("/api/atoms/:hash", get(handlers::get_atom_details))
        .route("/api/files/analyze", post(handlers::analyze_file))
        .route("/api/files/:hash/atoms", get(handlers::get_file_atoms))
}
```

### 2. Implémenter les handlers dans `crates/panini-api/src/handlers.rs`

```rust
use axum::{
    extract::{Path, Query, Multipart},
    Json,
};
use serde::{Deserialize, Serialize};

#[derive(Serialize)]
pub struct DedupStats {
    total_files: usize,
    total_size: u64,
    total_atoms: usize,
    unique_atoms: usize,
    dedup_ratio: f64,
    storage_saved: u64,
    avg_reuse: f64,
    top_atoms: Vec<TopAtom>,
}

#[derive(Serialize)]
pub struct TopAtom {
    hash: String,
    usage_count: usize,
    size: u64,
}

pub async fn get_dedup_stats() -> Json<DedupStats> {
    // TODO: Implémenter calcul stats depuis CAS
    Json(DedupStats {
        total_files: 400360,
        total_size: 9624887296,
        total_atoms: 491240,
        unique_atoms: 126177,
        dedup_ratio: 0.743,
        storage_saved: 7149823488,
        avg_reuse: 3.96,
        top_atoms: vec![],
    })
}

#[derive(Deserialize)]
pub struct SearchQuery {
    q: String,
}

pub async fn search_atoms(Query(params): Query<SearchQuery>) -> Json<AtomSearchResult> {
    // TODO: Implémenter recherche dans index CAS
    Json(AtomSearchResult {
        atoms: vec![],
        total: 0,
    })
}

pub async fn get_atom_details(Path(hash): Path<String>) -> Json<AtomDetails> {
    // TODO: Récupérer détails atome depuis CAS
    Json(AtomDetails {
        hash,
        size: 0,
        atom_type: "Container".to_string(),
        created_at: chrono::Utc::now().to_rfc3339(),
        usage_count: 0,
        files: vec![],
    })
}

pub async fn analyze_file(mut multipart: Multipart) -> Json<AnalysisResult> {
    // TODO: Traiter upload et analyser décomposition
    while let Some(field) = multipart.next_field().await.unwrap() {
        let name = field.name().unwrap().to_string();
        let data = field.bytes().await.unwrap();
        
        // Décomposer en atomes
        // Calculer stats
    }
    
    Json(AnalysisResult {
        filename: "example.txt".to_string(),
        size: 0,
        atoms_created: 0,
        atoms_reused: 0,
        dedup_ratio: 0.0,
        storage_saved: 0,
        hash: "".to_string(),
        processing_time_ms: 0,
    })
}
```

---

## 🎨 Mise à jour du routing

### `src/App.tsx`

```tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import DeduplicationDashboard from './pages/DeduplicationDashboard';
import AtomExplorer from './pages/AtomExplorer';
import FileUploadAnalysis from './pages/FileUploadAnalysis';
import ConceptsPage from './pages/ConceptsPage';
import TimelinePage from './pages/TimelinePage';
import SnapshotsPage from './pages/SnapshotsPage';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/dedup" element={<DeduplicationDashboard />} />
          <Route path="/atoms" element={<AtomExplorer />} />
          <Route path="/upload" element={<FileUploadAnalysis />} />
          <Route path="/concepts" element={<ConceptsPage />} />
          <Route path="/timeline" element={<TimelinePage />} />
          <Route path="/snapshots" element={<SnapshotsPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
```

### Mise à jour du menu dans `components/Layout.tsx`

```tsx
const menuItems = [
  { name: 'Dashboard', icon: Home, path: '/dashboard' },
  { name: 'Déduplication', icon: BarChart3, path: '/dedup' }, // NEW
  { name: 'Atom Explorer', icon: Search, path: '/atoms' },    // NEW
  { name: 'Upload', icon: Upload, path: '/upload' },          // NEW
  { name: 'Concepts', icon: Layers, path: '/concepts' },
  { name: 'Timeline', icon: Clock, path: '/timeline' },
  { name: 'Snapshots', icon: Camera, path: '/snapshots' },
];
```

---

## 🚀 Démarrage

```bash
# Terminal 1: Backend API
cd /home/stephane/GitHub/Panini-FS
cargo run --bin panini-api

# Terminal 2: Frontend
cd panini-fs-web-ui
npm install
npm run dev
```

Accéder à : `http://localhost:5173`

---

## ✅ Checklist de développement

### Phase 7.1 : Deduplication Dashboard
- [x] Créer composant React `DeduplicationDashboard.tsx`
- [x] Intégrer Recharts
- [x] KPI Cards (4 métriques)
- [x] Graphiques (bar, pie, line)
- [x] Table top atomes
- [x] Rafraîchissement auto
- [ ] Implémenter endpoint API `/api/dedup/stats`
- [ ] Connecter au vrai CAS backend
- [ ] Tests

### Phase 7.2 : Atom Explorer
- [x] Créer composant React `AtomExplorer.tsx`
- [x] Interface de recherche
- [x] Résultats avec preview
- [x] Panel de détails
- [x] Liste fichiers
- [x] Analyse d'impact
- [ ] Implémenter endpoints API search + details
- [ ] Connecter au CAS backend
- [ ] Tests

### Phase 7.3 : File Upload & Analysis
- [x] Créer composant React `FileUploadAnalysis.tsx`
- [x] Drag & drop zone
- [x] File preview
- [x] Upload progress
- [x] Résultats détaillés
- [x] Statistiques agrégées
- [ ] Implémenter endpoint API `/api/files/analyze`
- [ ] Traitement multipart/form-data
- [ ] Décomposition en atomes
- [ ] Calcul stats dédup
- [ ] Tests

### Phase 7.4 : Intégration
- [ ] Mettre à jour `App.tsx` avec nouvelles routes
- [ ] Mettre à jour `Layout.tsx` avec menu
- [ ] Tests end-to-end
- [ ] Documentation utilisateur
- [ ] Screenshots

---

## 📊 Métriques de succès

- ✅ **3 nouvelles pages** créées et fonctionnelles
- ✅ **5 nouveaux endpoints API** spécifiés
- ⏳ **Visualisations interactives** avec Recharts
- ⏳ **Upload temps réel** avec analyse
- ⏳ **Rafraîchissement auto** toutes les 5s
- ⏳ **Performance** : < 2s pour analyser un fichier
- ⏳ **UX** : Interface intuitive et responsive

---

## 🎯 Prochaines étapes

1. **Backend** : Implémenter les 5 nouveaux endpoints
2. **Tests** : Valider avec données réelles (400K+ fichiers)
3. **Optimisation** : Cache pour stats fréquemment accédées
4. **Documentation** : Guide utilisateur avec screenshots
5. **Phase 8** : FUSE filesystem

---

**Créé le** : 31 octobre 2025  
**Version** : Panini-FS 2.0.0 - Phase 7  
**Statut** : 🚧 En développement (Frontend complet, Backend TODO)
