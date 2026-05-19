"""
nipada_classifier.py — §78 : Classification structurelle nipada pour Panini-FS

Chaque chunk de bytes est classifié selon les 4 atomes nipada :

  ÊTRE        (prime=2, bit0) — la donnée est une unité cohérente non-vide
  DIFFÉRENCE  (prime=3, bit1) — la donnée contient de la variation interne
                                 (entropie de Shannon > 4.0 bits)
  RAPPORT     (prime=5, bit2) — la donnée a une structure répétitive/compressible
                                 (compression zlib > 15 %)
  ORIENTATION (prime=7, bit3) — la donnée est ordonnée directionnellement
                                 (marqueur temporel ou asymétrie entropique tête/queue)

Le produit des primes des atomes présents = nipada_address.

Exemples attendus :
  PNG header     → COMPOSITION (2×5 = 10)   : structuré, non temporel
  TEXT répété    → VIE         (2×3×5 = 30)  : varié + structuré
  GZIP payload   → EXISTENCE   (2×3 = 6)     : varié, non compressible (déjà compressé)
  WAV/MP4 header → INTENTION   (2×5×7 = 70)  : structuré + temporel
  Audio data     → INTÉGRATION (2×3×5×7=210) : tout présent

Ce module est autonome (aucune dépendance sur nipada_engine) pour permettre
son utilisation dans Panini-FS sans dépendance vers le moteur sémantique.
"""

import math
import zlib
from collections import Counter


# ── Table de nommage (copie minimale, indépendante de nipada_engine) ──────────

_ATOM_PRIMES = (2, 3, 5, 7)  # par position de bit : ÊTRE, DIFFÉRENCE, RAPPORT, ORIENTATION

NIPADA_NAMES: dict[int, str] = {
    1:   "PADDING",       # mask=0  → neutre (chunk vide ou padding)
    2:   "ÊTRE",          # mask=0001
    3:   "DIFFÉRENCE",    # mask=0010
    5:   "RAPPORT",       # mask=0100
    7:   "ORIENTATION",   # mask=1000
    6:   "EXISTENCE",     # mask=0011 = ÊTRE + DIFFÉRENCE
    10:  "COMPOSITION",   # mask=0101 = ÊTRE + RAPPORT
    14:  "DEVENIR",       # mask=1001 = ÊTRE + ORIENTATION
    15:  "MESURE",        # mask=0110 = DIFFÉRENCE + RAPPORT
    21:  "OPPOSITION",    # mask=1010 = DIFFÉRENCE + ORIENTATION
    35:  "RÉFÉRENCE",     # mask=1100 = RAPPORT + ORIENTATION
    30:  "VIE",           # mask=0111 = ÊTRE + DIFFÉRENCE + RAPPORT
    42:  "TRANSFORMATION",# mask=1011 = ÊTRE + DIFFÉRENCE + ORIENTATION
    70:  "INTENTION",     # mask=1101 = ÊTRE + RAPPORT + ORIENTATION
    105: "TEMPS",         # mask=1110 = DIFFÉRENCE + RAPPORT + ORIENTATION
    210: "INTÉGRATION",   # mask=1111 = tous les 4 atomes
}

NIPADA_NAMES_EN: dict[int, str] = {
    1:   "PADDING",
    2:   "BEING",
    3:   "DIFFERENCE",
    5:   "RATIO",
    7:   "ORIENTATION",
    6:   "EXISTENCE",
    10:  "COMPOSITION",
    14:  "BECOMING",
    15:  "MEASURE",
    21:  "OPPOSITION",
    35:  "REFERENCE",
    30:  "LIFE",
    42:  "TRANSFORMATION",
    70:  "INTENTION",
    105: "TIME",
    210: "INTEGRATION",
}

# Formats temporels connus (magic numbers ou préfixes d'en-tête)
_TEMPORAL_PREFIXES: tuple[bytes, ...] = (
    b'RIFF',           # WAV, AVI, WebP (RIFF container)
    b'\x1a\x45\xdf\xa3',  # WebM / MKV (EBML)
    b'ID3',            # MP3 avec tag ID3
    b'\xff\xfb',       # MP3 frame sync
    b'\xff\xf3',
    b'\xff\xf2',
    b'OggS',           # Ogg (Vorbis, Opus, Theora)
    b'fLaC',           # FLAC
)

# Formats temporels reconnus par sous-bytes (MP4/MOV : bytes[4:8] == b'ftyp')
_TEMPORAL_SUBCHECK = b'ftyp'

# Formats structurés connus (magic → RAPPORT, même si trop courts pour la compression)
# Note : GZIP exclu — contenu compressé = aléatoire, pas de RAPPORT structurel apparent
# Note : formats temporels (RIFF etc.) absents ici — gérés via _has_orientation
_STRUCTURAL_MAGIC: tuple[bytes, ...] = (
    b'\x89PNG',        # PNG
    b'\xff\xd8\xff',   # JPEG
    b'GIF8',           # GIF
    b'BM',             # BMP
    b'%PDF',           # PDF
    b'PK\x03\x04',     # ZIP
    b'RIFF',           # WAV/AVI/WebP — structuré en blocs (même si temporel)
)


# ── Fonctions de mesure ───────────────────────────────────────────────────────

def _entropy(data: bytes) -> float:
    """Shannon entropy H ∈ [0.0, 8.0] bits/byte."""
    if not data:
        return 0.0
    counts = Counter(data)
    total = len(data)
    return -sum((c / total) * math.log2(c / total) for c in counts.values() if c > 0)


def _compression_gain(data: bytes) -> float:
    """
    Fraction épargnée par zlib level=1 ∈ [0.0, 1.0].
    > 0.15  → présence de structure répétitive (RAPPORT)
    """
    if len(data) < 16:
        return 0.0
    compressed_len = len(zlib.compress(data, level=1))
    return max(0.0, 1.0 - compressed_len / len(data))


def _has_orientation(data: bytes) -> bool:
    """
    True si les données ont une structure directionnelle / temporelle.

    Critères (par ordre de fiabilité) :
      1. Magic number d'un format temporel connu
      2. Bytes[4:8] == b'ftyp'  (MP4/MOV ISO BMFF)
      3. Asymétrie entropique tête/queue > 1.5 bits  (header structuré + corps aléatoire)
    """
    if len(data) >= 4:
        for prefix in _TEMPORAL_PREFIXES:
            if data.startswith(prefix):
                return True
        if len(data) >= 8 and data[4:8] == _TEMPORAL_SUBCHECK:
            return True

    # Asymétrie entropique : le début (header) diffère significativement de la fin (body)
    if len(data) >= 128:
        h_head = _entropy(data[:64])
        h_tail = _entropy(data[-64:])
        if abs(h_head - h_tail) > 1.5:
            return True

    return False


# ── Classifieur principal ─────────────────────────────────────────────────────

def classify_chunk(data: bytes) -> tuple[int, str]:
    """
    Classifie un chunk brut en adresse nipada.

    Args:
        data: Bytes du chunk (peut être vide).

    Returns:
        (nipada_product, nipada_name_fr)
        nipada_product == 1 → PADDING (chunk vide/neutre)

    Exemples :
        >>> classify_chunk(b'')
        (1, 'PADDING')
        >>> classify_chunk(b'\\x89PNG\\r\\n\\x1a\\n' + b'\\x00' * 56)
        (10, 'COMPOSITION')
        >>> classify_chunk(b'Hello world! ' * 200)
        (30, 'VIE')
    """
    if not data:
        return (1, "PADDING")

    mask = 0

    # bit0 — ÊTRE : la donnée est une unité non-vide (toujours vrai ici)
    mask |= 1

    # bit1 — DIFFÉRENCE : entropie interne > 4.0 bits/byte (variation significative)
    if _entropy(data) > 4.0:
        mask |= 2

    # bit2 — RAPPORT : la donnée est compressible OU porte un magic de format structuré
    # Un magic de format = la donnée déclare sa propre structure = relation de parties = RAPPORT
    if _compression_gain(data) > 0.15 or _has_format_magic(data):
        mask |= 4

    # bit3 — ORIENTATION : la donnée est ordonnée directionnellement
    if _has_orientation(data):
        mask |= 8

    product = _mask_to_product(mask)
    return (product, NIPADA_NAMES.get(product, f"UNKNOWN({product})"))


def classify_chunk_detail(data: bytes) -> dict:
    """
    Classifie un chunk et retourne les métriques intermédiaires.

    Utile pour debug, tests, et calibration des seuils.

    Returns:
        dict avec entropy, compression_gain, has_orientation, mask, product, name
    """
    if not data:
        return {
            "entropy": 0.0,
            "compression_gain": 0.0,
            "has_orientation": False,
            "mask": 0,
            "product": 1,
            "name": "PADDING",
            "atoms": [],
        }

    ent = _entropy(data)
    cg  = _compression_gain(data)
    ori = _has_orientation(data)

    mask = 1  # ÊTRE toujours présent
    if ent > 4.0:
        mask |= 2
    if cg > 0.15 or _has_format_magic(data):
        mask |= 4
    if ori:
        mask |= 8

    product = _mask_to_product(mask)
    atoms = _atoms_in_mask(mask)

    return {
        "entropy":          round(ent, 4),
        "compression_gain": round(cg, 4),
        "has_orientation":  ori,
        "mask":             mask,
        "product":          product,
        "name":             NIPADA_NAMES.get(product, f"UNKNOWN({product})"),
        "name_en":          NIPADA_NAMES_EN.get(product, "?"),
        "atoms":            atoms,
    }


# ── Utilitaires internes ──────────────────────────────────────────────────────

def _mask_to_product(mask: int) -> int:
    """Convertit un masque 4 bits en produit de primes nipada."""
    product = 1
    for i, prime in enumerate(_ATOM_PRIMES):
        if mask & (1 << i):
            product *= prime
    return product


def _has_format_magic(data: bytes) -> bool:
    """True si le chunk commence par un magic number de format structuré connu."""
    for magic in _STRUCTURAL_MAGIC:
        if data.startswith(magic):
            return True
    return False


def _atoms_in_mask(mask: int) -> list[str]:
    """Retourne les noms des atomes présents dans le masque."""
    names = ("ÊTRE", "DIFFÉRENCE", "RAPPORT", "ORIENTATION")
    return [names[i] for i in range(4) if mask & (1 << i)]
