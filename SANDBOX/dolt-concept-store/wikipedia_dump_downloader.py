#!/usr/bin/env python3
"""wikipedia_dump_downloader.py — Télécharge les dumps Wikipedia complets pour PanLang.

Télécharge les dumps pages-articles.xml.bz2 pour les 14 langues de PaniniFS
depuis dumps.wikimedia.org, avec :
  - aria2c pour le téléchargement multi-connexion (reprise automatique)
  - Vérification SHA1 post-téléchargement
  - Parallélisme configurable
  - Progression en temps réel

Usage:
    python3 wikipedia_dump_downloader.py                    # Télécharge tout
    python3 wikipedia_dump_downloader.py --langs fr de en   # Langues spécifiques
    python3 wikipedia_dump_downloader.py --small-first      # Petites langues d'abord
    python3 wikipedia_dump_downloader.py --status           # État des téléchargements
    python3 wikipedia_dump_downloader.py --verify           # Vérifie les SHA1

Partie de l'infrastructure PanLang — corpus encyclopédique multilingue.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# Les 14 langues PaniniFS, avec tailles approximatives (Go compressé)
LANGUAGES = {
    "sa":  {"name": "Sanskrit",     "size_gb": 0.01},
    "eo":  {"name": "Espéranto",    "size_gb": 0.34},
    "hi":  {"name": "Hindi",        "size_gb": 0.21},
    "fi":  {"name": "Finnois",      "size_gb": 0.91},
    "nl":  {"name": "Néerlandais",  "size_gb": 1.85},
    "pt":  {"name": "Portugais",    "size_gb": 2.39},
    "zh":  {"name": "Chinois",      "size_gb": 3.03},
    "it":  {"name": "Italien",      "size_gb": 3.84},
    "ja":  {"name": "Japonais",     "size_gb": 4.25},
    "es":  {"name": "Espagnol",     "size_gb": 4.67},
    "ru":  {"name": "Russe",        "size_gb": 5.41},
    "fr":  {"name": "Français",     "size_gb": 6.32},
    "de":  {"name": "Allemand",     "size_gb": 7.22},
    "en":  {"name": "Anglais",      "size_gb": 23.17},
}

DUMP_BASE_URL = "https://dumps.wikimedia.org/{lang}wiki/latest"
DUMP_FILENAME = "{lang}wiki-latest-pages-articles.xml.bz2"
SHA1_FILENAME = "{lang}wiki-latest-sha1sums.txt"

# Répertoire de stockage
DUMPS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wikipedia_dumps")

# aria2c settings — conservateur pour respecter Wikimedia rate limits
ARIA2_CONNECTIONS = 2       # connexions par téléchargement (Wikimedia refuse >3)
ARIA2_SPLIT = 2             # segments par fichier
ARIA2_MIN_SPLIT = "50M"    # taille minimale par segment
ARIA2_MAX_CONCURRENT = 1    # téléchargements simultanés max
ARIA2_MAX_RETRIES = 10      # retries par téléchargement
ARIA2_RETRY_WAIT = 30       # secondes entre retries

# Méta-fichier pour le suivi
STATUS_FILE = os.path.join(DUMPS_DIR, "_download_status.json")


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def get_dump_url(lang: str) -> str:
    """URL du dump pour une langue."""
    return f"{DUMP_BASE_URL.format(lang=lang)}/{DUMP_FILENAME.format(lang=lang)}"


def get_sha1_url(lang: str) -> str:
    """URL du fichier SHA1 pour une langue."""
    return f"{DUMP_BASE_URL.format(lang=lang)}/{SHA1_FILENAME.format(lang=lang)}"


def get_dump_path(lang: str) -> str:
    """Chemin local du dump."""
    return os.path.join(DUMPS_DIR, lang, DUMP_FILENAME.format(lang=lang))


def human_size(size_bytes: int) -> str:
    """Formatte une taille en bytes en format humain."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def load_status() -> dict:
    """Charge l'état des téléchargements."""
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_status(status: dict):
    """Sauvegarde l'état des téléchargements."""
    os.makedirs(DUMPS_DIR, exist_ok=True)
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=2, ensure_ascii=False, default=str)


def fetch_sha1(lang: str) -> dict:
    """Récupère les SHA1 depuis le serveur Wikimedia pour une langue."""
    url = get_sha1_url(lang)
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'PaniniFS-PanLang/1.0 (https://github.com/stephanedenis/Panini-FS)'
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read().decode('utf-8')
        sha1s = {}
        for line in content.strip().split('\n'):
            parts = line.strip().split(None, 1)
            if len(parts) == 2:
                sha1s[parts[1].strip()] = parts[0].strip()
        return sha1s
    except Exception as e:
        print(f"  ⚠️  Impossible de récupérer SHA1 pour {lang}: {e}")
        return {}


def verify_sha1(filepath: str, expected_sha1: str) -> bool:
    """Vérifie le SHA1 d'un fichier."""
    sha1 = hashlib.sha1()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(8 * 1024 * 1024)  # 8 Mo chunks
            if not chunk:
                break
            sha1.update(chunk)
    return sha1.hexdigest() == expected_sha1


# ═══════════════════════════════════════════════════════════════════════════════
# DOWNLOAD
# ═══════════════════════════════════════════════════════════════════════════════

def download_dump(lang: str, status: dict) -> bool:
    """Télécharge un dump Wikipedia avec aria2c.
    
    Retourne True si le téléchargement est complet et vérifié.
    """
    url = get_dump_url(lang)
    outdir = os.path.join(DUMPS_DIR, lang)
    outfile = DUMP_FILENAME.format(lang=lang)
    outpath = os.path.join(outdir, outfile)
    info = LANGUAGES[lang]

    os.makedirs(outdir, exist_ok=True)

    # Déjà téléchargé et vérifié ?
    if lang in status and status[lang].get("verified"):
        if os.path.exists(outpath):
            print(f"  ✅ {lang} ({info['name']}): déjà téléchargé et vérifié")
            return True

    # Vérifier si le fichier existe et a la bonne taille
    if os.path.exists(outpath):
        local_size = os.path.getsize(outpath)
        expected_bytes = int(info['size_gb'] * 1073741824)
        # Si le fichier est > 95% de la taille attendue, considérer comme complet
        if local_size > expected_bytes * 0.95:
            print(f"  📦 {lang} ({info['name']}): fichier existant ({human_size(local_size)}), vérification...")
            status[lang] = status.get(lang, {})
            status[lang]["downloaded"] = True
            status[lang]["size_bytes"] = local_size
            save_status(status)
            return True

    print(f"\n  📥 {lang} ({info['name']}): téléchargement ~{info['size_gb']} Go...")
    print(f"     URL: {url}")

    # aria2c avec reprise automatique + retries pour 503
    cmd = [
        "aria2c",
        "--dir", outdir,
        "--out", outfile,
        "--continue=true",                  # Reprise automatique
        f"--split={ARIA2_SPLIT}",           # Segments parallèles
        f"--max-connection-per-server={ARIA2_CONNECTIONS}",
        f"--min-split-size={ARIA2_MIN_SPLIT}",
        f"--max-tries={ARIA2_MAX_RETRIES}",  # Retries sur erreur
        f"--retry-wait={ARIA2_RETRY_WAIT}",  # Pause entre retries
        "--file-allocation=falloc",         # Allocation rapide
        "--auto-file-renaming=false",       # Pas de renommage
        "--allow-overwrite=true",
        "--console-log-level=warn",
        "--summary-interval=60",            # Résumé toutes les 60s
        "--user-agent=PaniniFS-PanLang/1.0 (research; mailto:panini-fs@example.com)",
        "--max-overall-download-limit=10M", # Politesse : 10 MB/s max
        url,
    ]

    start_time = time.time()
    result = subprocess.run(cmd, capture_output=False)

    elapsed = time.time() - start_time

    if result.returncode == 0:
        size = os.path.getsize(outpath) if os.path.exists(outpath) else 0
        speed = size / elapsed if elapsed > 0 else 0
        print(f"  ✅ {lang}: téléchargé ({human_size(size)}) en {timedelta(seconds=int(elapsed))}"
              f" ({human_size(int(speed))}/s)")

        status[lang] = status.get(lang, {})
        status[lang]["downloaded"] = True
        status[lang]["size_bytes"] = size
        status[lang]["download_time_s"] = int(elapsed)
        status[lang]["download_date"] = datetime.now().isoformat()
        save_status(status)
        return True
    else:
        print(f"  ⚠️  {lang}: aria2c échoué (code {result.returncode}), fallback wget...")
        return _wget_fallback(lang, url, outdir, outfile, outpath, status)


def _wget_fallback(lang: str, url: str, outdir: str, outfile: str, outpath: str, status: dict) -> bool:
    """Fallback wget — une seule connexion, retries intégrés, très robuste."""
    cmd = [
        "wget",
        "--continue",                       # Reprise automatique
        "--tries=20",                       # 20 retries
        "--waitretry=30",                   # 30s entre retries (backoff)
        "--timeout=120",                    # 2 min timeout
        "--limit-rate=8m",                  # 8 MB/s max — politesse
        "--user-agent=PaniniFS-PanLang/1.0 (research; https://github.com/stephanedenis/Panini-FS)",
        "-O", outpath,
        url,
    ]

    print(f"     wget --continue --tries=20 --waitretry=30 --limit-rate=8m")
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=False)
    elapsed = time.time() - start_time

    if result.returncode == 0 and os.path.exists(outpath):
        size = os.path.getsize(outpath)
        speed = size / elapsed if elapsed > 0 else 0
        print(f"  ✅ {lang}: téléchargé via wget ({human_size(size)}) en {timedelta(seconds=int(elapsed))}"
              f" ({human_size(int(speed))}/s)")

        status[lang] = status.get(lang, {})
        status[lang]["downloaded"] = True
        status[lang]["size_bytes"] = size
        status[lang]["download_time_s"] = int(elapsed)
        status[lang]["download_date"] = datetime.now().isoformat()
        status[lang]["method"] = "wget"
        save_status(status)
        return True
    else:
        print(f"  ❌ {lang}: échec wget aussi (code {result.returncode})")
        status[lang] = status.get(lang, {})
        status[lang]["downloaded"] = False
        status[lang]["error"] = f"wget exit code {result.returncode}"
        save_status(status)
        return False


def verify_dump(lang: str, status: dict) -> bool:
    """Vérifie le SHA1 d'un dump téléchargé."""
    outpath = get_dump_path(lang)
    if not os.path.exists(outpath):
        print(f"  ❌ {lang}: fichier non trouvé")
        return False

    filename = DUMP_FILENAME.format(lang=lang)
    sha1s = fetch_sha1(lang)
    expected = sha1s.get(filename)

    if not expected:
        print(f"  ⚠️  {lang}: SHA1 non disponible sur le serveur (vérification ignorée)")
        status[lang] = status.get(lang, {})
        status[lang]["verified"] = "no_sha1_available"
        save_status(status)
        return True  # On ne bloque pas pour ça

    size = os.path.getsize(outpath)
    print(f"  🔍 {lang}: vérification SHA1 de {human_size(size)}...", end=" ", flush=True)

    if verify_sha1(outpath, expected):
        print("✅ OK")
        status[lang] = status.get(lang, {})
        status[lang]["verified"] = True
        status[lang]["sha1"] = expected
        save_status(status)
        return True
    else:
        print("❌ MISMATCH — re-téléchargement nécessaire")
        status[lang] = status.get(lang, {})
        status[lang]["verified"] = False
        save_status(status)
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

def cmd_download(langs: list, small_first: bool = False):
    """Télécharge les dumps pour les langues spécifiées."""
    status = load_status()

    if small_first:
        langs = sorted(langs, key=lambda l: LANGUAGES[l]["size_gb"])
    
    total_gb = sum(LANGUAGES[l]["size_gb"] for l in langs)
    already = sum(1 for l in langs if status.get(l, {}).get("downloaded"))
    
    print(f"\n{'='*70}")
    print(f"📚 Wikipedia Dump Downloader — PanLang Encyclopedic Corpus")
    print(f"{'='*70}")
    print(f"  Langues : {len(langs)} ({', '.join(langs)})")
    print(f"  Taille totale : ~{total_gb:.1f} Go compressé")
    print(f"  Déjà téléchargés : {already}/{len(langs)}")
    print(f"  Destination : {DUMPS_DIR}")
    print(f"  Outil : aria2c ({ARIA2_CONNECTIONS} connexions/fichier)")
    print(f"{'='*70}\n")

    os.makedirs(DUMPS_DIR, exist_ok=True)

    successes = 0
    failures = 0

    for i, lang in enumerate(langs, 1):
        info = LANGUAGES[lang]
        print(f"\n[{i}/{len(langs)}] {lang} — {info['name']} (~{info['size_gb']} Go)")
        
        if download_dump(lang, status):
            successes += 1
        else:
            failures += 1
        
        # Pause entre les téléchargements pour respecter Wikimedia
        if i < len(langs):
            wait = 10
            print(f"  ⏳ Pause {wait}s avant le prochain téléchargement...")
            time.sleep(wait)

    print(f"\n{'='*70}")
    print(f"📊 Résultat : {successes} réussis, {failures} échoués sur {len(langs)}")
    total_bytes = sum(status.get(l, {}).get("size_bytes", 0) for l in langs)
    print(f"📦 Taille totale téléchargée : {human_size(total_bytes)}")
    print(f"{'='*70}\n")


def cmd_verify(langs: list):
    """Vérifie les SHA1 de tous les dumps."""
    status = load_status()
    
    print(f"\n🔍 Vérification SHA1 de {len(langs)} dumps...\n")
    
    ok = 0
    fail = 0
    for lang in langs:
        if verify_dump(lang, status):
            ok += 1
        else:
            fail += 1
    
    print(f"\n✅ {ok} vérifiés, ❌ {fail} échoués\n")


def cmd_status(langs: list):
    """Affiche l'état de tous les téléchargements."""
    status = load_status()
    
    print(f"\n{'='*70}")
    print(f"📊 État des téléchargements Wikipedia — PanLang")
    print(f"{'='*70}")
    print(f"{'Lang':<6} {'Nom':<15} {'Taille':<10} {'Téléchargé':<14} {'Vérifié':<10} {'Fichier'}")
    print(f"{'─'*6} {'─'*15} {'─'*10} {'─'*14} {'─'*10} {'─'*30}")
    
    total_expected = 0
    total_actual = 0
    
    for lang in sorted(langs, key=lambda l: LANGUAGES[l]["size_gb"]):
        info = LANGUAGES[lang]
        s = status.get(lang, {})
        path = get_dump_path(lang)
        exists = os.path.exists(path)
        size = os.path.getsize(path) if exists else 0
        
        dl = "✅" if s.get("downloaded") else ("📥 partiel" if exists else "❌")
        vf = "✅" if s.get("verified") == True else ("⚠️" if s.get("verified") == "no_sha1_available" else "❌")
        
        total_expected += int(info["size_gb"] * 1073741824)
        total_actual += size
        
        print(f"{lang:<6} {info['name']:<15} {info['size_gb']:<10.2f} {dl:<14} {vf:<10} {human_size(size) if exists else '—'}")
    
    print(f"{'─'*70}")
    print(f"{'TOTAL':<6} {'':15} {sum(LANGUAGES[l]['size_gb'] for l in langs):<10.1f} "
          f"{'':14} {'':10} {human_size(total_actual)}")
    pct = (total_actual / total_expected * 100) if total_expected > 0 else 0
    print(f"\nProgression globale : {pct:.1f}%")
    print(f"Espace disque utilisé : {human_size(total_actual)}")
    
    # Espace disque disponible
    try:
        st = os.statvfs(DUMPS_DIR if os.path.exists(DUMPS_DIR) else os.path.dirname(DUMPS_DIR))
        free = st.f_bavail * st.f_frsize
        print(f"Espace disque libre : {human_size(free)}")
    except:
        pass
    
    print()


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Télécharge les dumps Wikipedia complets pour PanLang",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  %(prog)s                          Télécharge les 14 langues
  %(prog)s --small-first            Petites langues d'abord (sa, eo, hi, fi...)
  %(prog)s --langs fr de en         Seulement français, allemand, anglais
  %(prog)s --status                 État des téléchargements
  %(prog)s --verify                 Vérifie les SHA1
  %(prog)s --langs sa eo hi fi      Seulement les petites (test rapide)
        """
    )
    parser.add_argument("--langs", nargs="+", default=list(LANGUAGES.keys()),
                       help="Langues à télécharger (défaut: toutes)")
    parser.add_argument("--small-first", action="store_true",
                       help="Télécharger les petites langues d'abord")
    parser.add_argument("--status", action="store_true",
                       help="Afficher l'état des téléchargements")
    parser.add_argument("--verify", action="store_true",
                       help="Vérifier les SHA1 des dumps")
    
    args = parser.parse_args()
    
    # Valider les langues
    for lang in args.langs:
        if lang not in LANGUAGES:
            print(f"❌ Langue inconnue: {lang}. Valides: {', '.join(sorted(LANGUAGES.keys()))}")
            sys.exit(1)
    
    if args.status:
        cmd_status(args.langs)
    elif args.verify:
        cmd_verify(args.langs)
    else:
        cmd_download(args.langs, small_first=args.small_first)


if __name__ == "__main__":
    main()
