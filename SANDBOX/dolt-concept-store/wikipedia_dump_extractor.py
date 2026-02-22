#!/usr/bin/env python3
"""wikipedia_dump_extractor.py — Extrait les articles des dumps Wikipedia pour PanLang.

Parseur SAX streaming qui traite les dumps pages-articles.xml.bz2 sans charger
le fichier entier en RAM. Extrait le texte brut de chaque article via mwparserfromhell.

Output : 1 fichier texte par article, organisé par langue, dans wikipedia_fullcorpus/

Usage:
    python3 wikipedia_dump_extractor.py --lang fr          # Extraire le français
    python3 wikipedia_dump_extractor.py --all              # Extraire toutes les langues
    python3 wikipedia_dump_extractor.py --lang en --limit 10000  # 10K premiers articles EN
    python3 wikipedia_dump_extractor.py --status           # État de l'extraction

Architecture mémoire :
    - SAX parser : ~10 Mo RAM constant (streaming)
    - mwparserfromhell : ~50 Mo RAM par article (libéré immédiatement)
    - Total : ~100 Mo RAM indépendamment de la taille du dump

Partie de l'infrastructure PanLang — corpus encyclopédique multilingue.
"""

import argparse
import bz2
import json
import os
import re
import sys
import time
import unicodedata
import xml.sax
import xml.sax.handler
from datetime import datetime, timedelta
from pathlib import Path

try:
    import mwparserfromhell
    HAS_MWP = True
except ImportError:
    HAS_MWP = False
    print("⚠️  mwparserfromhell non installé — pip install mwparserfromhell")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

DUMPS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wikipedia_dumps")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wikipedia_fullcorpus")
STATUS_FILE = os.path.join(OUTPUT_DIR, "_extraction_status.json")

# Namespaces à ignorer (0 = article, les autres sont discussion, utilisateur, etc.)
ACCEPTED_NAMESPACES = {0}

# Articles trop courts pour être utiles (stubs, redirections)
MIN_ARTICLE_BYTES = 500       # Ignorer les articles < 500 octets de texte brut
MIN_ARTICLE_WORDS = 50        # Ignorer les articles < 50 mots

# Nettoyage wikitext
WIKITEXT_CLEANUP = [
    (re.compile(r'\{\{[^{}]*\}\}'), ''),          # Templates simples
    (re.compile(r'\[\[Catégorie:[^\]]*\]\]'), ''),  # Catégories FR
    (re.compile(r'\[\[Category:[^\]]*\]\]'), ''),    # Catégories EN
    (re.compile(r'\[\[Kategorie:[^\]]*\]\]'), ''),   # Catégories DE
    (re.compile(r'<ref[^>]*>.*?</ref>', re.DOTALL), ''),  # Références
    (re.compile(r'<ref[^>]*/>', re.DOTALL), ''),          # Références auto-fermantes
    (re.compile(r'<!--.*?-->', re.DOTALL), ''),     # Commentaires HTML
    (re.compile(r'\{\|.*?\|\}', re.DOTALL), ''),    # Tables wiki
    (re.compile(r'__[A-Z]+__'), ''),                # Magic words
]

# Patterns de titres à ignorer
SKIP_TITLE_PATTERNS = [
    re.compile(r'^(Fichier|File|Image|Imagen|Datei|Bestand|Bild):'),
    re.compile(r'^(Modèle|Template|Vorlage|Plantilla|Predefinição|Шаблон):'),
    re.compile(r'^(Catégorie|Category|Kategorie|Categoría|Categoria|Категория):'),
    re.compile(r'^(Portail|Portal|Wikipedia|Wikip[eé]dia|MediaWiki):'),
    re.compile(r'^(Module|Modulo|Módulo):'),
    re.compile(r'^(Aide|Help|Hilfe|Ayuda):'),
    re.compile(r'^(Projet|Project|Progetto|Proyecto):'),
    re.compile(r'^(Discussion|Talk|Diskussion|Discusión):'),
]


# ═══════════════════════════════════════════════════════════════════════════════
# WIKITEXT → PLAINTEXT
# ═══════════════════════════════════════════════════════════════════════════════

def wikitext_to_plaintext(wikitext: str) -> str:
    """Convertit du wikitext en texte brut lisible.
    
    Utilise mwparserfromhell pour le parsing structurel, puis nettoyage
    supplémentaire des artefacts résiduels.
    """
    if not wikitext or len(wikitext.strip()) < 10:
        return ""

    # Phase 1 : Pré-nettoyage (retire ce qui confond mwparserfromhell)
    text = wikitext
    for pattern, replacement in WIKITEXT_CLEANUP:
        text = pattern.sub(replacement, text)

    # Phase 2 : mwparserfromhell (parsing structurel)
    if HAS_MWP:
        try:
            parsed = mwparserfromhell.parse(text)
            # Retirer les templates restants
            for template in parsed.filter_templates():
                try:
                    parsed.remove(template)
                except ValueError:
                    pass
            # Retirer les tags HTML
            for tag in parsed.filter_tags():
                try:
                    parsed.remove(tag)
                except ValueError:
                    pass
            text = parsed.strip_code(
                normalize=True,
                collapse=True,
            )
        except Exception:
            # Fallback : nettoyage regex basique si mwparserfromhell échoue
            text = re.sub(r'\[\[([^|\]]*\|)?([^\]]*)\]\]', r'\2', text)  # [[lien|texte]] → texte
            text = re.sub(r"'''?", '', text)  # Gras/italique
    else:
        # Sans mwparserfromhell : nettoyage regex basique
        text = re.sub(r'\[\[([^|\]]*\|)?([^\]]*)\]\]', r'\2', text)
        text = re.sub(r'\[https?://[^\s\]]*\s?([^\]]*)\]', r'\1', text)
        text = re.sub(r"'''?", '', text)
        text = re.sub(r'<[^>]+>', '', text)

    # Phase 3 : Post-nettoyage
    text = re.sub(r'\n{3,}', '\n\n', text)       # Max 2 newlines consécutifs
    text = re.sub(r'[ \t]+', ' ', text)            # Espaces multiples
    text = re.sub(r'^\s+', '', text, flags=re.MULTILINE)  # Espaces en début de ligne
    text = re.sub(r'\(\s*\)', '', text)            # Parenthèses vides
    text = re.sub(r',\s*,', ',', text)             # Virgules doubles
    text = text.strip()

    # Phase 4 : NFC Unicode normalization
    text = unicodedata.normalize('NFC', text)

    return text


def sanitize_filename(title: str) -> str:
    """Convertit un titre Wikipedia en nom de fichier valide."""
    # Remplacer les caractères problématiques
    name = title.lower()
    name = re.sub(r'[/\\:*?"<>|]', '_', name)
    name = re.sub(r'\s+', '_', name)
    name = re.sub(r'_+', '_', name)
    name = name.strip('_')
    # Limiter la longueur (filesystem limit = 255, on garde de la marge)
    if len(name.encode('utf-8')) > 200:
        name = name[:80]
    return name


# ═══════════════════════════════════════════════════════════════════════════════
# SAX HANDLER — Streaming XML parser
# ═══════════════════════════════════════════════════════════════════════════════

class WikiDumpHandler(xml.sax.handler.ContentHandler):
    """Parseur SAX streaming pour les dumps Wikipedia.
    
    Mémoire constante : ne charge qu'un article à la fois.
    """

    def __init__(self, lang: str, output_dir: str, limit: int = 0,
                 progress_interval: int = 5000):
        super().__init__()
        self.lang = lang
        self.output_dir = output_dir
        self.limit = limit
        self.progress_interval = progress_interval

        # État du parsing
        self._path = []           # pile des éléments XML
        self._chars = []          # buffer de caractères
        self._title = ""
        self._ns = -1             # namespace
        self._text = ""
        self._page_id = 0

        # Compteurs
        self.articles_total = 0    # pages vues
        self.articles_saved = 0    # articles extraits
        self.articles_skipped = 0  # articles ignorés (trop courts, mauvais namespace, etc.)
        self.total_words = 0
        self.total_chars = 0
        self.start_time = time.time()

        os.makedirs(output_dir, exist_ok=True)

    def startElement(self, name, attrs):
        self._path.append(name)
        self._chars = []

    def characters(self, content):
        self._chars.append(content)

    def endElement(self, name):
        content = ''.join(self._chars).strip()

        if name == "title":
            self._title = content
        elif name == "ns":
            try:
                self._ns = int(content)
            except ValueError:
                self._ns = -1
        elif name == "id" and self._path[-2:] == ["page", "id"]:
            try:
                self._page_id = int(content)
            except ValueError:
                self._page_id = 0
        elif name == "text":
            self._text = ''.join(self._chars)  # Garder les espaces pour le wikitext
        elif name == "page":
            self._process_page()

        if self._path and self._path[-1] == name:
            self._path.pop()

    def _process_page(self):
        """Traite une page complète."""
        self.articles_total += 1

        # Vérifier la limite
        if self.limit > 0 and self.articles_saved >= self.limit:
            return

        # Ignorer les mauvais namespaces
        if self._ns not in ACCEPTED_NAMESPACES:
            self.articles_skipped += 1
            return

        # Ignorer les titres de maintenance
        for pattern in SKIP_TITLE_PATTERNS:
            if pattern.match(self._title):
                self.articles_skipped += 1
                return

        # Ignorer les redirections
        if self._text.strip().lower().startswith('#redirect') or \
           self._text.strip().lower().startswith('#redirection') or \
           self._text.strip().lower().startswith('#weiterleitung'):
            self.articles_skipped += 1
            return

        # Convertir wikitext → texte brut
        plaintext = wikitext_to_plaintext(self._text)

        # Vérifier la taille minimale
        if len(plaintext.encode('utf-8')) < MIN_ARTICLE_BYTES:
            self.articles_skipped += 1
            return

        word_count = len(plaintext.split())
        if word_count < MIN_ARTICLE_WORDS:
            self.articles_skipped += 1
            return

        # Sauvegarder
        filename = sanitize_filename(self._title) + ".txt"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            # En-tête minimale pour la traçabilité
            f.write(f"# {self._title}\n")
            f.write(f"# Wikipedia {self.lang} — ID: {self._page_id}\n")
            f.write(f"# Mots: {word_count}\n\n")
            f.write(plaintext)

        self.articles_saved += 1
        self.total_words += word_count
        self.total_chars += len(plaintext)

        # Progression
        if self.articles_saved % self.progress_interval == 0:
            elapsed = time.time() - self.start_time
            speed = self.articles_saved / elapsed if elapsed > 0 else 0
            print(f"    [{self.lang}] {self.articles_saved:,} articles extraits "
                  f"({self.articles_skipped:,} ignorés, {self.total_words:,} mots) "
                  f"— {speed:.0f} art/s — {timedelta(seconds=int(elapsed))}")

        # Libérer la mémoire
        self._text = ""
        self._title = ""


# ═══════════════════════════════════════════════════════════════════════════════
# EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════════

def extract_dump(lang: str, limit: int = 0) -> dict:
    """Extrait les articles d'un dump Wikipedia compressé.
    
    Retourne un dictionnaire de statistiques.
    """
    dump_path = os.path.join(DUMPS_DIR, lang,
                             f"{lang}wiki-latest-pages-articles.xml.bz2")
    output_dir = os.path.join(OUTPUT_DIR, lang)

    if not os.path.exists(dump_path):
        print(f"  ❌ {lang}: dump non trouvé ({dump_path})")
        return {"error": "dump not found"}

    dump_size = os.path.getsize(dump_path)
    print(f"\n  📖 {lang}: extraction depuis {dump_path}")
    print(f"     Taille dump: {dump_size / 1073741824:.2f} Go")
    print(f"     Sortie: {output_dir}")
    if limit > 0:
        print(f"     Limite: {limit:,} articles")

    handler = WikiDumpHandler(lang, output_dir, limit=limit)

    start = time.time()

    try:
        # Les dumps Wikipedia sont des bz2 multi-stream (blocs concaténés).
        # subprocess avec bzip2/pbzip2 est plus fiable et performant que bz2.open().
        import subprocess
        import shutil

        # Préférer pbzip2 (parallèle) si disponible, sinon bzip2
        decompressor = "pbzip2" if shutil.which("pbzip2") else "bzip2"
        proc = subprocess.Popen(
            [decompressor, "-dc", dump_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        xml.sax.parse(proc.stdout, handler)
        proc.wait()
    except xml.sax.SAXException as e:
        # SAX peut lever une exception quand on atteint la limite
        if handler.limit > 0 and handler.articles_saved >= handler.limit:
            pass  # Normal — on a atteint la limite
        else:
            print(f"  ⚠️  Erreur SAX: {e}")
    except (OSError, IOError) as e:
        # Erreur de décompression — dump peut-être tronqué
        if handler.articles_saved > 0:
            print(f"  ⚠️  Erreur I/O après {handler.articles_saved:,} articles: {e}")
        else:
            print(f"  ❌ Erreur I/O: {e}")
    except KeyboardInterrupt:
        print(f"\n  ⏸️  Interrompu par l'utilisateur")
    finally:
        if 'proc' in locals() and proc.poll() is None:
            proc.terminate()

    elapsed = time.time() - start
    speed = handler.articles_saved / elapsed if elapsed > 0 else 0

    stats = {
        "lang": lang,
        "articles_saved": handler.articles_saved,
        "articles_skipped": handler.articles_skipped,
        "articles_total": handler.articles_total,
        "total_words": handler.total_words,
        "total_chars": handler.total_chars,
        "extraction_time_s": int(elapsed),
        "articles_per_second": round(speed, 1),
        "extraction_date": datetime.now().isoformat(),
        "dump_size_bytes": dump_size,
        "limit": limit,
    }

    print(f"\n  📊 {lang}: extraction terminée")
    print(f"     Articles: {handler.articles_saved:,} extraits "
          f"({handler.articles_skipped:,} ignorés sur {handler.articles_total:,} pages)")
    print(f"     Mots: {handler.total_words:,}")
    print(f"     Temps: {timedelta(seconds=int(elapsed))}")
    print(f"     Vitesse: {speed:.0f} articles/seconde")

    return stats


def cmd_extract(langs: list, limit: int = 0):
    """Extrait les articles pour les langues spécifiées."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_stats = load_extraction_status()

    print(f"\n{'='*70}")
    print(f"📖 Wikipedia Dump Extractor — PanLang Encyclopedic Corpus")
    print(f"{'='*70}")
    print(f"  Langues: {', '.join(langs)}")
    print(f"  Limite: {'aucune' if limit == 0 else f'{limit:,} articles/langue'}")
    print(f"  Sortie: {OUTPUT_DIR}")
    print(f"{'='*70}")

    for lang in langs:
        stats = extract_dump(lang, limit=limit)
        all_stats[lang] = stats
        save_extraction_status(all_stats)

    # Résumé global
    print(f"\n{'='*70}")
    print(f"📊 Résumé global")
    print(f"{'='*70}")
    total_articles = sum(s.get("articles_saved", 0) for s in all_stats.values()
                         if isinstance(s, dict))
    total_words = sum(s.get("total_words", 0) for s in all_stats.values()
                      if isinstance(s, dict))
    total_time = sum(s.get("extraction_time_s", 0) for s in all_stats.values()
                     if isinstance(s, dict))
    print(f"  Articles totaux: {total_articles:,}")
    print(f"  Mots totaux: {total_words:,}")
    print(f"  Temps total: {timedelta(seconds=total_time)}")
    print(f"{'='*70}\n")


def cmd_status(langs: list):
    """Affiche l'état de l'extraction."""
    status = load_extraction_status()

    print(f"\n{'='*70}")
    print(f"📊 État de l'extraction — PanLang")
    print(f"{'='*70}")
    print(f"{'Lang':<6} {'Articles':<12} {'Mots':<15} {'Ignorés':<12} {'Temps':<10} {'Vitesse'}")
    print(f"{'─'*6} {'─'*12} {'─'*15} {'─'*12} {'─'*10} {'─'*10}")

    for lang in sorted(langs):
        s = status.get(lang, {})
        if not s or "error" in s:
            print(f"{lang:<6} {'—':<12} {'—':<15} {'—':<12} {'—':<10} —")
            continue
        arts = f"{s.get('articles_saved', 0):,}"
        words = f"{s.get('total_words', 0):,}"
        skip = f"{s.get('articles_skipped', 0):,}"
        t = str(timedelta(seconds=s.get('extraction_time_s', 0)))
        speed = f"{s.get('articles_per_second', 0):.0f} art/s"
        print(f"{lang:<6} {arts:<12} {words:<15} {skip:<12} {t:<10} {speed}")

    total_arts = sum(s.get("articles_saved", 0) for s in status.values() if isinstance(s, dict))
    total_words = sum(s.get("total_words", 0) for s in status.values() if isinstance(s, dict))
    print(f"{'─'*70}")
    print(f"{'TOTAL':<6} {total_arts:,}{'':<5} {total_words:,}")
    
    # Taille sur disque
    if os.path.exists(OUTPUT_DIR):
        total_size = sum(
            os.path.getsize(os.path.join(dp, f))
            for dp, dn, filenames in os.walk(OUTPUT_DIR)
            for f in filenames
        )
        print(f"\nEspace disque: {total_size / 1073741824:.2f} Go")
    print()


def load_extraction_status() -> dict:
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_extraction_status(status: dict):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=2, ensure_ascii=False, default=str)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

LANGUAGES = ["sa", "eo", "hi", "fi", "nl", "pt", "zh", "it", "ja", "es", "ru", "fr", "de", "en"]

def main():
    parser = argparse.ArgumentParser(
        description="Extrait les articles des dumps Wikipedia pour PanLang"
    )
    parser.add_argument("--lang", nargs="+", default=None,
                       help="Langues à extraire (défaut: toutes)")
    parser.add_argument("--all", action="store_true",
                       help="Extraire toutes les langues")
    parser.add_argument("--limit", type=int, default=0,
                       help="Nombre max d'articles par langue (0 = illimité)")
    parser.add_argument("--status", action="store_true",
                       help="Afficher l'état de l'extraction")

    args = parser.parse_args()

    if not HAS_MWP:
        print("❌ mwparserfromhell est requis : pip install mwparserfromhell")
        sys.exit(1)

    langs = args.lang if args.lang else LANGUAGES

    if args.status:
        cmd_status(langs)
    else:
        cmd_extract(langs, limit=args.limit)


if __name__ == "__main__":
    main()
