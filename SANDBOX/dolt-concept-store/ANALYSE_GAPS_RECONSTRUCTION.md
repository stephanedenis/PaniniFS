# Analyse des gaps : Reconstruction textuelle multilingue

**Date** : 17 février 2026  
**Contexte** : PaniniFS v2.2 — Validation Gutenberg multilingue  
**Question** : Peut-on reconstituer un texte à l'identique dans d'autres langues  
à partir de la représentation sémantique + nuances des traducteurs ?

---

## 1. Verdict

### 🔴 Non. Le système actuel ne permet pas la reconstruction textuelle.

Le système actuel est un **validateur de convergence sémantique** — il prouve que
les mêmes concepts universels traversent les traductions. Mais il n'est pas un
**codec sémantique** capable du trajet aller-retour :

```
Texte_A (langue X) → Représentation → Texte_A' (langue Y)
                      où Texte_A' ≈ traduction existante
```

**Analogie** : Le système est un spectromètre qui détecte les éléments chimiques
dans un tableau (carbone, fer, zinc) — mais ne peut pas reconstituer le tableau
à partir de cette liste.

---

## 2. Ce que le système capture aujourd'hui

### 2.1 Données stockées (examen direct dans Dolt)

| Couche | Stockage | Qualité | Exemple réel |
|--------|----------|---------|--------------|
| **Provenance** | Traducteur, époque, URL, crédits | ✅ Excellente | `Bué, Henri (1869)` |
| **Texte brut** | Segments ~300-700 mots | ✅ Complet | 46 segments, 7 langues |
| **Atomes détectés** | Liste plate (bag-of-atoms) | ⚠️ Trop large | `["MOUVEMENT","COGNITION","PERCEPTION","POSSESSION","EXISTENCE","CREATION","COMMUNICATION"]` |
| **Concepts** | Dérivés par subset-matching | ⚠️ Sur-détection | 19 concepts pour 1 segment |
| **Confidence** | Score densité mots-clés | ⚠️ Non ciblé | 0.283 (même valeur pour concepts différents) |
| **Evidence** | Top 10 mots-clés trouvés | ⚠️ Partagée | `"fallen, wissen, sehen, sagen"` sert de preuve pour 19 concepts |
| **Convergence** | Ratio inter-traductions | ✅ Correct | majority=54, minority=44, unique=100 |

### 2.2 Chiffres clés du corpus

```
46 segments × 7 langues
343 décompositions (segment → concept)
198 enregistrements de convergence
46 concepts distincts détectés
0 concepts « universels » (convergence = 1.0)
   → Meilleur ratio : 0.667 (4/6 éditions)
```

### 2.3 Problème de sur-détection (observation empirique)

Pour le segment `ch01_falling` en allemand, les 8 mots d'evidence
`"fallen, wissen, sehen, sagen, machen, sein, werden, finden"` activent
**19 concepts simultanément** : ACCUMULER, APPRENDRE, CAUSE, CHERCHER,
COMPRENDRE, CONSTRUIRE, ENSEIGNER, ENTENDRE, EXPLORER, EXPLIQUER,
INVENTER, MARCHER, PARTAGER, RACONTER, REALISER, SAISIR, SAVOIR, VOIR, VÉRITÉ.

**Cause** : le matching par inclusion de sous-ensemble (`required_atoms ⊆ detected_atoms`)
accepte tout concept dont les atomes sont un sous-ensemble des atomes présents.
Avec 7 atomes détectés dans un segment de 353 mots, la plupart des concepts passent.

---

## 3. Les 7 couches manquantes pour la reconstruction

### 3.1 Structure syntaxique
**Ce qu'elle capture** : Arbre de dépendances, ordre des mots (SVO/SOV/VSO),
fonctions grammaticales (sujet, objet, modifieur).

**Exemple** :
```
"Alice fell down the rabbit-hole"
→ AGENT(Alice) PRED(fall) DIR(down) GOAL(rabbit-hole)
→ fr: "Alice tomba dans le terrier du lapin"
→ de: "Alice fiel in den Kaninchenbau hinunter"
```

Sans syntaxe, on sait qu'il y a MOUVEMENT mais pas *qui* se déplace *vers où*.

### 3.2 Alignement mot↔atome
**Ce qu'elle capture** : Quel mot porte quel atome spécifiquement.

**État actuel** : `"fallen"` et `"sehen"` sont dans le même sac d'evidence
pour 19 concepts.

**État requis** :
```
"fallen" → MOUVEMENT (confidence 0.95)
"sehen"  → PERCEPTION (confidence 0.90)
"wissen" → COGNITION (confidence 0.85)
```

### 3.3 Morphologie
**Ce qu'elle capture** : Genre, nombre, temps, cas, aspect, personne.

**Pourquoi c'est critique** : En français, "elle tomba" (passé simple) vs
"elle tombait" (imparfait) changent l'aspect temporel sans changer l'atome
MOUVEMENT. Pour reconstruire fidèlement, il faut savoir que Bué (1869)
utilise le passé simple là où un traducteur moderne utiliserait le passé composé.

### 3.4 Registre et style
**Ce qu'elle capture** : Niveau de langue (formel/familier/littéraire),
époque stylistique, rythme prosodique.

**Exemple** : Bué (1869) écrit "elle se précipita" là où un traducteur
contemporain écrirait "elle sauta" — même atome MOUVEMENT, style différent.

**Métriques possibles** :
- Longueur moyenne des phrases
- Ratio subordonnées/principales  
- Richesse lexicale (type/token ratio)
- Fréquence de la voix passive
- Distribution des temps verbaux

### 3.5 Relations discursives
**Ce qu'elle capture** : Anaphore, co-référence, connecteurs logiques,
structure narrative.

**Exemple** : "She fell" → "elle" = Alice (résolution co-référence).
"Then she noticed..." → "then" = relation temporelle séquentielle.

### 3.6 Prosodie et rythme
**Ce qu'elle capture** : Cadence, ponctuation, longueur de phrase,
parallélisme, figures de style.

**Pertinence particulière** : Carroll utilise le non-sens et le jeu de mots
(intraduisibles mot-à-mot) ; Voltaire utilise l'ironie structurelle.

### 3.7 Référents culturels
**Ce qu'elle capture** : Adaptations spécifiques à la culture cible.

**Exemple** : "porridge" → différentes traductions selon les cultures
alimentaires. Les traducteurs du XIXe adaptent plus que ceux du XXe.

---

## 4. Diagnostic par composant

### 4.1 Pipeline de détection (`detect_atoms_in_text`)

```python
# État actuel — keyword substring matching
for kw in keywords:
    pattern = r'\b' + re.escape(kw.lower()) + r'\b'
    found = re.findall(pattern, text_lower)
    if found:
        matches += len(found)
```

**Problèmes** :
- ❌ Pas de désambiguïsation : "sein" (allemand : être/son) → 2 sens
- ❌ Pas de contexte : le mot "voir" dans "il faut voir" ≠ PERCEPTION
- ❌ Granularité segment (~500 mots) au lieu de phrase (~15 mots)
- ❌ Keywords partagés entre langues (faux positifs)

### 4.2 Mapping concepts (`map_atoms_to_concepts`)

```python
# État actuel — subset inclusion
if required_atoms.issubset(atom_set):
    # Concept activé dès que tous ses atomes sont présents
```

**Problème** : avec 7+ atomes détectés dans un segment, presque tous
les concepts à 2-3 atomes sont activés mécaniquement.

### 4.3 Convergence (`step6_compute_convergence`)

**Fonctionne bien** pour ce qu'il mesure — mais mesure la convergence
de signaux bruités. Le ratio 0.667 (meilleur) reflète le bruit autant
que le signal.

---

## 5. Feuille de route : du validateur au codec sémantique

### Phase 1 — Précision (réduire le bruit) `[priorité haute]`

#### 1a. Découpage phrase-par-phrase
Remplacer les segments de 500 mots par des phrases individuelles
alignées entre traductions via algorithmes d'alignement bilingue.

```
Segment actuel : ~500 mots → 19 concepts détectés
Phrase isolée :  ~15 mots → 2-3 concepts pertinents
```

#### 1b. Attribution mot→atome ciblée
Chaque atome doit pointer vers le(s) mot(s) spécifique(s) qui le portent,
pas vers le segment entier.

```sql
CREATE TABLE word_atom_attributions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sentence_id INT NOT NULL,
    word_position INT NOT NULL,          -- position du mot dans la phrase
    word_form VARCHAR(100) NOT NULL,     -- forme de surface
    word_lemma VARCHAR(100),             -- lemme
    atom_id VARCHAR(30) NOT NULL,        -- atome attribué
    confidence FLOAT NOT NULL,
    disambiguation_note TEXT             -- ex: "sein" = être (verbe), pas son (possessif)
);
```

#### 1c. Seuil de pertinence concept
Ne garder un concept que si ses atomes sont portés par des mots
**dans la même fenêtre syntaxique** (même proposition ou propositions
liées), pas juste dans le même segment.

### Phase 2 — Structure (ajouter la syntaxe) `[priorité moyenne]`

#### 2a. Arbres de dépendances
Stocker la structure syntaxique de chaque phrase.

```sql
CREATE TABLE sentence_syntax (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sentence_id INT NOT NULL,
    word_position INT NOT NULL,
    word_form VARCHAR(100) NOT NULL,
    pos_tag VARCHAR(20),                 -- NOUN, VERB, ADJ, etc.
    dep_relation VARCHAR(30),            -- nsubj, dobj, amod, etc.
    head_position INT,                   -- position du mot gouverneur
    lang VARCHAR(5) NOT NULL
);
```

#### 2b. Rôles sémantiques
Mapper les fonctions syntaxiques en rôles :
AGENT, PATIENT, INSTRUMENT, SOURCE, GOAL, MANNER, TIME, PLACE.

### Phase 3 — Style (capturer les nuances traducteur) `[priorité moyenne]`

#### 3a. Profil stylistique par traducteur

```sql
CREATE TABLE translator_style_profile (
    id INT AUTO_INCREMENT PRIMARY KEY,
    edition_id VARCHAR(50) NOT NULL,
    avg_sentence_length FLOAT,           -- mots par phrase
    type_token_ratio FLOAT,              -- richesse lexicale
    subordination_ratio FLOAT,           -- % de subordonnées
    passive_voice_ratio FLOAT,           -- % voix passive
    past_tense_distribution JSON,        -- {passé_simple: 0.4, imparfait: 0.3, ...}
    formality_score FLOAT,               -- 0 = familier, 1 = soutenu
    archaism_density FLOAT               -- fréquence de tournures datées
);
```

#### 3b. Marqueurs de choix traducteur
Quand deux traducteurs traduisent le même passage différemment,
capter quel choix a été fait et pourquoi.

### Phase 4 — Reconstruction (composer le texte) `[horizon lointain]`

La formule de reconstruction serait :

```
Texte' = f(
    graphe_sémantique,      -- atomes + relations + rôles
    syntaxe_langue_cible,   -- patron SVO/SOV, morphologie
    style_traducteur,       -- registre, époque, rythme
    lexique_cible           -- choix lexicaux de la langue
)
```

Ceci nécessite un modèle génératif contraint par la représentation.

---

## 6. Ce qui fonctionne et qu'il faut préserver

| Acquis | Valeur |
|--------|--------|
| **Provenance complète** | Chaîne édition → traducteur → Gutenberg avec dates |
| **Principe de convergence** | Mesure correcte du commun vs spécifique |
| **Texte brut stocké** | On peut toujours revenir enrichir l'analyse |
| **Versioning Dolt** | Itérer en préservant l'historique complet |
| **Corpus bien choisi** | Alice (non-sens) + Candide (ironie) = tests complémentaires |
| **30 primitifs validés** | Base théorique solide (72 références, 10 domaines) |
| **Axes émotionnels** | Modèle neurophysiologique rigoureux (Panksepp et al.) |

---

## 7. POC immédiat : Reconstruction phrase-level (v3-alpha)

Un script `poc_reconstruction_phrases.py` implémente les étapes 1a et 1b :

1. **Découpage en phrases** d'un segment existant
2. **Alignement inter-éditions** par position séquentielle
3. **Attribution mot→atome ciblée** avec preuve par mot
4. **Comparaison** : concepts par phrase vs concepts par segment (réduction du bruit)
5. **Stockage** dans de nouvelles tables Dolt

Résultats attendus : passer de ~19 concepts/segment à ~2-4 concepts/phrase,
avec evidence ciblée par mot au lieu de partagée.

---

## Références

- Hunalign : algorithme d'alignement bilingue phrase-par-phrase
- Universal Dependencies : standard pour les arbres de dépendances
- PropBank : standard pour les rôles sémantiques
- Panksepp (1998) : *Affective Neuroscience* — base des axes émotionnels v2.2
- Wierzbicka (1996) : *Semantics: Primes and Universals* — fondation théorique PanLang
