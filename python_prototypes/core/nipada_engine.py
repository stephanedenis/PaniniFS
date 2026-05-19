"""
nipada_engine.py — Moteur d'encodage nipada v1.0

Encodage 4 bits canonique :
    bit0 = ÊTRE        (prime 2)
    bit1 = DIFFÉRENCE  (prime 3)
    bit2 = RAPPORT     (prime 5)
    bit3 = ORIENTATION (prime 7)

    0b0000 = 0 → PADDING (produit vide = 1)
    0b1111 = 15 → INTÉGRATION (nipada value = 210)

Domaines :
    Z+  : molécules positives    — mask ∈ 1..15, sign=+1
    Z-  : crossings Spencer-Brown — mask ∈ 1..15, sign=-1
    iZ  : auto-références        — mask ∈ 1..15, operator='i'
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property
from pathlib import Path
from typing import Iterator

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

PRIMES = (2, 3, 5, 7)          # Les 4 atomes dans l'ordre des bits
ATOM_NAMES = ("ÊTRE", "DIFFÉRENCE", "RAPPORT", "ORIENTATION")
PADDING_MASK = 0                # produit vide = 1, aucun concept
MAX_MASK = 0b1111               # 15 = INTÉGRATION

# Chemin vers le catalogue JSON (relatif à ce fichier → src/core/)
_CATALOG_PATH = Path(__file__).parent.parent.parent / "research" / "nipada" / "src"


class Domain(str, Enum):
    Z_POS = "Z+"
    Z_NEG = "Z-"
    IZ    = "iZ"


# ---------------------------------------------------------------------------
# Fonctions bas niveau (opérations sur masques)
# ---------------------------------------------------------------------------

def mask_to_product(mask: int) -> int:
    """
    Convertit un masque 4 bits en produit de primes (nipada value).

    mask=0  → 1   (produit vide, padding)
    mask=1  → 2   (ÊTRE)
    mask=15 → 210 (INTÉGRATION)
    """
    if mask == PADDING_MASK:
        return 1
    result = 1
    for bit, prime in enumerate(PRIMES):
        if mask & (1 << bit):
            result *= prime
    return result


def product_to_mask(n: int) -> int | None:
    """
    Convertit un produit de primes nipada en masque 4 bits.

    Retourne None si n n'est pas un produit valide des primes {2,3,5,7}.
    """
    if n == 1:
        return PADDING_MASK
    mask = 0
    remaining = n
    for bit, prime in enumerate(PRIMES):
        if remaining % prime == 0:
            remaining //= prime
            mask |= (1 << bit)
            if remaining % prime == 0:
                return None  # prime apparaît 2×, invalide (Grassmann)
    return mask if remaining == 1 else None


def level(mask: int) -> int:
    """Niveau = popcount(mask) = nombre d'atomes dans la molécule."""
    return bin(mask).count("1")


def atoms_in(mask: int) -> tuple[int, ...]:
    """Retourne les primes (atomes) actifs dans un masque."""
    return tuple(p for bit, p in enumerate(PRIMES) if mask & (1 << bit))


def atom_names_in(mask: int) -> tuple[str, ...]:
    """Retourne les noms des atomes actifs."""
    return tuple(n for bit, n in enumerate(ATOM_NAMES) if mask & (1 << bit))


def is_subset(mask_a: int, mask_b: int) -> bool:
    """Vrai si les atomes de A sont tous présents dans B (A ⊆ B)."""
    return (mask_a & mask_b) == mask_a


def shared_atoms(mask_a: int, mask_b: int) -> int:
    """Masque des atomes communs entre A et B."""
    return mask_a & mask_b


def jaccard(mask_a: int, mask_b: int) -> float:
    """
    Similarité de Jaccard sur les ensembles d'atomes.
    0.0 = aucun atome commun, 1.0 = même ensemble d'atomes.
    """
    inter = bin(mask_a & mask_b).count("1")
    union = bin(mask_a | mask_b).count("1")
    return inter / union if union > 0 else 0.0


def iter_all_masks() -> Iterator[int]:
    """Itère sur les 15 masques non-nuls dans l'ordre croissant de niveau."""
    for lvl in range(1, 5):
        for mask in range(1, 16):
            if level(mask) == lvl:
                yield mask


# ---------------------------------------------------------------------------
# Structure de données : NipadaEntry
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class NipadaEntry:
    """Représentation d'une entrée de l'encyclopédie nipada."""

    mask:       int
    name:       str
    name_en:    str
    name_sa:    str
    domain:     Domain
    nipada_id:  int | str     # entier pour Z, "70i" etc. pour iZ
    factors:    tuple[int, ...]
    lvl:        int
    status:     str
    formula:    str
    notes:      str
    convergences: tuple[str, ...]

    @cached_property
    def nipada_value(self) -> int:
        """Valeur numérique absolue = produit des primes."""
        return mask_to_product(self.mask)

    @cached_property
    def atom_names(self) -> tuple[str, ...]:
        return atom_names_in(self.mask)

    def __str__(self) -> str:
        sign = {Domain.Z_POS: "+", Domain.Z_NEG: "−", Domain.IZ: ""}[self.domain]
        suffix = "i" if self.domain == Domain.IZ else ""
        return f"{sign}{self.nipada_value}{suffix} [{self.mask:04b}] {self.name}"

    def __repr__(self) -> str:
        return f"NipadaEntry(mask={self.mask}, name={self.name!r}, domain={self.domain})"


# ---------------------------------------------------------------------------
# Chargement du catalogue
# ---------------------------------------------------------------------------

def _load_entry(path: Path, domain: Domain) -> NipadaEntry | None:
    """Charge un fichier JSON en NipadaEntry. Retourne None si invalide."""
    try:
        with open(path) as f:
            d = json.load(f)
        raw_id = d.get("id")
        mask = d.get("mask")
        if mask is None:
            return None

        # Convertir le domain string JSON → enum
        dom_map = {"Z": Domain.Z_POS, "iZ": Domain.IZ}
        if d.get("type") == "crossing":
            dom = Domain.Z_NEG
        elif d.get("type") == "imaginary":
            dom = Domain.IZ
        else:
            dom = Domain.Z_POS

        return NipadaEntry(
            mask=mask,
            name=d.get("name", ""),
            name_en=d.get("name_en", ""),
            name_sa=d.get("name_sa", ""),
            domain=dom,
            nipada_id=raw_id,
            factors=tuple(d.get("factors", [])),
            lvl=d.get("level", level(mask)),
            status=d.get("status", "unknown"),
            formula=d.get("formula", ""),
            notes=d.get("notes", ""),
            convergences=tuple(d.get("convergences", [])),
        )
    except Exception:
        return None


class NipadaCatalog:
    """
    Catalogue complet des entrées nipada, chargé depuis le répertoire JSON.

    Usage :
        catalog = NipadaCatalog()
        e = catalog.by_mask(3, Domain.Z_POS)   # EXISTENCE
        e = catalog.by_name("MORT")             # MORT (-30)
        e = catalog.by_product(210)             # INTÉGRATION
        e = catalog.crossing_of(35)             # ANTICIPATION (-35)
    """

    def __init__(self, catalog_path: Path = _CATALOG_PATH) -> None:
        self._path = catalog_path
        self._entries: list[NipadaEntry] = []
        self._by_mask_domain: dict[tuple[int, Domain], NipadaEntry] = {}
        self._by_name: dict[str, NipadaEntry] = {}
        self._load()

    def _load(self) -> None:
        subdirs = {
            "atoms":              Domain.Z_POS,
            "molecules/level1":   Domain.Z_POS,
            "molecules/level2":   Domain.Z_POS,
            "molecules/level3":   Domain.Z_POS,
            "crossings":          Domain.Z_NEG,
            "imaginary":          Domain.IZ,
        }
        seen_files: set[str] = set()
        for subdir, domain in subdirs.items():
            for path in sorted((self._path / subdir).glob("*.json")):
                # Éviter les doublons (ex: 6_existence_rstar.json)
                stem = path.stem
                if stem in seen_files:
                    continue
                # Ignorer les variantes expérimentales, hypothèses et meta
                if "HYPOTHESIS" in stem or "_rstar" in stem:
                    continue
                entry = _load_entry(path, domain)
                if entry is not None:
                    seen_files.add(stem)
                    self._entries.append(entry)
                    key = (entry.mask, entry.domain)
                    if key not in self._by_mask_domain:
                        self._by_mask_domain[key] = entry
                    self._by_name[entry.name] = entry

    # --- Accès par clé ---

    def by_mask(self, mask: int, domain: Domain = Domain.Z_POS) -> NipadaEntry | None:
        """Entrée par masque + domaine."""
        return self._by_mask_domain.get((mask, domain))

    def by_product(self, value: int, domain: Domain = Domain.Z_POS) -> NipadaEntry | None:
        """Entrée par valeur numérique (nipada value)."""
        mask = product_to_mask(abs(value))
        if mask is None:
            return None
        if value < 0:
            domain = Domain.Z_NEG
        return self._by_mask_domain.get((mask, domain))

    def by_name(self, name: str) -> NipadaEntry | None:
        """Entrée par nom canonique (MAJUSCULES)."""
        return self._by_name.get(name.upper())

    def crossing_of(self, value: int) -> NipadaEntry | None:
        """Retourne le crossing Z- d'une molécule Z+ (par valeur)."""
        mask = product_to_mask(value)
        if mask is None:
            return None
        return self._by_mask_domain.get((mask, Domain.Z_NEG))

    def imaginary_of(self, value: int) -> NipadaEntry | None:
        """Retourne l'entrée iZ d'une molécule (si elle existe)."""
        mask = product_to_mask(value)
        if mask is None:
            return None
        return self._by_mask_domain.get((mask, Domain.IZ))

    # --- Requêtes ---

    def by_level(self, lvl: int) -> list[NipadaEntry]:
        """Toutes les entrées d'un niveau donné."""
        return [e for e in self._entries if e.lvl == lvl]

    def by_domain(self, domain: Domain) -> list[NipadaEntry]:
        """Toutes les entrées d'un domaine."""
        return [e for e in self._entries if e.domain == domain]

    def containing_atom(self, prime: int) -> list[NipadaEntry]:
        """
        Toutes les molécules Z+ contenant un atome donné (par son prime).
        """
        bit = PRIMES.index(prime)
        mask_bit = 1 << bit
        return [
            e for e in self._entries
            if e.domain == Domain.Z_POS and (e.mask & mask_bit)
        ]

    def most_similar(self, mask: int, domain: Domain = Domain.Z_POS, top: int = 3) -> list[tuple[float, NipadaEntry]]:
        """
        Retourne les top entrées les plus similaires (Jaccard sur atomes).
        """
        candidates = [e for e in self._entries if e.domain == domain and e.mask != mask]
        scored = [(jaccard(mask, e.mask), e) for e in candidates]
        scored.sort(key=lambda x: -x[0])
        return scored[:top]

    def all_positive(self) -> list[NipadaEntry]:
        """Les 15 molécules canoniques Z+, triées par niveau puis par masque."""
        return sorted(
            [e for e in self._entries if e.domain == Domain.Z_POS],
            key=lambda e: (e.lvl, e.mask)
        )

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self) -> Iterator[NipadaEntry]:
        return iter(self._entries)

    def __repr__(self) -> str:
        return f"NipadaCatalog({len(self)} entrées depuis {self._path})"

    def summary(self) -> str:
        z_pos = sum(1 for e in self._entries if e.domain == Domain.Z_POS)
        z_neg = sum(1 for e in self._entries if e.domain == Domain.Z_NEG)
        iz    = sum(1 for e in self._entries if e.domain == Domain.IZ)
        return (
            f"NipadaCatalog v1.0\n"
            f"  Z+ (positifs)  : {z_pos:2d} entrées\n"
            f"  Z- (crossings) : {z_neg:2d} entrées\n"
            f"  iZ (imaginaires): {iz:2d} entrées\n"
            f"  Total          : {len(self):2d} entrées\n"
        )


# ---------------------------------------------------------------------------
# Encodage / décodage de tokens
# ---------------------------------------------------------------------------

def encode(value: int | str) -> bytes:
    """
    Encode une valeur nipada en 1 octet.

    Format de l'octet :
        bits 7-4 : domaine + signe
            0000 = padding
            0001 = Z+ (positif)
            0010 = Z- (crossing)
            0011 = iZ (imaginaire)
        bits 3-0 : mask (0..15)

    Deux tokens nipada par octet possible avec pack_pair().
    """
    if isinstance(value, str) and value.endswith("i"):
        domain_bits = 0b0011
        mask = product_to_mask(int(value[:-1]))
    elif isinstance(value, int) and value < 0:
        domain_bits = 0b0010
        mask = product_to_mask(-value)
    elif value == 0 or value == 1:
        return bytes([0x00])  # padding
    else:
        domain_bits = 0b0001
        mask = product_to_mask(int(value))

    if mask is None:
        raise ValueError(f"Valeur nipada invalide : {value!r}")
    return bytes([(domain_bits << 4) | mask])


def decode(byte: int) -> tuple[Domain | None, int]:
    """
    Décode un octet nipada.

    Retourne (domain, mask). Domain=None pour le padding.
    """
    domain_bits = (byte >> 4) & 0x0F
    mask = byte & 0x0F
    domain_map = {
        0b0000: None,
        0b0001: Domain.Z_POS,
        0b0010: Domain.Z_NEG,
        0b0011: Domain.IZ,
    }
    return domain_map.get(domain_bits), mask


def pack_pair(value_a: int | str, value_b: int | str) -> bytes:
    """
    Encode deux tokens nipada dans un seul octet (nibble packing).

    token_a dans les bits hauts (7-4), token_b dans les bits bas (3-0).
    Applicable uniquement quand les deux sont dans le même domaine Z+.
    """
    mask_a = product_to_mask(int(value_a))
    mask_b = product_to_mask(int(value_b))
    if mask_a is None or mask_b is None:
        raise ValueError("pack_pair : valeurs Z+ uniquement")
    return bytes([(mask_a << 4) | mask_b])


def unpack_pair(byte: int) -> tuple[int, int]:
    """Décode un octet nibble-packed. Retourne (mask_a, mask_b)."""
    return (byte >> 4) & 0x0F, byte & 0x0F


# ---------------------------------------------------------------------------
# Point d'entrée pour tests rapides
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== nipada_engine v1.0 ===\n")

    # Test fonctions de base
    assert mask_to_product(0)  == 1
    assert mask_to_product(1)  == 2    # ÊTRE
    assert mask_to_product(3)  == 6    # EXISTENCE
    assert mask_to_product(15) == 210  # INTÉGRATION
    assert product_to_mask(210) == 15
    assert product_to_mask(6)   == 3
    assert product_to_mask(1)   == 0
    assert product_to_mask(4)   is None  # 4 = 2², pas un produit nipada valide
    assert level(0)  == 0
    assert level(1)  == 1
    assert level(15) == 4
    assert is_subset(3, 15)    # EXISTENCE ⊆ INTÉGRATION
    assert not is_subset(3, 8) # EXISTENCE ⊄ ORIENTATION
    assert jaccard(3, 15) == 0.5  # 2 atomes communs / 4 total

    print("Fonctions de base : OK\n")

    # Test encodage/décodage
    b = encode(210)
    dom, mask = decode(b[0])
    assert dom == Domain.Z_POS and mask == 15
    b2 = encode(-35)
    dom2, mask2 = decode(b2[0])
    assert dom2 == Domain.Z_NEG and mask2 == 12

    packed = pack_pair(2, 3)
    a, bm = unpack_pair(packed[0])
    assert a == 1 and bm == 2  # masks de ÊTRE et DIFFÉRENCE

    print("Encodage/décodage : OK\n")

    # Test catalogue
    catalog = NipadaCatalog()
    print(catalog.summary())

    e = catalog.by_product(210)
    print(f"by_product(210) → {e}")
    assert e.name == "INTÉGRATION"
    assert e.lvl == 3  # Convention JSON : atoms=0, binaires=1, ternaires=2, quaternaire=3

    e2 = catalog.by_name("MORT")
    print(f"by_name('MORT') → {e2}")
    assert e2 is not None
    assert e2.domain == Domain.Z_NEG

    e3 = catalog.crossing_of(30)
    print(f"crossing_of(30=VIE) → {e3}")
    assert e3.name == "MORT"

    e4 = catalog.imaginary_of(70)
    print(f"imaginary_of(70=INTENTION) → {e4}")
    assert e4.name == "MOI"

    print("\nMolécules contenant ÊTRE (2) :")
    for e in catalog.containing_atom(2):
        print(f"  {e}")

    print("\nMolécules niveau 2 :")
    for e in catalog.by_level(2):
        print(f"  {e}")

    sim = catalog.most_similar(mask=7, top=3)  # VIE (0b0111)
    print(f"\nLes 3 plus proches de VIE (mask=7) :")
    for score, e in sim:
        print(f"  Jaccard={score:.2f}  {e}")

    print("\nTous les invariants : OK")
