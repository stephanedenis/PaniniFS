#!/bin/bash
# 🔬 VALIDATION EXPÉRIMENTALE DES DHĀTU SUR CORPUS PANINIFS

echo "🎯 DÉBUT DE LA VALIDATION DHĀTU"
echo "=================================="

# Test 1: Validation sur le code Python du projet
echo ""
echo "📊 TEST 1: Analyse des scripts Python PaniniFS"
echo "------------------------------------------------"

python3 dhatu_detector.py > dhatu_test_results.txt
echo "✅ Test de base effectué"

# Test 2: Analyse de tous les fichiers .py
echo ""
echo "📊 TEST 2: Corpus Python complet"
echo "---------------------------------"

echo "Analyse des fichiers Python:"
find . -name "*.py" -exec echo "Analyzing: {}" \; -exec python3 -c "
import sys
sys.path.append('.')
from dhatu_detector import DhatuDetector
detector = DhatuDetector()
result = detector.detect_in_file('{}')
if 'detected_dhatus' in result and result['detected_dhatus']:
    print('  Dhātu détectés:', [d['dhatu'] for d in result['detected_dhatus']])
else:
    print('  Aucun dhātu détecté')
" \;

# Test 3: Analyse des fichiers Markdown (documentation)
echo ""
echo "📊 TEST 3: Corpus Documentation (Markdown)"
echo "-------------------------------------------"

echo "Analyse des fichiers de documentation:"
find . -name "*.md" | head -5 | while read file; do
    echo "Analyzing: $file"
    python3 -c "
import sys
sys.path.append('.')
from dhatu_detector import DhatuDetector
detector = DhatuDetector()
result = detector.detect_in_file('$file')
if 'detected_dhatus' in result and result['detected_dhatus']:
    dhatus = [d['dhatu'] for d in result['detected_dhatus']]
    print('  Dhātu détectés:', dhatus)
    # Affiche les concepts détectés
    for d in result['detected_dhatus']:
        if d['count'] > 2:  # Seulement si fréquent
            print(f'    {d[\"dhatu\"]}: {d[\"matches\"][:3]}...')
else:
    print('  Aucun dhātu détecté')
"
done

# Test 4: Analyse cross-linguistique
echo ""
echo "📊 TEST 4: Validation Cross-Linguistique"
echo "-----------------------------------------"

# Créer des exemples équivalents en différents langages
cat > test_cross_lang.py << 'EOF'
#!/usr/bin/env python3
"""Test de validation cross-linguistique des dhātu"""

import sys
sys.path.append('.')
from dhatu_detector import DhatuDetector

# Exemples équivalents en différents langages
test_cases = [
    {
        'concept': 'ITERATION',
        'implementations': {
            'python': 'for i in range(10): print(i)',
            'javascript': 'for(let i=0; i<10; i++) console.log(i)',
            'rust': 'for i in 0..10 { println!("{}", i); }',
            'natural': 'repeat this action for each item in the list'
        }
    },
    {
        'concept': 'TRANSFORMATION',
        'implementations': {
            'python': 'result = [transform(x) for x in items]',
            'javascript': 'result = items.map(x => transform(x))',
            'haskell': 'result = map transform items',
            'natural': 'convert each item into a new format'
        }
    },
    {
        'concept': 'DECISION',
        'implementations': {
            'python': 'if condition: do_something() else: do_other()',
            'javascript': 'condition ? doSomething() : doOther()',
            'rust': 'if condition { do_something() } else { do_other() }',
            'natural': 'if the situation requires it, take action, otherwise wait'
        }
    }
]

detector = DhatuDetector()

print("🌍 VALIDATION CROSS-LINGUISTIQUE DES DHĀTU")
print("=" * 50)

for test_case in test_cases:
    print(f"\n🎯 Concept testé: {test_case['concept']}")
    print("-" * 30)
    
    detected_dhatus = {}
    
    for lang, code in test_case['implementations'].items():
        content_type = 'programming' if lang != 'natural' else 'natural_language'
        result = detector.detect_in_text(code, content_type)
        
        dhatus = [d['dhatu'] for d in result['detected_dhatus']]
        detected_dhatus[lang] = dhatus
        
        print(f"{lang:12}: {dhatus}")
    
    # Vérifie la cohérence cross-linguistique
    all_dhatus = set()
    for dhatus in detected_dhatus.values():
        all_dhatus.update(dhatus)
    
    if len(all_dhatus) > 0:
        print(f"✅ Dhātu détectés: {list(all_dhatus)}")
        
        # Vérifie si au moins un dhātu est commun
        common_dhatus = set(detected_dhatus[list(detected_dhatus.keys())[0]])
        for dhatus in detected_dhatus.values():
            common_dhatus &= set(dhatus)
        
        if common_dhatus:
            print(f"🌟 Dhātu universels: {list(common_dhatus)}")
        else:
            print("⚠️  Aucun dhātu complètement universel")
    else:
        print("❌ Aucun dhātu détecté")

EOF

python3 test_cross_lang.py

# Test 5: Statistiques générales
echo ""
echo "📊 TEST 5: Statistiques Corpus Complet"
echo "======================================="

python3 -c "
import sys
from pathlib import Path
sys.path.append('.')
from dhatu_detector import DhatuDetector

detector = DhatuDetector()
corpus_results = detector.analyze_corpus(Path('.'))
report = detector.generate_report(corpus_results)
print(report)

# Sauvegarde le rapport
with open('dhatu_corpus_analysis.md', 'w') as f:
    f.write(report)
print('\n📄 Rapport sauvegardé dans dhatu_corpus_analysis.md')
"

echo ""
echo "🎉 VALIDATION DHĀTU TERMINÉE"
echo "============================"
echo "📄 Résultats disponibles dans:"
echo "  - dhatu_test_results.txt"
echo "  - dhatu_corpus_analysis.md"
echo ""
echo "🎯 Prochaines étapes:"
echo "  1. Analyser les résultats d'universalité"
echo "  2. Raffiner le catalogue des dhātu"
echo "  3. Tester sur corpus externes"
echo "  4. Valider avec baby sign language"
