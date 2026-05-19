---
title: Atomes universaux — tableau complet
---

# Les 34 atomes universaux de PaniniFS

Le moteur sémantique PaniniFS repose sur **34 atomes sémantiques** répartis en 4 catégories ontologiques et 6 couches d'abstraction. Ces atomes constituent le vocabulaire minimal permettant d'encoder l'essentiel des concepts humains dans toute langue naturelle.

!!! info "Convention de nommage"
    Les noms d'atomes (MOUVEMENT, COGNITION, CRÉATION…) sont des **identifiants canoniques** en MAJUSCULES. Ils sont définis en français dans le code source (`import_panlang_v2.py`) mais servent d'identifiants universels indépendants de la langue. Le code Python et les bases Dolt utilisent ces noms comme clés stables.

!!! success "Validation"
    Ces 34 atomes ont été validés sur **14 langues** et **~8M mots** (Gutenberg + Wikipédia).
    Couverture de présence : **34/34 = 100%** sur le corpus Wikipédia 14 langues.

---

## Tableau synthétique des 34 atomes

### Couche 3a — Prédicats sémantiques (9 atomes)

| Atome | Catégorie | Sens opérationnel | Primitives NSM | Dhātu sanscrit |
|-------|-----------|-------------------|----------------|----------------|
| **MOUVEMENT** | PROCESSUS | Déplacement dans l'espace | MOVE | √gam |
| **COGNITION** | PROCESSUS/QUALITÉ | Pensée, connaissance | THINK, KNOW | √jñā |
| **PERCEPTION** | PROCESSUS/QUALITÉ | Voir, entendre, ressentir | SEE, HEAR | √dṛś |
| **COMMUNICATION** | PROCESSUS/RELATION | Dire, transmettre | SAY | √vac |
| **CRÉATION** | PROCESSUS | Faire, causer | DO, HAPPEN | √kṛ |
| **EXISTENCE** | ENTITÉ/PROCESSUS | Être, exister | EXIST, THERE IS | √as |
| **DESTRUCTION** | PROCESSUS | Mourir, briser | DIE | — |
| **POSSESSION** | RELATION/PROCESSUS | Avoir, obtenir | HAVE | √labh |
| **DOMINATION** | MODALITÉ/RELATION | Vouloir, pouvoir | WANT, CAN | √īś |

### Couche 3c — Axes émotionnels (8 atomes)

| Atome | Catégorie | Sens opérationnel | Primitives NSM | Dhātu sanscrit |
|-------|-----------|-------------------|----------------|----------------|
| **SEEKING** | QUALITÉ/PROCESSUS | Chercher, désirer | WANT | √iṣ |
| **FEAR** | QUALITÉ/PROCESSUS | Peur, crainte | FEEL | √bhī |
| **CARE** | QUALITÉ/RELATION | Soin, amour | FEEL, GOOD | √snuh |
| **GRIEF** | QUALITÉ/PROCESSUS | Chagrin, tristesse | FEEL, BAD | √śuc |
| **RAGE** | QUALITÉ/PROCESSUS | Colère, fureur | FEEL, BAD | √krudh |
| **DISGUST** | QUALITÉ/PROCESSUS | Dégoût, rejet | FEEL, BAD | √jugupsā |
| **PLAY** | QUALITÉ/PROCESSUS | Jeu, plaisir | FEEL, GOOD | √krīḍ |
| **TEDIUM** | QUALITÉ/PROCESSUS | Ennui, lassitude | FEEL, BAD | √glai |

### Couche 4 — Atomes abstraits (7 atomes)

| Atome | Catégorie | Sens opérationnel | Primitives NSM | Jackendoff |
|-------|-----------|-------------------|----------------|-----------|
| **RELATION** | RELATION | Lien entre entités | LIKE, OF, WITH | — |
| **STRUCTURE** | STRUCTURE/RELATION | Organisation, hiérarchie | PART, KIND | — |
| **INVARIANCE** | QUALITÉ/STRUCTURE | Stabilité, persistance | SAME | STAY |
| **RÉCURRENCE** | PROCESSUS/STRUCTURE | Répétition, itération | AGAIN, MORE | — |
| **DUALITÉ** | RELATION/MODALITÉ | Opposition, négation, condition | OTHER, NOT, IF | — |
| **MESURE** | QUALITÉ/RELATION | Quantité, taille, degré | BIG, SMALL, MUCH | AMOUNT |
| **ORDRE** | RELATION/STRUCTURE | Séquence, avant/après | BEFORE, AFTER, ABOVE | — |

### Couche 5 — Atomes d'entité (5 atomes)

| Atome | Catégorie | Sens opérationnel | Primitives NSM | Jackendoff |
|-------|-----------|-------------------|----------------|-----------|
| **CHOSE** | ENTITÉ | Objet, substance | SOMETHING, THING | THING |
| **AGENT** | ENTITÉ/PROCESSUS | Être animé, personne | SOMEONE, PEOPLE, I, YOU | — |
| **CORPS** | ENTITÉ/STRUCTURE | Corps physique, partie | BODY | — |
| **LIEU** | ENTITÉ/STRUCTURE | Endroit, position | WHERE, PLACE, HERE | PLACE |
| **MATIÈRE** | ENTITÉ/QUALITÉ | Substance, matériau | PART | — |

### Couche 6 — Atomes de qualité (5 atomes)

| Atome | Catégorie | Sens opérationnel | Primitives NSM | Aristote |
|-------|-----------|-------------------|----------------|---------|
| **BON** | QUALITÉ | Valeur positive, bien | GOOD | ποιότης |
| **GRAND** | QUALITÉ/ENTITÉ | Taille, grandeur | BIG | ποιότης |
| **VRAI** | QUALITÉ/MODALITÉ | Vérité, exactitude | TRUE | ποιότης |
| **INTENSE** | QUALITÉ/PROCESSUS | Intensité, degré | VERY, MUCH | ποιότης |
| **ANCIEN** | QUALITÉ/PROCESSUS | Ancienneté, durée | BEFORE, A LONG TIME | ποιότης |

---

## Répartition par catégorie ontologique

| Catégorie | Français | Sanskrit | Atomes | Count |
|-----------|----------|----------|--------|-------|
| **PROCESSUS** (dominant) | Processus | kriyā | MOUVEMENT, COGNITION, COMMUNICATION, CRÉATION, EXISTENCE, DESTRUCTION, POSSESSION, SEEKING, FEAR, CARE, GRIEF, RAGE, DISGUST, PLAY, TEDIUM, RÉCURRENCE | ~16 |
| **RELATION** (dominant) | Relation | sambandha | DOMINATION, POSSESSION, RELATION, STRUCTURE, INVARIANCE, ORDRE | ~6 |
| **QUALITÉ** (dominant) | Qualité | guṇa | PERCEPTION, COGNITION, BON, GRAND, VRAI, INTENSE, ANCIEN, MESURE | ~8 |
| **ENTITÉ** (dominant) | Entité | dravya | CHOSE, AGENT, CORPS, LIEU, MATIÈRE, EXISTENCE | ~6 |

> Note : les catégories sont indicatives ; de nombreux atomes couvrent plusieurs catégories (ex. COGNITION est 70% PROCESSUS + 30% QUALITÉ).

---

## Les 7 opérateurs dhātu informationnels

En complément des 34 atomes analytiques, PaniniFS utilise **7 opérateurs dhātu** pour encoder les flux d'information à haut niveau :

| Dhātu | Opération | Sous-primitives |
|-------|-----------|----------------|
| **COMM** | Communiquer/partager | canal, source, cible |
| **ITER** | Itérer/répéter | boucle, fréquence, cumul |
| **TRANS** | Transformer | entrée, opération, sortie |
| **DECIDE** | Choisir/régler | critères, seuils, branches |
| **LOCATE** | Localiser/ancrer | position, contexte, repères |
| **GROUP** | Regrouper/structurer | collection, appartenance |
| **SEQ** | Séquencer/ordonner | ordre, dépendances, timeline |

**Correspondance avec les 34 atomes** :
- COMM ↔ COMMUNICATION, RELATION
- ITER ↔ RÉCURRENCE, MESURE
- TRANS ↔ CRÉATION, DESTRUCTION, MOUVEMENT
- DECIDE ↔ DOMINATION, DUALITÉ
- LOCATE ↔ LIEU, ORDRE, RELATION
- GROUP ↔ STRUCTURE, RELATION
- SEQ ↔ ORDRE, RÉCURRENCE

---

## Correspondances théoriques

Les 34 atomes PaniniFS sont mis en correspondance avec plusieurs systèmes sémantiques :

| Système | Références | Correspondance |
|---------|-----------|----------------|
| **NSM** (Natural Semantic Metalanguage) | Wierzbicka 1972, Goddard 2002 | Primes universels : GOOD, BAD, BIG, SMALL, THINK, KNOW, FEEL, SAY, DO, HAPPEN… |
| **Jackendoff** | Conceptual Semantics 1990 | GO, STAY, BE, CAUSE, LET, INCH, HAVE, AFFECT, THING, PLACE, AMOUNT |
| **Pustejovsky** | Generative Lexicon 1995 | Qualia : FORMAL, AGENTIVE, TELIC, CONSTITUTIVE |
| **Dhātu sanscrit** | Pāṇini Ashtādhyāyī | √gam, √jñā, √dṛś, √vac, √kṛ, √as, √labh, √iṣ, √bhī… |

---

## Exemple d'encodage

**Phrase** : « Le chat chasse la souris. »

| Segment | Atome(s) | Catégorie |
|---------|----------|-----------|
| Le chat | AGENT | ENTITÉ |
| chasse | MOUVEMENT + DESTRUCTION | PROCESSUS |
| la souris | CHOSE + PATIENT | ENTITÉ |
| (habituel) | RÉCURRENCE | ABS |

**Représentation** : `[AGENT:chat][MOUVEMENT][DESTRUCTION][CHOSE:souris][RÉCURRENCE]`

---

## Voir aussi

- [Résultats de couverture](resultats-couverture.md) — métriques de validation sur corpus
- [Universaux sémantiques](universaux-semantique.md) — protocole de validation
- [Expériences Dhātu v0.1](experiences-dhatu-typologie-v0-1.md) — corpus typologique
- [Inventaire Dhātu v0.1](inventaire-dhatu-v0-1.md) — format YAML
- [Cadre Dhātu](../dhatu-framework.md) — vue d'ensemble
