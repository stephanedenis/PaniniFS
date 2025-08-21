#!/usr/bin/env python3
"""
🎭 PLAYWRIGHT GITHUB SETUP AUTOMATION
Automatise la configuration complète GitHub Project Management pour PaniniFS
"""

import asyncio
from playwright.async_api import async_playwright
import json

# Configuration des labels selon GOVERNANCE/roadmap/GITHUB_PROJECT_PLAN.md
LABELS_CONFIG = [
    # 🔬 RECHERCHE & VALIDATION
    {"name": "research:dhatu-validation", "color": "8B5CF6", "description": "Validation des 7 dhātu informationnels"},
    {"name": "research:compression", "color": "8B5CF6", "description": "Recherche compression sémantique"},
    {"name": "research:linguistics", "color": "8B5CF6", "description": "Analyses linguistiques et expérimentations"},
    {"name": "research:publications", "color": "8B5CF6", "description": "Publications académiques et articles"},
    
    # 💻 DÉVELOPPEMENT TECHNIQUE
    {"name": "core:rust", "color": "F97316", "description": "Engine Rust compression"},
    {"name": "core:performance", "color": "F97316", "description": "Optimisations et benchmarks"},
    {"name": "core:api", "color": "F97316", "description": "APIs et interfaces"},
    {"name": "core:tests", "color": "F97316", "description": "Tests unitaires et intégration"},
    
    # 🌐 ÉCOSYSTÈME & INTÉGRATIONS
    {"name": "ecosystem:python", "color": "10B981", "description": "Outils Python et intégrations"},
    {"name": "ecosystem:cloud", "color": "10B981", "description": "Intégrations cloud (Azure, Google Drive)"},
    {"name": "ecosystem:automation", "color": "10B981", "description": "Outils automation et workflows"},
    {"name": "ecosystem:integrations", "color": "10B981", "description": "Extensions et plugins externes"},
    
    # 🚀 OPÉRATIONS & INFRASTRUCTURE
    {"name": "ops:deployment", "color": "EF4444", "description": "Déploiement et infrastructure"},
    {"name": "ops:monitoring", "color": "EF4444", "description": "Monitoring et observabilité"},
    {"name": "ops:security", "color": "EF4444", "description": "Sécurité et audit"},
    {"name": "ops:project-management", "color": "EF4444", "description": "Gestion projet et coordination"},
    
    # 📖 DOCUMENTATION
    {"name": "docs:api", "color": "3B82F6", "description": "Documentation API"},
    {"name": "docs:user-guides", "color": "3B82F6", "description": "Guides utilisateurs"},
    {"name": "docs:architecture", "color": "3B82F6", "description": "Documentation architecture"},
    {"name": "docs:tutorials", "color": "3B82F6", "description": "Tutoriels et exemples"},
    
    # ⚙️ WORKFLOW & PROCESS
    {"name": "workflow:triage", "color": "6B7280", "description": "Nouveau, besoin évaluation"},
    {"name": "workflow:blocked", "color": "6B7280", "description": "Bloqué, attend dépendance"},
    {"name": "workflow:ready", "color": "6B7280", "description": "Prêt pour développement"},
    {"name": "workflow:in-progress", "color": "6B7280", "description": "En cours développement"},
    {"name": "workflow:review", "color": "6B7280", "description": "En revue/validation"},
    {"name": "workflow:testing", "color": "6B7280", "description": "En phase de test"},
    
    # 🎯 PRIORITÉS
    {"name": "priority:critical", "color": "DC2626", "description": "Critique, bloque le projet"},
    {"name": "priority:high", "color": "EA580C", "description": "Haute priorité"},
    {"name": "priority:medium", "color": "D97706", "description": "Priorité moyenne"},
    {"name": "priority:low", "color": "65A30D", "description": "Peut attendre"},
    
    # 👥 INTERVENANTS
    {"name": "human:required", "color": "8B5CF6", "description": "Validation humaine requise"},
    {"name": "human:preferred", "color": "A855F7", "description": "Input humain préférable"},
    {"name": "ai:autonomous", "color": "06B6D4", "description": "IA peut gérer en autonomie"},
    {"name": "ai:assisted", "color": "0891B2", "description": "IA assistée par humain"},
    
    # 🏷️ TYPES GÉNÉRIQUES
    {"name": "bug", "color": "DC2626", "description": "Quelque chose ne fonctionne pas"},
    {"name": "enhancement", "color": "10B981", "description": "Nouvelle fonctionnalité ou amélioration"},
    {"name": "question", "color": "3B82F6", "description": "Question ou demande d'information"},
    {"name": "duplicate", "color": "6B7280", "description": "Issue ou PR duplicate"},
    {"name": "good first issue", "color": "22C55E", "description": "Bon pour nouveaux contributeurs"},
    {"name": "help wanted", "color": "0EA5E9", "description": "Aide communautaire souhaitée"},
    {"name": "setup", "color": "F59E0B", "description": "Configuration initiale et setup"},
]

# Topics à ajouter au repository
TOPICS = [
    "file-system", "compression", "semantic-analysis", "rust", 
    "research", "linguistics", "dhatu", "generative-ai", 
    "panini", "sanskrit", "open-source", "academic-research"
]

async def create_labels(page):
    """Créer tous les labels GitHub"""
    print("📋 Création des labels GitHub...")
    
    # Naviguer vers la page des labels
    await page.goto("https://github.com/stephanedenis/PaniniFS/labels")
    await page.wait_for_load_state('networkidle', timeout=30000)
    
    for i, label in enumerate(LABELS_CONFIG):
        try:
            print(f"  🏷️  [{i+1}/{len(LABELS_CONFIG)}] Création: {label['name']}")
            
            # Attendre que la page soit complètement chargée
            await page.wait_for_timeout(1000)
            
            # Chercher le bouton "New label" avec plusieurs sélecteurs possibles
            new_label_selectors = [
                "a:has-text('New label')",
                ".btn:has-text('New label')", 
                "[data-content='New label']",
                "a[href*='/labels/new']",
                ".btn-primary:has-text('New')",
                "text=New label"
            ]
            
            button_found = False
            for selector in new_label_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    await page.click(selector)
                    button_found = True
                    print(f"    🎯 Bouton trouvé avec: {selector}")
                    break
                except:
                    continue
            
            if not button_found:
                print(f"    ⚠️  Bouton 'New label' non trouvé pour {label['name']}")
                continue
            
            # Attendre le formulaire
            await page.wait_for_selector("input[name='label[name]'], #label_name", timeout=10000)
            
            # Remplir le formulaire avec sélecteurs multiples
            name_selectors = ["input[name='label[name]']", "#label_name", "input[placeholder*='label name']"]
            for selector in name_selectors:
                try:
                    await page.fill(selector, label['name'])
                    break
                except:
                    continue
            
            desc_selectors = ["input[name='label[description]']", "#label_description", "input[placeholder*='description']"]
            for selector in desc_selectors:
                try:
                    await page.fill(selector, label['description'])
                    break
                except:
                    continue
            
            # Couleur (supprimer le # si présent)
            color = label['color'].replace('#', '')
            color_selectors = ["input[name='label[color]']", "#label_color", "input[type='text'][placeholder*='color']"]
            for selector in color_selectors:
                try:
                    await page.fill(selector, color)
                    break
                except:
                    continue
            
            # Sauvegarder avec sélecteurs multiples
            save_selectors = [
                "button[type='submit']:has-text('Create label')",
                "button:has-text('Create label')",
                ".btn-primary:has-text('Create')",
                "input[type='submit']",
                "button[type='submit']"
            ]
            
            for selector in save_selectors:
                try:
                    await page.click(selector)
                    break
                except:
                    continue
            
            await page.wait_for_load_state('networkidle', timeout=15000)
            
            print(f"    ✅ Label '{label['name']}' créé")
            
        except Exception as e:
            print(f"    ⚠️  Erreur label '{label['name']}': {e}")
            # Retourner à la page des labels si erreur
            await page.goto("https://github.com/stephanedenis/PaniniFS/labels")
            await page.wait_for_load_state('networkidle', timeout=30000)

async def setup_topics(page):
    """Configurer les topics du repository"""
    print("🏷️  Configuration des topics...")
    
    # Naviguer vers la page principale du repo
    await page.goto("https://github.com/stephanedenis/PaniniFS")
    await page.wait_for_load_state('networkidle', timeout=30000)
    
    try:
        # Cliquer sur l'icône settings avec sélecteurs multiples
        settings_selectors = [
            "button[data-target='repository-details-dialog']",
            "button[aria-label='Repository details']",
            ".btn:has-text('About')",
            "button:has([data-octicon='gear'])",
            ".repository-content button[aria-label*='settings']"
        ]
        
        button_found = False
        for selector in settings_selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                await page.click(selector)
                button_found = True
                print(f"    🎯 Settings trouvé avec: {selector}")
                break
            except:
                continue
        
        if not button_found:
            print("    ⚠️  Bouton settings non trouvé, essai méthode alternative...")
            # Essayer de cliquer directement sur "About" ou équivalent
            await page.click("text=About")
            await page.wait_for_timeout(2000)
        
        # Attendre le champ topics avec sélecteurs multiples
        topic_selectors = [
            "input[name='repository[topics][]']",
            "input[placeholder*='topic']",
            ".topic-tag-input input",
            "#repository_topics",
            "input[data-target*='topic']"
        ]
        
        input_found = False
        for selector in topic_selectors:
            try:
                await page.wait_for_selector(selector, timeout=10000)
                input_found = True
                print(f"    🎯 Input topics trouvé avec: {selector}")
                
                # Ajouter chaque topic
                for topic in TOPICS:
                    print(f"  🏷️  Ajout topic: {topic}")
                    await page.fill(selector, topic)
                    await page.press(selector, "Enter")
                    await asyncio.sleep(0.5)  # Petite pause
                
                break
            except:
                continue
        
        if not input_found:
            print("    ⚠️  Champ topics non trouvé")
            return
        
        # Sauvegarder avec sélecteurs multiples
        save_selectors = [
            "button:has-text('Save changes')",
            "button[type='submit']",
            ".btn-primary:has-text('Save')",
            "input[type='submit']"
        ]
        
        for selector in save_selectors:
            try:
                await page.click(selector)
                break
            except:
                continue
        
        await page.wait_for_load_state('networkidle', timeout=15000)
        
        print("    ✅ Topics configurés")
        
    except Exception as e:
        print(f"    ⚠️  Erreur topics: {e}")
        print(f"    🔍 Essai inspection manuelle nécessaire")

async def create_project_board(page):
    """Créer le Project Board avec colonnes"""
    print("📊 Création du Project Board...")
    
    try:
        # Naviguer vers la page des projects
        await page.goto("https://github.com/stephanedenis/PaniniFS/projects")
        await page.wait_for_load_state('networkidle')
        
        # Créer nouveau project
        await page.click("a:has-text('New project'), button:has-text('New project')")
        await page.wait_for_selector("input[name='name']")
        
        # Nom et description
        await page.fill("input[name='name']", "PaniniFS Development Hub")
        await page.fill("textarea[name='body']", 
                       "Hub de coordination multi-intervenants (humains + AI agents) pour PaniniFS")
        
        # Template: Board
        await page.click("button:has-text('Board')")
        
        # Créer le project
        await page.click("button:has-text('Create project')")
        await page.wait_for_load_state('networkidle')
        
        print("    ✅ Project Board 'PaniniFS Development Hub' créé")
        
        # Configuration des colonnes (GitHub va créer des colonnes par défaut)
        # On peut les renommer si nécessaire
        
    except Exception as e:
        print(f"    ⚠️  Erreur Project Board: {e}")

async def apply_labels_to_issue(page):
    """Appliquer les labels à l'Issue #2"""
    print("🏷️  Application des labels à Issue #2...")
    
    try:
        # Naviguer vers l'Issue #2
        await page.goto("https://github.com/stephanedenis/PaniniFS/issues/2")
        await page.wait_for_load_state('networkidle', timeout=30000)
        
        # Cliquer sur le bouton Labels avec sélecteurs multiples
        labels_selectors = [
            "button[aria-label='Labels']",
            ".js-issue-labels button",
            "button:has-text('Labels')",
            ".sidebar-labels button",
            "[data-target='labels-select-menu']"
        ]
        
        button_found = False
        for selector in labels_selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                await page.click(selector)
                button_found = True
                print(f"    🎯 Bouton Labels trouvé avec: {selector}")
                break
            except:
                continue
        
        if not button_found:
            print("    ⚠️  Bouton Labels non trouvé")
            return
        
        await page.wait_for_selector(".select-menu-list, .SelectMenu-list", timeout=10000)
        
        # Labels à appliquer
        labels_to_apply = [
            "workflow:ready", "priority:high", "ai:autonomous", 
            "ops:project-management", "setup"
        ]
        
        for label in labels_to_apply:
            try:
                # Sélecteurs multiples pour les labels
                label_selectors = [
                    f".select-menu-item:has-text('{label}')",
                    f".SelectMenu-item:has-text('{label}')",
                    f"[data-label-name='{label}']",
                    f"text={label}",
                    f".label-select-menu-item:has-text('{label}')"
                ]
                
                label_found = False
                for label_selector in label_selectors:
                    try:
                        await page.click(label_selector, timeout=3000)
                        print(f"    ✅ Label '{label}' appliqué avec: {label_selector}")
                        label_found = True
                        break
                    except:
                        continue
                
                if not label_found:
                    print(f"    ⚠️  Label '{label}' non trouvé")
                
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"    ⚠️  Erreur label '{label}': {e}")
        
        # Fermer le menu en cliquant ailleurs
        await page.click("body")
        await page.wait_for_timeout(1000)
        
        print("    ✅ Labels appliqués à Issue #2")
        
    except Exception as e:
        print(f"    ⚠️  Erreur application labels: {e}")

async def debug_page_elements(page, step_name):
    """Fonction de debug pour capturer l'état de la page"""
    print(f"🔍 DEBUG {step_name}:")
    
    # Screenshot
    await page.screenshot(path=f"/tmp/github_debug_{step_name.lower().replace(' ', '_')}.png")
    print(f"    📸 Screenshot: /tmp/github_debug_{step_name.lower().replace(' ', '_')}.png")
    
    # URL actuelle
    print(f"    🌍 URL: {page.url}")
    
    # Rechercher des boutons/liens communs
    common_selectors = [
        "button", "a", ".btn", "[role='button']", 
        "input[type='submit']", "[data-target]", "[aria-label]"
    ]
    
    for selector in common_selectors:
        try:
            elements = await page.query_selector_all(selector)
            if elements:
                print(f"    🎯 Trouvé {len(elements)} éléments: {selector}")
                # Afficher les 3 premiers textes/attributs
                for i, elem in enumerate(elements[:3]):
                    try:
                        text = await elem.text_content()
                        if text and text.strip():
                            print(f"      - [{i+1}] Texte: '{text.strip()[:50]}'")
                    except:
                        pass
        except:
            pass

async def github_setup_automation():
    """Script principal d'automatisation GitHub"""
    print("🚀 DÉMARRAGE AUTOMATION GITHUB SETUP")
    print("=" * 50)
    
    async with async_playwright() as p:
        print("🎭 Lancement Firefox...")
        browser = await p.firefox.launch(headless=False, slow_mo=800)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # 1. Navigation vers GitHub et attente de connexion manuelle
            print("📍 Navigation vers GitHub...")
            await page.goto("https://github.com/login")
            await page.wait_for_load_state('networkidle', timeout=30000)
            
            print("🔐 VEUILLEZ VOUS CONNECTER À GITHUB")
            print("   Connectez-vous dans le navigateur ouvert")
            print("   Appuyez sur ENTRÉE ici quand c'est fait...")
            input("   Prêt ? [ENTRÉE]")
            
            # Debug initial
            await debug_page_elements(page, "After Login")
            
            # 2. Création des labels (seulement les 5 premiers pour test)
            print(f"\n🧪 TEST MODE: Création des 5 premiers labels seulement")
            original_labels = LABELS_CONFIG.copy()
            global LABELS_CONFIG
            LABELS_CONFIG = LABELS_CONFIG[:5]  # Test avec 5 labels seulement
            
            await create_labels(page)
            
            print("⏱️  Pause 10 secondes...")
            await asyncio.sleep(10)
            
            # 3. Configuration des topics
            await setup_topics(page)
            
            print("⏱️  Pause 10 secondes...")
            await asyncio.sleep(10)
            
            # 4. Création Project Board
            await create_project_board(page)
            
            print("⏱️  Pause 10 secondos...")
            await asyncio.sleep(10)
            
            # 5. Application labels à Issue #2
            await apply_labels_to_issue(page)
            
            print("\n🎉 AUTOMATION TEST COMPLÉTÉE !")
            print("=" * 50)
            print("✅ Labels GitHub: 5 premiers labels testés")
            print("✅ Topics: Configuration tentée")
            print("✅ Project Board: Création tentée")
            print("✅ Issue #2: Labels tentés")
            print("\n🔍 Vérifiez les résultats et screenshots dans /tmp/")
            print("📋 Si tout fonctionne, relancez avec tous les labels")
            
            print("\n⏰ Navigateur reste ouvert 60 secondes pour vérification...")
            await asyncio.sleep(60)
            
        except Exception as e:
            print(f"\n🚨 ERREUR CRITIQUE: {e}")
            await debug_page_elements(page, "Error State")
            print("🛠️  Débug possible: vérifiez les screenshots")
            await asyncio.sleep(30)
        
        finally:
            await browser.close()
            print("🔚 Automation terminée")

if __name__ == "__main__":
    print("🎭 PLAYWRIGHT GITHUB AUTOMATION - PaniniFS")
    print("🎯 Automatise: Labels + Topics + Project Board + Issue #2")
    print("")
    asyncio.run(github_setup_automation())
