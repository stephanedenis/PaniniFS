# Test Wikipedia avec Dolt Concept Store

## ✅ Statut de l'installation

- **Dolt v1.82.1**: ✅ Installé
- **Base initialisée**: ✅ `panini-concepts-db/`
- **Corpus test**: ✅ 35 phrases en 7 langues (100% déduplication)

## 🚀 Tester avec Wikipedia

### Option 1: Petit test (recommandé pour commencer)

```bash
# 1000 phrases par langue (rapide, ~5 minutes)
python3 wikipedia_corpus_loader.py --languages fr,en,es --limit 1000
```

### Option 2: Test moyen

```bash
# 5000 phrases par langue (~20 minutes)
python3 wikipedia_corpus_loader.py --languages fr,en,es,ar --limit 5000
```

### Option 3: Test complet (7 langues)

```bash
# Toutes les langues supportées
python3 wikipedia_corpus_loader.py \
    --languages fr,en,es,de,ar,zh,ja \
    --limit 10000
```

## 📊 Analyse des résultats

### Voir les clusters multilingues

```bash
cd panini-concepts-db
dolt sql -q "SELECT * FROM semantic_deduplication LIMIT 10"
```

### Statistiques de déduplication

```bash
dolt sql -q "
    SELECT 
        COUNT(*) as total_mappings,
        COUNT(DISTINCT semantic_hash) as unique_concepts,
        COUNT(DISTINCT language) as languages
    FROM semantic_mappings
"
```

### Top concepts par nombre de langues

```bash
dolt sql -q "
    SELECT 
        semantic_hash,
        COUNT(DISTINCT language) as lang_count,
        GROUP_CONCAT(DISTINCT language) as languages
    FROM semantic_mappings
    GROUP BY semantic_hash
    HAVING lang_count > 3
    ORDER BY lang_count DESC
    LIMIT 20
"
```

### Distribution des dhātu

```bash
dolt sql -q "SELECT * FROM dhatu_statistics"
```

## 🔍 Explorer le versioning Git-like

### Voir l'historique

```bash
cd panini-concepts-db
dolt log
```

### Créer une branche expérimentale

```bash
dolt branch experimental
dolt checkout experimental

# Ajouter plus de données...
python3 ../wikipedia_corpus_loader.py --languages de,it --limit 500

# Comparer avec main
dolt diff main
```

### Merger si satisfait

```bash
dolt checkout main
dolt merge experimental
```

## 🎯 Ce qui a été validé

✅ **Déduplication cross-langue**: 5 concepts testés avec 7 langues → 100% unification  
✅ **Versioning Git-like**: Commits, branches, diffs  
✅ **SQL sur signatures**: Requêtes analytiques sur dhātu  
✅ **Notifications système**: KDE Connect + sons lors des interventions  

## 📝 Prochaines étapes

1. **Analyzer Rust réel**: Remplacer `simulate_dhatu_analysis()` par le vrai analyzer
2. **CI/CD Integration**: Bridge automatique Rust ↔ Dolt
3. **Corpus Wikipedia complet**: Millions de phrases, toutes langues
4. **Recherche sémantique**: Query par signature dhātu

## 🔧 Debug

### Problème de permissions
```bash
chmod +x *.sh *.py
```

### Réinitialiser la base
```bash
rm -rf panini-concepts-db
python3 init_dolt.py
```

### Voir les logs Dolt
```bash
cd panini-concepts-db
dolt log --oneline
dolt show <commit-hash>
```

## 📚 Documentation complète

Voir [README.md](README.md) pour l'architecture détaillée du Dolt Concept Store.
