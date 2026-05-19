# 2026-02-21 — Téléchargement dumps Wikipedia complets pour PanLang

- **Host** : hauru
- **Agent** : GitHub Copilot (Claude Opus 4.6)
- **Durée** : ~2h (préparation) + téléchargement background (~1.5h estimé)

## Contexte

PanLang est une langue construite à fondation encyclopédique graduée par l'âge
du locuteur. Pour élaborer cette fondation, il faut un corpus encyclopédique
complet dans les 14 langues supportées par Panini-FS. Le corpus Wikipedia
existant (973 articles, 21 MB, échantillon curé) est insuffisant — il couvre
~0.0015% de Wikipedia.

La machine (hauru) est au repos : 5.9 TB libre, 62 GB RAM (~46 GB dispo),
16 cores Xeon E5-2650, bande passante abondante. Bon moment pour lancer le
téléchargement massif.

## Décisions clés

### Constat → Décision → Impact

1. **Corpus insuffisant** → Télécharger les 14 dumps Wikipedia complets
   (`pages-articles.xml.bz2`) → ~63.6 GB compressé, ~250 GB décompressé,
   ~65M articles

2. **aria2c pour le téléchargement** → Multi-connexion (8 conn/fichier),
   auto-resume, SHA1 vérification → Débit observé ~10-12 MB/s, robuste
   face aux erreurs 503 de Wikimedia

3. **SAX streaming pour l'extraction** → mwparserfromhell + SAX XML parser
   → ~100 MB RAM constant, pas de DOM loading, filtre redirections/stubs

4. **Ordre small-first** → sa (18 MB) → en (23 GB) → Valider le pipeline
   sur les petits dumps avant les gros

5. **Filtrage qualité** → MIN_ARTICLE_BYTES=500, MIN_ARTICLE_WORDS=50,
   namespace 0 uniquement → Exclure stubs, pages maintenance, catégories

## Fichiers créés

| Fichier | Rôle | Lignes |
|---------|------|--------|
| `SANDBOX/dolt-concept-store/wikipedia_dump_downloader.py` | Orchestrateur aria2c : téléchargement, SHA1, resume, progress | ~300 |
| `SANDBOX/dolt-concept-store/wikipedia_dump_extractor.py` | Parseur SAX streaming : XML.bz2 → plaintext NFC | ~380 |

## Dépendances installées

| Paquet | Version | Méthode |
|--------|---------|---------|
| `mwparserfromhell` | 0.7.2 | `pip3 install --user --break-system-packages` |
| `aria2c` | 1.37.0 | `sudo zypper install -y aria2` |

## Dumps Wikipedia — tailles confirmées (curl HEAD)

| Lang | Nom | Taille compressée |
|------|-----|-------------------|
| sa | Sanskrit | 0.01 GB |
| hi | Hindi | 0.21 GB |
| eo | Espéranto | 0.34 GB |
| fi | Finnois | 0.91 GB |
| nl | Néerlandais | 1.85 GB |
| pt | Portugais | 2.39 GB |
| zh | Chinois | 3.03 GB |
| it | Italien | 3.84 GB |
| ja | Japonais | 4.25 GB |
| es | Espagnol | 4.67 GB |
| ru | Russe | 5.41 GB |
| fr | Français | 6.32 GB |
| de | Allemand | 7.22 GB |
| en | Anglais | 23.17 GB |
| **TOTAL** | | **63.62 GB** |

## Tests effectués

- ✅ `wikipedia_dump_downloader.py --status` : affichage correct 14 langues
- ✅ Téléchargement sa (18.6 MB, 5s, 3.6 MB/s) — validé
- ✅ Téléchargement hi (220 MB, 20s, 10.7 MB/s) — validé malgré 503s
- ✅ Téléchargement eo (352 MB, 33s, 10.4 MB/s) — validé
- ✅ Téléchargement fi (938 MB, 87s, 10.8 MB/s) — validé
- 🔄 nl, pt, zh, it, ja, es, ru, fr, de, en — en cours (background)

## Architecture des scripts

### wikipedia_dump_downloader.py
```
DUMPS_DIR = wikipedia_dumps/{lang}/
ARIA2_CONNECTIONS = 8
ARIA2_MAX_CONCURRENT = 3

Commandes:
  --small-first    : tri par taille croissante
  --langs sa hi    : langues spécifiques
  --status         : tableau de progression
  --verify         : vérification SHA1
```

### wikipedia_dump_extractor.py
```
OUTPUT_DIR = wikipedia_fullcorpus/{lang}/
MIN_ARTICLE_BYTES = 500
MIN_ARTICLE_WORDS = 50
ACCEPTED_NAMESPACES = {0}

Pipeline:
  bz2.open() → SAX handler → mwparserfromhell → NFC → plaintext

Filtres:
  - Redirections (#REDIRECT, #WEITERLEITUNG, etc.)
  - Stubs (< 500 bytes ou < 50 mots)
  - Namespaces non-article (File:, Template:, Category:, etc.)
  - Pages maintenance (Portal:, Wikipedia:, etc.)
```

## Prochaines étapes

1. **Attendre fin des téléchargements** (~1h pour les 10 langues restantes)
2. **Vérifier SHA1** : `python3 wikipedia_dump_downloader.py --verify`
3. **Extraire les articles** : `python3 wikipedia_dump_extractor.py --all`
4. **Tester sur sa d'abord** : `python3 wikipedia_dump_extractor.py --lang sa --limit 100`
5. **Intégrer au pipeline Panini-FS** : créer un ingester wikipedia_fullcorpus → seven_layers_engine
6. **Créer l'index PanLang** : mapper articles → atomes → niveaux d'âge
