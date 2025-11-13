#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PaniniFS Chunker - Découpage Sémantique pour Compression Asynchrone

Découpe fichiers en chunks sémantiquement cohérents pour traitement
GPU-accéléré asynchrone sur Colab Pro avec garantie bit-perfect.

Author: Équipe PaniniFS
Date: 2025-11-12
Version: 0.2.0 - Multi-format video support (MP4, MOV, WebM, AVI)
"""

__version__ = "0.2.0"

import hashlib
import json
import struct
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class ChunkStrategy(Enum):
    """Stratégies de découpage"""
    SEMANTIC = "semantic"      # Basé sur structure binaire
    SIZE = "size"              # Chunks de taille fixe
    ADAPTIVE = "adaptive"      # Hybride selon complexité


@dataclass
class ChunkMetadata:
    """Métadonnées d'un chunk pour reconstruction"""
    chunk_id: int
    offset: int
    size: int
    original_hash: str
    pattern_type: str
    dependencies: List[int]
    grammar_id: Optional[str] = None
    status: str = "pending"
    created_at: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Chunk:
    """Représentation d'un chunk de données"""
    chunk_id: int
    data: bytes
    metadata: ChunkMetadata
    reconstruction_recipe: dict


class FormatDetector:
    """Détection de format de fichier et patterns universels"""
    
    # Magic numbers connus (simples)
    # Note: RIFF géré séparément car nécessite vérification subtype
    MAGIC_NUMBERS = {
        b'\x89PNG\r\n\x1a\n': ('PNG', 'image'),
        b'\xff\xd8\xff': ('JPEG', 'image'),
        b'GIF87a': ('GIF87', 'image'),
        b'GIF89a': ('GIF89', 'image'),
        b'%PDF': ('PDF', 'document'),
        b'PK\x03\x04': ('ZIP', 'archive'),
        b'\x1f\x8b': ('GZIP', 'compressed'),
        b'BM': ('BMP', 'image'),
    }
    
    @classmethod
    def detect(cls, data: bytes) -> Tuple[str, str, Optional[str]]:
        """
        Détecte format et grammaire associée
        
        Returns:
            (format_name, category, grammar_id)
        """
        # Check magic numbers
        for magic, (fmt, cat) in cls.MAGIC_NUMBERS.items():
            if data.startswith(magic):
                grammar_id = cls._get_grammar_id(fmt)
                return (fmt, cat, grammar_id)
        
        # Special case: MP4/MOV/M4V (ISO BMFF)
        # Format: size(4 bytes) + 'ftyp' + brand
        if len(data) >= 12 and data[4:8] == b'ftyp':
            # Vérifier brands
            brand = data[8:12]
            if brand in [b'mp41', b'mp42', b'isom', b'iso2', b'avc1',
                         b'M4V ', b'M4A ']:
                return ('MP4', 'video', 'mp4_v1')
            elif brand in [b'qt  ', b'qtif']:
                return ('MOV', 'video', 'mov_v1')
        
        # Special case: WebM/MKV (Matroska/EBML)
        # EBML header: 0x1A45DFA3
        if len(data) >= 4 and data[:4] == b'\x1a\x45\xdf\xa3':
            # Parse DocType to distinguish WebM from MKV
            if b'webm' in data[:100].lower():
                return ('WebM', 'video', 'webm_v1')
            elif b'matroska' in data[:100].lower():
                return ('MKV', 'video', 'mkv_v1')
        
        # Special case: RIFF with subtype (AVI, WAV, WebP)
        if data.startswith(b'RIFF') and len(data) >= 12:
            riff_type = data[8:12]
            if riff_type == b'WAVE':
                return ('WAV', 'audio', 'riff_wav')
            elif riff_type == b'WEBP':
                return ('WebP', 'image', 'riff_webp')
            elif riff_type == b'AVI ':
                return ('AVI', 'video', 'avi_v1')
        
        # Fallback: binary detection
        if cls._is_text(data[:512]):
            return ('TEXT', 'text', 'text_generic')
        else:
            return ('BINARY', 'binary', 'binary_generic')
    
    @staticmethod
    def _get_grammar_id(format_name: str) -> str:
        """Map format vers grammar ID"""
        grammar_map = {
            'PNG': 'png_v1',
            'JPEG': 'jpeg_v1',
            'GIF87': 'gif87_v1',
            'GIF89': 'gif89_v1',
            'PDF': 'pdf_v1',
            'ZIP': 'zip_v1',
            'GZIP': 'gzip_v1',
            'BMP': 'bmp_v1',
            'MP4': 'mp4_v1',
        }
        return grammar_map.get(format_name, 'generic_binary_v1')
    
    @staticmethod
    def _is_text(data: bytes) -> bool:
        """Détection heuristique de texte"""
        try:
            data.decode('utf-8')
            return True
        except UnicodeDecodeError:
            # Check ASCII printable ratio
            printable = sum(1 for b in data if 32 <= b <= 126 or b in [9, 10, 13])
            return printable / len(data) > 0.85 if data else False


class SemanticChunker:
    """Découpage sémantique basé sur structure binaire"""
    
    def __init__(self, grammar_id: str):
        self.grammar_id = grammar_id
    
    def chunk(self, data: bytes, max_chunk_size: int = 1024 * 1024) -> List[Tuple[int, int, str]]:
        """
        Découpe selon patterns sémantiques
        
        Returns:
            List of (offset, size, pattern_type)
        """
        chunks = []
        
        if self.grammar_id == 'png_v1':
            chunks = self._chunk_png(data)
        elif self.grammar_id == 'jpeg_v1':
            chunks = self._chunk_jpeg(data)
        elif self.grammar_id in ['mp4_v1', 'mov_v1']:
            # MP4 et MOV utilisent ISO Base Media File Format
            chunks = self._chunk_isobmff(data)
        elif self.grammar_id in ['webm_v1', 'mkv_v1']:
            # WebM et MKV utilisent Matroska/EBML
            chunks = self._chunk_ebml(data)
        elif self.grammar_id == 'avi_v1':
            # AVI utilise RIFF mais avec découpage vidéo spécifique
            chunks = self._chunk_avi(data)
        elif self.grammar_id.startswith('riff_'):
            chunks = self._chunk_riff(data)
        elif self.grammar_id == 'pdf_v1':
            chunks = self._chunk_pdf(data)
        else:
            # Fallback: fixed size chunks
            chunks = self._chunk_fixed_size(data, max_chunk_size)
        
        return chunks
    
    def _chunk_png(self, data: bytes) -> List[Tuple[int, int, str]]:
        """Découpage PNG par chunks IHDR, PLTE, IDAT, etc."""
        chunks = []
        
        # Signature (8 bytes)
        chunks.append((0, 8, 'PNG_SIGNATURE'))
        
        offset = 8
        while offset + 12 <= len(data):
            # Length (4 bytes)
            length = struct.unpack('>I', data[offset:offset+4])[0]
            
            # Chunk type (4 bytes)
            chunk_type = data[offset+4:offset+8].decode('ascii', errors='ignore')
            
            # Total: length + type + data + CRC
            chunk_size = 4 + 4 + length + 4
            
            if offset + chunk_size > len(data):
                break
            
            chunks.append((offset, chunk_size, f'PNG_{chunk_type}'))
            offset += chunk_size
        
        return chunks
    
    def _chunk_jpeg(self, data: bytes) -> List[Tuple[int, int, str]]:
        """Découpage JPEG par segments (SOI, APP, DQT, SOF, SOS, EOI)"""
        chunks = []
        
        # SOI marker (2 bytes)
        if data[:2] == b'\xff\xd8':
            chunks.append((0, 2, 'JPEG_SOI'))
        
        offset = 2
        while offset + 2 <= len(data):
            if data[offset] != 0xff:
                break
            
            marker = data[offset+1]
            
            # Special markers without length
            if marker in [0xd8, 0xd9, 0x01] or (0xd0 <= marker <= 0xd7):
                chunks.append((offset, 2, f'JPEG_MARKER_{marker:02X}'))
                offset += 2
                continue
            
            # Markers with length
            if offset + 4 > len(data):
                break
            
            length = struct.unpack('>H', data[offset+2:offset+4])[0]
            segment_size = 2 + length
            
            if offset + segment_size > len(data):
                break
            
            marker_name = self._get_jpeg_marker_name(marker)
            chunks.append((offset, segment_size, f'JPEG_{marker_name}'))
            
            # SOS: start of scan, contains image data until EOI
            if marker == 0xda:
                # Find next marker or EOI
                scan_end = offset + segment_size
                while scan_end + 1 < len(data):
                    if data[scan_end] == 0xff and data[scan_end+1] != 0x00:
                        break
                    scan_end += 1
                
                # Image data chunk
                if scan_end > offset + segment_size:
                    chunks.append((offset + segment_size, 
                                 scan_end - (offset + segment_size), 
                                 'JPEG_SCAN_DATA'))
                offset = scan_end
            else:
                offset += segment_size
        
        return chunks
    
    def _chunk_riff(self, data: bytes) -> List[Tuple[int, int, str]]:
        """Découpage RIFF (WAV, WebP, AVI)"""
        chunks = []
        
        # RIFF header (12 bytes: RIFF + size + type)
        if len(data) >= 12:
            chunks.append((0, 12, 'RIFF_HEADER'))
        
        offset = 12
        while offset + 8 <= len(data):
            # FourCC (4 bytes)
            fourcc = data[offset:offset+4].decode('ascii', errors='ignore')
            
            # Size (4 bytes, little-endian)
            size = struct.unpack('<I', data[offset+4:offset+8])[0]
            
            # Total chunk size (aligned to even boundary)
            chunk_size = 8 + size
            if size % 2 == 1:
                chunk_size += 1
            
            if offset + chunk_size > len(data):
                break
            
            chunks.append((offset, chunk_size, f'RIFF_{fourcc}'))
            offset += chunk_size
        
        return chunks
    
    def _chunk_pdf(self, data: bytes) -> List[Tuple[int, int, str]]:
        """Découpage PDF par objets"""
        # Simplified: split on %%EOF for now
        chunks = []
        text = data.decode('latin-1', errors='ignore')
        
        # Header
        pdf_start = text.find('%PDF')
        if pdf_start >= 0:
            header_end = text.find('\n', pdf_start)
            chunks.append((pdf_start, header_end - pdf_start + 1, 'PDF_HEADER'))
        
        # Find objects (simplified)
        offset = 0
        while True:
            obj_start = text.find('\nobj\n', offset)
            if obj_start == -1:
                break
            
            obj_end = text.find('\nendobj', obj_start)
            if obj_end == -1:
                break
            
            obj_end += 7  # len('\nendobj')
            chunks.append((obj_start, obj_end - obj_start, 'PDF_OBJECT'))
            offset = obj_end
        
        # If no chunks, fallback to fixed size
        if not chunks:
            return self._chunk_fixed_size(data, 64 * 1024)
        
        return chunks
    
    def _chunk_isobmff(self, data: bytes) -> List[Tuple[int, int, str]]:
        """
        Découpage ISO Base Media File Format (MP4/MOV/M4V)
        
        Structure commune:
        - ftyp: File type box
        - moov: Movie metadata (contient stss = sync sample table)
        - mdat: Media data (audio/vidéo samples)
        
        Note: Pour extraction complète des keyframes, il faudrait parser
        moov>trak>mdia>minf>stbl>stss (sync sample table)
        """
        chunks = []
        offset = 0
        
        # Parse ISO BMFF boxes
        while offset + 8 <= len(data):
            # Box header: size (4 bytes) + type (4 bytes)
            box_size = struct.unpack('>I', data[offset:offset+4])[0]
            box_type = data[offset+4:offset+8].decode('ascii',
                                                      errors='ignore')
            
            # Handle extended size (size == 1 means 64-bit size follows)
            if box_size == 1 and offset + 16 <= len(data):
                box_size = struct.unpack('>Q', data[offset+8:offset+16])[0]
                header_size = 16
            else:
                header_size = 8
            
            # Size == 0 means box extends to end of file
            if box_size == 0:
                box_size = len(data) - offset
            
            # Validate box size
            if box_size < header_size:
                break
            
            if offset + box_size > len(data):
                break
            
            # Classify box type (patterns génériques pour MP4/MOV)
            if box_type == 'ftyp':
                pattern = 'ISOBMFF_FTYP'
            elif box_type == 'moov':
                pattern = 'ISOBMFF_MOOV_METADATA'
            elif box_type == 'mdat':
                pattern = 'ISOBMFF_MDAT_MEDIA'
            elif box_type == 'free' or box_type == 'skip':
                pattern = 'ISOBMFF_FREE_SPACE'
            elif box_type == 'moof':
                pattern = 'ISOBMFF_MOOF_FRAGMENT'
            elif box_type == 'sidx':
                pattern = 'ISOBMFF_SIDX_INDEX'
            elif box_type == 'wide':
                pattern = 'ISOBMFF_WIDE'
            else:
                pattern = f'ISOBMFF_BOX_{box_type.upper()}'
            
            chunks.append((offset, box_size, pattern))
            offset += box_size
        
        return chunks
    
    def _chunk_ebml(self, data: bytes) -> List[Tuple[int, int, str]]:
        """
        Découpage EBML (WebM/MKV Matroska)
        
        Structure hiérarchique avec VINT (Variable Integer):
        - EBML Header
        - Segment (container principal)
          - SeekHead, Info, Tracks, Cluster (frames), Cues (index)
        
        Note: Parsing EBML complet nécessiterait bibliothèque spécialisée.
        Implémentation simplifiée: découpage par éléments top-level.
        """
        chunks = []
        offset = 0
        
        # EBML header signature
        if len(data) >= 4 and data[:4] == b'\x1a\x45\xdf\xa3':
            # Parse EBML header (approximatif)
            # Element ID (4 bytes) + Size (VINT variable)
            # Pour simplifier, on prend les premiers ~100 bytes
            header_end = min(100, len(data))
            chunks.append((0, header_end, 'EBML_HEADER'))
            offset = header_end
        
        # Pour le reste, découpage fixe avec patterns
        # TODO: Implémenter parsing VINT complet pour Segment/Cluster
        while offset < len(data):
            chunk_size = min(1024 * 1024, len(data) - offset)
            
            # Tenter de détecter éléments connus
            if offset + 4 <= len(data):
                elem_id = data[offset:offset+4]
                if elem_id == b'\x18\x53\x80\x67':  # Segment
                    pattern = 'EBML_SEGMENT'
                elif elem_id == b'\x1f\x43\xb6\x75':  # Cluster
                    pattern = 'EBML_CLUSTER'
                elif elem_id == b'\x16\x54\xae\x6b':  # Tracks
                    pattern = 'EBML_TRACKS'
                elif elem_id == b'\x15\x49\xa9\x66':  # Info
                    pattern = 'EBML_INFO'
                else:
                    pattern = 'EBML_DATA'
            else:
                pattern = 'EBML_DATA'
            
            chunks.append((offset, chunk_size, pattern))
            offset += chunk_size
        
        return chunks
    
    def _chunk_avi(self, data: bytes) -> List[Tuple[int, int, str]]:
        """
        Découpage AVI (RIFF avec structure vidéo)
        
        Structure:
        - RIFF header + 'AVI ' type
        - LIST hdrl (headers: avih, strl)
        - LIST movi (movie data: frames 00dc/01wb)
        - idx1 (index)
        """
        chunks = []
        
        # RIFF header (12 bytes: 'RIFF' + size + 'AVI ')
        if len(data) >= 12 and data[:4] == b'RIFF':
            chunks.append((0, 12, 'AVI_RIFF_HEADER'))
            offset = 12
        else:
            return self._chunk_riff(data)
        
        # Parse RIFF chunks
        while offset + 8 <= len(data):
            chunk_id = data[offset:offset+4]
            chunk_size = struct.unpack('<I', data[offset+4:offset+8])[0]
            
            # Align to word boundary
            padded_size = (chunk_size + 1) & ~1
            total_size = 8 + padded_size
            
            if offset + total_size > len(data):
                break
            
            # Classifier les chunks AVI
            chunk_id_str = chunk_id.decode('ascii', errors='ignore')
            if chunk_id == b'LIST':
                # LIST chunks contiennent type (4 bytes) puis sub-chunks
                if offset + 12 <= len(data):
                    list_type = data[offset+8:offset+12].decode('ascii',
                                                                errors='ignore')
                    if list_type == 'hdrl':
                        pattern = 'AVI_LIST_HEADERS'
                    elif list_type == 'movi':
                        pattern = 'AVI_LIST_MOVIE_DATA'
                    elif list_type == 'INFO':
                        pattern = 'AVI_LIST_INFO'
                    else:
                        pattern = f'AVI_LIST_{list_type.upper()}'
                else:
                    pattern = 'AVI_LIST'
            elif chunk_id == b'idx1':
                pattern = 'AVI_INDEX'
            elif chunk_id_str.endswith('dc'):  # Video frame (00dc, 01dc)
                pattern = 'AVI_VIDEO_FRAME'
            elif chunk_id_str.endswith('wb'):  # Audio data (01wb)
                pattern = 'AVI_AUDIO_DATA'
            else:
                pattern = f'AVI_CHUNK_{chunk_id_str.upper()}'
            
            chunks.append((offset, total_size, pattern))
            offset += total_size
        
        return chunks
    
    def _chunk_fixed_size(
            self, data: bytes, chunk_size: int
    ) -> List[Tuple[int, int, str]]:
        """Découpage taille fixe"""
        chunks = []
        offset = 0
        
        while offset < len(data):
            size = min(chunk_size, len(data) - offset)
            chunks.append((offset, size, 'FIXED_SIZE'))
            offset += size
        
        return chunks
    
    @staticmethod
    def _get_jpeg_marker_name(marker: int) -> str:
        """Map JPEG marker byte to name"""
        markers = {
            0xd8: 'SOI', 0xd9: 'EOI', 0xda: 'SOS', 0xdb: 'DQT',
            0xc0: 'SOF0', 0xc2: 'SOF2', 0xc4: 'DHT', 0xdd: 'DRI',
            0xe0: 'APP0', 0xe1: 'APP1', 0xfe: 'COM'
        }
        return markers.get(marker, f'MARKER_{marker:02X}')


class PaniniFSChunker:
    """
    Chunker principal pour compression asynchrone bit-perfect
    """
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def chunk_file(self, 
                   file_path: Path, 
                   strategy: ChunkStrategy = ChunkStrategy.SEMANTIC,
                   max_chunk_size: int = 1024 * 1024) -> List[Chunk]:
        """
        Découpe fichier en chunks sémantiques
        
        Args:
            file_path: Chemin du fichier à découper
            strategy: Stratégie de chunking
            max_chunk_size: Taille max d'un chunk (pour SIZE et ADAPTIVE)
        
        Returns:
            Liste de Chunk objets
        """
        print(f"📂 Chunking file: {file_path}")
        print(f"   Strategy: {strategy.value}")
        
        # Lecture fichier
        data = file_path.read_bytes()
        original_hash = hashlib.sha256(data).hexdigest()
        
        print(f"   Size: {len(data):,} bytes")
        print(f"   Hash: {original_hash[:16]}...")
        
        # Détection format
        format_name, category, grammar_id = FormatDetector.detect(data)
        print(f"   Format: {format_name} ({category})")
        print(f"   Grammar: {grammar_id}")
        
        # Découpage selon stratégie
        if strategy == ChunkStrategy.SEMANTIC:
            chunker = SemanticChunker(grammar_id)
            chunk_specs = chunker.chunk(data, max_chunk_size)
        elif strategy == ChunkStrategy.SIZE:
            chunk_specs = self._chunk_by_size(data, max_chunk_size)
        else:  # ADAPTIVE
            chunk_specs = self._chunk_adaptive(data, format_name, max_chunk_size)
        
        print(f"   Chunks: {len(chunk_specs)}")
        
        # Création objets Chunk
        chunks = []
        for i, (offset, size, pattern_type) in enumerate(chunk_specs):
            chunk_data = data[offset:offset+size]
            chunk_hash = hashlib.sha256(chunk_data).hexdigest()
            
            metadata = ChunkMetadata(
                chunk_id=i,
                offset=offset,
                size=size,
                original_hash=chunk_hash,
                pattern_type=pattern_type,
                dependencies=[],
                grammar_id=grammar_id,
                status="pending",
                created_at=datetime.now().isoformat()
            )
            
            recipe = self._generate_reconstruction_recipe(
                chunk_id=i,
                offset=offset,
                size=size,
                pattern_type=pattern_type,
                grammar_id=grammar_id,
                total_chunks=len(chunk_specs)
            )
            
            chunk = Chunk(
                chunk_id=i,
                data=chunk_data,
                metadata=metadata,
                reconstruction_recipe=recipe
            )
            chunks.append(chunk)
        
        return chunks
    
    def save_chunks_to_git(self, chunks: List[Chunk], base_name: str) -> Path:
        """
        Sauvegarde chunks dans structure Git
        
        Returns:
            Path du répertoire de chunks
        """
        chunks_dir = self.output_dir / base_name
        chunks_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n💾 Saving {len(chunks)} chunks to: {chunks_dir}")
        
        for chunk in chunks:
            chunk_dir = chunks_dir / f"chunk_{chunk.chunk_id:04d}"
            chunk_dir.mkdir(parents=True, exist_ok=True)
            
            # Données brutes
            data_file = chunk_dir / 'data.bin'
            data_file.write_bytes(chunk.data)
            
            # Métadonnées JSON
            meta_file = chunk_dir / 'metadata.json'
            meta_file.write_text(json.dumps(chunk.metadata.to_dict(), indent=2))
            
            # Recipe reconstruction
            recipe_file = chunk_dir / 'reconstruction.recipe'
            recipe_file.write_text(json.dumps(chunk.reconstruction_recipe, indent=2))
            
            print(f"   ✅ chunk_{chunk.chunk_id:04d}: {chunk.metadata.size:,} bytes ({chunk.metadata.pattern_type})")
        
        # Manifest global
        manifest = {
            'base_name': base_name,
            'total_chunks': len(chunks),
            'created_at': datetime.now().isoformat(),
            'grammar_id': chunks[0].metadata.grammar_id if chunks else None,
            'chunks': [
                {
                    'chunk_id': c.chunk_id,
                    'offset': c.metadata.offset,
                    'size': c.metadata.size,
                    'hash': c.metadata.original_hash,
                    'pattern': c.metadata.pattern_type
                }
                for c in chunks
            ]
        }
        
        manifest_file = chunks_dir / 'manifest.json'
        manifest_file.write_text(json.dumps(manifest, indent=2))
        print(f"\n📋 Manifest: {manifest_file}")
        
        return chunks_dir
    
    def _chunk_by_size(self, data: bytes, chunk_size: int) -> List[Tuple[int, int, str]]:
        """Chunking taille fixe"""
        chunks = []
        offset = 0
        
        while offset < len(data):
            size = min(chunk_size, len(data) - offset)
            chunks.append((offset, size, 'FIXED_SIZE'))
            offset += size
        
        return chunks
    
    def _chunk_adaptive(self, data: bytes, format_name: str, 
                       max_chunk_size: int) -> List[Tuple[int, int, str]]:
        """Chunking adaptatif: sémantique si possible, sinon taille fixe"""
        # Try semantic first
        grammar_id = FormatDetector._get_grammar_id(format_name)
        
        if grammar_id != 'generic_binary_v1':
            chunker = SemanticChunker(grammar_id)
            return chunker.chunk(data, max_chunk_size)
        else:
            return self._chunk_by_size(data, max_chunk_size)
    
    def _generate_reconstruction_recipe(self, chunk_id: int, offset: int,
                                       size: int, pattern_type: str,
                                       grammar_id: str, total_chunks: int) -> dict:
        """Génère recipe de reconstruction bit-perfect"""
        return {
            'version': '1.0',
            'chunk_id': chunk_id,
            'grammar_id': grammar_id,
            'pattern_type': pattern_type,
            'reconstruction_steps': [
                {
                    'step': 1,
                    'operation': 'LOAD_CHUNK_DATA',
                    'description': 'Load chunk binary data'
                },
                {
                    'step': 2,
                    'operation': 'VALIDATE_HASH',
                    'description': 'Verify chunk integrity via SHA-256'
                },
                {
                    'step': 3,
                    'operation': 'DECOMPRESS',
                    'description': 'Semantic decompression using grammar'
                },
                {
                    'step': 4,
                    'operation': 'ASSEMBLE',
                    'description': 'Assemble at original offset',
                    'offset': offset,
                    'size': size
                }
            ],
            'assembly_info': {
                'offset': offset,
                'size': size,
                'total_chunks': total_chunks,
                'ordering': chunk_id
            },
            'validation': {
                'method': 'SHA-256',
                'expected_size': size
            }
        }


def main():
    """CLI pour chunker"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PaniniFS Chunker - Semantic File Chunking')
    parser.add_argument('file', type=Path, help='File to chunk')
    parser.add_argument('--output', type=Path, default=Path('pending_compression'),
                       help='Output directory (default: pending_compression/)')
    parser.add_argument('--strategy', choices=['semantic', 'size', 'adaptive'],
                       default='semantic', help='Chunking strategy')
    parser.add_argument('--chunk-size', type=int, default=1024*1024,
                       help='Max chunk size in bytes (default: 1MB)')
    
    args = parser.parse_args()
    
    if not args.file.exists():
        print(f"❌ Error: File not found: {args.file}")
        return 1
    
    # Chunking
    chunker = PaniniFSChunker(args.output)
    strategy = ChunkStrategy(args.strategy)
    
    chunks = chunker.chunk_file(
        args.file,
        strategy=strategy,
        max_chunk_size=args.chunk_size
    )
    
    # Sauvegarde
    base_name = args.file.stem
    chunks_dir = chunker.save_chunks_to_git(chunks, base_name)
    
    print(f"\n✅ Chunking completed!")
    print(f"   Directory: {chunks_dir}")
    print(f"   Ready for: git add {chunks_dir} && git commit && git push")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
