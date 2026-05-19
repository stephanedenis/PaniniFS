#!/usr/bin/env python3
"""
SYSTÈME DE MARQUEURS ONOMASTIQUES - Pipeline v7.3 Enhanced

Système de balisage spécialisé pour isoler les noms propres et leurs analyses
sémantiques du flux principal de traitement linguistique.

Principe : Les noms propres sont encapsulés dans des marqueurs spéciaux
qui préservent l'analyse onomastique sans interférer avec le traitement
sémantique du reste de l'énoncé.
"""

import re
import json
import time
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

@dataclass
class MarqueurOnomastique:
    """Marqueur spécialisé pour un nom propre"""
    id_marqueur: str  # UUID unique du marqueur
    nom_original: str  # Nom propre original
    type_onomastique: str  # anthroponyme, toponyme, taxonyme
    marqueur_ouverture: str  # Balise d'ouverture
    marqueur_fermeture: str  # Balise de fermeture
    contenu_semantique_isole: Dict[str, Any]  # Analyse complète isolée
    position_debut: int  # Position dans le texte original
    position_fin: int  # Position de fin
    langue_detectee: str
    
    # Métadonnées de séparation
    niveau_isolation: str  # "complet", "partiel", "minimal"
    interference_possible: bool  # Si le marqueur peut interférer
    priorite_traitement: int  # Ordre de traitement (1=priority)

@dataclass
class TexteAvecMarqueurs:
    """Texte avec marqueurs onomastiques intégrés"""
    texte_original: str
    texte_avec_marqueurs: str
    texte_semantique_pur: str  # Sans les noms propres
    marqueurs_onomastiques: List[MarqueurOnomastique]
    mapping_positions: Dict[str, Tuple[int, int]]  # id_marqueur -> (debut, fin)
    
    # Statistiques de séparation
    nombre_noms_marques: int
    pourcentage_contenu_onomastique: float
    pourcentage_contenu_semantique: float

class GestionnaireMarqueursOnomastiques:
    """Gestionnaire des marqueurs onomastiques"""
    
    def __init__(self):
        self.version = "v7.3-Marqueurs"
        self.timestamp_init = datetime.now().isoformat()
        
        # Configuration des marqueurs
        self.config_marqueurs = {
            "anthroponyme": {
                "prefixe": "⟨👤",
                "suffixe": "👤⟩",
                "classe": "PERS",
                "couleur_debug": "\033[94m"  # Bleu
            },
            "toponyme": {
                "prefixe": "⟨🗺️",
                "suffixe": "🗺️⟩",
                "classe": "LIEU",
                "couleur_debug": "\033[92m"  # Vert
            },
            "taxonyme": {
                "prefixe": "⟨🔬",
                "suffixe": "🔬⟩",
                "classe": "TAXO",
                "couleur_debug": "\033[93m"  # Jaune
            },
            "inconnu": {
                "prefixe": "⟨❓",
                "suffixe": "❓⟩",
                "classe": "UNKN",
                "couleur_debug": "\033[91m"  # Rouge
            }
        }
        
        # Patterns de reconnaissance
        self.patterns_protection = {
            "debut_phrase": r'^[A-ZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ]',
            "nom_propre": r'\b[A-ZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ][a-zàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ]*\b',
            "nom_compose": r'[A-ZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ][a-zàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ]*[-\'][A-ZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞA-zàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ]*',
            "titre_honorifique": r'\b(Dr|Mr|Mrs|Ms|Prof|St|Ste)\.'
        }
        
        print(f"🏷️ Gestionnaire Marqueurs Onomastiques {self.version} initialisé")
        print(f"🎯 Marqueurs configurés : {len(self.config_marqueurs)} types")
    
    def traiter_phrase_avec_marqueurs(self, phrase: str, langue: str, 
                                    contexte_locuteur: str = "inconnu") -> TexteAvecMarqueurs:
        """Traite une phrase en ajoutant les marqueurs onomastiques"""
        
        print(f"\n🏷️ MARQUAGE ONOMASTIQUE : '{phrase}'")
        print(f"🌍 Langue: {langue} | 👤 Locuteur: {contexte_locuteur}")
        print("-" * 70)
        
        debut = time.time()
        
        # Détection des noms propres avec positions
        noms_detectes = self._detecter_noms_avec_positions(phrase)
        print(f"📋 Noms détectés : {[(nom, pos) for nom, pos, _ in noms_detectes]}")
        
        # Création des marqueurs
        marqueurs = []
        texte_avec_marqueurs = phrase
        offset_position = 0
        
        for nom, position_debut, position_fin in noms_detectes:
            marqueur = self._creer_marqueur_onomastique(
                nom, position_debut + offset_position, langue, contexte_locuteur
            )
            marqueurs.append(marqueur)
            
            # Remplacement dans le texte
            avant = texte_avec_marqueurs[:position_debut + offset_position]
            apres = texte_avec_marqueurs[position_fin + offset_position:]
            
            texte_remplace = f"{marqueur.marqueur_ouverture}{nom}{marqueur.marqueur_fermeture}"
            texte_avec_marqueurs = avant + texte_remplace + apres
            
            # Mise à jour de l'offset
            offset_position += len(texte_remplace) - len(nom)
        
        # Création du texte sémantique pur (sans noms propres)
        texte_semantique_pur = self._creer_texte_semantique_pur(phrase, noms_detectes)
        
        # Mapping des positions
        mapping_positions = self._creer_mapping_positions(marqueurs, texte_avec_marqueurs)
        
        # Statistiques
        stats = self._calculer_statistiques_separation(phrase, marqueurs)
        
        resultat = TexteAvecMarqueurs(
            texte_original=phrase,
            texte_avec_marqueurs=texte_avec_marqueurs,
            texte_semantique_pur=texte_semantique_pur,
            marqueurs_onomastiques=marqueurs,
            mapping_positions=mapping_positions,
            nombre_noms_marques=len(marqueurs),
            pourcentage_contenu_onomastique=stats["onomastique"],
            pourcentage_contenu_semantique=stats["semantique"]
        )
        
        temps_total = (time.time() - debut) * 1000
        self._afficher_resultat_marquage(resultat, temps_total)
        
        return resultat
    
    def _detecter_noms_avec_positions(self, phrase: str) -> List[Tuple[str, int, int]]:
        """Détecte les noms propres avec leurs positions exactes"""
        noms_avec_positions = []
        
        # Pattern principal pour noms propres
        for match in re.finditer(self.patterns_protection["nom_propre"], phrase):
            nom = match.group()
            debut = match.start()
            fin = match.end()
            
            # Filtrage intelligent
            if self._est_vraiment_nom_propre(nom, debut, phrase):
                noms_avec_positions.append((nom, debut, fin))
        
        # Pattern pour noms composés
        for match in re.finditer(self.patterns_protection["nom_compose"], phrase):
            nom = match.group()
            debut = match.start()
            fin = match.end()
            
            if self._est_vraiment_nom_propre(nom, debut, phrase):
                noms_avec_positions.append((nom, debut, fin))
        
        # Pattern pour titres honorifiques
        for match in re.finditer(self.patterns_protection["titre_honorifique"], phrase):
            nom = match.group()
            debut = match.start()
            fin = match.end()
            noms_avec_positions.append((nom, debut, fin))
        
        # Suppression des doublons et tri par position
        noms_uniques = list(set(noms_avec_positions))
        return sorted(noms_uniques, key=lambda x: x[1])
    
    def _est_vraiment_nom_propre(self, nom: str, position: int, phrase: str) -> bool:
        """Détermine si c'est vraiment un nom propre ou juste début de phrase"""
        
        # Si c'est au début de phrase, vérification supplémentaire
        if position == 0:
            # Liste des mots courants qui ne sont pas des noms propres
            mots_non_propres = {
                'fr': ['Un', 'Une', 'Le', 'La', 'Les', 'Ce', 'Cette', 'Il', 'Elle', 'Ils', 'Elles'],
                'en': ['The', 'A', 'An', 'This', 'That', 'It', 'He', 'She', 'They'],
                'de': ['Der', 'Die', 'Das', 'Ein', 'Eine', 'Es', 'Er', 'Sie']
            }
            
            # Si le mot est dans la liste des non-propres, ce n'est pas un nom propre
            for langue, liste in mots_non_propres.items():
                if nom in liste:
                    return False
        
        # Autres heuristiques
        if len(nom) < 2:
            return False
        
        if nom in ['Dr', 'Mr', 'Mrs', 'Ms', 'Prof', 'St', 'Ste']:
            return True  # Titres honorifiques
        
        return True  # Par défaut, considérer comme nom propre
    
    def _creer_marqueur_onomastique(self, nom: str, position: int, langue: str, 
                                  contexte: str) -> MarqueurOnomastique:
        """Crée un marqueur onomastique pour un nom"""
        
        # Génération d'un ID unique
        id_marqueur = f"ONO_{uuid.uuid4().hex[:8].upper()}"
        
        # Détermination du type onomastique
        type_ono = self._determiner_type_onomastique_simple(nom)
        
        # Configuration du marqueur
        config = self.config_marqueurs.get(type_ono, self.config_marqueurs["inconnu"])
        
        # Analyse sémantique isolée (version simplifiée)
        contenu_isole = self._analyser_semantique_isole(nom, type_ono, langue)
        
        # Création du marqueur
        marqueur_ouv = f"{config['prefixe']}#{id_marqueur}:"
        marqueur_ferm = f":{config['classe']}#{config['suffixe']}"
        
        return MarqueurOnomastique(
            id_marqueur=id_marqueur,
            nom_original=nom,
            type_onomastique=type_ono,
            marqueur_ouverture=marqueur_ouv,
            marqueur_fermeture=marqueur_ferm,
            contenu_semantique_isole=contenu_isole,
            position_debut=position,
            position_fin=position + len(nom),
            langue_detectee=langue,
            niveau_isolation="complet",
            interference_possible=False,
            priorite_traitement=1
        )
    
    def _determiner_type_onomastique_simple(self, nom: str) -> str:
        """Détermine le type onomastique de façon simplifiée"""
        
        # Bases de données simplifiées
        anthroponymes_courants = {
            'fr': ['Jean', 'Marie', 'Pierre', 'Paul', 'Jacques', 'François', 'Louis', 'Ésope'],
            'en': ['John', 'Mary', 'James', 'Smith', 'Johnson', 'Williams', 'Brown', 'Dr'],
            'de': ['Hans', 'Anna', 'Klaus', 'Grete', 'Wolfgang', 'Schmidt', 'Mueller']
        }
        
        toponymes_courants = {
            'fr': ['Paris', 'Lyon', 'Marseille', 'France', 'Europe', 'Berlin'],
            'en': ['London', 'Paris', 'New York', 'Europe', 'America', 'Africa'],
            'de': ['Berlin', 'München', 'Hamburg', 'Deutschland', 'Europa']
        }
        
        taxonymes_courants = ['Homo', 'Quercus', 'Felis', 'Rosa', 'Canis']
        
        # Classification
        for langue, liste in anthroponymes_courants.items():
            if nom in liste:
                return "anthroponyme"
        
        for langue, liste in toponymes_courants.items():
            if nom in liste:
                return "toponyme"
        
        if nom in taxonymes_courants:
            return "taxonyme"
        
        # Heuristiques
        if nom.endswith(('us', 'a', 'um')):
            return "taxonyme"
        elif len(nom) > 6:
            return "toponyme"
        else:
            return "anthroponyme"
    
    def _analyser_semantique_isole(self, nom: str, type_ono: str, langue: str) -> Dict[str, Any]:
        """Analyse sémantique isolée dans le marqueur"""
        
        # Dhātu simplifiés selon le type
        dhatus_par_type = {
            "anthroponyme": ["EXIST", "COMMUNICATE"],
            "toponyme": ["SPACE", "EXIST", "COMMUNICATE"],
            "taxonyme": ["QUALITY", "EXIST"]
        }
        
        return {
            "dhatus_associes": dhatus_par_type.get(type_ono, ["EXIST"]),
            "representation_universelle": f"{'+'.join(dhatus_par_type.get(type_ono, ['EXIST']))}[{nom}]",
            "niveau_analyse": "basique",
            "necessite_approfondissement": True,
            "timestamp_isolation": datetime.now().isoformat()
        }
    
    def _creer_texte_semantique_pur(self, phrase: str, noms_detectes: List[Tuple[str, int, int]]) -> str:
        """Crée un texte sémantique pur sans les noms propres"""
        
        texte_pur = phrase
        
        # Remplacement des noms par des placeholders sémantiques
        for nom, debut, fin in reversed(noms_detectes):  # Ordre inverse pour préserver positions
            type_ono = self._determiner_type_onomastique_simple(nom)
            
            placeholders = {
                "anthroponyme": "[INDIVIDU]",
                "toponyme": "[LIEU]",
                "taxonyme": "[ESPÈCE]",
                "inconnu": "[ENTITÉ]"
            }
            
            placeholder = placeholders.get(type_ono, "[ENTITÉ]")
            texte_pur = texte_pur[:debut] + placeholder + texte_pur[fin:]
        
        return texte_pur
    
    def _creer_mapping_positions(self, marqueurs: List[MarqueurOnomastique], 
                               texte_marque: str) -> Dict[str, Tuple[int, int]]:
        """Crée un mapping des positions des marqueurs"""
        mapping = {}
        
        for marqueur in marqueurs:
            # Recherche de la position du marqueur dans le texte marqué
            pattern = re.escape(marqueur.marqueur_ouverture)
            match = re.search(pattern, texte_marque)
            if match:
                debut = match.start()
                fin = debut + len(marqueur.marqueur_ouverture) + len(marqueur.nom_original) + len(marqueur.marqueur_fermeture)
                mapping[marqueur.id_marqueur] = (debut, fin)
        
        return mapping
    
    def _calculer_statistiques_separation(self, phrase: str, 
                                        marqueurs: List[MarqueurOnomastique]) -> Dict[str, float]:
        """Calcule les statistiques de séparation"""
        
        longueur_totale = len(phrase)
        longueur_noms = sum(len(m.nom_original) for m in marqueurs)
        
        pourcentage_onomastique = (longueur_noms / longueur_totale) * 100 if longueur_totale > 0 else 0
        pourcentage_semantique = 100 - pourcentage_onomastique
        
        return {
            "onomastique": pourcentage_onomastique,
            "semantique": pourcentage_semantique
        }
    
    def _afficher_resultat_marquage(self, resultat: TexteAvecMarqueurs, temps_ms: float):
        """Affiche le résultat du marquage"""
        
        print(f"\n📊 RÉSULTAT DU MARQUAGE")
        print(f"⏱️ Temps: {temps_ms:.2f}ms")
        print(f"🔢 Noms marqués: {resultat.nombre_noms_marques}")
        print(f"📈 Contenu onomastique: {resultat.pourcentage_contenu_onomastique:.1f}%")
        print(f"📈 Contenu sémantique: {resultat.pourcentage_contenu_semantique:.1f}%")
        
        print(f"\n📝 TEXTE ORIGINAL:")
        print(f"   {resultat.texte_original}")
        
        print(f"\n🏷️ TEXTE AVEC MARQUEURS:")
        print(f"   {resultat.texte_avec_marqueurs}")
        
        print(f"\n🧠 TEXTE SÉMANTIQUE PUR:")
        print(f"   {resultat.texte_semantique_pur}")
        
        print(f"\n📋 MARQUEURS CRÉÉS:")
        for i, marqueur in enumerate(resultat.marqueurs_onomastiques, 1):
            print(f"   {i}. {marqueur.id_marqueur} : '{marqueur.nom_original}' "
                  f"({marqueur.type_onomastique})")
            print(f"      Dhātu: {' + '.join(marqueur.contenu_semantique_isole['dhatus_associes'])}")
            print(f"      Isolation: {marqueur.niveau_isolation}")
    
    def extraire_nom_depuis_marqueur(self, texte_marque: str, id_marqueur: str) -> Optional[str]:
        """Extrait un nom depuis son marqueur"""
        
        # Pattern pour extraire le contenu d'un marqueur spécifique
        pattern = rf"⟨[^⟩]*#{id_marqueur}:([^:]+):[^⟩]*⟩"
        match = re.search(pattern, texte_marque)
        
        return match.group(1) if match else None
    
    def reconstituer_texte_original(self, texte_marque: str) -> str:
        """Reconstitue le texte original depuis la version marquée"""
        
        # Pattern pour tous les marqueurs
        pattern = r"⟨[^⟩]*#[^:]+:([^:]+):[^⟩]*⟩"
        
        def remplacer_marqueur(match):
            return match.group(1)  # Retourne juste le nom
        
        return re.sub(pattern, remplacer_marqueur, texte_marque)


def test_marqueurs_onomastiques():
    """Test du système de marqueurs onomastiques"""
    print("🧪 TEST DU SYSTÈME DE MARQUEURS ONOMASTIQUES")
    print("=" * 80)
    
    gestionnaire = GestionnaireMarqueursOnomastiques()
    
    # Phrases de test
    phrases_test = [
        ("Dr. Smith's cat—what a story!", "en", "narrateur_moderne"),
        ("Ésope racontait ses fables à Paris.", "fr", "conteur_traditionnel"),
        ("Marie et Jean visitent Berlin chaque été.", "fr", "narrateur_quotidien"),
        ("The species Homo sapiens evolved in Africa.", "en", "scientifique")
    ]
    
    for phrase, langue, contexte in phrases_test:
        print(f"\n" + "="*80)
        
        resultat = gestionnaire.traiter_phrase_avec_marqueurs(phrase, langue, contexte)
        
        # Test de reconstitution
        print(f"\n🔄 TEST DE RECONSTITUTION:")
        texte_reconstitue = gestionnaire.reconstituer_texte_original(resultat.texte_avec_marqueurs)
        print(f"   Original    : {resultat.texte_original}")
        print(f"   Reconstitué : {texte_reconstitue}")
        print(f"   Identique   : {'✅' if texte_reconstitue == resultat.texte_original else '❌'}")
        
        # Sauvegarde
        nom_fichier = f"marquage_onomastique_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{langue}.json"
        with open(nom_fichier, 'w', encoding='utf-8') as f:
            resultat_dict = asdict(resultat)
            json.dump(resultat_dict, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Marquage sauvegardé: {nom_fichier}")


if __name__ == "__main__":
    test_marqueurs_onomastiques()