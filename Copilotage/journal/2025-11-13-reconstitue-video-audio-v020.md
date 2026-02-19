# 📓 Journal reconstitué — 2025-11-13

**Host**: hauru
**Source**: Reconstitué depuis `git log` le 2026-02-18
**Auteur commits**: Stéphane Denis

> ⚠️ Ce journal a été reconstitué rétrospectivement depuis l'historique Git.
> Un journal automatique existe : `copilotage/journal/JOURNAL_AUTO_2025-11-13_hauru.md`

---

## Contexte

Journée intensive de développement PaniniFS core : support vidéo multi-format,
parsing avancé, fingerprinting audio, web UI. Version 0.2.0 → 0.2.2.

## Décisions clés

### 1. Version 0.2.0 — Support vidéo multi-format

PaniniFS gère désormais le chunking de fichiers vidéo avec extraction de
keyframes et support EBML VINT (Matroska/WebM).

### 2. Web UI de visualisation de déduplication

Interface web pour visualiser les résultats de déduplication sémantique.

### 3. Parsing vidéo avancé — Keyframes + EBML VINT

Extraction des keyframes vidéo et implémentation du parsing EBML Variable
Integer (format Matroska).

### 4. Audio fingerprinting type Shazam

Implémentation d'un système de fingerprinting audio inspiré de Shazam pour
la déduplication de contenus audio.

### 5. Désactivation des workflows GitHub problématiques

Tous les workflows CI sont désactivés (`.disabled`) car ils échouaient
systématiquement après les réorganisations de septembre. 25 workflows
concernés.

## Fichiers modifiés

- `src/panini_fs_chunker.py` — Support vidéo multi-format
- `web-ui/` — Interface de visualisation déduplication
- `src/` — Parsing EBML, keyframes, fingerprinting audio
- `.github/workflows/*.disabled` — 25 workflows désactivés
- `copilotage/journal/JOURNAL_AUTO_2025-11-13_hauru.md` — Journal auto

## Tests effectués

- Version 0.2.0 puis 0.2.2 taggée
- Fonctionnalités vidéo et audio testées localement

## Prochaines étapes

- Pause de ~3 mois (aucun commit entre nov 13 et fév 16)
- Reprendre avec le concept store Dolt
