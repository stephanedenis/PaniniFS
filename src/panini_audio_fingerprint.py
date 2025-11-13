#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Panini Audio Fingerprinting - Shazam-like Audio Similarity Index

Implémente une approche type Shazam pour créer des empreintes audio
et des index de similarité permettant:
- Déduplication audio (même chanson, différents encodages)
- Recherche par similarité (covers, remixes)
- Compression sémantique (référence vers original + delta)

Architecture inspirée de:
- Shazam: spectrogramme + constellation map + hashing
- Chromaprint: empreintes perceptuelles compactes
- AcoustID: matching robuste aux transformations

Author: Équipe PaniniFS
Date: 2025-11-13
Version: 0.3.0 - Audio fingerprinting & similarity index
"""

__version__ = "0.3.0"

import hashlib
import struct
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple
import numpy as np


@dataclass
class AudioFingerprint:
    """Empreinte audio type Shazam"""
    file_hash: str                    # SHA256 du fichier original
    duration_ms: int                  # Durée en millisecondes
    sample_rate: int                  # Taux d'échantillonnage (Hz)
    channels: int                     # Nombre de canaux
    constellation_points: List[Tuple[int, int]]  # (temps_ms, fréquence_bin)
    hash_pairs: Set[str]              # Paires de points hashées
    spectral_centroid: float          # Centre spectral moyen
    zero_crossing_rate: float         # Taux de passage par zéro
    tempo_bpm: Optional[float] = None # Tempo estimé (BPM)
    key: Optional[str] = None         # Tonalité détectée
    
    def to_dict(self) -> dict:
        """Conversion en dict pour sérialisation JSON"""
        return {
            'file_hash': self.file_hash,
            'duration_ms': self.duration_ms,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'constellation_points': self.constellation_points,
            'hash_pairs': list(self.hash_pairs),
            'spectral_centroid': self.spectral_centroid,
            'zero_crossing_rate': self.zero_crossing_rate,
            'tempo_bpm': self.tempo_bpm,
            'key': self.key,
        }


class AudioFingerprintExtractor:
    """
    Extracteur d'empreintes audio type Shazam
    
    Algorithme:
    1. Conversion en mono si stéréo
    2. STFT (Short-Time Fourier Transform) → spectrogramme
    3. Détection de pics dans le spectrogramme (constellation map)
    4. Génération de paires de pics avec offset temporel
    5. Hashing des paires pour index de recherche rapide
    
    Configuration:
    - FFT size: 4096 samples (bonne résolution fréquentielle)
    - Hop size: 128 samples (overlap important)
    - Bandes de fréquence: 30 Hz - 8000 Hz (zone utile pour musique)
    - Seuil de pics: top 5% des valeurs du spectrogramme
    """
    
    # Configuration FFT
    FFT_SIZE = 4096
    HOP_SIZE = 128
    
    # Bandes de fréquence (en bins FFT)
    FREQ_BANDS = [
        (0, 10),      # 0-300 Hz (graves)
        (10, 20),     # 300-600 Hz (basses)
        (20, 40),     # 600-1200 Hz (mediums bas)
        (40, 80),     # 1200-2400 Hz (mediums)
        (80, 160),    # 2400-4800 Hz (mediums haut)
        (160, 512),   # 4800+ Hz (aigus)
    ]
    
    # Paramètres constellation map
    PEAK_THRESHOLD = 0.95  # Percentile pour détection de pics
    MIN_PEAK_DISTANCE = 5  # Distance minimale entre pics (en bins)
    
    # Paramètres hashing
    TARGET_ZONE_WIDTH = 10  # Largeur zone cible (frames)
    TARGET_ZONE_HEIGHT = 10 # Hauteur zone cible (bins fréquence)
    MAX_TIME_DELTA = 200    # Delta temps max entre pics (ms)
    
    def __init__(self):
        self.sample_rate = 44100  # Par défaut
    
    def extract_from_wav(self, data: bytes) -> AudioFingerprint:
        """
        Extrait empreinte depuis fichier WAV
        
        Format WAV (RIFF):
        - RIFF header (12 bytes)
        - fmt chunk: sample_rate, channels, bits_per_sample
        - data chunk: PCM samples
        """
        # Parser WAV header
        if len(data) < 44 or data[:4] != b'RIFF' or data[8:12] != b'WAVE':
            raise ValueError("Format WAV invalide")
        
        # Trouver fmt chunk
        offset = 12
        fmt_found = False
        while offset + 8 <= len(data):
            chunk_id = data[offset:offset+4]
            chunk_size = struct.unpack('<I', data[offset+4:offset+8])[0]
            
            if chunk_id == b'fmt ':
                # Parser fmt chunk
                fmt_data = data[offset+8:offset+8+chunk_size]
                audio_format = struct.unpack('<H', fmt_data[0:2])[0]
                channels = struct.unpack('<H', fmt_data[2:4])[0]
                sample_rate = struct.unpack('<I', fmt_data[4:8])[0]
                bits_per_sample = struct.unpack('<H', fmt_data[14:16])[0]
                fmt_found = True
            
            elif chunk_id == b'data' and fmt_found:
                # Extraire samples PCM
                pcm_data = data[offset+8:offset+8+chunk_size]
                samples = self._decode_pcm(pcm_data, bits_per_sample, channels)
                
                # Calculer durée
                duration_ms = int((len(samples) / sample_rate) * 1000)
                
                # Extraire features
                return self._extract_fingerprint(
                    samples=samples,
                    sample_rate=sample_rate,
                    channels=channels,
                    duration_ms=duration_ms,
                    file_hash=hashlib.sha256(data).hexdigest()
                )
            
            offset += 8 + chunk_size
            if chunk_size % 2 == 1:
                offset += 1
        
        raise ValueError("Chunk 'data' non trouvé dans WAV")
    
    def _decode_pcm(self, pcm_data: bytes, bits_per_sample: int,
                    channels: int) -> np.ndarray:
        """Décode PCM en array numpy float32 normalisé [-1, 1]"""
        if bits_per_sample == 16:
            samples = np.frombuffer(pcm_data, dtype=np.int16)
            samples = samples.astype(np.float32) / 32768.0
        elif bits_per_sample == 24:
            # 24-bit: 3 bytes par sample, little-endian
            samples = []
            for i in range(0, len(pcm_data), 3):
                val = int.from_bytes(pcm_data[i:i+3], 'little', signed=True)
                samples.append(val / 8388608.0)
            samples = np.array(samples, dtype=np.float32)
        elif bits_per_sample == 32:
            samples = np.frombuffer(pcm_data, dtype=np.float32)
        else:
            raise ValueError(f"Bits per sample {bits_per_sample} non supporté")
        
        # Convertir stéréo → mono (moyenne des canaux)
        if channels == 2:
            samples = samples.reshape(-1, 2).mean(axis=1)
        elif channels > 2:
            samples = samples.reshape(-1, channels).mean(axis=1)
        
        return samples
    
    def _extract_fingerprint(self, samples: np.ndarray, sample_rate: int,
                           channels: int, duration_ms: int,
                           file_hash: str) -> AudioFingerprint:
        """Extrait empreinte complète depuis samples audio"""
        self.sample_rate = sample_rate
        
        # 1. Calculer spectrogramme
        spectrogram = self._compute_spectrogram(samples)
        
        # 2. Détecter pics (constellation map)
        constellation = self._detect_peaks(spectrogram)
        
        # 3. Générer paires de hashes
        hash_pairs = self._generate_hash_pairs(constellation)
        
        # 4. Calculer features additionnelles
        spectral_centroid = self._compute_spectral_centroid(spectrogram)
        zero_crossing_rate = self._compute_zero_crossing_rate(samples)
        
        return AudioFingerprint(
            file_hash=file_hash,
            duration_ms=duration_ms,
            sample_rate=sample_rate,
            channels=channels,
            constellation_points=constellation,
            hash_pairs=hash_pairs,
            spectral_centroid=spectral_centroid,
            zero_crossing_rate=zero_crossing_rate,
        )
    
    def _compute_spectrogram(self, samples: np.ndarray) -> np.ndarray:
        """
        Calcule spectrogramme via STFT
        
        Returns:
            Array 2D (freq_bins x time_frames) avec magnitudes
        """
        # Window function (Hann pour réduire spectral leakage)
        window = np.hanning(self.FFT_SIZE)
        
        # Nombre de frames
        num_frames = (len(samples) - self.FFT_SIZE) // self.HOP_SIZE + 1
        
        # Array pour spectrogramme
        spec = np.zeros((self.FFT_SIZE // 2, num_frames))
        
        for i in range(num_frames):
            start = i * self.HOP_SIZE
            end = start + self.FFT_SIZE
            
            if end > len(samples):
                break
            
            # Fenêtre + FFT
            frame = samples[start:end] * window
            fft = np.fft.rfft(frame, n=self.FFT_SIZE)
            
            # Magnitude (ignorer phase)
            magnitude = np.abs(fft[:-1])  # Retirer Nyquist
            
            # Log scale pour compression dynamique
            spec[:, i] = np.log1p(magnitude)
        
        return spec
    
    def _detect_peaks(self, spectrogram: np.ndarray) -> List[Tuple[int, int]]:
        """
        Détecte pics dans spectrogramme (constellation map)
        
        Stratégie: Pour chaque bande de fréquence, garder top N% des pics
        avec suppression des pics trop proches (non-maximum suppression)
        
        Returns:
            Liste de (time_frame, freq_bin)
        """
        constellation = []
        
        for freq_start, freq_end in self.FREQ_BANDS:
            # Extraire bande de fréquence
            band = spectrogram[freq_start:freq_end, :]
            
            # Seuil: percentile élevé
            threshold = np.percentile(band, self.PEAK_THRESHOLD * 100)
            
            # Trouver pics au-dessus du seuil
            peaks = np.where(band > threshold)
            
            # Non-maximum suppression spatiale
            for i in range(len(peaks[0])):
                freq_bin = peaks[0][i] + freq_start
                time_frame = peaks[1][i]
                
                # Vérifier distance minimale avec pics existants
                too_close = False
                for existing_time, existing_freq in constellation:
                    time_dist = abs(time_frame - existing_time)
                    freq_dist = abs(freq_bin - existing_freq)
                    
                    if (time_dist < self.MIN_PEAK_DISTANCE and
                        freq_dist < self.MIN_PEAK_DISTANCE):
                        too_close = True
                        break
                
                if not too_close:
                    constellation.append((time_frame, freq_bin))
        
        return sorted(constellation)  # Trier par temps
    
    def _generate_hash_pairs(self,
                            constellation: List[Tuple[int, int]]) -> Set[str]:
        """
        Génère paires de hashes depuis constellation map
        
        Pour chaque pic "anchor", chercher pics "target" dans une zone
        future (TARGET_ZONE), puis hasher la combinaison:
        hash = H(freq1, freq2, delta_time)
        
        Stockage: hash → offset_anchor (pour matching rapide)
        """
        hash_pairs = set()
        
        for i, (anchor_time, anchor_freq) in enumerate(constellation):
            # Zone cible: pics futurs dans fenêtre spatio-temporelle
            for target_time, target_freq in constellation[i+1:]:
                # Contraintes zone cible
                time_delta = target_time - anchor_time
                freq_delta = abs(target_freq - anchor_freq)
                
                if time_delta > self.TARGET_ZONE_WIDTH:
                    break  # Trop loin temporellement
                
                if freq_delta > self.TARGET_ZONE_HEIGHT:
                    continue  # Trop loin fréquentiellement
                
                # Générer hash de la paire
                # Format: "f1:f2:dt:at" (freq1:freq2:delta_time:anchor_time)
                hash_str = f"{anchor_freq}:{target_freq}:{time_delta}:{anchor_time}"
                hash_val = hashlib.md5(hash_str.encode()).hexdigest()[:16]
                
                hash_pairs.add(hash_val)
        
        return hash_pairs
    
    def _compute_spectral_centroid(self, spectrogram: np.ndarray) -> float:
        """
        Centre spectral: fréquence "moyenne" du signal
        Utile pour distinguer voix vs instruments
        """
        freqs = np.arange(spectrogram.shape[0])
        
        # Moyenne pondérée des fréquences par magnitude
        centroids = []
        for frame in range(spectrogram.shape[1]):
            magnitude = spectrogram[:, frame]
            if magnitude.sum() > 0:
                centroid = np.sum(freqs * magnitude) / magnitude.sum()
                centroids.append(centroid)
        
        return float(np.mean(centroids)) if centroids else 0.0
    
    def _compute_zero_crossing_rate(self, samples: np.ndarray) -> float:
        """
        Taux de passage par zéro: indicateur de contenu haute fréquence
        Élevé → sons percussifs, voix sifflante
        Bas → sons graves, basses
        """
        zero_crossings = np.sum(np.abs(np.diff(np.sign(samples)))) / 2
        return float(zero_crossings / len(samples))


class AudioSimilarityIndex:
    """
    Index de similarité audio pour recherche rapide
    
    Architecture:
    - Index inversé: hash → [list of (file_id, offset)]
    - Scoring: nombre de hashes en commun + cohérence temporelle
    - Seuil: minimum X hashes communs pour match
    """
    
    def __init__(self):
        self.fingerprints: Dict[str, AudioFingerprint] = {}
        self.inverted_index: Dict[str, List[Tuple[str, int]]] = {}
        self.min_match_count = 5  # Minimum hashes communs
    
    def add_fingerprint(self, file_id: str, fingerprint: AudioFingerprint):
        """Ajoute empreinte à l'index"""
        self.fingerprints[file_id] = fingerprint
        
        # Indexer tous les hashes
        for i, hash_val in enumerate(fingerprint.hash_pairs):
            if hash_val not in self.inverted_index:
                self.inverted_index[hash_val] = []
            self.inverted_index[hash_val].append((file_id, i))
    
    def find_similar(self, query_fingerprint: AudioFingerprint,
                    top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Trouve fichiers similaires dans l'index
        
        Returns:
            Liste de (file_id, similarity_score) triée par score décroissant
        """
        # Compter matches par fichier
        match_counts: Dict[str, int] = {}
        
        for query_hash in query_fingerprint.hash_pairs:
            if query_hash in self.inverted_index:
                for file_id, offset in self.inverted_index[query_hash]:
                    match_counts[file_id] = match_counts.get(file_id, 0) + 1
        
        # Filtrer par seuil minimum
        candidates = [
            (file_id, count)
            for file_id, count in match_counts.items()
            if count >= self.min_match_count
        ]
        
        # Calculer score normalisé
        results = []
        for file_id, match_count in candidates:
            ref_fp = self.fingerprints[file_id]
            
            # Score Jaccard: intersection / union
            intersection = match_count
            union = (len(query_fingerprint.hash_pairs) +
                    len(ref_fp.hash_pairs) - intersection)
            
            if union > 0:
                jaccard_score = intersection / union
                
                # Bonus: similarité de features
                duration_ratio = min(
                    query_fingerprint.duration_ms / ref_fp.duration_ms,
                    ref_fp.duration_ms / query_fingerprint.duration_ms
                )
                
                centroid_diff = abs(
                    query_fingerprint.spectral_centroid -
                    ref_fp.spectral_centroid
                )
                centroid_similarity = 1.0 / (1.0 + centroid_diff / 100)
                
                # Score final: 70% Jaccard + 20% durée + 10% centroid
                final_score = (
                    0.7 * jaccard_score +
                    0.2 * duration_ratio +
                    0.1 * centroid_similarity
                )
                
                results.append((file_id, final_score))
        
        # Trier par score décroissant
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:top_k]
    
    def export_index(self) -> dict:
        """Exporte l'index pour sauvegarde JSON"""
        return {
            'fingerprints': {
                file_id: fp.to_dict()
                for file_id, fp in self.fingerprints.items()
            },
            'inverted_index': {
                hash_val: entries
                for hash_val, entries in self.inverted_index.items()
            },
            'stats': {
                'total_files': len(self.fingerprints),
                'total_hashes': len(self.inverted_index),
                'avg_hashes_per_file': sum(
                    len(fp.hash_pairs)
                    for fp in self.fingerprints.values()
                ) / max(len(self.fingerprints), 1)
            }
        }


if __name__ == '__main__':
    print("=" * 60)
    print("Panini Audio Fingerprinting - Shazam-like Similarity")
    print("=" * 60)
    print(f"Version: {__version__}")
    print()
    print("Fonctionnalités:")
    print("  ✓ Extraction empreintes audio (constellation map)")
    print("  ✓ Hashing robuste pour matching rapide")
    print("  ✓ Index inversé pour recherche O(1)")
    print("  ✓ Scoring Jaccard + features perceptuelles")
    print()
    print("Formats supportés: WAV (PCM 16/24/32-bit)")
    print("À venir: MP3, FLAC, OGG, AAC via décodeurs externes")
    print()
    print("Usage:")
    print("  from panini_audio_fingerprint import AudioFingerprintExtractor")
    print("  extractor = AudioFingerprintExtractor()")
    print("  fp = extractor.extract_from_wav(wav_data)")
    print("  # Ajouter à l'index pour recherche de similarité")
