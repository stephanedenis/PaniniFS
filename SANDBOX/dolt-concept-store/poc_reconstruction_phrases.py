#!/usr/bin/env python3
"""
poc_reconstruction_phrases.py — POC v3-alpha : Reconstruction phrase-level

Objectif : Démontrer que le découpage phrase-par-phrase + attribution mot→atome
ciblée réduit drastiquement le bruit (de ~19 concepts/segment à ~2-4 concepts/phrase).

Pipeline :
  1. Appliquer le schéma v3 (4 tables + 2 vues)
  2. Découper les segments existants en phrases
  3. Alignement séquentiel inter-éditions (même passage, même index)
  4. Attribution mot→atome ciblée (chaque mot → son atome spécifique)
  5. Détection de concepts phrase-level (fenêtre syntaxique)
  6. Calcul du profil stylistique par traducteur
  7. Rapport comparatif : segment-level vs phrase-level
  8. Commit Dolt

Usage :
  cd SANDBOX/dolt-concept-store
  python3 poc_reconstruction_phrases.py
"""

import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import date

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

DOLT_DB = os.path.join(os.path.dirname(__file__), "panini-unified-db")
CORPUS_DIR = os.path.join(os.path.dirname(__file__), "gutenberg_corpus")
SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "schema_v3_reconstruction.sql")
TODAY = date.today().isoformat()

# Import the ATOM_KEYWORDS and EDITIONS from the existing validator
sys.path.insert(0, os.path.dirname(__file__))
from gutenberg_multilingual_validator import (
    ATOM_KEYWORDS, EDITIONS, ALICE_KEY_PASSAGES, CANDIDE_KEY_PASSAGES,
    strip_gutenberg_header_footer, extract_segment
)

# Focus passage for detailed POC — Alice ch01_falling (all 6 languages)
FOCUS_SEGMENT_REF = "ch01_falling"
FOCUS_WORK_ID = "ALICE"


# ─────────────────────────────────────────────────────────────────────────────
# Dolt helpers (reuse pattern from validator)
# ─────────────────────────────────────────────────────────────────────────────

def dolt_sql(query, check=True):
    env = os.environ.copy()
    env["DOLT_CLI_NO_PAGER"] = "1"
    r = subprocess.run(
        ["dolt", "sql", "-r", "csv", "-q", query],
        capture_output=True, text=True, cwd=DOLT_DB, env=env
    )
    if check and r.returncode != 0:
        print(f"  ⚠️  SQL error: {r.stderr.strip()[:200]}")
        return None
    return r.stdout.strip()


def dolt_source(filepath):
    env = os.environ.copy()
    env["DOLT_CLI_NO_PAGER"] = "1"
    r = subprocess.run(
        ["dolt", "sql", "--file", filepath],
        capture_output=True, text=True, cwd=DOLT_DB, env=env
    )
    return r.returncode == 0


def dolt_commit(message):
    env = os.environ.copy()
    env["DOLT_CLI_NO_PAGER"] = "1"
    subprocess.run(
        ["dolt", "add", "."],
        capture_output=True, text=True, cwd=DOLT_DB, env=env
    )
    r = subprocess.run(
        ["dolt", "commit", "-m", message, "--allow-empty"],
        capture_output=True, text=True, cwd=DOLT_DB, env=env
    )
    return r.returncode == 0


def esc(val):
    if val is None:
        return "NULL"
    return "'" + str(val).replace("'", "''").replace("\\", "\\\\") + "'"


# ─────────────────────────────────────────────────────────────────────────────
# Step 1: Apply v3 schema
# ─────────────────────────────────────────────────────────────────────────────

def step1_apply_schema():
    """Apply the v3 reconstruction schema (4 tables + 2 views).
    
    Uses inline SQL instead of --file to avoid Dolt issues with
    special characters in SQL comments.
    """
    print("\n" + "=" * 70)
    print("STEP 1: Applying v3 reconstruction schema")
    print("=" * 70)

    # Read schema file and extract SQL statements (skip comments)
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        schema_text = f.read()

    # Extract SQL statements between semicolons, skipping comment-only blocks
    statements = []
    for stmt in schema_text.split(';'):
        # Remove comment lines
        lines = [l for l in stmt.strip().split('\n')
                 if l.strip() and not l.strip().startswith('--')]
        clean = '\n'.join(lines).strip()
        if clean and ('CREATE' in clean.upper() or 'INSERT' in clean.upper()):
            statements.append(clean)

    for stmt in statements:
        keyword = stmt.split()[0:4]
        label = ' '.join(keyword)
        result = dolt_sql(stmt, check=False)
        print(f"  ✅ {label}...")

    # Verify
    tables = dolt_sql("SHOW TABLES")
    for t in ["gutenberg_sentences", "word_atom_attributions",
              "sentence_concepts", "translator_style_profile"]:
        if t in tables:
            print(f"  ✅ Table: {t}")
        else:
            print(f"  ❌ Missing table: {t}")
            return False
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Step 2: Split segments into sentences
# ─────────────────────────────────────────────────────────────────────────────

def split_into_sentences(text, lang):
    """Split text into sentences using language-aware heuristics.
    
    Not using NLP libraries (no dependency) — rule-based splitting that
    handles:
    - Standard sentence-ending punctuation (. ! ?)
    - Abbreviations (Mr., Mrs., Dr., etc.)
    - Dialogue quotes
    - Ellipsis (...)
    """
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Sentence-ending patterns
    # Split on . ! ? followed by space + uppercase letter (or end of string)
    # But not on common abbreviations
    abbreviations = {
        "en": r"(?:Mr|Mrs|Ms|Dr|St|Jr|Sr|vs|etc|Vol|Ch|Fig|No|pp)",
        "fr": r"(?:Mr|Mme|Mlle|Dr|St|etc|vol|ch|fig|pp|av|J.-C)",
        "de": r"(?:Hr|Fr|Dr|St|Nr|Bd|Kap|usw|bzw|vgl|sog)",
        "it": r"(?:Sig|Dott|Prof|ecc|vol|cap|fig|pag)",
        "es": r"(?:Sr|Sra|Dr|Ud|Uds|etc|vol|cap|fig|pág)",
        "eo": r"(?:S-ro|S-ino|D-ro|k\.t\.p)",
        "fi": r"(?:hr|rva|tri|prof|esim|jne|ks|mm)",
    }

    abbr = abbreviations.get(lang, abbreviations["en"])

    # Split strategy: use regex to find sentence boundaries
    # A sentence ends with [.!?] followed by whitespace + uppercase or end
    sentences = []
    current = []

    # Simple but effective: split on sentence-ending punctuation
    parts = re.split(r'([.!?]+(?:\s+|$))', text)

    buffer = ""
    for i, part in enumerate(parts):
        buffer += part
        # Check if this looks like a sentence end
        if re.search(r'[.!?]\s*$', buffer):
            # Check it's not an abbreviation
            if re.search(abbr + r'\.\s*$', buffer):
                continue  # Abbreviation, keep accumulating
            sentence = buffer.strip()
            if sentence and len(sentence) > 5:  # Skip very short fragments
                sentences.append(sentence)
            buffer = ""

    # Don't forget remaining text
    if buffer.strip() and len(buffer.strip()) > 5:
        sentences.append(buffer.strip())

    return sentences


def step2_split_into_sentences():
    """Split existing segments into individual sentences."""
    print("\n" + "=" * 70)
    print(f"STEP 2: Splitting segments into sentences (focus: {FOCUS_SEGMENT_REF})")
    print("=" * 70)

    passages = ALICE_KEY_PASSAGES if FOCUS_WORK_ID == "ALICE" else CANDIDE_KEY_PASSAGES
    passage = passages.get(FOCUS_SEGMENT_REF)
    if not passage:
        print(f"  ❌ Passage {FOCUS_SEGMENT_REF} not found")
        return False

    total_sentences = 0
    edition_sentences = {}  # edition_id → list of sentences

    for eid, e in EDITIONS.items():
        if e["work_id"] != FOCUS_WORK_ID:
            continue
        lang = e["lang"]
        if lang not in passage.get("markers", {}):
            continue

        # Get segment_id from Dolt
        seg_result = dolt_sql(
            f"SELECT id FROM gutenberg_segments "
            f"WHERE edition_id = {esc(eid)} AND segment_ref = {esc(FOCUS_SEGMENT_REF)}"
        )
        if not seg_result:
            continue
        lines = seg_result.strip().split('\n')
        if len(lines) < 2:
            continue
        segment_id = int(lines[1].strip())

        # Load text from local corpus
        filepath = os.path.join(CORPUS_DIR, f"pg{e['gutenberg_id']}_{lang}.txt")
        if not os.path.exists(filepath):
            print(f"  ⚠️  [{lang}] Corpus file not found: {filepath}")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            full_text = f.read()

        clean_text = strip_gutenberg_header_footer(full_text)
        markers = passage["markers"][lang]
        segment_text = extract_segment(clean_text, markers)

        if not segment_text:
            print(f"  ⚠️  [{lang}] Segment not found for markers")
            continue

        # Split into sentences
        sentences = split_into_sentences(segment_text, lang)
        edition_sentences[eid] = sentences

        for idx, sent in enumerate(sentences):
            word_count = len(sent.split())
            char_count = len(sent)
            alignment_group = f"{FOCUS_SEGMENT_REF}_s{idx:03d}"

            sql = (
                f"INSERT IGNORE INTO gutenberg_sentences "
                f"(segment_id, sentence_index, text_content, word_count, char_count, "
                f"lang, alignment_group, alignment_confidence, alignment_method) VALUES ("
                f"{segment_id}, {idx}, {esc(sent[:2000])}, {word_count}, {char_count}, "
                f"{esc(lang)}, {esc(alignment_group)}, 0.5, 'sequential')"
            )
            dolt_sql(sql, check=False)
            total_sentences += 1

        print(f"  ✅ [{lang}] {eid}: {len(sentences)} phrases (segment {segment_id})")
        for i, s in enumerate(sentences[:5]):
            preview = s[:80] + "..." if len(s) > 80 else s
            print(f"      {i}: {preview}")
        if len(sentences) > 5:
            print(f"      ... (+{len(sentences) - 5} more)")

    print(f"\n  → {total_sentences} phrases insérées")
    return total_sentences > 0


# ─────────────────────────────────────────────────────────────────────────────
# Step 3: Word-level atom attribution
# ─────────────────────────────────────────────────────────────────────────────

def attribute_atoms_to_words(sentence_text, lang):
    """Attribute each atom to the specific word(s) that carry it.
    
    Returns list of (word_position, word_form, atom_id, confidence, keyword_matched).
    
    Key difference from detect_atoms_in_text:
    - That function: "are atoms present in this 500-word segment?" → bag
    - This function: "which specific word carries which atom?" → targeted
    """
    words = sentence_text.split()
    attributions = []

    for word_pos, word_form in enumerate(words):
        word_lower = word_form.lower().strip('.,;:!?"\'"()[]{}—–-')
        if len(word_lower) < 2:
            continue

        for atom, keywords_by_lang in ATOM_KEYWORDS.items():
            if lang not in keywords_by_lang:
                continue

            for kw in keywords_by_lang[lang]:
                kw_lower = kw.lower()
                # Match: exact word, or word starts with keyword (for inflections)
                if word_lower == kw_lower or (
                    len(kw_lower) >= 4 and word_lower.startswith(kw_lower[:max(4, len(kw_lower)-2)])
                ):
                    # Confidence based on match quality
                    if word_lower == kw_lower:
                        confidence = 0.95  # Exact match
                    elif word_lower.startswith(kw_lower):
                        confidence = 0.80  # Prefix match (inflection)
                    else:
                        confidence = 0.60  # Stem match

                    attributions.append({
                        "word_position": word_pos,
                        "word_form": word_form,
                        "word_lemma": kw,  # The keyword serves as approximate lemma
                        "atom_id": atom,
                        "confidence": confidence,
                        "keyword_matched": kw,
                    })
                    break  # One keyword per atom per word

    return attributions


def step3_word_atom_attribution():
    """Attribute atoms to specific words in each sentence.
    
    Strategy: query sentence IDs and metadata separately from text content
    to avoid CSV parsing issues with multilingual text containing commas.
    """
    print("\n" + "=" * 70)
    print("STEP 3: Word-level atom attribution (mot → atome ciblé)")
    print("=" * 70)

    # Get sentence IDs and metadata (no text — avoids CSV issues)
    result = dolt_sql(
        f"SELECT gs.id, gs.lang, gs.sentence_index "
        f"FROM gutenberg_sentences gs "
        f"JOIN gutenberg_segments seg ON gs.segment_id = seg.id "
        f"WHERE seg.segment_ref = {esc(FOCUS_SEGMENT_REF)} "
        f"ORDER BY gs.lang, gs.sentence_index"
    )

    if not result:
        print("  ❌ No sentences found")
        return False

    lines = result.strip().split('\n')
    total_attributions = 0

    for line in lines[1:]:
        parts = line.split(',')
        if len(parts) < 3:
            continue

        sent_id = int(parts[0].strip())
        lang = parts[1].strip()
        sent_idx = parts[2].strip()

        # Get text content separately using CONCAT to avoid CSV issues
        # Use REPLACE to remove commas from the text in the query
        text_result = dolt_sql(
            f"SELECT CHAR_LENGTH(text_content), text_content "
            f"FROM gutenberg_sentences WHERE id = {sent_id}"
        )
        if not text_result:
            continue

        # Parse: first line is header, second line is "length,text..."
        text_lines = text_result.strip().split('\n')
        if len(text_lines) < 2:
            continue

        # The text may span multiple lines due to newlines in content
        # Join everything after header, then extract
        full_data = '\n'.join(text_lines[1:])
        first_comma = full_data.index(',')
        text_content = full_data[first_comma + 1:]

        # Attribute atoms to words
        attributions = attribute_atoms_to_words(text_content, lang)

        for attr in attributions:
            sql = (
                f"INSERT IGNORE INTO word_atom_attributions "
                f"(sentence_id, word_position, word_form, word_lemma, atom_id, "
                f"confidence, keyword_matched) VALUES ("
                f"{sent_id}, {attr['word_position']}, "
                f"{esc(attr['word_form'])}, {esc(attr['word_lemma'])}, "
                f"{esc(attr['atom_id'])}, {attr['confidence']}, "
                f"{esc(attr['keyword_matched'])})"
            )
            dolt_sql(sql, check=False)
            total_attributions += 1

        if attributions:
            atoms_summary = {}
            for a in attributions:
                atom = a["atom_id"]
                if atom not in atoms_summary:
                    atoms_summary[atom] = []
                atoms_summary[atom].append(a["word_form"])

            print(f"  [{lang}] phrase {sent_idx}: {len(attributions)} attributions")
            for atom, words in sorted(atoms_summary.items()):
                print(f"      {atom} ← {', '.join(words[:3])}")

    print(f"\n  → {total_attributions} attributions mot→atome")
    return total_attributions > 0


# ─────────────────────────────────────────────────────────────────────────────
# Step 4: Sentence-level concept detection
# ─────────────────────────────────────────────────────────────────────────────

# Same concept mappings as validator, for consistency
CONCEPT_MAPPINGS = {
    "COLÈRE": {"RAGE", "DOMINATION"},
    "PEUR": {"FEAR", "PERCEPTION"},
    "SURPRISE": {"SEEKING", "PERCEPTION"},
    "JOIE": {"PLAY", "CREATION"},
    "TRISTESSE": {"GRIEF", "DESTRUCTION"},
    "MÉLANCOLIE": {"GRIEF", "COGNITION", "TEDIUM"},
    "COMPRENDRE": {"PERCEPTION", "COGNITION"},
    "ENTENDRE": {"PERCEPTION", "COGNITION"},
    "VOIR": {"PERCEPTION", "MOUVEMENT"},
    "CHERCHER": {"MOUVEMENT", "PERCEPTION", "COGNITION"},
    "EXPLORER": {"MOUVEMENT", "PERCEPTION"},
    "FUIR": {"MOUVEMENT", "FEAR"},
    "AIMER": {"CARE", "COMMUNICATION", "POSSESSION"},
    "AMOUR": {"CARE", "PERCEPTION", "EXISTENCE"},
    "MARCHER": {"MOUVEMENT", "EXISTENCE"},
    "CONSTRUIRE": {"MOUVEMENT", "CREATION"},
    "CAUSE": {"CREATION", "MOUVEMENT", "COGNITION"},
    "BEAUTÉ": {"PERCEPTION", "SEEKING", "CREATION"},
    "VÉRITÉ": {"COGNITION", "PERCEPTION", "EXISTENCE"},
    "SOUFFRIR": {"DESTRUCTION", "GRIEF"},
    "GUERRE": {"MOUVEMENT", "DOMINATION", "DESTRUCTION"},
    "LIBERTÉ": {"MOUVEMENT", "DOMINATION", "EXISTENCE"},
    "DANSER": {"MOUVEMENT", "PLAY"},
    "CONSOLER": {"COMMUNICATION", "CARE"},
    "RACONTER": {"COMMUNICATION", "CREATION"},
    "COMMANDER": {"COMMUNICATION", "DOMINATION"},
    "INVENTER": {"COGNITION", "CREATION"},
    "SAVOIR": {"COGNITION", "POSSESSION"},
    "APPRENDRE": {"PERCEPTION", "COGNITION", "POSSESSION"},
    "DÉGOÛT": {"DISGUST", "PERCEPTION"},
    "ENNUI": {"TEDIUM", "COGNITION"},
}


def step4_sentence_concepts():
    """Detect concepts at sentence level with targeted evidence."""
    print("\n" + "=" * 70)
    print("STEP 4: Sentence-level concept detection (précis)")
    print("=" * 70)

    # Get sentences with their word-atom attributions
    result = dolt_sql(
        f"SELECT gs.id, gs.lang, gs.sentence_index "
        f"FROM gutenberg_sentences gs "
        f"JOIN gutenberg_segments seg ON gs.segment_id = seg.id "
        f"WHERE seg.segment_ref = {esc(FOCUS_SEGMENT_REF)} "
        f"ORDER BY gs.lang, gs.sentence_index"
    )

    if not result:
        print("  ❌ No sentences found")
        return False

    lines = result.strip().split('\n')
    total_concepts = 0
    concepts_per_sentence = []

    for line in lines[1:]:
        parts = line.split(',')
        if len(parts) < 3:
            continue

        sent_id = int(parts[0])
        lang = parts[1].strip()
        sent_idx = parts[2].strip()

        # Get atoms attributed to words in this sentence
        atoms_result = dolt_sql(
            f"SELECT atom_id, word_form, word_position, confidence "
            f"FROM word_atom_attributions "
            f"WHERE sentence_id = {sent_id} "
            f"ORDER BY word_position"
        )

        if not atoms_result:
            concepts_per_sentence.append(0)
            continue

        atom_lines = atoms_result.strip().split('\n')
        atoms_detected = {}
        for al in atom_lines[1:]:
            # CSV: atom_id,word_form,word_position,confidence
            # word_form may contain commas or quotes, so parse carefully
            # atom_id is always first (no commas), confidence is always last
            parts = al.split(',')
            if len(parts) < 4:
                continue
            atom = parts[0].strip()
            # confidence is always the last part
            try:
                conf = float(parts[-1].strip())
            except ValueError:
                continue
            # word_position is second-to-last
            try:
                pos = int(parts[-2].strip())
            except ValueError:
                continue
            # word_form is everything between atom and position
            word = ','.join(parts[1:-2]).strip().strip('"')
            if atom not in atoms_detected:
                atoms_detected[atom] = {"word": word, "pos": pos, "conf": conf}

        # Now check concepts — only activate if atoms are from THIS sentence
        atom_set = set(atoms_detected.keys())
        detected_concepts = {}

        for concept, required_atoms in CONCEPT_MAPPINGS.items():
            if required_atoms.issubset(atom_set):
                # Build evidence JSON
                evidence = {}
                total_conf = 0
                for a in required_atoms:
                    info = atoms_detected.get(a, {})
                    evidence[a] = {
                        "word": info.get("word", "?"),
                        "pos": info.get("pos", -1),
                        "conf": info.get("conf", 0),
                    }
                    total_conf += info.get("conf", 0)

                avg_conf = total_conf / len(required_atoms)

                # Check if atoms are in a reasonable window (within 20 words)
                positions = [info.get("pos", 0) for info in evidence.values()]
                window_size = max(positions) - min(positions) if positions else 0
                is_in_window = window_size <= 20

                detected_concepts[concept] = {
                    "confidence": round(avg_conf, 3),
                    "evidence": evidence,
                    "in_window": is_in_window,
                }

        concepts_per_sentence.append(len(detected_concepts))

        # Insert into sentence_concepts
        for concept, data in detected_concepts.items():
            sql = (
                f"INSERT IGNORE INTO sentence_concepts "
                f"(sentence_id, concept_id, atoms_evidence, confidence, "
                f"is_in_window, analysis_method) VALUES ("
                f"{sent_id}, {esc(concept)}, "
                f"'{json.dumps(data['evidence'])}', {data['confidence']}, "
                f"{1 if data['in_window'] else 0}, 'keyword_targeted')"
            )
            dolt_sql(sql, check=False)
            total_concepts += 1

        if detected_concepts:
            concepts_str = ", ".join(
                f"{c}({'✓' if d['in_window'] else '✗'} {d['confidence']:.2f})"
                for c, d in sorted(detected_concepts.items())
            )
            print(f"  [{lang}] phrase {sent_idx}: {len(detected_concepts)} concepts → {concepts_str}")

    avg_concepts = sum(concepts_per_sentence) / max(len(concepts_per_sentence), 1)
    print(f"\n  → {total_concepts} concepts détectés")
    print(f"  → Moyenne: {avg_concepts:.1f} concepts/phrase")
    return total_concepts > 0


# ─────────────────────────────────────────────────────────────────────────────
# Step 5: Translator style profile
# ─────────────────────────────────────────────────────────────────────────────

def step5_style_profiles():
    """Compute stylistic metrics for each translator on the focus segment."""
    print("\n" + "=" * 70)
    print("STEP 5: Profil stylistique par traducteur")
    print("=" * 70)

    for eid, e in EDITIONS.items():
        if e["work_id"] != FOCUS_WORK_ID:
            continue
        lang = e["lang"]

        # Get sentence word counts for this edition (no text content in CSV)
        result = dolt_sql(
            f"SELECT gs.id, gs.word_count "
            f"FROM gutenberg_sentences gs "
            f"JOIN gutenberg_segments seg ON gs.segment_id = seg.id "
            f"WHERE seg.edition_id = {esc(eid)} "
            f"AND seg.segment_ref = {esc(FOCUS_SEGMENT_REF)} "
            f"ORDER BY gs.sentence_index"
        )
        if not result:
            continue

        lines = result.strip().split('\n')
        if len(lines) < 2:
            continue

        sentence_lengths = []
        sent_ids = []
        for line in lines[1:]:
            parts = line.split(',')
            if len(parts) >= 2:
                sent_ids.append(int(parts[0].strip()))
                sentence_lengths.append(int(parts[1].strip()))

        if not sentence_lengths:
            continue

        # Get all text for lexical metrics
        all_words = []
        punct_counts = {"!": 0, "?": 0, ";": 0, "—": 0, "–": 0}
        for sid in sent_ids:
            text_result = dolt_sql(f"SELECT text_content FROM gutenberg_sentences WHERE id = {sid}")
            if text_result:
                text_lines = text_result.strip().split('\n')
                if len(text_lines) >= 2:
                    text = '\n'.join(text_lines[1:])
                    words = text.lower().split()
                    all_words.extend(words)
                    for char in punct_counts:
                        punct_counts[char] += text.count(char)

        if not sentence_lengths:
            continue

        # Compute metrics
        avg_len = sum(sentence_lengths) / len(sentence_lengths)
        max_len = max(sentence_lengths)
        min_len = min(sentence_lengths)
        sent_count = len(sentence_lengths)

        # Type-token ratio
        word_types = set(all_words)
        ttr = len(word_types) / max(len(all_words), 1)

        # Hapax ratio (words appearing exactly once)
        word_freq = Counter(all_words)
        hapax = sum(1 for w, c in word_freq.items() if c == 1)
        hapax_ratio = hapax / max(len(word_types), 1)

        # Punctuation density
        total_punct = sum(punct_counts.values())
        punct_density = total_punct / max(len(all_words), 1)

        # Insert
        sql = (
            f"INSERT IGNORE INTO translator_style_profile "
            f"(edition_id, segment_ref, avg_sentence_length, max_sentence_length, "
            f"min_sentence_length, sentence_count, type_token_ratio, hapax_ratio, "
            f"avg_punctuation_density, exclamation_count, question_count, "
            f"semicolon_count, dash_count) VALUES ("
            f"{esc(eid)}, {esc(FOCUS_SEGMENT_REF)}, "
            f"{avg_len:.1f}, {max_len}, {min_len}, {sent_count}, "
            f"{ttr:.3f}, {hapax_ratio:.3f}, {punct_density:.4f}, "
            f"{punct_counts['!']}, {punct_counts['?']}, "
            f"{punct_counts[';']}, {punct_counts['—'] + punct_counts['–']})"
        )
        dolt_sql(sql, check=False)

        translator = e.get('translator', '(original)')
        year = e.get('translation_year', '?')
        print(f"  [{lang}] {translator} ({year}):")
        print(f"      Phrases: {sent_count}, moy. {avg_len:.0f} mots "
              f"(min {min_len}, max {max_len})")
        print(f"      Richesse lexicale: TTR={ttr:.3f}, hapax={hapax_ratio:.3f}")
        print(f"      Ponctuation: densité={punct_density:.4f}, "
              f"!={punct_counts['!']}, ?={punct_counts['?']}, "
              f";={punct_counts[';']}, —={punct_counts['—'] + punct_counts['–']}")

    return True


# ─────────────────────────────────────────────────────────────────────────────
# Step 6: Comparative report (segment-level vs phrase-level)
# ─────────────────────────────────────────────────────────────────────────────

def step6_comparative_report():
    """Compare segment-level and phrase-level detection to quantify improvement."""
    print("\n" + "=" * 70)
    print("STEP 6: Rapport comparatif — Segment-level vs Phrase-level")
    print("  'Réduction du bruit de détection'")
    print("=" * 70)

    # Segment-level stats (from existing data)
    seg_result = dolt_sql(
        f"SELECT ge.lang, ge.translator, "
        f"(SELECT COUNT(*) FROM segment_decompositions sd WHERE sd.segment_id = gs.id) as seg_concepts "
        f"FROM gutenberg_segments gs "
        f"JOIN gutenberg_editions ge ON gs.edition_id = ge.id "
        f"WHERE gs.segment_ref = {esc(FOCUS_SEGMENT_REF)} "
        f"AND ge.work_id = {esc(FOCUS_WORK_ID)} "
        f"ORDER BY ge.lang"
    )

    # Phrase-level stats
    sent_result = dolt_sql(
        f"SELECT gs_sent.lang, gs_sent.sentence_index, "
        f"(SELECT COUNT(*) FROM sentence_concepts sc WHERE sc.sentence_id = gs_sent.id) as sent_concepts "
        f"FROM gutenberg_sentences gs_sent "
        f"JOIN gutenberg_segments seg ON gs_sent.segment_id = seg.id "
        f"WHERE seg.segment_ref = {esc(FOCUS_SEGMENT_REF)} "
        f"ORDER BY gs_sent.lang, gs_sent.sentence_index"
    )

    print("\n  ── SEGMENT-LEVEL (actuel v2.2) ──")
    if seg_result:
        seg_concepts_list = []
        for line in seg_result.strip().split('\n')[1:]:
            # CSV: lang,translator,seg_concepts
            # translator may contain commas, so parse from edges
            parts = line.split(',')
            if len(parts) >= 3:
                lang = parts[0].strip()
                seg_concepts = int(parts[-1].strip())
                translator = ','.join(parts[1:-1]).strip()
                seg_concepts_list.append(seg_concepts)
                print(f"    [{lang}] {translator}: {seg_concepts} concepts détectés pour tout le segment")
        if seg_concepts_list:
            print(f"    → Moyenne: {sum(seg_concepts_list)/len(seg_concepts_list):.1f} concepts/segment")

    print("\n  ── PHRASE-LEVEL (v3-alpha) ──")
    if sent_result:
        phrase_concepts_by_lang = {}
        for line in sent_result.strip().split('\n')[1:]:
            parts = line.split(',')
            if len(parts) >= 3:
                lang = parts[0].strip()
                sent_concepts = int(parts[2].strip())
                if lang not in phrase_concepts_by_lang:
                    phrase_concepts_by_lang[lang] = []
                phrase_concepts_by_lang[lang].append(sent_concepts)

        for lang, concepts in sorted(phrase_concepts_by_lang.items()):
            avg = sum(concepts) / len(concepts) if concepts else 0
            total = sum(concepts)
            print(f"    [{lang}] {len(concepts)} phrases, "
                  f"moy. {avg:.1f} concepts/phrase, total {total}")

    print("\n  ── VERDICT ──")
    # Get overall comparison numbers
    total_seg = dolt_sql(
        f"SELECT COUNT(*) FROM segment_decompositions sd "
        f"JOIN gutenberg_segments gs ON sd.segment_id = gs.id "
        f"WHERE gs.segment_ref = {esc(FOCUS_SEGMENT_REF)}"
    )
    total_sent = dolt_sql(
        f"SELECT COUNT(*) FROM sentence_concepts sc "
        f"JOIN gutenberg_sentences gs ON sc.sentence_id = gs.id "
        f"JOIN gutenberg_segments seg ON gs.segment_id = seg.id "
        f"WHERE seg.segment_ref = {esc(FOCUS_SEGMENT_REF)}"
    )

    seg_count = int(total_seg.split('\n')[-1]) if total_seg else 0
    sent_count = int(total_sent.split('\n')[-1]) if total_sent else 0

    # Count sentences
    n_sentences = dolt_sql(
        f"SELECT COUNT(*) FROM gutenberg_sentences gs "
        f"JOIN gutenberg_segments seg ON gs.segment_id = seg.id "
        f"WHERE seg.segment_ref = {esc(FOCUS_SEGMENT_REF)}"
    )
    n_sents = int(n_sentences.split('\n')[-1]) if n_sentences else 1

    if seg_count > 0:
        reduction = (1 - sent_count / max(seg_count, 1)) * 100
        print(f"    Segment-level: {seg_count} concept-détections totales")
        print(f"    Phrase-level:  {sent_count} concept-détections totales")
        print(f"    → Réduction du bruit: {reduction:.0f}%")
        print(f"    → Granularité: {n_sents} phrases vs 1 segment par édition")

    return True


# ─────────────────────────────────────────────────────────────────────────────
# Step 7: Dolt commit
# ─────────────────────────────────────────────────────────────────────────────

def step7_commit():
    """Commit all v3-alpha data to Dolt."""
    print("\n" + "=" * 70)
    print("STEP 7: Dolt commit")
    print("=" * 70)

    message = (
        f"feat(v3-alpha): POC reconstruction phrase-level\n\n"
        f"- Schéma v3: 4 tables (sentences, word_atoms, sentence_concepts, style_profiles)\n"
        f"- Découpage phrase-par-phrase du segment {FOCUS_SEGMENT_REF}\n"
        f"- Attribution mot→atome ciblée (preuve par mot, pas par segment)\n"
        f"- Détection concepts phrase-level avec fenêtre syntaxique\n"
        f"- Profil stylistique par traducteur (TTR, hapax, ponctuation)\n"
        f"- Rapport comparatif segment-level vs phrase-level\n"
        f"- Objectif: réduire le bruit de sur-détection (~19 → ~3 concepts)"
    )

    ok = dolt_commit(message)
    if ok:
        print(f"  ✅ Committed to Dolt")
    else:
        print(f"  ⚠️  Commit result unclear")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  PaniniFS — POC v3-alpha : Reconstruction phrase-level             ║")
    print("║  Du bag-of-atoms (segment) à l'attribution ciblée (phrase)         ║")
    print("║  Objectif : réduire le bruit de ~19 concepts à ~2-4 par phrase     ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    steps = [
        ("Apply v3 schema", step1_apply_schema),
        ("Split into sentences", step2_split_into_sentences),
        ("Word→atom attribution", step3_word_atom_attribution),
        ("Sentence-level concepts", step4_sentence_concepts),
        ("Style profiles", step5_style_profiles),
        ("Comparative report", step6_comparative_report),
        ("Dolt commit", step7_commit),
    ]

    results = {}
    for name, func in steps:
        try:
            ok = func()
            results[name] = "✅" if ok else "⚠️"
        except Exception as e:
            print(f"\n❌ ERROR in {name}: {e}")
            import traceback
            traceback.print_exc()
            results[name] = "❌"

    print("\n" + "=" * 70)
    print("RESULTS:")
    for name, status in results.items():
        print(f"  {status} {name}")
    print("=" * 70)


if __name__ == "__main__":
    main()
