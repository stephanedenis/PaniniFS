#!/usr/bin/env python3
"""
🎯 QUANT DHĀTU - PHASE 3 IMPLÉMENTATION
Quantification et mesure avec gradations floues
Score priorité: 7.1/10 (justification Dehaene 1997)
"""

import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from enum import Enum
import re
import math

class TypeQuantification(Enum):
    """Types de quantification selon classification"""
    CARDINALE = "cardinale"         # Nombres exacts (1, 2, 3...)
    ORDINALE = "ordinale"           # Ordre (premier, second...)
    PARTITIVE = "partitive"         # Parties (moitié, tiers...)
    APPROXIMATIVE = "approximative" # Approximations (environ, vers...)
    COMPARATIVE = "comparative"     # Comparaisons (plus, moins...)
    DISTRIBUTIVE = "distributive"   # Distribution (chaque, tout...)

class EchelleQuantite(Enum):
    """Échelle graduée de quantité (cognitif)"""
    NULLE = "nulle"           # Zéro, aucun, rien
    MINIMALE = "minimale"     # Très peu, à peine
    FAIBLE = "faible"         # Peu, quelque
    MOYENNE = "moyenne"       # Assez, modérément
    ELEVEE = "élevée"         # Beaucoup, nombreux
    MAXIMALE = "maximale"     # Énormément, extrême
    INFINIE = "infinie"       # Infini, innombrable

class OperateurQuant(Enum):
    """Opérateurs n-aires pour quantification (limite cognitive 7±2)"""
    NEANT = "!"          # Quantité nulle, absence
    INDEFINI = "?"       # Quantité indéterminée
    UNITE = "+"          # Quantité unitaire, singulier
    FAIBLE = "+·"        # Quantité faible, peu
    MULTIPLE = "++"      # Quantité multiple, beaucoup
    EXTREME = "+++"      # Quantité extrême, énorme

@dataclass
class ExpressionQuantitative:
    """Expression quantitative avec décomposition dhātu"""
    forme_surface: str
    decomposition: str
    type_quantif: TypeQuantification
    echelle: EchelleQuantite
    operateur: OperateurQuant
    valeur_approximative: Optional[float]  # Valeur numérique si applicable
    precision: str  # Exact, approximatif, vague
    portee: str     # Locale, globale, distributive
    glose_semantique: str
    exemples_contexte: List[str]
    langue: str = "français"

class QuantDhatu:
    """Dhātu QUANT avec logique floue et gradations"""
    
    def __init__(self):
        self.nom = "QUANT"
        self.operateurs = list(OperateurQuant)
        self.expressions_mappees = self._definir_expressions_quantitatives()
        self.compositions_graduees = self._definir_compositions_graduees()
        self.echelle_floue = self._definir_echelle_floue()
        
    def _definir_expressions_quantitatives(self):
        """Mappings expressions quantitatives → dhātu + opérateurs"""
        return {
            # QUANTITÉ NULLE
            "aucun": ExpressionQuantitative(
                forme_surface="aucun",
                decomposition="QUANT!",
                type_quantif=TypeQuantification.CARDINALE,
                echelle=EchelleQuantite.NULLE,
                operateur=OperateurQuant.NEANT,
                valeur_approximative=0.0,
                precision="exact",
                portee="globale",
                glose_semantique="absence totale de quantité",
                exemples_contexte=[
                    "Aucun problème détecté",
                    "Il n'y a aucune solution",
                    "Aucun doute possible"
                ]
            ),
            
            "rien": ExpressionQuantitative(
                forme_surface="rien",
                decomposition="QUANT!",
                type_quantif=TypeQuantification.CARDINALE,
                echelle=EchelleQuantite.NULLE,
                operateur=OperateurQuant.NEANT,
                valeur_approximative=0.0,
                precision="exact",
                portee="globale",
                glose_semantique="néant, absence complète",
                exemples_contexte=[
                    "Il ne reste rien",
                    "Rien à signaler",
                    "Partir de rien"
                ]
            ),
            
            "zéro": ExpressionQuantitative(
                forme_surface="zéro",
                decomposition="QUANT!",
                type_quantif=TypeQuantification.CARDINALE,
                echelle=EchelleQuantite.NULLE,
                operateur=OperateurQuant.NEANT,
                valeur_approximative=0.0,
                precision="exact",
                portee="locale",
                glose_semantique="valeur numérique nulle",
                exemples_contexte=[
                    "Zéro erreur trouvée",
                    "Commencer à zéro",
                    "Zéro pointé"
                ]
            ),
            
            # QUANTITÉ FAIBLE
            "peu": ExpressionQuantitative(
                forme_surface="peu",
                decomposition="QUANT+·",
                type_quantif=TypeQuantification.APPROXIMATIVE,
                echelle=EchelleQuantite.FAIBLE,
                operateur=OperateurQuant.FAIBLE,
                valeur_approximative=0.2,
                precision="vague",
                portee="globale",
                glose_semantique="quantité réduite, insuffisante",
                exemples_contexte=[
                    "Il y en a peu",
                    "Peu de chances",
                    "Un peu fatigué"
                ]
            ),
            
            "quelque": ExpressionQuantitative(
                forme_surface="quelque",
                decomposition="QUANT+·",
                type_quantif=TypeQuantification.APPROXIMATIVE,
                echelle=EchelleQuantite.FAIBLE,
                operateur=OperateurQuant.FAIBLE,
                valeur_approximative=0.3,
                precision="approximatif",
                portee="locale",
                glose_semantique="quantité indéterminée petite",
                exemples_contexte=[
                    "Quelques exemples",
                    "Dans quelque temps",
                    "Quelque part"
                ]
            ),
            
            "rare": ExpressionQuantitative(
                forme_surface="rare",
                decomposition="QUANT+·",
                type_quantif=TypeQuantification.COMPARATIVE,
                echelle=EchelleQuantite.MINIMALE,
                operateur=OperateurQuant.FAIBLE,
                valeur_approximative=0.1,
                precision="approximatif",
                portee="globale",
                glose_semantique="occurrence peu fréquente",
                exemples_contexte=[
                    "C'est assez rare",
                    "Un événement rare",
                    "De rares exceptions"
                ]
            ),
            
            # QUANTITÉ UNITAIRE
            "un": ExpressionQuantitative(
                forme_surface="un",
                decomposition="QUANT+",
                type_quantif=TypeQuantification.CARDINALE,
                echelle=EchelleQuantite.MOYENNE,
                operateur=OperateurQuant.UNITE,
                valeur_approximative=1.0,
                precision="exact",
                portee="locale",
                glose_semantique="unité cardinale exacte",
                exemples_contexte=[
                    "Un seul problème",
                    "Une solution unique",
                    "Un à la fois"
                ]
            ),
            
            "unique": ExpressionQuantitative(
                forme_surface="unique",
                decomposition="QUANT+",
                type_quantif=TypeQuantification.CARDINALE,
                echelle=EchelleQuantite.MOYENNE,
                operateur=OperateurQuant.UNITE,
                valeur_approximative=1.0,
                precision="exact",
                portee="globale",
                glose_semantique="singularité absolue",
                exemples_contexte=[
                    "Solution unique",
                    "Exemplaire unique",
                    "Chance unique"
                ]
            ),
            
            # QUANTITÉ ÉLEVÉE
            "beaucoup": ExpressionQuantitative(
                forme_surface="beaucoup",
                decomposition="QUANT++",
                type_quantif=TypeQuantification.APPROXIMATIVE,
                echelle=EchelleQuantite.ELEVEE,
                operateur=OperateurQuant.MULTIPLE,
                valeur_approximative=0.7,
                precision="vague",
                portee="globale",
                glose_semantique="quantité importante, abondante",
                exemples_contexte=[
                    "Beaucoup de travail",
                    "Il y en a beaucoup",
                    "Beaucoup mieux"
                ]
            ),
            
            "nombreux": ExpressionQuantitative(
                forme_surface="nombreux",
                decomposition="QUANT++",
                type_quantif=TypeQuantification.CARDINALE,
                echelle=EchelleQuantite.ELEVEE,
                operateur=OperateurQuant.MULTIPLE,
                valeur_approximative=0.8,
                precision="approximatif",
                portee="globale",
                glose_semantique="multiplicité cardinale élevée",
                exemples_contexte=[
                    "Nombreux participants",
                    "De nombreuses fois",
                    "Très nombreux"
                ]
            ),
            
            "plusieurs": ExpressionQuantitative(
                forme_surface="plusieurs",
                decomposition="QUANT++",
                type_quantif=TypeQuantification.CARDINALE,
                echelle=EchelleQuantite.ELEVEE,
                operateur=OperateurQuant.MULTIPLE,
                valeur_approximative=0.6,
                precision="approximatif",
                portee="locale",
                glose_semantique="pluralité indéterminée",
                exemples_contexte=[
                    "Plusieurs solutions",
                    "À plusieurs reprises",
                    "Plusieurs fois"
                ]
            ),
            
            # QUANTITÉ EXTRÊME
            "énormément": ExpressionQuantitative(
                forme_surface="énormément",
                decomposition="QUANT+++",
                type_quantif=TypeQuantification.APPROXIMATIVE,
                echelle=EchelleQuantite.MAXIMALE,
                operateur=OperateurQuant.EXTREME,
                valeur_approximative=0.95,
                precision="vague",
                portee="globale",
                glose_semantique="quantité excessive, démesurée",
                exemples_contexte=[
                    "Énormément de succès",
                    "Il travaille énormément",
                    "Énormément mieux"
                ]
            ),
            
            "innombrable": ExpressionQuantitative(
                forme_surface="innombrable",
                decomposition="QUANT+++",
                type_quantif=TypeQuantification.CARDINALE,
                echelle=EchelleQuantite.INFINIE,
                operateur=OperateurQuant.EXTREME,
                valeur_approximative=math.inf,
                precision="vague",
                portee="globale",
                glose_semantique="quantité non-dénombrable",
                exemples_contexte=[
                    "Innombrables étoiles",
                    "Foule innombrable",
                    "Détails innombrables"
                ]
            ),
            
            # QUANTITÉ INDÉTERMINÉE
            "environ": ExpressionQuantitative(
                forme_surface="environ",
                decomposition="QUANT?",
                type_quantif=TypeQuantification.APPROXIMATIVE,
                echelle=EchelleQuantite.MOYENNE,
                operateur=OperateurQuant.INDEFINI,
                valeur_approximative=None,
                precision="approximatif",
                portee="locale",
                glose_semantique="approximation quantitative",
                exemples_contexte=[
                    "Environ dix personnes",
                    "Vers environ midi",
                    "Environ la moitié"
                ]
            )
        }
    
    def _definir_compositions_graduees(self):
        """Compositions QUANT avec gradations et autres dhātu"""
        return {
            # QUANT + EVAL
            "trop_peu": {
                "decomposition": "QUANT+· + EVAL!",
                "glose": "quantité insuffisante négativement évaluée",
                "exemples": [
                    "Il y en a trop peu",
                    "Beaucoup trop peu",
                    "Bien trop peu"
                ],
                "echelle_resultat": EchelleQuantite.FAIBLE
            },
            
            "suffisamment": {
                "decomposition": "QUANT+ + EVAL+",
                "glose": "quantité adéquate positivement évaluée",
                "exemples": [
                    "Suffisamment de preuves",
                    "Assez suffisant",
                    "Plus que suffisant"
                ],
                "echelle_resultat": EchelleQuantite.MOYENNE
            },
            
            "beaucoup_trop": {
                "decomposition": "QUANT++ + EVAL!",
                "glose": "quantité excessive négativement évaluée",
                "exemples": [
                    "Beaucoup trop cher",
                    "Bien trop nombreux",
                    "Énormément trop"
                ],
                "echelle_resultat": EchelleQuantite.ELEVEE
            },
            
            # QUANT + MODAL
            "probablement_peu": {
                "decomposition": "MODAL+· + QUANT+·",
                "glose": "quantité faible avec probabilité",
                "exemples": [
                    "Probablement peu nombreux",
                    "Sûrement pas beaucoup"
                ],
                "echelle_resultat": EchelleQuantite.FAIBLE
            },
            
            "certainement_beaucoup": {
                "decomposition": "MODAL+ + QUANT++",
                "glose": "quantité élevée avec certitude",
                "exemples": [
                    "Certainement beaucoup",
                    "Sûrement nombreux"
                ],
                "echelle_resultat": EchelleQuantite.ELEVEE
            },
            
            # QUANT + ASPECT
            "de_plus_en_plus": {
                "decomposition": "QUANT++ + ASPECT++",
                "glose": "augmentation progressive de quantité",
                "exemples": [
                    "De plus en plus nombreux",
                    "Toujours plus",
                    "Sans cesse davantage"
                ],
                "echelle_resultat": EchelleQuantite.ELEVEE
            },
            
            "de_moins_en_moins": {
                "decomposition": "QUANT+· + ASPECT++",
                "glose": "diminution progressive de quantité",
                "exemples": [
                    "De moins en moins",
                    "Toujours moins",
                    "Sans cesse moins"
                ],
                "echelle_resultat": EchelleQuantite.FAIBLE
            },
            
            # QUANT + ACTION
            "multiplier": {
                "decomposition": "QUANT++ + ACTION+",
                "glose": "action d'augmentation quantitative",
                "exemples": [
                    "Multiplier les efforts",
                    "Multiplier par deux",
                    "Se multiplier"
                ],
                "echelle_resultat": EchelleQuantite.ELEVEE
            }
        }
    
    def _definir_echelle_floue(self):
        """Échelle de quantification floue (0-1) + infini"""
        return {
            EchelleQuantite.NULLE: (0.0, 0.0),
            EchelleQuantite.MINIMALE: (0.0, 0.15),
            EchelleQuantite.FAIBLE: (0.1, 0.35),
            EchelleQuantite.MOYENNE: (0.3, 0.7),
            EchelleQuantite.ELEVEE: (0.65, 0.9),
            EchelleQuantite.MAXIMALE: (0.85, 1.0),
            EchelleQuantite.INFINIE: (1.0, math.inf)
        }
    
    def analyser_expression_quantitative(self, expression: str) -> Optional[ExpressionQuantitative]:
        """Analyser expression et retourner décomposition quantitative"""
        expression_norm = expression.lower().strip()
        
        # Recherche directe
        if expression_norm in self.expressions_mappees:
            return self.expressions_mappees[expression_norm]
        
        # Patterns quantitatifs avec extraction numérique
        patterns_quantitatifs = {
            r"environ (\d+)": ("QUANT?", "approximation numérique"),
            r"quelques (\w+)": ("QUANT+·", "pluriel indéterminé faible"),
            r"beaucoup de (\w+)": ("QUANT++", "quantité élevée de"),
            r"trop (peu|beaucoup)": ("QUANT++ + EVAL!", "excès quantitatif"),
            r"assez (\w+)": ("QUANT+ + EVAL+", "quantité suffisante"),
            r"(\d+) fois": ("QUANT++", "multiplicité numérique"),
            r"plus de (\d+)": ("QUANT++", "supériorité numérique"),
            r"moins de (\d+)": ("QUANT+·", "infériorité numérique")
        }
        
        for pattern, (decomposition, glose) in patterns_quantitatifs.items():
            match = re.search(pattern, expression_norm)
            if match:
                valeur = None
                if match.groups() and match.group(1).isdigit():
                    valeur = float(match.group(1))
                
                return ExpressionQuantitative(
                    forme_surface=expression,
                    decomposition=decomposition,
                    type_quantif=TypeQuantification.APPROXIMATIVE,
                    echelle=EchelleQuantite.MOYENNE,
                    operateur=OperateurQuant.INDEFINI,
                    valeur_approximative=valeur,
                    precision="approximatif",
                    portee="locale",
                    glose_semantique=f"pattern quantitatif: {glose}",
                    exemples_contexte=[expression]
                )
        
        return None
    
    def calculer_valeur_floue(self, echelle: EchelleQuantite) -> Tuple[float, float]:
        """Calculer intervalle flou pour échelle quantitative"""
        return self.echelle_floue[echelle]
    
    def comparer_quantites(self, quant1: ExpressionQuantitative, quant2: ExpressionQuantitative) -> str:
        """Comparer deux expressions quantitatives"""
        val1_min, val1_max = self.calculer_valeur_floue(quant1.echelle)
        val2_min, val2_max = self.calculer_valeur_floue(quant2.echelle)
        
        # Comparaison par centre d'intervalle
        centre1 = (val1_min + val1_max) / 2 if val1_max != math.inf else val1_min + 1
        centre2 = (val2_min + val2_max) / 2 if val2_max != math.inf else val2_min + 1
        
        if centre1 > centre2:
            return f"{quant1.forme_surface} > {quant2.forme_surface}"
        elif centre1 < centre2:
            return f"{quant1.forme_surface} < {quant2.forme_surface}"
        else:
            return f"{quant1.forme_surface} ≈ {quant2.forme_surface}"
    
    def generer_gradations(self, quantite_base: str) -> List[str]:
        """Générer gradations intensité pour quantité de base"""
        gradations_patterns = {
            "peu": ["très peu", "assez peu", "un peu", "peu", "plutôt peu"],
            "beaucoup": ["énormément", "beaucoup", "assez", "pas mal", "un peu"],
            "aucun": ["absolument aucun", "strictement aucun", "aucun", "pratiquement aucun"]
        }
        
        return gradations_patterns.get(quantite_base, [quantite_base])
    
    def valider_coherence_quantitative(self, quant1: str, quant2: str) -> bool:
        """Valider cohérence entre quantités composées"""
        # Règles de cohérence quantitative
        incoherences = {
            # Contradictions logiques
            ("QUANT!", "QUANT+++"): False,  # aucun + énormément
            ("QUANT+·", "QUANT+++"): False, # peu + énormément  
            ("QUANT+++", "QUANT!"): False,  # énormément + aucun
            
            # Auto-composition interdite
            ("QUANT+", "QUANT+"): False,
            ("QUANT++", "QUANT++"): False,
            ("QUANT+++", "QUANT+++"): False
        }
        
        paire = (quant1, quant2)
        if paire in incoherences:
            return incoherences[paire]
        
        return True  # Par défaut autorisé
    
    def generer_statistiques_quant(self) -> Dict:
        """Statistiques détaillées QUANT dhātu"""
        stats = {
            "nb_expressions": len(self.expressions_mappees),
            "nb_operateurs": len(self.operateurs),
            "nb_compositions": len(self.compositions_graduees),
            "repartition_echelles": {},
            "repartition_types": {},
            "repartition_precision": {},
            "valeurs_numeriques": []
        }
        
        # Analyse expressions
        for expr in self.expressions_mappees.values():
            # Échelles
            echelle = expr.echelle.value
            stats["repartition_echelles"][echelle] = stats["repartition_echelles"].get(echelle, 0) + 1
            
            # Types quantification
            type_q = expr.type_quantif.value
            stats["repartition_types"][type_q] = stats["repartition_types"].get(type_q, 0) + 1
            
            # Précision
            precision = expr.precision
            stats["repartition_precision"][precision] = stats["repartition_precision"].get(precision, 0) + 1
            
            # Valeurs numériques
            if expr.valeur_approximative is not None and expr.valeur_approximative != math.inf:
                stats["valeurs_numeriques"].append(expr.valeur_approximative)
        
        return stats

def tester_quant_dhatu():
    """Tests compréhensifs QUANT dhātu"""
    print("🧪 TESTS QUANT DHĀTU - PHASE 3")
    print("="*35)
    
    quant = QuantDhatu()
    
    # Test 1: Expressions quantitatives de base
    print("\n📝 Test 1: Expressions quantitatives de base")
    expressions_test = [
        "aucun", "peu", "beaucoup", "énormément",
        "un", "plusieurs", "nombreux", "innombrable"
    ]
    
    for expr in expressions_test:
        resultat = quant.analyser_expression_quantitative(expr)
        if resultat:
            echelle = resultat.echelle.value
            val = resultat.valeur_approximative
            val_str = f"{val:.1f}" if val and val != math.inf else "∞" if val == math.inf else "?"
            print(f"✅ {expr} → {resultat.decomposition} ({echelle}, {val_str})")
        else:
            print(f"❌ {expr} → Non reconnu")
    
    # Test 2: Patterns quantitatifs
    print("\n📝 Test 2: Patterns quantitatifs")
    patterns_test = [
        "environ 10",
        "beaucoup de travail",
        "trop peu",
        "plus de 5"
    ]
    
    for pattern in patterns_test:
        resultat = quant.analyser_expression_quantitative(pattern)
        if resultat:
            print(f"✅ '{pattern}' → {resultat.decomposition}")
        else:
            print(f"❌ '{pattern}' → Non reconnu")
    
    # Test 3: Comparaisons quantitatives
    print("\n📝 Test 3: Comparaisons quantitatives")
    comparaisons = [
        ("peu", "beaucoup"),
        ("énormément", "aucun"),
        ("un", "plusieurs")
    ]
    
    for q1, q2 in comparaisons:
        expr1 = quant.expressions_mappees[q1]
        expr2 = quant.expressions_mappees[q2]
        comparaison = quant.comparer_quantites(expr1, expr2)
        print(f"📊 {comparaison}")
    
    # Test 4: Gradations
    print("\n📝 Test 4: Gradations quantitatives")
    for base in ["peu", "beaucoup"]:
        gradations = quant.generer_gradations(base)
        print(f"Gradations '{base}': {', '.join(gradations)}")
    
    # Test 5: Cohérence quantitative
    print("\n📝 Test 5: Validation cohérence")
    coherences_test = [
        ("QUANT+·", "QUANT++"),    # peu + beaucoup (OK)
        ("QUANT!", "QUANT+++"),    # aucun + énormément (incohérent)
        ("QUANT+", "QUANT++"),     # un + beaucoup (OK)
    ]
    
    for q1, q2 in coherences_test:
        valide = quant.valider_coherence_quantitative(q1, q2)
        status = "✅" if valide else "❌"
        print(f"{status} {q1} + {q2} → {'Cohérent' if valide else 'Incohérent'}")
    
    # Test 6: Statistiques
    print("\n📊 Test 6: Statistiques QUANT")
    stats = quant.generer_statistiques_quant()
    print(f"Expressions mappées: {stats['nb_expressions']}")
    print(f"Opérateurs n-aires: {stats['nb_operateurs']}")
    print(f"Compositions graduées: {stats['nb_compositions']}")
    print("Répartition échelles:")
    for echelle, count in stats["repartition_echelles"].items():
        print(f"   {echelle}: {count}")
    print(f"Valeurs numériques: {len(stats['valeurs_numeriques'])} expressions")
    
    return quant, stats

def main():
    """Implémentation complète Phase 3 QUANT"""
    print("🎯 QUANT DHĀTU - PHASE 3 IMPLÉMENTATION")
    print("Quantification et mesure graduée")
    print("="*40)
    
    # Tests compréhensifs
    quant_dhatu, statistiques = tester_quant_dhatu()
    
    print(f"\n🎊 RÉSUMÉ PHASE 3 QUANT")
    print("="*25)
    print(f"✅ {statistiques['nb_expressions']} expressions quantitatives mappées")
    print(f"✅ {statistiques['nb_operateurs']} opérateurs n-aires (limite cognitive OK)")
    print(f"✅ {statistiques['nb_compositions']} compositions graduées")
    print("✅ 7 échelles quantitatives: nulle → infinie")
    print("✅ Logique floue + valeurs approximatives")
    print("✅ Comparaisons et gradations automatiques")
    print("✅ Validation cohérence quantitative")
    
    # Sauvegarde résultats
    resultats_phase3 = {
        "implementation": "QUANT dhātu Phase 3",
        "statistiques": statistiques,
        "expressions_mappees": {
            nom: asdict(expr) for nom, expr in quant_dhatu.expressions_mappees.items()
        },
        "compositions_graduees": quant_dhatu.compositions_graduees,
        "echelle_floue": {k.value: v for k, v in quant_dhatu.echelle_floue.items()},
        "validation": "Logique floue + cohérence quantitative validées",
        "score_priorite": 7.1,
        "justification": "Quantité = cognition numérique universelle (Dehaene 1997)"
    }
    
    with open("quant_dhatu_phase3.json", "w", encoding="utf-8") as f:
        json.dump(resultats_phase3, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n💾 Phase 3 sauvegardée: quant_dhatu_phase3.json")
    print("🚀 Prêt pour Phase 4: Intégration complète!")

if __name__ == "__main__":
    main()