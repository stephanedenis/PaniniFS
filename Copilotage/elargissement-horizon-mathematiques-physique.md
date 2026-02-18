# Élargissement de l'horizon : Mathématiques & Physique

> *Date : 2026-02-18*
> *Statut : RFC — Request for Comments*
> *Auteur : copilotage PaniniFS*

## 1. Constat

### 1.1 Les atomes actuels sont tous processuels

Les 17 atomes sémantiques de PaniniFS sont **tous de catégorie PROC** (processus) :

| Couche | Atomes |
|--------|--------|
| **Prédicats sémantiques** (9) | MOUVEMENT, COGNITION, PERCEPTION, COMMUNICATION, CREATION, EXISTENCE, DESTRUCTION, POSSESSION, DOMINATION |
| **Axes émotionnels** (8) | SEEKING, FEAR, CARE, GRIEF, RAGE, DISGUST, PLAY, TEDIUM |

Conséquence : `compute_primary_category()` retourne `"PROC"` en dur pour les 104 concepts.

### 1.2 Les extensions non-verbales existent mais sont orphelines

La table `nonverbal_extensions` contient 4 entrées (ESPACE, TEMPS, EVAL, TAXO)
qui ne sont **jamais utilisées** comme atomes dans les formules de concepts.

### 1.3 Le cadre formel est déjà mathématique

Les 5 opérations structurelles (COMP, ID, NEG, QUANT, MOD) viennent de la
théorie des catégories, la logique et le λ-calcul. PaniniFS parle *avec* les
maths sans pouvoir parler *des* maths.

---

## 2. Proposition : 7 atomes abstraits (catégorie ABS)

### 2.1 Critères de sélection

Un atome PaniniFS doit être :
1. **Irréductible** — non décomposable en d'autres atomes
2. **Cross-domaine** — applicable au-delà du linguistique
3. **Fondé scientifiquement** — ancré dans une théorie établie
4. **Composable** — combinable avec les atomes existants

### 2.2 Les 7 atomes proposés

| Atome | Catégorie | Dhātu sanskrit | Description | Fondement |
|-------|-----------|----------------|-------------|-----------|
| **RELATION** | ABS | √bandh (lier) | Correspondance entre éléments : →, ↦, ∼, = | Théorie des catégories (morphismes) |
| **STRUCTURE** | ABS | √dhā (poser) | Organisation qui survit aux transformations | Algèbre abstraite (groupes, anneaux) |
| **INVARIANCE** | ABS | √sthā (se tenir) | Ce qui ne change pas sous transformation | Théorème de Noether, symétries |
| **RÉCURRENCE** | ABS | √vṛt (tourner) | Auto-référence, induction, itération | Logique (induction), λ-calcul (Y combinator) |
| **DUALITÉ** | ABS | √dvā (deux) | Opposition productive : ∀/∃, ∧/∨, espace/co-espace | Dualité catégorielle |
| **MESURE** | ABS | √mā (mesurer) | Quantité continue, taille, norme, distance | Théorie de la mesure |
| **ORDRE** | ABS | √kram (marcher en ordre) | Relation antisymétrique transitive : ≤, ⊂, ≺ | Théorie des ordres, treillis |

### 2.3 Mapping NSM (Natural Semantic Metalanguage)

```
RELATION   → [LIKE, OF, WITH]        (Wierzbicka : relational primes)
STRUCTURE  → [PART, KIND]            (méréologie + taxonomie)
INVARIANCE → [SAME, NOT CHANGE]      (identité persistante)
RÉCURRENCE → [AGAIN, MORE, BECAUSE]  (itération + causalité)
DUALITÉ    → [OTHER, NOT, IF]        (altérité + conditionalité)
MESURE     → [BIG, SMALL, MUCH]      (évaluateurs scalaires)
ORDRE      → [BEFORE, AFTER, ABOVE]  (séquence + hiérarchie)
```

### 2.4 Mapping dimensionnel

```python
# Nouveaux atomes → dimensions (comme ATOM_DIMENSIONS existant)
"RELATION":    {"RELATION": 1.0},
"STRUCTURE":   {"STRUCTURE": 0.8, "RELATION": 0.2},
"INVARIANCE":  {"QUALITÉ": 0.5, "STRUCTURE": 0.5},
"RÉCURRENCE":  {"PROCESSUS": 0.4, "STRUCTURE": 0.6},
"DUALITÉ":     {"RELATION": 0.5, "MODALITÉ": 0.5},
"MESURE":      {"QUALITÉ": 0.7, "RELATION": 0.3},
"ORDRE":       {"RELATION": 0.6, "STRUCTURE": 0.4},
```

---

## 3. Concepts mathématiques décomposables

### 3.1 Objets fondamentaux

| Concept | Formule PaniniFS | Catégorie |
|---------|-----------------|-----------|
| **ENSEMBLE** | EXISTENCE + STRUCTURE + POSSESSION | ABS |
| **FONCTION** | RELATION + MOUVEMENT | ABS |
| **NOMBRE** | MESURE + ORDRE + EXISTENCE | ABS |
| **ESPACE** | STRUCTURE + MESURE + EXISTENCE | ABS |
| **CATÉGORIE** | STRUCTURE + RELATION + COMP | ABS |
| **PROPOSITION** | COGNITION + RELATION + STRUCTURE | ABS |

### 3.2 Opérations et transformations

| Concept | Formule PaniniFS |
|---------|-----------------|
| **PREUVE** | COGNITION + CREATION + STRUCTURE + RÉCURRENCE |
| **THÉORÈME** | COGNITION + CREATION + INVARIANCE |
| **ISOMORPHISME** | RELATION + INVARIANCE + STRUCTURE |
| **CONVERGENCE** | MOUVEMENT + MESURE + EXISTENCE |
| **SYMÉTRIE** | INVARIANCE + STRUCTURE + DUALITÉ |
| **INDUCTION** | RÉCURRENCE + COGNITION + ORDRE |
| **PROJECTION** | MOUVEMENT + STRUCTURE + RELATION |
| **COMPOSITION** | RELATION + STRUCTURE + CREATION |

### 3.3 Structures algébriques

| Concept | Formule PaniniFS |
|---------|-----------------|
| **GROUPE** | STRUCTURE + COMP + ID + NEG |
| **ANNEAU** | STRUCTURE + COMP + COMP + ID + NEG |
| **CORPS** | STRUCTURE + COMP + COMP + ID + NEG + DUALITÉ |
| **ESPACE VECTORIEL** | STRUCTURE + MESURE + COMP |
| **TOPOLOGIE** | STRUCTURE + EXISTENCE + ORDRE |
| **VARIÉTÉ** | STRUCTURE + MESURE + MOUVEMENT |

---

## 4. Extension à la physique

Les mêmes atomes ABS couvrent la physique via les symétries (Noether) :

| Concept physique | Formule PaniniFS |
|-----------------|-----------------|
| **ÉNERGIE** | INVARIANCE + MOUVEMENT + MESURE |
| **FORCE** | MOUVEMENT + DOMINATION + MESURE |
| **CHAMP** | EXISTENCE + STRUCTURE + MESURE |
| **PARTICULE** | EXISTENCE + MOUVEMENT + MESURE |
| **ONDE** | MOUVEMENT + RÉCURRENCE + MESURE |
| **ENTROPIE** | DESTRUCTION + MESURE + ORDRE |
| **CONSERVATION** | INVARIANCE + POSSESSION + MESURE |
| **CAUSALITÉ** | RELATION + ORDRE + CRÉATION |
| **QUANTIFICATION** | MESURE + STRUCTURE + DUALITÉ |
| **RELATIVITÉ** | INVARIANCE + MOUVEMENT + MESURE + STRUCTURE |

### 4.1 Le théorème de Noether comme validation

Emmy Noether (1918) : *À chaque symétrie continue correspond une loi de conservation.*

En PaniniFS : `INVARIANCE(STRUCTURE) → POSSESSION(MESURE)`

Ce théorème *est* la preuve que INVARIANCE et STRUCTURE sont des atomes
fondamentaux — ils engendrent les lois physiques par composition.

---

## 5. Impact sur l'architecture

### 5.1 Fichiers à modifier

| Fichier | Modification |
|---------|-------------|
| `import_panlang_v2.py` | Ajouter atomes ABS dans `ATOM_DIMENSIONS`, `ATOM_NSM`, `ATOMS` ; corriger `compute_primary_category()` |
| `schema_v2_universals.sql` | Aucune — le schéma supporte déjà les catégories ENT/QUAL/ABS |
| `gutenberg_multilingual_validator.py` | Ajouter `ATOM_KEYWORDS` pour les 7 atomes ABS (mots-clés multilingues) |
| `seven_layers_engine.py` | Optionnel — les atomes ABS seront surtout détectés dans des corpus scientifiques, pas littéraires |

### 5.2 Rétrocompatibilité

- Les 17 atomes PROC ne changent **pas**
- Les 104 concepts existants gardent leurs formules
- Les nouveaux atomes ABS **enrichissent** sans casser
- `compute_primary_category()` pourra enfin retourner ENT/QUAL/ABS selon la dominance dimensionnelle

### 5.3 Prochaines étapes

1. ✅ Ce document (RFC)
2. Enrichir `import_panlang_v2.py` avec les 7 atomes ABS
3. Corriger `compute_primary_category()` pour un calcul réel
4. Créer un corpus de test mathématique (extraits d'Euclide, Euler, Noether)
5. Valider les formules sur le corpus
6. Étendre au corpus physique (Newton, Einstein, Feynman)

---

## 6. Fondements philosophiques

### 6.1 Pāṇini et les mathématiques

L'*Aṣṭādhyāyī* de Pāṇini (IVe siècle av. J.-C.) est considéré comme le
**premier système formel** de l'histoire — avant Euclide, avant Aristote.

Ses sūtra sont des **règles de réécriture** (comme les grammaires formelles
de Chomsky), ses pratyāhāra sont des **ensembles ordonnés** (comme les
ordinaux), sa métarègle d'application est un **algorithme d'unification**
(comme en Prolog).

Les dhātu (√) sont les **atomes** du système pāṇinéen. En étendant les
dhātu au-delà du verbal, nous suivons exactement la trajectoire que Pāṇini
aurait empruntée s'il avait eu accès aux mathématiques modernes.

### 6.2 Le pont Curry-Howard-Lambek

Le triptyque :
- **Logique** (propositions, preuves)
- **Calcul** (types, programmes)
- **Catégories** (objets, morphismes)

... est exactement ce que les 5 opérations structurelles de PaniniFS encodent
déjà. Les 7 atomes ABS proposés complètent le vocabulaire nécessaire pour
que PaniniFS puisse se décrire lui-même — résolvant la circularité par une
**stratification** explicite (les atomes sont au niveau 0, les concepts au
niveau 1, les méta-concepts au niveau 2).
