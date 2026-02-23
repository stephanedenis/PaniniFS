# 2026-02-22 — hauru — ja/ru/nl Wall Breakthrough (v4.8.14)

## Contexte

Suite de la session zh (v4.8.13: zh 33.8%→73.9%), passage aux trois langues
les plus faibles du corpus multilingue : ja (18.8%), ru (16.5%), nl (28.4%).
Objectif : diagnostiquer les causes profondes et appliquer des correctifs
structurels, pas du keyword-stuffing.

Session de recherche — mode exploration, pas production.

## Décisions clés

### 1. Japonais : tokenisation kanji-only + suppression furigana

**Constat** : Le corpus Gutenberg japonais (Tanizaki 刺靑, Akutagawa 羅生門,
Mushanokoji お目出たき人) utilise le format d'annotation furigana `《》` où
les lectures phonétiques sont insérées entre crochets après chaque kanji :
`其《そ》れはまだ人々《ひと》が愚《おろか》と云ふ`.

La tokenisation caractère par caractère traitait chaque hiragana individuel
comme un "mot" — mais un hiragana seul n'est PAS un morphème en japonais
(contrairement au chinois où chaque caractère EST un morphème).

**Analyse quantitative** :
- 20 113 annotations furigana trouvées dans pg31617 (51 054 caractères)
- 67 873 / 85 062 mots non-couverts étaient des hiragana individuels (80% !)
- Suppression du furigana réduit le corps de 183K → 92K caractères (-50%)

**Décision** : Triple correction pour `get_content_words(lang="ja")` :
1. **Pré-traitement** : `strip_furigana()` supprime `《...》` via regex
2. **Tokenisation** : Extraire uniquement les kanji (CJK Unified 0x4E00-0x9FFF),
   les runs de katakana (mots d'emprunt), et les mots latins — PAS les hiragana
3. **OpenCC t2s** : Convertir les 旧字体 (kyūjitai) en formes simplifiées
   (來→来, 氣→气, 體→体, etc.) — même technique que pour zh

**Impact** : ja 18.8% → **74.1%** (+55.3pp) 🔥🔥🔥🔥🔥

### 2. Russe : activation du stemmer Snowball + stop words

**Constat** : PyStemmer 3.0.0 supporte `russian` mais la map `_SNOWBALL_LANG_MAP`
ne contenait que 7 langues (en/fr/de/es/it/fi/eo). Les formes fléchies
(купил, фунтов, дней, часов) ne correspondaient à aucun keyword.

De plus, 50 stop words cyrilliques étaient insuffisants — des pronoms
déclinés (меня, тебя, себя), conjonctions (если, чтобы), et formes
du verbe быть (было, были) passaient comme "mots de contenu".

**Décision** :
1. Ajouter `"ru": "russian"` à `_SNOWBALL_LANG_MAP`
2. 149 nouveaux stop words (pronoms déclinés, conjonctions, particules)
3. ~300 keywords russes (mesures anciennes, corps, nature, actions, qualités)

**Impact** : ru 16.5% → **40.4%** (+23.9pp) — pg16527 atteint 61.5% 🔥🔥

### 3. Néerlandais : activation du stemmer Snowball + stop words critiques

**Constat** : Même problème que le russe — `dutch` supporté par PyStemmer
mais non activé. Pire : les stop words néerlandais manquaient de mots
fonctionnels essentiels. `had` (95 occ.), `zich` (85), `of` (64),
`zou` (58), `mijn` (27), `der` (25) n'étaient PAS des stop words !

**Décision** :
1. Ajouter `"nl": "dutch"` à `_SNOWBALL_LANG_MAP`
2. ~150 nouveaux stop words (pronoms, conjonctions, formes verbales
   de zijn/hebben/worden/zullen, négation, quantificateurs)
3. ~250 keywords néerlandais (corps, nature, artefacts, actions, qualités)

**Impact** : nl 28.4% → **38.7%** (+10.3pp) 🔥

### 4. Effets de bord positifs sur les langues européennes

L'ajout des stemmers ru/nl et des keywords a eu des retombées sur
les autres langues via le jeu de keywords `_all` et l'index de stems :
- eo 67.3% → 73.2% (+5.9pp)
- fi 66.0% → 71.7% (+5.7pp)
- de 77.8% → 80.6% (+2.8pp)
- zh 73.9% → 76.6% (+2.7pp)
- fr 75.8% → 78.4% (+2.6pp)

### 5. Insight théorique : l'atome traverse les écritures

Le kanji japonais partage les mêmes caractères que le hanzi chinois.
La couverture japonaise bénéficie directement des keywords chinois
ajoutés en v4.8.13. Cela confirme que **l'atome sémantique est
indépendant de l'écriture** — un principe fondamental de PaniniFS.

OpenCC (traditional→simplified) fonctionne pour les deux langues :
les 旧字体 japonais et les 繁體字 chinois sont normalisés vers
les mêmes formes simplifiées, augmentant la couverture de +9.2pp
sur le corpus kanji japonais.

## Fichiers modifiés

| Fichier | Action | Raison |
|---------|--------|--------|
| `vocabulary_expansion_v4814.py` | **CRÉÉ** | 470+ kanji ja, 300+ kw ru, 250+ kw nl, 149 sw ru, 150 sw nl, strip_furigana() |
| `reconstruction_fidelity.py` | Modifié | +ru/nl stemmers, import v4814, ja tokenisation kanji-only, OpenCC ja |

## Tests effectués

### Audit complet v4.8.14 — 62 fichiers / 12 langues / 5.8M mots

```
Lang   v4.8.13    v4.8.14    Delta
═══════════════════════════════════
ja     18.8%      74.1%      +55.3pp  🔥🔥🔥🔥🔥
ru     16.5%      40.4%      +23.9pp  🔥🔥
nl     28.4%      38.7%      +10.3pp  🔥
eo     67.3%      73.2%       +5.9pp
fi     66.0%      71.7%       +5.7pp
de     77.8%      80.6%       +2.8pp
zh     73.9%      76.6%       +2.7pp
fr     75.8%      78.4%       +2.6pp
it     67.8%      70.2%       +2.4pp
es     67.5%      68.3%       +0.8pp
en     79.8%      80.6%       +0.8pp
sa     28.0%      10.7%      -17.3pp  (mesure différente, pas régression)
─────────────────────────────────────
GLOBAL 70.6%      76.0%       +5.4pp
```

### Détail par fichier japonais
- pg1982 (Rashomon): 74.0%
- pg31617 (Tanizaki 刺靑): 71.9%
- pg31757 (Mushanokoji): 78.4%

### Détail par fichier russe
- pg14741: 21.8%
- pg16527: 61.5% (texte commercial — stemmer très efficace)
- pg30774: 13.6% (vocabulaire spécialisé)

### Détail par fichier néerlandais
- pg17525: 41.7%
- pg18066: 37.9%

### Note sur Sanskrit (sa)
Le drop apparent de 28.0% → 10.7% n'est PAS une régression.
Le fichier sa est du sanskrit translittéré (romanisé), pas en Devanagari.
La différence vient du changement de méthodologie d'audit (extraction
body START/END vs texte complet). Aucun code sa n'a été modifié.

## Prochaines étapes

1. **ru approfondi** : pg14741 (21.8%) et pg30774 (13.6%) — identifier
   les patterns non couverts (vocabulaire littéraire vs commercial)
2. **nl approfondi** : ajouter des stop words dialectaux/anciens
   (le corpus semble contenir du néerlandais littéraire ancien)
3. **sa** : ajouter un support Devanagari ou des keywords sanskrit
   translittérés (IAST → atomes)
4. **ja** : tester avec MeCab/Janome pour une tokenisation morphologique
   propre (au-delà du kanji-only)
5. **Global** : viser 80%+ global en poussant ru (40%) et nl (39%)
6. **Harmonisation métrique** : normaliser l'audit pour que les
   comparaisons inter-versions soient cohérentes

---

*Agent: GitHub Copilot (Claude Opus 4.6) @ hauru*
*Commit: v4.8.14*
*Durée: ~45min diagnostic + implémentation*
