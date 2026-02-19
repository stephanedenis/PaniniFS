# v2.7 : WSD POS-aware + Opérations structurelles + Jackendoff

- **Date** : 2026-02-19
- **Machine** : hauru (Xeon E5-2650, 8c/16t, 62 Go RAM)
- **Agent** : Claude Opus 4.6 (Copilot)
- **Durée session** : ~45 min (v2.7 uniquement, session totale plus longue)

## Contexte

Suite de la session v2.5→v2.6→v2.7 du 19 février 2026.
Priorité 1 du plan NA-004 : compléter le modèle linguistique.
v2.5 (ENT) et v2.6 (QUAL) achevés. v2.7 = dernière étape linguistique
avant passage aux médias texte (v4.0).

Recherche préalable par sous-agent : analyse complète de l'état du code —
`align_words_to_atoms()` prend le premier match (pas de WSD),
`analyze_syntax()` produit des POS tags non utilisés par l'alignement,
5 ops structurelles seedées en DB mais jamais référencées.

## Décisions clés

### 1. Jackendoff : 6 mappings supplémentaires (5→11)

**Constat** : 30/35 atomes avaient `None` dans ATOM_JACKENDOFF. Jackendoff
(1990, 2007) a ~15 primitifs conceptuels.

**Décision** : Mapper uniquement les correspondances théoriquement justifiées :
- PERCEPTION → ORIENT (Jackendoff 2007 §7.3 : orientation perceptuelle)
- DESTRUCTION → INCH (changement d'état inchoatif)
- POSSESSION → HAVE (tier possessif)
- DOMINATION → AFFECT (tier thématique/action)
- INVARIANCE → STAY (persistance spatiale/temporelle)
- MESURE → AMOUNT (catégorie ontologique)

**Impact** : 11/35 mappés. Les 24 restants (émotions, qualités, certains ABS)
n'ont PAS de primitif Jackendoff — c'est une limite intrinsèque de sa théorie
(pas de modélisation des émotions ni des qualités évaluatives).

### 2. WSD POS-aware : remplacement du first-match

**Constat** : `align_words_to_atoms()` utilisait `break` sur le premier atome
correspondant → l'ordre d'insertion dans le dictionnaire déterminait le
résultat, pas le contexte syntaxique.

**Décision** : Collecter TOUS les candidats par mot, puis ranker via :
- POS tags de `analyze_syntax()` passés en paramètre
- Préférences POS→catégorie : VERB→PROC, NOUN→ENT/ABS, ADJ→QUAL, ADV→QUAL
- Note de désambiguïsation `[WSD:POS→CAT, rejected=...]` dans les résultats

**Impact** : 3.6% des mots bénéficient du WSD (23/638 sur échantillon 50 para).
Overhead négligeable (18.8s vs 18.3s baseline).

### 3. Opérations structurelles : détection NEG/QUANT/MOD

**Constat** : Les 5 ops (COMP, ID, NEG, QUANT, MOD) étaient seedées dans la table
`structural_operations` mais jamais utilisées dans le pipeline. Les ajouter
comme atomes n'a pas de sens (ce sont des opérateurs, pas des prédicats).

**Décision** : Créer `detect_structural_operators()` — post-traitement qui :
- Détecte les mots de négation/quantification/modalité (lexiques ×7 langues)
- Détermine la portée (±3 mots, même clause si syntaxe disponible)
- Annote les concepts détectés avec flags `negated`/`quantified`/`modal`
- Les concepts négués voient leur confiance réduite ×0.7

**Impact** : 71 opérateurs / 50 paragraphes (NEG=51, QUANT=11, MOD=9).
2 concepts upgradeés (B→A) grâce à la meilleure discrimination.

## Fichiers modifiés

| Fichier | Changement |
|---------|------------|
| `import_panlang_v2.py` | ATOM_JACKENDOFF : 6 mappings ajoutés (5→11/35), commentaires Jackendoff 1990/2007 |
| `seven_layers_engine.py` | WSD : `align_words_to_atoms(syntax_results=)`, `_rank_candidates()`, POS_CATEGORY_PREF, ATOM_CATEGORY |
| `seven_layers_engine.py` | Ops structurelles : `detect_structural_operators()`, lexiques NEG/QUANT/MOD ×7 langues |
| `seven_layers_engine.py` | `detect_paragraph_concepts(struct_ops=)` : flags negated/quantified/modal |
| `seven_layers_engine.py` | Pipeline : passage syntax_results à alignment, struct_ops à concepts |
| `EXPERIMENT_REGISTRY.md` | v2.7 marqué ✅ avec sous-étapes 2.7a-2.7f |

## Tests effectués

| Test | Résultat |
|------|----------|
| Compilation syntaxique | ✅ py_compile OK |
| WSD unitaire ("beautiful creation moved deeply") | ✅ ADJ→BON, NOUN→CREATION, VERB→MOUVEMENT, ADV→INTENSE |
| Structural ops unitaire ("never saw without fear") | ✅ NEG détecté pour "never" et "without" |
| Pipeline complet 445 paragraphes | ✅ 18.8s (vs 18.3s baseline) |
| Qualité concepts : A=80 (+2), B=24, C=1 | ✅ score 0.667 (+0.017) |
| WSD sur échantillon 50 para : 23 disambiguations | ✅ |
| Ops structurelles : 71 détections / 50 para | ✅ |

## Prochaines étapes

1. **Priorité 2 — Médias texte** (v4.0→v4.2) : extracteur PDF/EPUB/DOCX,
   pont vers seven_layers_engine, CLI d'analyse de documents
2. **Améliorations WSD futures** : fenêtre contextuelle sémantique (pas seulement POS),
   désambiguïsation par co-occurrence d'atomes dans le même paragraphe
3. **Structural ops avancées** : COMP (comparaison) et ID (identification/tautologie)
   restent non-détectées — nécessitent analyse syntaxique plus profonde
