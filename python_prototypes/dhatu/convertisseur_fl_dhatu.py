#!/usr/bin/env python3
"""
🔄 CONVERTISSEUR BIDIRECTIONNEL FL ↔ DHĀTU
Outil de conversion entre Fonctions Lexicales Mel'čuk et combinaisons dhātu
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Tuple, Optional

class ConvertisseurFLDhatu:
    def __init__(self):
        self.dhatu_universaux = {
            'TRANS': "Transformation, changement d'état",
            'EVAL': "Évaluation, jugement, appréciation", 
            'LOCATE': "Localisation, positionnement spatial/temporel",
            'FEEL': "Émotion, ressenti, identité personnelle",
            'ACT': "Action, mouvement, dynamisme",
            'QUAL': "Qualité, propriété, caractéristique",
            'REL': "Relation, connexion, lien",
            'KNOW': "Connaissance, information, savoir",
            'EXIST': "Existence, être, présence"
        }
        
        # Extensions proposées après analyse des gaps
        self.dhatu_etendus = {
            'QUANT': "Quantité, nombre, mesure",
            'TEMP': "Temporalité, durée, fréquence", 
            'MODAL': "Modalité, possibilité, nécessité",
            'ASPECT': "Aspect, perspective, point de vue",
            'INTENSE': "Intensité, degré, force"
        }
        
        # Mapping bidirectionnel FL ↔ Dhātu
        self.mapping_fl_vers_dhatu = {
            # Fonctions d'intensité
            "Magn": ["EVAL", "TRANS"],
            "Anti-Magn": ["EVAL", "TRANS", "!INTENSE"],  # Négation d'intensité
            "Ver": ["EVAL", "EXIST"],
            "Bon": ["EVAL", "QUAL"],
            "AntiBon": ["EVAL", "QUAL", "!QUAL"],
            
            # Fonctions d'action
            "Oper1": ["ACT", "REL"],
            "Oper2": ["FEEL", "TRANS"], 
            "Oper3": ["ACT", "MODAL"],  # Action modale
            "Func0": ["EXIST", "LOCATE"],
            "Func1": ["EXIST", "QUAL"],
            "Func2": ["EXIST", "REL"],
            
            # Fonctions de réalisation
            "Real1": ["ACT", "TRANS"],
            "Real2": ["ACT", "KNOW"],
            "Real3": ["ACT", "MODAL"],
            "Fact0": ["ACT", "EXIST"],
            "Fact1": ["ACT", "EXIST", "REL"],
            "Fact2": ["ACT", "EXIST", "QUAL"],
            
            # Fonctions causatives et liquidatives
            "Caus": ["ACT", "TRANS"],
            "Liqu": ["TRANS", "EXIST", "!EXIST"],
            "Perm": ["MODAL", "EXIST"],
            
            # Fonctions aspectuelles
            "Incep": ["TRANS", "LOCATE", "TEMP"],
            "Cont": ["TRANS", "LOCATE", "TEMP"],
            "Fin": ["TRANS", "EXIST", "TEMP"],
            "Culm": ["TRANS", "EVAL", "TEMP"],
            "Prox": ["LOCATE", "TEMP"],
            
            # Fonctions de degré
            "Plus": ["EVAL", "QUANT"],
            "Minus": ["EVAL", "QUANT", "!QUANT"],
            "Equ": ["EVAL", "REL"],
            "Excess": ["EVAL", "QUANT", "INTENSE"],
            
            # Fonctions distributives
            "Centr": ["LOCATE", "ASPECT"],
            "Distr": ["QUANT", "LOCATE"],
            "Adv": ["MODAL", "ASPECT"]
        }
        
        # Mapping inverse (généré automatiquement)
        self.mapping_dhatu_vers_fl = {}
        self._generer_mapping_inverse()
        
        # Règles de composition dhātu
        self.regles_composition = {
            ("EVAL", "TRANS"): ["Magn", "Anti-Magn"],
            ("ACT", "REL"): ["Oper1"],
            ("ACT", "TRANS"): ["Real1", "Caus"],
            ("EXIST", "LOCATE"): ["Func0"],
            ("TRANS", "EXIST"): ["Liqu", "Fin"],
            ("EVAL", "QUAL"): ["Bon", "AntiBon"]
        }
        
    def _generer_mapping_inverse(self):
        """Générer le mapping inverse dhātu → fonctions lexicales"""
        for fl, dhatus in self.mapping_fl_vers_dhatu.items():
            # Nettoyer les dhātu (enlever les négations)
            dhatus_clean = [d.replace("!", "") for d in dhatus if not d.startswith("!")]
            dhatus_tuple = tuple(sorted(dhatus_clean))
            
            if dhatus_tuple not in self.mapping_dhatu_vers_fl:
                self.mapping_dhatu_vers_fl[dhatus_tuple] = []
            self.mapping_dhatu_vers_fl[dhatus_tuple].append(fl)
    
    def fl_vers_dhatu(self, fonction_lexicale: str) -> Dict:
        """Convertir une fonction lexicale vers dhātu"""
        if fonction_lexicale not in self.mapping_fl_vers_dhatu:
            return {
                "succes": False,
                "erreur": f"Fonction lexicale '{fonction_lexicale}' non reconnue",
                "suggestions": self._suggerer_fl_similaires(fonction_lexicale)
            }
        
        dhatus = self.mapping_fl_vers_dhatu[fonction_lexicale]
        dhatus_positifs = [d for d in dhatus if not d.startswith("!")]
        dhatus_negatifs = [d.replace("!", "") for d in dhatus if d.startswith("!")]
        
        return {
            "succes": True,
            "fonction_lexicale": fonction_lexicale,
            "dhatu_primaires": dhatus_positifs,
            "dhatu_negatifs": dhatus_negatifs,
            "interpretation": self._interpreter_combinaison_dhatu(dhatus_positifs),
            "exemples": self._generer_exemples_fl(fonction_lexicale),
            "confiance": self._calculer_confiance_mapping(fonction_lexicale)
        }
    
    def dhatu_vers_fl(self, dhatus: List[str]) -> Dict:
        """Convertir une combinaison de dhātu vers fonctions lexicales"""
        dhatus_tuple = tuple(sorted(dhatus))
        
        if dhatus_tuple not in self.mapping_dhatu_vers_fl:
            return {
                "succes": False,
                "erreur": f"Combinaison dhātu {dhatus} non mappée",
                "dhatus_entree": dhatus,
                "fonctions_approximatives": self._trouver_fl_approximatives(dhatus),
                "nouvelle_fonction_proposee": self._proposer_nouvelle_fonction(dhatus)
            }
        
        fonctions_possibles = self.mapping_dhatu_vers_fl[dhatus_tuple]
        
        return {
            "succes": True,
            "dhatus_entree": dhatus,
            "fonctions_lexicales": fonctions_possibles,
            "fonction_principale": fonctions_possibles[0] if fonctions_possibles else None,
            "interpretation": self._interpreter_combinaison_dhatu(dhatus),
            "exemples": {fl: self._generer_exemples_fl(fl) for fl in fonctions_possibles},
            "ambiguites": len(fonctions_possibles) > 1
        }
    
    def analyser_mot_vers_dhatu(self, mot: str, contexte: str = "") -> Dict:
        """Analyser un mot en contexte et proposer décomposition dhātu"""
        
        # Base de décompositions sémantiques (à étendre)
        decompositions_connues = {
            "torrentielle": ["EVAL", "TRANS", "LOCATE"],  # Magn(pluie)
            "prendre": ["ACT", "REL"],                    # Oper1(décision)
            "tenir": ["ACT", "TRANS"],                    # Real1(promesse)
            "suivre": ["ACT", "KNOW"],                    # Real2(conseil)
            "commencer": ["TRANS", "LOCATE"],             # Incep
            "terminer": ["TRANS", "EXIST"],               # Fin
            "provoquer": ["ACT", "TRANS"],                # Caus
            "dissiper": ["TRANS", "EXIST"],               # Liqu
            
            # Nouveaux exemples
            "intensifier": ["EVAL", "TRANS", "INTENSE"],
            "diminuer": ["EVAL", "TRANS", "!INTENSE"],
            "localiser": ["LOCATE", "KNOW"],
            "ressentir": ["FEEL", "EXIST"],
            "qualifier": ["EVAL", "QUAL"],
            "relier": ["REL", "ACT"],
            "transformer": ["TRANS", "ACT"],
            "exister": ["EXIST"],
            "connaître": ["KNOW", "EXIST"]
        }
        
        mot_lower = mot.lower()
        
        if mot_lower in decompositions_connues:
            dhatus = decompositions_connues[mot_lower]
            fl_possibles = self.dhatu_vers_fl(dhatus)
            
            return {
                "succes": True,
                "mot": mot,
                "contexte": contexte,
                "dhatus": dhatus,
                "fonctions_lexicales": fl_possibles,
                "confiance": 0.8,
                "source": "décomposition_connue"
            }
        else:
            # Analyse morphologique et sémantique approximative
            dhatus_proposes = self._analyser_morphologie(mot)
            
            return {
                "succes": False,
                "mot": mot,
                "contexte": contexte,
                "dhatus_proposes": dhatus_proposes,
                "confiance": 0.3,
                "source": "analyse_morphologique",
                "recommandation": f"Analyse manuelle nécessaire pour '{mot}'"
            }
    
    def _analyser_morphologie(self, mot: str) -> List[str]:
        """Analyse morphologique basique pour proposer dhātu"""
        dhatus = []
        mot_lower = mot.lower()
        
        # Règles morphologiques simples
        if any(suffixe in mot_lower for suffixe in ["-er", "-ir", "-re"]):
            dhatus.append("ACT")
        if any(prefixe in mot_lower for prefixe in ["trans-", "re-", "dé-"]):
            dhatus.append("TRANS")
        if any(radical in mot_lower for radical in ["sent", "émo", "feel"]):
            dhatus.append("FEEL")
        if any(radical in mot_lower for radical in ["sav", "conn", "know"]):
            dhatus.append("KNOW")
        if any(radical in mot_lower for radical in ["qual", "bon", "mauv"]):
            dhatus.append("QUAL")
        if any(radical in mot_lower for radical in ["loc", "place", "où"]):
            dhatus.append("LOCATE")
        if any(radical in mot_lower for radical in ["exist", "être", "est"]):
            dhatus.append("EXIST")
        if any(radical in mot_lower for radical in ["rel", "lien", "avec"]):
            dhatus.append("REL")
        if any(radical in mot_lower for radical in ["éval", "jug", "mes"]):
            dhatus.append("EVAL")
            
        return dhatus if dhatus else ["UNKNOWN"]
    
    def _interpreter_combinaison_dhatu(self, dhatus: List[str]) -> str:
        """Interpréter une combinaison de dhātu en langage naturel"""
        if not dhatus:
            return "Combinaison vide"
        
        interpretations = {
            ("EVAL", "TRANS"): "Évaluation impliquant changement d'intensité",
            ("ACT", "REL"): "Action établissant une relation",
            ("ACT", "TRANS"): "Action transformatrice",
            ("ACT", "KNOW"): "Action basée sur connaissance",
            ("EXIST", "LOCATE"): "Existence située dans espace/temps",
            ("TRANS", "EXIST"): "Changement d'état d'existence",
            ("EVAL", "QUAL"): "Évaluation de qualité",
            ("FEEL", "TRANS"): "Émotion/ressenti transformateur"
        }
        
        dhatus_tuple = tuple(sorted(dhatus))
        if dhatus_tuple in interpretations:
            return interpretations[dhatus_tuple]
        
        # Interprétation générique
        descriptions = []
        for dhatu in dhatus:
            if dhatu in self.dhatu_universaux:
                descriptions.append(self.dhatu_universaux[dhatu].split(",")[0])
            elif dhatu in self.dhatu_etendus:
                descriptions.append(self.dhatu_etendus[dhatu].split(",")[0])
        
        return " + ".join(descriptions)
    
    def _generer_exemples_fl(self, fonction_lexicale: str) -> List[str]:
        """Générer des exemples pour une fonction lexicale"""
        exemples_db = {
            "Magn": ["pluie torrentielle", "erreur monumentale", "silence absolu"],
            "Oper1": ["prendre une décision", "faire attention", "mener une guerre"],
            "Oper2": ["essuyer une critique", "subir un échec", "recevoir une punition"],
            "Real1": ["tenir une promesse", "réaliser un projet", "atteindre un objectif"],
            "Real2": ["suivre un conseil", "appliquer une méthode", "respecter une règle"],
            "Incep": ["commencer le travail", "débuter une carrière", "entamer des négociations"],
            "Cont": ["poursuivre l'effort", "maintenir la cadence", "continuer la lutte"],
            "Fin": ["terminer l'étude", "achever le projet", "clore la discussion"],
            "Caus": ["provoquer un changement", "déclencher une réaction", "susciter l'intérêt"],
            "Liqu": ["dissiper le doute", "lever l'ambiguïté", "détendre l'atmosphère"]
        }
        
        return exemples_db.get(fonction_lexicale, [f"Exemples pour {fonction_lexicale} à définir"])
    
    def _suggerer_fl_similaires(self, fonction: str) -> List[str]:
        """Suggérer des fonctions lexicales similaires"""
        toutes_fl = list(self.mapping_fl_vers_dhatu.keys())
        suggestions = []
        
        for fl in toutes_fl:
            if any(char in fl.lower() for char in fonction.lower()):
                suggestions.append(fl)
        
        return suggestions[:5]
    
    def _trouver_fl_approximatives(self, dhatus: List[str]) -> List[str]:
        """Trouver des FL approximatives pour une combinaison dhātu"""
        approximatives = []
        
        for dhatus_mapped, fls in self.mapping_dhatu_vers_fl.items():
            intersection = set(dhatus) & set(dhatus_mapped)
            if len(intersection) >= min(len(dhatus), len(dhatus_mapped)) // 2:
                approximatives.extend(fls)
        
        return list(set(approximatives))[:3]
    
    def _proposer_nouvelle_fonction(self, dhatus: List[str]) -> str:
        """Proposer un nom pour une nouvelle fonction lexicale"""
        if "EVAL" in dhatus and "INTENSE" in dhatus:
            return "Intens"
        elif "ACT" in dhatus and "MODAL" in dhatus:
            return "Modal"
        elif "TEMP" in dhatus and "TRANS" in dhatus:
            return "Tempor"
        elif "QUANT" in dhatus:
            return "Quant"
        else:
            return f"Func_{'+'.join(dhatus[:2])}"
    
    def _calculer_confiance_mapping(self, fonction_lexicale: str) -> float:
        """Calculer la confiance dans le mapping"""
        # Basé sur la fréquence d'occurrence dans la littérature
        confiances = {
            "Magn": 0.95, "Oper1": 0.90, "Oper2": 0.85, "Real1": 0.88,
            "Real2": 0.82, "Incep": 0.75, "Cont": 0.75, "Fin": 0.78,
            "Caus": 0.80, "Liqu": 0.70, "Ver": 0.65, "Bon": 0.85
        }
        return confiances.get(fonction_lexicale, 0.50)
    
    def tester_conversion_bidirectionnelle(self):
        """Tester la conversion bidirectionnelle"""
        print("🔄 TEST CONVERSION BIDIRECTIONNELLE FL ↔ DHĀTU")
        print("="*60)
        
        # Test FL → Dhātu
        exemples_fl = ["Magn", "Oper1", "Real1", "Incep", "Caus"]
        
        print("\n📊 FL → DHĀTU:")
        for fl in exemples_fl:
            resultat = self.fl_vers_dhatu(fl)
            if resultat["succes"]:
                print(f"✅ {fl} → {resultat['dhatu_primaires']}")
                print(f"   Interprétation: {resultat['interpretation']}")
            else:
                print(f"❌ {fl} → {resultat['erreur']}")
        
        # Test Dhātu → FL
        exemples_dhatu = [
            ["EVAL", "TRANS"],
            ["ACT", "REL"], 
            ["ACT", "TRANS"],
            ["EXIST", "LOCATE"]
        ]
        
        print("\n📊 DHĀTU → FL:")
        for dhatus in exemples_dhatu:
            resultat = self.dhatu_vers_fl(dhatus)
            if resultat["succes"]:
                print(f"✅ {dhatus} → {resultat['fonctions_lexicales']}")
                if resultat["ambiguites"]:
                    print(f"   ⚠️ Ambiguïté détectée")
            else:
                print(f"❌ {dhatus} → {resultat['erreur']}")
                if "nouvelle_fonction_proposee" in resultat:
                    print(f"   💡 Fonction proposée: {resultat['nouvelle_fonction_proposee']}")
        
        # Test analyse de mots
        exemples_mots = ["intensifier", "relier", "transformer", "inexistant"]
        
        print("\n📊 ANALYSE MOTS → DHĀTU:")
        for mot in exemples_mots:
            resultat = self.analyser_mot_vers_dhatu(mot)
            if resultat["succes"]:
                print(f"✅ '{mot}' → {resultat['dhatus']}")
            else:
                print(f"❌ '{mot}' → {resultat['dhatus_proposes']}")
                print(f"   {resultat['recommandation']}")

def main():
    convertisseur = ConvertisseurFLDhatu()
    convertisseur.tester_conversion_bidirectionnelle()
    
    # Interface interactive basique
    print("\n🎯 CONVERTISSEUR INTERACTIF")
    print("Tapez 'FL:nom' pour convertir FL→dhātu")
    print("Tapez 'DHATU:d1,d2' pour convertir dhātu→FL") 
    print("Tapez 'MOT:mot' pour analyser un mot")
    print("Tapez 'quit' pour quitter")
    
    while True:
        try:
            entree = input("\n> ").strip()
            if entree.lower() == "quit":
                break
            elif entree.startswith("FL:"):
                fl = entree[3:]
                resultat = convertisseur.fl_vers_dhatu(fl)
                print(json.dumps(resultat, ensure_ascii=False, indent=2))
            elif entree.startswith("DHATU:"):
                dhatus = [d.strip() for d in entree[6:].split(",")]
                resultat = convertisseur.dhatu_vers_fl(dhatus)
                print(json.dumps(resultat, ensure_ascii=False, indent=2))
            elif entree.startswith("MOT:"):
                mot = entree[4:]
                resultat = convertisseur.analyser_mot_vers_dhatu(mot)
                print(json.dumps(resultat, ensure_ascii=False, indent=2))
            else:
                print("Format non reconnu. Utilisez FL:, DHATU: ou MOT:")
        except KeyboardInterrupt:
            print("\nAu revoir!")
            break

if __name__ == "__main__":
    main()