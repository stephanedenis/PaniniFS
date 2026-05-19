# Universaux sémantiques : revue interdisciplinaire de littérature

## Pour une refondation de la vision universaliste de Panini-FS

**Auteur** : Stéphane (assisté par IA)  
**Date** : Juillet 2025  
**Contexte** : Phase préparatoire avant import des concepts PanLang dans Dolt  
**Objectif** : Revisiter la vision universaliste de PanLang à la lumière des théories de l'information, de la calculabilité, de la compression sémantique, de l'ontologie formelle et de la sémiotique — afin de converger vers des universaux ne se limitant pas à la linguistique.

---

## Table des matières

1. [Introduction et motivation](#1-introduction-et-motivation)
2. [État actuel de PanLang : diagnostic](#2-état-actuel-de-panlang--diagnostic)
3. [Théorie de l'information](#3-théorie-de-linformation)
4. [Communication sémantique](#4-communication-sémantique)
5. [Calculabilité et primitives computationnelles](#5-calculabilité-et-primitives-computationnelles)
6. [Théorie des catégories et correspondance Curry-Howard-Lambek](#6-théorie-des-catégories-et-correspondance-curry-howard-lambek)
7. [Ontologies formelles supérieures](#7-ontologies-formelles-supérieures)
8. [Linguistique formelle et sémantique universelle](#8-linguistique-formelle-et-sémantique-universelle)
9. [Sémiotique et phénoménologie](#9-sémiotique-et-phénoménologie)
10. [Panini historique : l'Aṣṭādhyāyī comme système computationnel](#10-panini-historique--laṣṭādhyāyī-comme-système-computationnel)
11. [Convergence : vers des universaux transversaux](#11-convergence--vers-des-universaux-transversaux)
12. [Positionnement de PanLang](#12-positionnement-de-panlang)
13. [Proposition de primitives révisées](#13-proposition-de-primitives-révisées)
14. [Bibliographie complète](#14-bibliographie-complète)

---

## 1. Introduction et motivation

Le projet PanLang propose de décomposer tout concept humain en combinaisons d'**atomes sémantiques** dérivés des racines verbales (dhātu) du sanskrit. La prétention est universaliste : ces atomes devraient suffire à représenter tout sens possible.

Avant de procéder à l'import de 144 concepts dans une base de données Dolt, il est impératif de vérifier cette prétention à la lumière d'un panorama interdisciplinaire large. La question n'est pas seulement « est-ce linguistiquement fondé ? » mais bien :

> **Quels sont les véritables primitifs universels de la représentation sémantique, quand on prend en compte la théorie de l'information, la calculabilité, les mathématiques des structures, l'ontologie formelle et la sémiotique ?**

Ce document rassemble les résultats d'une exploration systématique de 10 domaines scientifiques et identifie les convergences.

---

## 2. État actuel de PanLang : diagnostic

### 2.1 Les 10 atomes actuels

PanLang ULTIME définit 10 atomes sémantiques, chacun dérivé d'un dhātu sanskrit :

| Atome | Dhātu originel | Domaine sémantique |
|-------|---------------|-------------------|
| MOUVEMENT | √gam (ITER) | Déplacement, processus |
| COGNITION | √jñā (DECIDE) | Pensée, raisonnement |
| PERCEPTION | √dṛś (EVAL) | Observation, évaluation |
| COMMUNICATION | √vac (COMM) | Parole, échange |
| CRÉATION | √kṛ (CAUSE) | Fabrication, causation |
| ÉMOTION | √hṛd (FEEL) | Affect, sentiment |
| EXISTENCE | √as (EXIST) | Être, présence |
| DESTRUCTION | ??? | Fin, annihilation |
| POSSESSION | √labh (RELATE) | Avoir, relation |
| DOMINATION | √īś (MODAL) | Pouvoir, modalité |

### 2.2 Problèmes identifiés par l'audit

L'audit de qualité (Phase 17) a révélé :

- **Score global** : 0.614 / 1.0
- **Couverture NSM** : seulement 23% des 65 primes de Wierzbicka (15/65)
- **Biais verbal** : les 10 atomes sont tous des **prédicats verbaux** — ils manquent les catégories substantives, quantitatives, temporelles, spatiales et logiques
- **Discriminabilité faible** : 10 concepts ont la même formule que leur atome (tautologies)
- **10 doublons sémantiques** : formules identiques pour concepts différents
- **Pollution Wikipedia** : 9 concepts avec validité < 0.3 provenant de `wikipedia_directe_optimisee`
- **Couverture catégorielle** : 5/16 catégories seulement

### 2.3 Question centrale

> Les 10 atomes de PanLang sont-ils de bons *universaux de la prédication verbale* (oui, dans une large mesure) ou de bons *universaux de la représentation sémantique* (non, pas en l'état) ?

Pour répondre, examinons ce que chaque discipline considère comme « primitif ».

---

## 3. Théorie de l'information

### 3.1 Shannon : l'information syntaxique (1948)

Claude Shannon fonde la théorie de l'information avec un article fondateur qui définit l'information comme **réduction de l'incertitude** :

$$H(X) = -\sum_{i} p(x_i) \log_2 p(x_i)$$

Point crucial : Shannon exclut explicitement la sémantique. Son cadre traite de la transmission fidèle de **symboles**, indépendamment de leur signification.

> « The fundamental problem of communication is that of reproducing at one point either exactly or approximately a message selected at another point. Frequently the messages have meaning [...] These semantic aspects of communication are irrelevant to the engineering problem. » — Shannon (1948, p. 379)

**Implication pour PanLang** : Shannon fournit les bornes théoriques de la *compression* mais pas de la *représentation du sens*. Un système d'atomes sémantiques doit aller au-delà.

### 3.2 Weaver : les trois niveaux (1949)

Warren Weaver, dans l'introduction du livre Shannon & Weaver (1949), distingue trois niveaux de communication :

| Niveau | Question | Discipline |
|--------|----------|-----------|
| **A — Technique** | Comment transmettre les symboles ? | Théorie de l'information |
| **B — Sémantique** | Les symboles transmettent-ils le sens voulu ? | Sémantique formelle |
| **C — Efficacité** | Le sens reçu produit-il l'effet désiré ? | Pragmatique |

PanLang opère au **niveau B** — mais doit intégrer des contraintes du niveau A (compression) et du niveau C (pertinence de la tâche).

### 3.3 Kolmogorov : la complexité algorithmique (1965)

La complexité de Kolmogorov $K(x)$ d'un objet $x$ est la longueur du **plus court programme** qui produit $x$ sur une machine de Turing universelle :

$$K(x) = \min \{ |p| : U(p) = x \}$$

Propriétés clés :
- **Incompressibilité** : la plupart des objets sont algorithmiquement aléatoires ($K(x) \approx |x|$)
- **Invariance** : $K(x)$ ne dépend pas du choix de la machine universelle (à une constante additive près)
- **Incalculabilité** : $K(x)$ n'est pas calculable en général (théorème de Chaitin)

**Implication pour PanLang** : la décomposition d'un concept en atomes est exactement un problème de compression. La question est : les 10 atomes forment-ils un bon « langage de description » (au sens MDL) pour les concepts ?

### 3.4 Minimum Description Length — MDL (Rissanen, 1978)

Le principe MDL formalise le rasoir d'Occam : le meilleur modèle $M$ pour des données $D$ est celui qui minimise :

$$L(D) = L(M) + L(D|M)$$

où $L(M)$ est la longueur de description du modèle et $L(D|M)$ la longueur résiduelle des données sous le modèle.

**Implication pour PanLang** : si on considère les 144 concepts comme « données » et les 10 atomes + règles de composition comme « modèle », le MDL nous dit que :
- Trop peu d'atomes → $L(D|M)$ élevé (perte d'information, compositions absurdes comme MUSIQUE = DESTRUCTION + MOUVEMENT)
- Trop d'atomes → $L(M)$ élevé (le modèle est aussi complexe que les données)
- L'optimum est entre les deux

### 3.5 Floridi : l'information sémantique (2011)

Luciano Floridi propose une théorie de l'**information sémantique** (GDI — General Definition of Information) :

> Donnée $d$ est de l'information sémantique ssi $d$ est :
> 1. **Bien formée** (syntaxiquement correcte)
> 2. **Significative** (sémantiquement interprétable)  
> 3. **Véridique** (vraie)

Cette « veridicality thesis » distingue Floridi de Bar-Hillel et Carnap qui, dès 1952, proposaient la première théorie formelle de l'information sémantique dans *An Outline of a Theory of Semantic Information* (MIT Technical Report).

**Implication pour PanLang** : les formules PanLang satisfont (1) — elles sont syntaxiquement bien formées. Mais (2) est problématique (MUSIQUE = DESTRUCTION + MOUVEMENT n'est pas sémantiquement satisfaisant) et (3) n'est pas vérifié empiriquement.

### 3.6 Solomonoff, Chaitin, Hutter : compression et intelligence

**Solomonoff (1964)** : l'induction universelle assigne à chaque séquence observable une probabilité a priori proportionnelle à $2^{-K(x)}$ (la probabilité algorithmique). C'est le « prior universel » — le meilleur prior possible en l'absence de toute connaissance préalable.

**Chaitin** : le nombre $\Omega$ (probabilité d'arrêt) est un réel bien défini mais incalculable, incarnant les limites de la raison formelle. Chaque bit de $\Omega$ contient de l'information irréductible.

**Hutter (2000)** : AIXI est l'agent universel optimal qui combine l'induction de Solomonoff avec la théorie de la décision séquentielle :

$$a_k = \arg\max_{a_k} \sum_{o_k r_k} \ldots \max_{a_m} \sum_{o_m r_m} [r_k + \ldots + r_m] \sum_{q: |q| \leq l} 2^{-|q|} \prod_{i=1}^{m} q(o_i r_i | a_1 o_1 r_1 \ldots a_{i-1} o_{i-1} r_{i-1} a_i)$$

**Implication pour PanLang** : La leçon fondamentale est que **compression = compréhension = prédiction**. Un système de primitifs sémantiques est bon dans la mesure où il compresse efficacement le corpus des significations humaines tout en préservant la capacité prédictive.

---

## 4. Communication sémantique

### 4.1 Au-delà de Shannon : la communication orientée tâche

Depuis ~2020, un champ émergent étend la théorie de Shannon au niveau sémantique. Le constat de départ : dans de nombreuses applications (IoT, IA, robotique), transmettre fidèlement les bits est inutile — ce qui compte est que le **sens** pertinent pour la **tâche** soit préservé.

### 4.2 Rate-distortion sémantique (Liu et al., 2022)

Liu et al. proposent une **théorie rate-distortion étendue** pour la communication sémantique :

$$R_s(D_s) = \min_{p(\hat{s}|s): E[d_s(s,\hat{s})] \leq D_s} I(S; \hat{S})$$

où $d_s$ est une **mesure de distorsion sémantique** (et non bit-à-bit). Différentes tâches requièrent différentes métriques :

| Tâche | Métrique de distorsion sémantique |
|-------|----------------------------------|
| Classification | Divergence KL |
| Génération de texte | Distance de Wasserstein |
| Réponse à questions | Similarité cosinus des embeddings |
| Résumé | ROUGE / BERTScore |

### 4.3 Information Bottleneck (Tishby et al., 1999)

La méthode Information Bottleneck (IB) cherche la **compression optimale** d'une variable $X$ en une représentation $T$ qui préserve l'information pertinente sur une variable cible $Y$ :

$$\min_{p(t|x)} I(X;T) - \beta \cdot I(T;Y)$$

Le paramètre $\beta$ contrôle le compromis compression/pertinence.

**Implication profonde pour PanLang** : les 10 atomes de PanLang sont une tentative de « bottleneck » — comprimer le flux infini des significations humaines en 10 « goulots ». La question IB est : préservent-ils suffisamment d'information sur la variable cible (la compréhension) ?

### 4.4 Communication sémantique orientée tâche (Chai et al., 2025)

Chai et al. (PMC12385448) formalisent un cadre où :
- L'émetteur encode l'information sémantique pertinente pour une tâche
- Le canal sémantique n'est pas le canal physique mais la « bande passante du sens »
- Le récepteur reconstruit le sens nécessaire à l'accomplissement de la tâche

Résultat clé : **il n'y a pas de compression sémantique universelle** — la compression optimale dépend de la tâche. Ceci remet en question l'idée d'atomes sémantiques « universels » au sens absolu.

---

## 5. Calculabilité et primitives computationnelles

### 5.1 Lambda-calcul (Church, 1936)

Alonzo Church montre que le lambda-calcul est Turing-complet avec seulement :
- **Abstraction** : $\lambda x. M$ (créer une fonction)
- **Application** : $M \; N$ (appliquer une fonction)
- **Variable** : $x$ (référence)

Le Church encoding montre que toutes les structures de données (nombres, booléens, listes, paires) peuvent être encodées comme des **fonctions pures**.

### 5.2 Calcul combinatoire SKI (Schönfinkel, 1924 ; Curry)

Le calcul SKI montre qu'on peut se passer des variables avec seulement 3 combinateurs :

| Combinateur | Définition | Rôle |
|------------|-----------|------|
| **S** | $S \; f \; g \; x = f \; x \; (g \; x)$ | Distribution / composition |
| **K** | $K \; x \; y = x$ | Constante / projection |
| **I** | $I \; x = x$ | Identité |

Plus remarquable encore :
- **S et K seuls** suffisent (car $I = S \; K \; K$)
- Le combinateur **ι (iota)** de Barker est un **unique** combinateur Turing-complet :  
  $\iota \; x = x \; S \; K$

**Implication fondamentale** : la computation universelle peut se réduire à **un seul** primitif. Mais un tel primitif est inutilisable en pratique — la « bonne » granularité de primitifs est un compromis entre minimalité et lisibilité.

### 5.3 Machines de Turing et universalité

La machine de Turing universelle (1936) montre que **tout calcul possible** peut être réalisé par une machine ayant un alphabet fini, un ensemble d'états fini, et une table de transitions. Les primitifs sont :

- Lire un symbole
- Écrire un symbole  
- Déplacer la tête (gauche/droite)
- Changer d'état

Soit 4 opérations primitives pour toute computation possible.

### 5.4 Leçon pour PanLang

Le parallèle avec la computation suggère que :

| Système | Nb de primitifs | Turing-complet ? | Utilisable ? |
|---------|----------------|-------------------|-------------|
| Iota (ι) | 1 | Oui | Non |
| S, K | 2 | Oui | Difficilement |
| S, K, I | 3 | Oui | Acceptable |
| Lambda-calcul | 3 opérations | Oui | Bon |
| Turing machine | 4 opérations | Oui | Bon |
| PanLang | 10 atomes | ? | ? |

La question pour PanLang n'est pas « combien de primitifs ? » mais « sont-ils les bons ? » et « couvrent-ils les bonnes dimensions ? ».

---

## 6. Théorie des catégories et correspondance Curry-Howard-Lambek

### 6.1 Théorie des catégories (Eilenberg & Mac Lane, 1945)

La théorie des catégories est la « mathématique des mathématiques » — elle étudie les **structures** et leurs **relations structurelles**. Ses primitifs sont :

| Primitif | Définition |
|---------|-----------|
| **Objet** | Entité abstraite (type, ensemble, espace...) |
| **Morphisme** (flèche) | Transformation entre objets |
| **Composition** | Chaîner deux morphismes : $g \circ f$ |
| **Identité** | Morphisme $\text{id}_A : A \to A$ |

Avec seulement ces 4 notions et 2 axiomes (associativité de la composition, neutralité de l'identité), on peut exprimer une quantité stupéfiante de mathématiques.

### 6.2 Constructions universelles

La théorie des catégories identifie des **constructions universelles** — des patterns qui se retrouvent dans toutes les branches des mathématiques :

| Construction | Ce qu'elle capture | Exemples |
|-------------|-------------------|---------|
| **Produit** | Combinaison conjonctive (ET) | Paire $(A, B)$, intersection |
| **Coproduit** | Alternative disjonctive (OU) | Somme $A + B$, union |
| **Exponential** | Fonction / transformation | $B^A$ = espace des fonctions $A \to B$ |
| **Pullback** | Intersection contrainte | Produit fibré |
| **Pushout** | Recollement | Somme amalgamée |
| **Limite** | Généralisation du produit | Limite projective |
| **Colimite** | Généralisation du coproduit | Limite inductive |
| **Foncteur** | Transformation de structure | Correspondance entre catégories |
| **Transformation naturelle** | Transformation de transformations | Polymorphisme |

### 6.3 Lawvere : théories algébriques (1963)

F. William Lawvere, dans sa thèse de 1963 (*Functorial Semantics of Algebraic Theories*), révolutionne l'algèbre en montrant que toute théorie algébrique (groupes, anneaux, algèbres de Lie...) peut être représentée comme une catégorie spéciale. Les « modèles » d'une théorie sont les **foncteurs** préservant les produits finis.

**Implication** : les « atomes sémantiques » de PanLang pourraient être vus comme les **opérations de base** d'une théorie algébrique du sens, et les concepts comme des « termes » construits à partir de ces opérations.

### 6.4 Correspondance Curry-Howard-Lambek

L'une des découvertes les plus profondes du XXe siècle est la **triple correspondance** :

| Logique | Calcul | Catégorie |
|---------|--------|----------|
| Proposition | Type | Objet |
| Preuve | Programme | Morphisme |
| Implication $A \Rightarrow B$ | Fonction $A \to B$ | Exponentielle $B^A$ |
| Conjonction $A \wedge B$ | Produit $A \times B$ | Produit catégoriel |
| Disjonction $A \vee B$ | Somme $A + B$ | Coproduit |
| Vérité $\top$ | Type unité | Objet terminal |
| Fausseté $\bot$ | Type vide | Objet initial |

> « In the Curry–Howard–Lambek correspondence, a proof in logic, a program in computation, and a morphism in a category are not merely analogous — they are **the same thing**. » — Wadler (2015)

**Implication pour PanLang** : cette correspondance suggère que les « vrais » universaux ne sont ni purement linguistiques, ni purement logiques, ni purement computationnels — ils sont **structurels**. Toute tentative de primitifs universels devrait se situer à ce niveau d'abstraction.

---

## 7. Ontologies formelles supérieures

### 7.1 DOLCE (Masolo, Borgo, Gangemi et al., 2003)

DOLCE (*Descriptive Ontology for Linguistic and Cognitive Engineering*) est la première ontologie fondationnelle axiomatisée. Ses catégories de plus haut niveau :

| Catégorie | Description | Exemples |
|-----------|------------|---------|
| **Endurant** (Continuant) | Entités qui persistent dans le temps, entièrement présentes à chaque instant | Personnes, objets, lieux |
| **Perdurant** (Occurrent) | Entités qui se déploient dans le temps, présentes seulement en parties | Événements, processus, états |
| **Quality** | Propriétés inhérentes | Couleur, poids, forme |
| **Abstract** | Entités sans localisation spatio-temporelle | Nombres, propositions, régions |

DOLCE est stable depuis 20+ ans et utilisée dans de nombreux systèmes (Gangemi et al., 2023, arXiv:2308.01597).

### 7.2 BFO — Basic Formal Ontology (Smith et al., 2002 ; Arp, Smith & Spear, 2015)

BFO est l'ontologie supérieure la plus utilisée en sciences (550+ projets). Sa structure :

```
Entity
├── Continuant (persiste dans le temps)
│   ├── Independent Continuant (substances)
│   │   ├── Material Entity
│   │   └── Immaterial Entity (limites, sites)
│   ├── Specifically Dependent Continuant (qualités, dispositions)
│   └── Generically Dependent Continuant (patterns, informations)
└── Occurrent (se déploie dans le temps)
    ├── Process
    ├── Process Boundary
    ├── Temporal Region
    └── Spatiotemporal Region
```

BFO a été standardisé ISO/IEC 21838-2:2021.

### 7.3 SUMO — Suggested Upper Merged Ontology (Niles & Pease, 2001)

SUMO est la plus grande ontologie formelle publique (~25,000 termes). Sa racine :

```
Entity
├── Physical
│   ├── Object
│   └── Process
└── Abstract
    ├── Quantity
    ├── Attribute
    ├── Relation
    ├── Proposition
    └── Set/Class
```

### 7.4 Convergence des ontologies supérieures

Une comparaison (Mascardi, Cordì & Rosso, 2007 ; CEUR-WS Vol-2519) montre que les ontologies supérieures convergent vers une **partition fondamentale en 4 méta-catégories** :

| Méta-catégorie | DOLCE | BFO | SUMO |
|---------------|-------|-----|------|
| **Entité persistante** | Endurant | Continuant | Object |
| **Processus/Événement** | Perdurant | Occurrent | Process |
| **Qualité/Propriété** | Quality | Dependent Continuant | Attribute |
| **Abstraction** | Abstract | Generically Dependent | Abstract |

**Implication pour PanLang** : les 10 atomes de PanLang sont tous dans la catégorie **Perdurant/Occurrent** (processus verbaux). Il manque complètement les 3 autres méta-catégories : les entités (qui?), les qualités (comment?), et les abstractions (quoi?).

---

## 8. Linguistique formelle et sémantique universelle

### 8.1 NSM — Natural Semantic Metalanguage (Wierzbicka, 1972, 1996 ; Goddard & Wierzbicka, 2014)

Le NSM postule ~65 **primes sémantiques** — des concepts indéfinissables qui se retrouvent dans toutes les langues :

| Catégorie (16) | Primes |
|---------------|--------|
| Substantifs | I, YOU, SOMEONE, SOMETHING, PEOPLE, BODY |
| Déterminants | THIS, THE SAME, OTHER~ELSE |
| Quantificateurs | ONE, TWO, SOME, ALL, MUCH~MANY |
| Évaluateurs | GOOD, BAD |
| Descripteurs | BIG, SMALL |
| Prédicats mentaux | THINK, KNOW, WANT, DON'T WANT, FEEL, SEE, HEAR |
| Parole | SAY, WORDS, TRUE |
| Actions, événements | DO, HAPPEN, MOVE |
| Existence, possession | THERE IS~EXIST, BE (SOMEONE/SOMETHING), HAVE |
| Vie et mort | LIVE, DIE |
| Temps | WHEN~TIME, NOW, BEFORE, AFTER, A LONG TIME, A SHORT TIME, FOR SOME TIME, MOMENT |
| Espace | WHERE~PLACE, HERE, ABOVE, BELOW, FAR, NEAR, SIDE, INSIDE, TOUCH |
| Logique | NOT, MAYBE, CAN, BECAUSE, IF |
| Augmenteurs/intensifieurs | VERY, MORE |
| Similitude | LIKE~AS~WAY |
| Taxonomie | KIND OF, PART OF |

**Couverture PanLang** : seulement **15/65** primes (~23%). PanLang couvre bien les prédicats mentaux et les actions, mais manque les substantifs, quantificateurs, espace, temps et logique.

### 8.2 Jackendoff : Sémantique conceptuelle (1983, 1987, 1990)

Ray Jackendoff propose des **fonctions conceptuelles primitives** :

| Primitive | Rôle | Couvert par PanLang ? |
|----------|------|----------------------|
| GO(X, FROM, TO) | Mouvement/changement | ✅ MOUVEMENT |
| BE(X, AT/IN) | État/localisation | ✅ EXISTENCE |
| STAY(X, AT) | Permanence | ~ (partiellement EXISTENCE) |
| CAUSE(X, EVENT) | Causation | ✅ CRÉATION |
| LET(X, EVENT) | Permission | ❌ |
| AFFECT(X, Y) | Impact | ❌ |

### 8.3 Chomsky : le Programme Minimaliste (1995 ; Hauser, Chomsky & Fitch, 2002)

Le programme minimaliste de Chomsky réduit la Faculty of Language in the Narrow sense (FLN) à une seule opération :

> **Merge** : prendre deux éléments syntaxiques $\alpha$ et $\beta$ et former l'ensemble $\{\alpha, \beta\}$

Hauser, Chomsky & Fitch (2002) dans « The Faculty of Language: What Is It, Who Has It, and How Did It Evolve? » (Science, 298) proposent que **Merge est peut-être l'unique composante proprement linguistique** de la cognition humaine.

Important : Merge est considéré comme **domain-general** — il pourrait provenir de mécanismes cognitifs plus larges et ne serait pas spécifique au langage.

**Implication** : si l'opération fondamentale du langage est la **composition récursive** (Merge), alors les « atomes » de PanLang ne sont que la moitié du problème. L'autre moitié est la **règle de composition** — et PanLang utilise simplement l'addition (+), ce qui est trop pauvre.

### 8.4 Montague : sémantique formelle (1970, 1973)

Richard Montague dans « Universal Grammar » (1970) et « The Proper Treatment of Quantification in Ordinary English » (1973) montre que :

> « There is in my opinion no important theoretical difference between natural languages and the artificial languages of logicians. »

Son cadre clé : la **compositionnalité** — le sens d'une expression complexe est une **fonction** des sens de ses parties et de leur mode de combinaison syntaxique. Formellement, la sémantique est un **homomorphisme** de l'algèbre syntaxique vers l'algèbre sémantique.

### 8.5 Pustejovsky : le lexique génératif (1991, 1995)

James Pustejovsky propose la **structure des qualia** — 4 dimensions qui caractérisent le sens de tout item lexical, inspirées des 4 causes d'Aristote :

| Quale | Question | Cause aristotélicienne |
|-------|----------|----------------------|
| **Formel** (FORMAL) | Qu'est-ce que c'est ? | Cause formelle |
| **Constitutif** (CONSTITUTIVE) | De quoi est-ce fait ? | Cause matérielle |
| **Télique** (TELIC) | À quoi ça sert ? | Cause finale |
| **Agentif** (AGENTIVE) | Comment ça a été créé ? | Cause efficiente |

**Implication pour PanLang** : Pustejovsky montre que la description d'un concept nécessite au minimum 4 dimensions indépendantes. Les 10 atomes de PanLang, étant tous des prédicats verbaux, ne couvrent principalement que la dimension **agentive**.

### 8.6 Levin : classes verbales et alternances (1993)

Beth Levin dans *English Verb Classes and Alternations* montre que les verbes anglais se regroupent en classes basées sur leurs **alternances syntaxiques**, et que ces classes reflètent des **composantes sémantiques sous-jacentes** plus fines que les rôles thématiques.

Les classes de Levin (~200 classes, ~3000 verbes) corrèlent avec le Dhātupāṭha sanskrit (les 10 gaṇa de Pāṇini, ~2000 racines), confirmant que les classes verbales ont un fondement sémantique cross-linguistique.

FrameNet (Fillmore & Baker, 1998 ; Baker et al., 1998) et VerbNet (Schuler, 2006) étendent cette approche au-delà des verbes :
- **FrameNet** : ~1200 frames sémantiques, chacun avec des rôles (Frame Elements)
- **VerbNet** : 274 classes verbales avec prédicats sémantiques explicites

### 8.7 Baker : les atomes du langage (2001)

Mark Baker dans *The Atoms of Language* (2001) propose un ensemble de **paramètres syntaxiques** binaires qui génèrent la diversité des langues à partir d'une grammaire universelle. L'analogie avec la chimie est explicite : comme les éléments chimiques, quelques paramètres en nombre fini engendrent une diversité apparemment infinie.

---

## 9. Sémiotique et phénoménologie

### 9.1 Peirce : la sémiotique triadique (1867-1914)

Charles Sanders Peirce développe une théorie des signes fondée sur **trois catégories philosophiques** :

| Catégorie | Nature | Caractéristique |
|-----------|--------|----------------|
| **Priméité** (Firstness) | Qualité pure, potentialité | Sentiment, possibilité, icône |
| **Secondéité** (Secondness) | Fait brut, résistance, relation dyadique | Existant, réaction, index |
| **Tiercéité** (Thirdness) | Loi, médiation, relation triadique | Habitude, convention, symbole |

La **sémiose** est le processus triadique entre :
- **Representamen** (le signe lui-même) → First
- **Object** (ce à quoi le signe se réfère) → Second  
- **Interpretant** (l'effet du signe sur l'interprète) → Third

De cette structure, Peirce dérive **10 classes de signes** par application de la hiérarchie des catégories aux 3 corrélats.

La classification représentamen–objet donne le célèbre triptyque :

| Type | Relation signe-objet | Exemple |
|------|---------------------|---------|
| **Icône** | Ressemblance | Carte, diagramme, photo |
| **Index** | Connexion factuelle/causale | Fumée→feu, girouette→vent |
| **Symbole** | Convention arbitraire | Mots d'une langue, feux tricolores |

**Implication pour PanLang** : Peirce montre que toute sémiotique nécessite **3 catégories irréductibles** (qualité, fait, loi). Les 10 atomes de PanLang opèrent uniquement au niveau de la tiercéité (conventions symboliques) sans distinguer les niveaux de priméité (qualités pures) et de secondéité (faits).

### 9.2 Hjelmslev : glossématique (1943)

Louis Hjelmslev dans *Prolégomènes à une théorie du langage* (1943) propose une architecture du signe en **4 strates** par croisement de deux dichotomies :

|  | **Forme** | **Substance** |
|--|----------|--------------|
| **Expression** | Forme de l'expression (phonologie, syntaxe) | Substance de l'expression (sons, graphèmes) |
| **Contenu** | Forme du contenu (structure sémantique) | Substance du contenu (pensée, référence) |

Le **purport** (matière amorphe) est ce qui est antérieur à toute structuration linguistique. La langue est la **forme** qui structure le purport en expression et contenu.

Le **glossème** est l'unité minimale — soit du plan de l'expression (cénème), soit du plan du contenu (plérème).

**Implication pour PanLang** : Hjelmslev montre que les primitifs sémantiques (plérèmes) sont des **formes du contenu**, pas des « choses dans le monde ». Les atomes PanLang confondent forme du contenu et substance du contenu — ils désignent des processus réels (mouvement, cognition) plutôt que des formes sémantiques pures.

### 9.3 Eco : sémiose illimitée (1976, 1984, 1990)

Umberto Eco, dans *A Theory of Semiotics* (1976) et *Semiotics and the Philosophy of Language* (1984), étend la notion peircéenne de **sémiose illimitée** :

> Les signes renvoient toujours à d'autres signes. Il n'y a pas de « signifié final » — seulement un réseau encyclopédique de renvois.

Eco oppose le **modèle dictionnaire** (arborescent, hiérarchique — comme PanLang) au **modèle encyclopédique** (rhizomatique, réticulaire, ouvert).

Dans *The Limits of Interpretation* (1990), Eco tempère : la sémiose est illimitée en droit mais **limitée en pratique** par les conventions et les contextes d'usage.

**Implication pour PanLang** : Le modèle PanLang (décomposition en atomes fixes) est un modèle « dictionnaire ». Eco nous avertit que toute décomposition fixe est une **fermeture artificielle** d'un réseau ouvert. Mais il admet aussi que des structures locales existent et sont utiles.

---

## 10. Panini historique : l'Aṣṭādhyāyī comme système computationnel

### 10.1 L'exploit de Pāṇini

L'Aṣṭādhyāyī de Pāṇini (~4e siècle AEC) est un système de **~4000 règles** (sūtra) qui génère toutes les formes valides du sanskrit. C'est reconnu comme le premier système formel de l'histoire (Staal, 1965 ; Kiparsky, 2002 ; Cardona, 1997).

Les parallèles avec l'informatique moderne sont frappants (Mishra, 2018) :

| Concept Pāṇini | Équivalent informatique |
|----------------|------------------------|
| Sūtra conditionnels | Instructions IF-THEN |
| Récursivité des règles | Fonctions récursives |
| Règles plus spécifiques prévalent | Surcharge, exception handling |
| IT markers (marqueurs techniques) | Métadonnées, escape characters |
| Adhikāra sūtra (portée) | Namespaces, variable scope |
| Pratyāhāra (shortcodes) | Expressions régulières, macros |
| Dhātu (racines) | Données primitives |
| Prakriyā (dérivation) | Compilation, pipeline |

### 10.2 Le Dhātupāṭha

Le Dhātupāṭha de Pāṇini organise ~2000 racines verbales en **10 classes** (gaṇa). Ces classes ne sont pas seulement morphologiques — elles reflètent des distinctions sémantiques profondes.

PanLang s'inspire de cette tradition mais fait un saut qualitatif discutable : passer de ~2000 racines en 10 classes à **10 atomes** censés tout recouvrir. C'est une compression extrême ($\times 200$) qui n'est pas justifiée par la tradition sanskrite elle-même.

### 10.3 L'Aṣṭādhyāyī comme MDL

Vue sous l'angle MDL, l'Aṣṭādhyāyī est un chef-d'œuvre de compression : 4000 sūtra ultra-compacts pour générer un espace linguistique immense. Pāṇini optimise $L(M) + L(D|M)$ en :
- Minimisant $L(M)$ (sūtra courts, pratyāhāra, adhikāra)
- Maintenant $L(D|M) = 0$ (couverture complète du sanskrit)

PanLang devrait s'inspirer de cette rigueur : une compression qui **perd** de l'information n'est pas dans l'esprit de Pāṇini.

---

## 11. Convergence : vers des universaux transversaux

### 11.1 Tableau de convergence

En croisant les 10 domaines étudiés, on identifie des **motifs récurrents** :

| Motif universel | Théorie info | Computation | Catégories | Ontologie | Linguistique | Sémiotique |
|----------------|-------------|-------------|-----------|-----------|-------------|-----------|
| **Entité / Objet** | Source | Donnée | Objet | Endurant | SOMETHING | Objet (second) |
| **Processus / Transformation** | Canal | Fonction | Morphisme | Perdurant | DO, HAPPEN | Sémiose |
| **Qualité / Propriété** | Signal | Type | Attribut | Quality | BIG, GOOD | Qualisign |
| **Relation / Structure** | Code | Application | Foncteur | Relation | PART OF, KIND OF | Interprétant |
| **Composition** | Encodage | λ-abstraction | Composition ∘ | Méréologie | Merge | Sémiose illimitée |
| **Identité** | Identité | I combinator | id | Identité | SAME | Icône |
| **Négation / Absence** | Bruit | ⊥ (bottom) | Objet initial | — | NOT | — |
| **Quantification** | Entropie | Récursion | Limites | Quantité | ONE, ALL, SOME | — |
| **Temporalité** | Séquence | Étape | Séquence | Temporal Region | BEFORE, AFTER | Index temporel |
| **Spatialité** | Canal | Adressage | Topos | Spatial Region | HERE, ABOVE | Index spatial |
| **Modalité** | Probabilité | Possibilité | Sous-objet | Disposition | CAN, MAYBE | — |
| **Causation** | — | S combinator | Flèche | Dépendance | BECAUSE | Index causal |
| **Intentionnalité** | Pertinence (β) | But, tâche | — | Agentivité | WANT, KNOW | Interprétant final |

### 11.2 Les 7 dimensions irréductibles

De cette convergence émergent **7 dimensions** que tout système de primitifs sémantiques devrait couvrir :

1. **ENTITÉ** — ce qui *est* (ontologie : endurant ; logique : objet ; computation : donnée)
2. **PROCESSUS** — ce qui *se passe* (ontologie : perdurant ; calcul : fonction/morphisme)
3. **QUALITÉ** — ce qui *caractérise* (ontologie : quality ; calcul : type ; sémiotique : firstness)
4. **RELATION** — ce qui *relie* (catégories : foncteur ; logique : relation ; sémiotique : thirdness)
5. **STRUCTURE** — ce qui *compose* (Merge, composition catégorielle, encodage, abstraction lambda)
6. **SITUATION** — ce qui *situe* dans l'espace-temps (topos, régions spatio-temporelles, indexicaux)
7. **MODALITÉ** — ce qui est *possible, nécessaire, voulu* (probabilité, disposition, can/want)

### 11.3 Ce que PanLang couvre et ce qui manque

| Dimension | Couverture PanLang | Atomes correspondants |
|-----------|-------------------|----------------------|
| ENTITÉ | ❌ Absente | — |
| PROCESSUS | ✅ Excellente | MOUVEMENT, CRÉATION, DESTRUCTION |
| QUALITÉ | ⚠️ Partielle | PERCEPTION (mais passive) |
| RELATION | ⚠️ Partielle | POSSESSION, COMMUNICATION |
| STRUCTURE | ❌ Absente | — (seulement l'opérateur +) |
| SITUATION | ❌ Absente | — |
| MODALITÉ | ⚠️ Partielle | DOMINATION (trop étroite) |

**Verdict** : PanLang excelle sur la dimension PROCESSUS (qui correspond aux dhātu verbaux) mais **ignore 3 dimensions sur 7** et ne couvre que partiellement 2 autres.

---

## 12. Positionnement de PanLang

### 12.1 Forces

1. **Ancrage dans une tradition éprouvée** : le Dhātupāṭha et l'Aṣṭādhyāyī de Pāṇini sont des chefs-d'œuvre validés par 2500 ans d'usage
2. **Bonne couverture de la prédication verbale** : les 10 atomes capturent raisonnablement les grandes familles de procès (Vendler : états, activités, accomplissements, achèvements)
3. **Ambition compositionnelle** : l'idée de décomposer les concepts en formules est conforme au principe de compositionnalité (Montague)
4. **Compression forte** : 10 atomes pour des milliers de concepts est une compression agressive, dans l'esprit de Kolmogorov/MDL

### 12.2 Faiblesses

1. **Confusion verbal/universel** : les dhātu sont des racines *verbales* — ils ne couvrent pas les catégories ontologiques non-verbales (entités, qualités, abstractions)
2. **Règle de composition trop pauvre** : l'opérateur `+` est commutatif et sans structure — il est loin de la puissance de Merge (Chomsky), de la composition catégorielle, ou du lambda-calcul
3. **Pas de distinction sémiotique** : pas de niveaux peircéens (icône/index/symbole), pas de strates hjelmslévienne (forme/substance)
4. **Compression lossy non contrôlée** : MUSIQUE = DESTRUCTION + MOUVEMENT est une perte d'information inacceptable (la distorsion sémantique au sens rate-distortion est trop élevée)
5. **Pas de mécanisme de pertinence** : pas de paramètre $\beta$ (Information Bottleneck) pour contrôler le compromis compression/fidélité
6. **Pas de qualia** : pas de dimensions pustojevskiennes (formel, constitutif, télique, agentif)

### 12.3 Position dans le paysage

```
Expressivité
    ↑
    │  FrameNet (1200 frames)
    │  VerbNet (274 classes)
    │  NSM (65 primes) ◄─── cible raisonnable
    │  Levin (200 classes)
    │
    │  Jackendoff (6 fonctions)
    │
    │  PanLang (10 atomes) ◄─── ICI
    │  Pustejovsky (4 qualia)
    │
    │  S, K, I (3 combinateurs)
    │  Lambda-calcul (3 opérations)
    │
    │  ι iota (1 combinateur)
    ↓
    Minimalité ──────────────────→ Couverture
```

PanLang se situe dans la **zone de sur-compression** — trop peu de primitifs pour être sémantiquement fidèle, trop spécialisé (verbal) pour être véritablement universel.

---

## 13. Proposition de primitives révisées

### 13.1 Architecture proposée : 3 couches

Inspirée de la convergence interdisciplinaire, nous proposons une architecture à **3 couches** :

#### Couche 1 : Méta-catégories ontologiques (4)

Issues de DOLCE/BFO/SUMO :

| # | Méta-catégorie | Notation | Source |
|---|---------------|----------|--------|
| 1 | ENTITÉ | `ENT` | Endurant (DOLCE), Continuant (BFO), Object (SUMO) |
| 2 | PROCESSUS | `PROC` | Perdurant (DOLCE), Occurrent (BFO), Process (SUMO) |
| 3 | QUALITÉ | `QUAL` | Quality (DOLCE), Dep. Continuant (BFO), Attribute (SUMO) |
| 4 | ABSTRACTION | `ABS` | Abstract (DOLCE), Gen. Dep. (BFO), Abstract (SUMO) |

#### Couche 2 : Opérations structurelles (5)

Issues de la théorie des catégories + logique + computation :

| # | Opération | Notation | Source |
|---|----------|----------|--------|
| 5 | COMPOSITION | `COMP` | Merge (Chomsky), ∘ (catégories), λ (Church), S (SKI) |
| 6 | IDENTITÉ | `ID` | id (catégories), I (SKI), SAME (NSM) |
| 7 | NÉGATION | `NEG` | NOT (NSM), ⊥ (logique), objet initial |
| 8 | QUANTIFICATION | `QUANT` | Limites (catégories), ONE/ALL/SOME (NSM), entropie |
| 9 | MODALITÉ | `MOD` | CAN/MAYBE (NSM), probabilité, disposition (BFO) |

#### Couche 3a : Prédicats sémantiques (9, revus — ÉMOTION → couche 3c)

Les 9 atomes PanLang sémantiques, réorganisés dans la dimension PROCESSUS et enrichis.
L'ancien atome ÉMOTION (√hṛd) a été retiré et remplacé par 8 sous-primitifs émotionnels
fondés sur les neurosciences affectives (voir couche 3c ci-dessous).

| # | Prédicat | Dhātu | Couverture |
|---|---------|-------|-----------|
| 10 | MOUVEMENT | √gam | GO (Jackendoff), MOVE (NSM) |
| 11 | COGNITION | √jñā | THINK, KNOW (NSM) |
| 12 | PERCEPTION | √dṛś | SEE, HEAR (NSM) |
| 13 | COMMUNICATION | √vac | SAY (NSM) |
| 14 | CRÉATION | √kṛ | CAUSE (Jackendoff), DO (NSM) |
| 15 | EXISTENCE | √as | EXIST, BE (NSM, Jackendoff) |
| 16 | DESTRUCTION | — | DIE (NSM) |
| 17 | POSSESSION | √labh | HAVE (NSM) |
| 18 | VOLITION | √īś | WANT (NSM) — renommé de DOMINATION |

#### Couche 3b : Extensions nécessaires (non-verbales) :

| # | Extension | Justification |
|---|----------|--------------|
| 19 | SITUATION (espace) | WHERE, HERE, ABOVE (NSM), Spatial Region (BFO), topos |
| 20 | SITUATION (temps) | WHEN, BEFORE, AFTER (NSM), Temporal Region (BFO) |
| 21 | ÉVALUATION | GOOD, BAD (NSM), axiologie |
| 22 | TAXONOMIE | KIND OF, PART OF (NSM), méréologie |

#### Couche 3c : Axes émotionnels (v2.2 — Panksepp/Ekman/Plutchik/Damasio) :

L'atome unique ÉMOTION (√hṛd) ne discriminait pas entre des circuits neuronaux
fondamentalement distincts. La validation Gutenberg (v2.1) a confirmé empiriquement
que les concepts émotionnels ne convergent jamais entre traductions (0 concept majorité).

8 sous-primitifs émotionnels organisés en 4 axes bipolaires :

| # | Axe | Pôle + | Dhātu | Pôle − | Dhātu | Circuit neural |
|---|-----|--------|-------|--------|-------|---------------|
| 23-24 | APPÉTENCE | SEEKING | √iṣ | FEAR | √bhī | Mésolimbique DA ↔ Amygdale-PAG |
| 25-26 | LIEN | CARE | √snuh | GRIEF | √śuc | Ocytocine ↔ Opioïdes↓ |
| 27-28 | ASSERTION | RAGE | √krudh | DISGUST | √jugupsā | PAG/hypothal. ↔ Insula |
| 29-30 | JOUISSANCE | PLAY | √krīḍ | TEDIUM | √glai | Thalamo-striatal ↔ Hypo-DA |

Références : Panksepp (1998, 2012), Ekman (1992), Plutchik (2001), Damasio (1994, 1999),
LeDoux (1996, 2012), Barrett (2017). Voir PROPOSITION_SOUS_PRIMITIFS_EMOTIONNELS.md.

### 13.2 Total : 30 primitifs en 3 couches + sous-couche émotionnelle

- **4** méta-catégories ontologiques (ce qui *est*)
- **5** opérations structurelles (comment on *compose*)  
- **9** prédicats sémantiques verbaux (ce qui *se passe*) — les dhātu PanLang (EMOTION retiré)
- **4** extensions non-verbales (où, quand, comment, quoi)
- **8** axes émotionnels (circuits neurophysiologiques distincts)

= **30 primitifs** — à comparer avec :
- PanLang actuel : 10 (sous-spécifié)
- NSM : 65 (linguistiquement motivé)
- SKI : 3 (Turing-complet mais inutilisable)
- DOLCE : 4 catégories + axiomes

### 13.3 Règle de composition enrichie

Remplacer l'opérateur `+` par un **système typé** :

```
concept := PROC(prédicat, [rôle1: ENT, rôle2: ENT, ...]) 
         | QUAL(qualité, ENT)
         | ABS(relation, [terme1, terme2, ...])
         | COMP(concept1, concept2, mode)
```

où `mode` peut être :
- `AND` — conjonction
- `SEQ` — séquence temporelle
- `CAUSE` — relation causale
- `PART` — méréologie
- `TYPE` — taxonomie

Ce système est conforme à :
- Pustejovsky : qualia structure (Formel, Constitutif, Télique, Agentif → types de `mode`)
- Montague : compositionnalité comme homomorphisme
- Catégories : morphismes typés
- Lambda-calcul : application fonctionnelle

---

## 14. Bibliographie complète

### Théorie de l'information

1. Shannon, C. E. (1948). « A Mathematical Theory of Communication ». *Bell System Technical Journal*, 27(3), 379–423.
2. Shannon, C. E. & Weaver, W. (1949). *The Mathematical Theory of Communication*. University of Illinois Press.
3. Kolmogorov, A. N. (1965). « Three Approaches to the Quantitative Definition of Information ». *Problems of Information Transmission*, 1(1), 1–7.
4. Rissanen, J. (1978). « Modeling by Shortest Data Description ». *Automatica*, 14(5), 465–471.
5. Carnap, R. & Bar-Hillel, Y. (1952). *An Outline of a Theory of Semantic Information*. MIT Technical Report No. 247.
6. Floridi, L. (2011). *The Philosophy of Information*. Oxford University Press.
7. Floridi, L. (2004). « Outline of a Theory of Strongly Semantic Information ». *Minds and Machines*, 14(2), 197–221.

### Information algorithmique et intelligence universelle

8. Solomonoff, R. J. (1964). « A Formal Theory of Inductive Inference ». *Information and Control*, 7(1–2), 1–22, 224–254.
9. Chaitin, G. J. (1966). « On the Length of Programs for Computing Finite Binary Sequences ». *Journal of the ACM*, 13(4), 547–569.
10. Hutter, M. (2000). « A Theory of Universal Artificial Intelligence based on Algorithmic Complexity ». arXiv:cs/0004001.
11. Hutter, M. (2005). *Universal Artificial Intelligence: Sequential Decisions Based on Algorithmic Probability*. Springer.
12. Sunehag, P. & Hutter, M. (2015). « Principles of Solomonoff Induction and AIXI ». In *Algorithmic Probability and Friends*, LNCS 7070.

### Communication sémantique

13. Tishby, N., Pereira, F. C. & Bialek, W. (1999). « The Information Bottleneck Method ». In *Proc. 37th Annual Allerton Conference on Communication, Control, and Computing*.
14. Liu, F. et al. (2022). « Task-Oriented Semantic Communication Systems Based on Extended Rate-Distortion Theory ». *IEEE Transactions*.
15. Chai, J. et al. (2025). « Rate-Distortion Theory for Task-Specific Semantic Communication ». *PMC12385448*.
16. Bao, J. et al. (2011). « Towards a Theory of Semantic Communication ». In *IEEE Network Science Workshop*.

### Calculabilité

17. Turing, A. M. (1936). « On Computable Numbers, with an Application to the Entscheidungsproblem ». *Proc. London Math. Soc.*, s2-42(1), 230–265.
18. Church, A. (1936). « An Unsolvable Problem of Elementary Number Theory ». *American Journal of Mathematics*, 58(2), 345–363.
19. Schönfinkel, M. (1924). « Über die Bausteine der mathematischen Logik ». *Mathematische Annalen*, 92, 305–316.
20. Curry, H. B. & Feys, R. (1958). *Combinatory Logic*, Vol. I. North-Holland.
21. Barker, C. (2001). « Iota: A Formal Language with a Single One-Character Combinator ».

### Théorie des catégories

22. Eilenberg, S. & Mac Lane, S. (1945). « General Theory of Natural Equivalences ». *Transactions of the AMS*, 58(2), 231–294.
23. Lawvere, F. W. (1963). *Functorial Semantics of Algebraic Theories*. PhD thesis, Columbia University. Reprinted in *Theory and Applications of Categories*, 5 (2004), 1–121.
24. Mac Lane, S. (1971). *Categories for the Working Mathematician*. Springer.
25. Lambek, J. (1968). « The Mathematics of Sentence Structure ». *American Mathematical Monthly*, 65, 154–170.

### Correspondance Curry-Howard-Lambek

26. Howard, W. A. (1969/1980). « The Formulae-as-Types Notion of Construction ». In *To H.B. Curry: Essays on Combinatory Logic, Lambda Calculus and Formalism*, Academic Press.
27. Wadler, P. (2015). « Propositions as Types ». *Communications of the ACM*, 58(12), 75–84.

### Ontologies formelles supérieures

28. Masolo, C., Borgo, S., Gangemi, A., Guarino, N. & Oltramari, A. (2003). *WonderWeb Deliverable D18: Ontology Library*. DOLCE.
29. Gangemi, A. et al. (2023). « DOLCE: A Descriptive Ontology for Linguistic and Cognitive Engineering ». arXiv:2308.01597.
30. Arp, R., Smith, B. & Spear, A. D. (2015). *Building Ontologies with Basic Formal Ontology*. MIT Press.
31. Smith, B. et al. (2005). « Relations in Biomedical Ontologies ». *Genome Biology*, 6(5), R46.
32. ISO/IEC 21838-2:2021. *Information technology — Top-level ontologies (TLO) — Part 2: Basic Formal Ontology (BFO)*.
33. Niles, I. & Pease, A. (2001). « Towards a Standard Upper Ontology ». In *Proc. FOIS 2001*, 2–9.
34. Mascardi, V., Cordì, V. & Rosso, P. (2007). « A Comparison of Upper Ontologies ». In *Proc. AI*IA 2007*, LNAI 4733.
35. CEUR-WS Vol-2519 (2019). Foundational Ontology Comparison Papers.

### Linguistique formelle et sémantique universelle

36. Wierzbicka, A. (1972). *Semantic Primitives*. Athenäum.
37. Wierzbicka, A. (1996). *Semantics: Primes and Universals*. Oxford University Press.
38. Goddard, C. & Wierzbicka, A. (2014). « Semantic Primes and Universal Grammar ». In *Words and Meanings: Lexical Semantics Across Domains, Languages, and Cultures*. Oxford University Press.
39. Goddard, C. & Wierzbicka, A. (2018). « Minimal English and How It Can Add to Global English ». In *Minimal Languages in Action*, Palgrave.
40. Jackendoff, R. (1983). *Semantics and Cognition*. MIT Press.
41. Jackendoff, R. (1987). *Consciousness and the Computational Mind*. MIT Press.
42. Jackendoff, R. (1990). *Semantic Structures*. MIT Press.
43. Chomsky, N. (1995). *The Minimalist Program*. MIT Press.
44. Hauser, M. D., Chomsky, N. & Fitch, W. T. (2002). « The Faculty of Language: What Is It, Who Has It, and How Did It Evolve? ». *Science*, 298(5598), 1569–1579.
45. Montague, R. (1970a). « English as a Formal Language ». In *Linguaggi nella società e nella tecnica*.
46. Montague, R. (1970b). « Universal Grammar ». *Theoria*, 36(3), 373–398.
47. Montague, R. (1973). « The Proper Treatment of Quantification in Ordinary English ». In *Approaches to Natural Language*, Reidel.
48. Partee, B. H. (2001). « Montague Grammar ». In *International Encyclopedia of the Social & Behavioral Sciences*, Elsevier.
49. Martin-Löf, P. (1984). *Intuitionistic Type Theory*. Bibliopolis.
50. Pustejovsky, J. (1991). « The Generative Lexicon ». *Computational Linguistics*, 17(4), 409–441.
51. Pustejovsky, J. (1995). *The Generative Lexicon*. MIT Press.
52. Levin, B. (1993). *English Verb Classes and Alternations: A Preliminary Investigation*. University of Chicago Press.
53. Baker, C. F., Fillmore, C. J. & Lowe, J. B. (1998). « The Berkeley FrameNet Project ». In *Proc. ACL/COLING 1998*.
54. Schuler, K. K. (2006). *VerbNet: A Broad-Coverage, Comprehensive Verb Lexicon*. PhD thesis, University of Pennsylvania.
55. Baker, M. C. (2001). *The Atoms of Language*. Basic Books.

### Sémiotique et phénoménologie

56. Peirce, C. S. (1931–1958). *Collected Papers of Charles Sanders Peirce*. 8 vols. Harvard University Press. [Eds. C. Hartshorne, P. Weiss, A. W. Burks].
57. Peirce, C. S. (1906). « Prolegomena to an Apology for Pragmaticism ». *The Monist*, 16(4), 492–546.
58. Eco, U. (1976). *A Theory of Semiotics*. Indiana University Press.
59. Eco, U. (1984). *Semiotics and the Philosophy of Language*. Indiana University Press.
60. Eco, U. (1990). *The Limits of Interpretation*. Indiana University Press.
61. Hjelmslev, L. (1943/1961). *Prolegomena to a Theory of Language*. [Trad. F. J. Whitfield]. University of Wisconsin Press.
62. Greimas, A. J. (1966). *Sémantique structurale*. Larousse.
63. Everaert-Desmedt, N. (2011). « Peirce's Semiotics ». In L. Hébert (dir.), *Signo* [en ligne].

### Lakoff et sémantique cognitive

64. Lakoff, G. & Johnson, M. (1980). *Metaphors We Live By*. University of Chicago Press.
65. Lakoff, G. (1987). *Women, Fire, and Dangerous Things*. University of Chicago Press.

### Panini et grammaire sanskrite

66. Pāṇini (~4e s. AEC). *Aṣṭādhyāyī*.
67. Staal, J. F. (1965). « Euclid and Pāṇini ». *Philosophy East and West*, 15(2), 99–116.
68. Kiparsky, P. (2002). « On the Architecture of Pāṇini's Grammar ». In *Three lectures at the Hyderabad conference on the Ashtadhyayi*.
69. Cardona, G. (1997). *Pāṇini: His Work and Its Traditions*. 2nd ed. Motilal Banarsidass.
70. Mishra, A. (2018). *Modeling the Pāṇinian System of Sanskrit Grammar*. Heidelberg University Publishing.

### Philosophie et fondements

71. Tegmark, M. (2008). « The Mathematical Universe ». *Foundations of Physics*, 38, 101–150. arXiv:0704.0646.
72. Yanofsky, N. S. (2013). *The Outer Limits of Reason*. MIT Press.

---

## Annexe : Glossaire des acronymes

| Acronyme | Signification |
|----------|--------------|
| BFO | Basic Formal Ontology |
| DOLCE | Descriptive Ontology for Linguistic and Cognitive Engineering |
| FLN | Faculty of Language — Narrow sense |
| GDI | General Definition of Information (Floridi) |
| GL | Generative Lexicon |
| IB | Information Bottleneck |
| MDL | Minimum Description Length |
| MUH | Mathematical Universe Hypothesis |
| NSM | Natural Semantic Metalanguage |
| SKI | S, K, I combinator calculus |
| SUMO | Suggested Upper Merged Ontology |

---

*Document généré le 2025-07-24. Dernière mise à jour : 2025-07-24.*  
*Ce document fait partie du projet Panini-FS, SANDBOX/dolt-concept-store/.*
