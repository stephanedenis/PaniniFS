#!/bin/bash

# 🚀 PANINIFS MVP DATASET SETUP - <30 MINUTES TOTAL
# Échantillon ultra-concentré pour validation agile

set -e

echo "⚡ PaniniFS MVP Dataset Setup - Starting..."
start_time=$(date +%s)

# Configuration
MVP_DIR="/tmp/paninifs_mvp"
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Nettoyage et création structure
echo "📁 Setting up directory structure..."
rm -rf "$MVP_DIR"
mkdir -p "$MVP_DIR"/{gutenberg,wikipedia,formats,results}

cd "$MVP_DIR"

echo "📚 Downloading Gutenberg samples..."
cd gutenberg

# Romeo and Juliet (EN) - Project Gutenberg #1513
echo "  → Romeo and Juliet (EN)..."
curl -s -o romeo_en.txt "https://www.gutenberg.org/files/1513/1513-0.txt" || echo "⚠️  Gutenberg download failed, using fallback"

# Créer versions simplifiées pour test rapide si download échoue
if [ ! -f "romeo_en.txt" ] || [ ! -s "romeo_en.txt" ]; then
    echo "Creating fallback Romeo EN..."
    cat > romeo_en.txt << 'EOF'
THE TRAGEDY OF ROMEO AND JULIET by William Shakespeare

Two households, both alike in dignity,
In fair Verona, where we lay our scene,
From ancient grudge break to new mutiny,
Where civil blood makes civil hands unclean.
From forth the fatal loins of these two foes
A pair of star-cross'd lovers take their life;
Whose misadventured piteous overthrows
Do with their death bury their parents' strife.

Act I, Scene I
[Enter ROMEO]
ROMEO: Did my heart love till now? forswear it, sight!
For I ne'er saw true beauty till this night.

[Enter JULIET]
JULIET: Romeo, Romeo! wherefore art thou Romeo?
Deny thy father and refuse thy name;
Or, if thou wilt not, be but sworn my love,
And I'll no longer be a Capulet.
EOF
fi

# Romeo et Juliette (FR) - Version française
echo "  → Romeo et Juliette (FR)..."
cat > romeo_fr.txt << 'EOF'
LA TRAGÉDIE DE ROMÉO ET JULIETTE par William Shakespeare

Deux maisons, toutes deux égales en noblesse,
Dans la belle Vérone, où nous plaçons notre scène,
D'une rancune ancienne éclatent en nouveaux troubles,
Où le sang civil souille les mains civiles.
Des entrailles fatales de ces deux ennemis
Une paire d'amants infortunés prennent leur vie;
Dont les mésaventures pitoyables
Enterrent avec leur mort la querelle de leurs parents.

Acte I, Scène I
[Entre ROMÉO]
ROMÉO: Mon cœur a-t-il aimé jusqu'à présent? Reniez-le, vue!
Car je n'ai jamais vu la vraie beauté jusqu'à cette nuit.

[Entre JULIETTE]  
JULIETTE: Roméo, Roméo! pourquoi es-tu Roméo?
Renie ton père et refuse ton nom;
Ou, si tu ne veux pas, jure seulement ton amour,
Et je ne serai plus une Capulet.
EOF

# Version simplifiée Hamlet pour comparaison
echo "  → Hamlet (EN) sample..."
cat > hamlet_en.txt << 'EOF'
THE TRAGEDY OF HAMLET, PRINCE OF DENMARK by William Shakespeare

Act III, Scene I
HAMLET: To be, or not to be, that is the question:
Whether 'tis nobler in the mind to suffer
The slings and arrows of outrageous fortune,
Or to take arms against a sea of troubles
And by opposing end them. To die—to sleep,
No more; and by a sleep to say we end
The heart-ache and the thousand natural shocks
That flesh is heir to: 'tis a consummation
Devoutly to be wish'd.
EOF

echo "🌐 Creating Wikipedia samples..."
cd ../wikipedia

# Mathematics concepts in multiple languages
echo "  → Mathematics (EN)..."
cat > math_en.txt << 'EOF'
Mathematics

Mathematics is the science of structure, order, and relation that has evolved from elemental practices of counting, measuring, and describing the shapes of objects. It deals with logical reasoning and quantitative calculation, and its development has involved an increasing degree of idealization and abstraction of its subject matter.

Core areas include:
- Arithmetic: fundamental operations with numbers
- Algebra: study of mathematical symbols and rules
- Geometry: properties and relations of points, lines, surfaces
- Calculus: mathematical study of continuous change
- Statistics: collection, analysis, and interpretation of data

Mathematical proof is a logical argument demonstrating the truth of a mathematical statement.
EOF

echo "  → Mathématiques (FR)..."
cat > math_fr.txt << 'EOF'
Mathématiques

Les mathématiques sont la science de la structure, de l'ordre et des relations qui a évolué à partir de pratiques élémentaires de comptage, de mesure et de description des formes d'objets. Elle traite du raisonnement logique et du calcul quantitatif, et son développement a impliqué un degré croissant d'idéalisation et d'abstraction de son sujet.

Les domaines principaux comprennent:
- Arithmétique: opérations fondamentales avec les nombres
- Algèbre: étude des symboles mathématiques et des règles  
- Géométrie: propriétés et relations des points, lignes, surfaces
- Calcul: étude mathématique du changement continu
- Statistiques: collecte, analyse et interprétation des données

La preuve mathématique est un argument logique démontrant la vérité d'une déclaration mathématique.
EOF

echo "  → Democracy (EN)..."
cat > democracy_en.txt << 'EOF'
Democracy

Democracy is a form of government in which power is held by the people, either directly or through elected representatives. The term comes from the Greek words "demos" (people) and "kratos" (power or rule).

Key principles:
- Popular sovereignty: ultimate authority rests with the people
- Political equality: all citizens have equal political rights
- Majority rule with minority rights protection
- Regular free and fair elections
- Constitutional limitations on government power

Democratic systems vary widely in their institutional arrangements and practices.
EOF

echo "📁 Creating multi-format test files..."
cd ../formats

# Créer contenu identique en différents formats
CONTENT="# Data Processing Algorithm

This algorithm processes user input data and validates it.

## Function: validate_input
- Input: user_data (string)  
- Output: boolean (valid/invalid)
- Process: check format, sanitize, validate rules

## Implementation Notes
The validation follows security best practices:
1. Input sanitization
2. Format verification  
3. Business rule validation
4. Error handling"

# Format Markdown
echo "$CONTENT" > demo_doc.md

# Format texte simple
echo "$CONTENT" | sed 's/^#*//g' | sed 's/^[[:space:]]*//' > demo_doc.txt

# Configuration en différents formats
cat > demo_config.yml << 'EOF'
app:
  name: "DataProcessor"
  version: "1.0"
  settings:
    debug: true
    timeout: 30
    max_connections: 100
EOF

cat > demo_config.json << 'EOF'
{
  "app": {
    "name": "DataProcessor",
    "version": "1.0",
    "settings": {
      "debug": true,
      "timeout": 30,
      "max_connections": 100
    }
  }
}
EOF

# Code en différents langages - même algorithme
cat > demo_algo.py << 'EOF'
def validate_input(user_data):
    """Validate user input data"""
    if not isinstance(user_data, str):
        return False
    
    if len(user_data.strip()) == 0:
        return False
        
    if len(user_data) > 1000:
        return False
        
    return True

def process_data(data):
    """Process validated data"""
    if validate_input(data):
        return data.strip().lower()
    return None
EOF

cat > demo_algo.js << 'EOF'
function validateInput(userData) {
    // Validate user input data
    if (typeof userData !== 'string') {
        return false;
    }
    
    if (userData.trim().length === 0) {
        return false;
    }
    
    if (userData.length > 1000) {
        return false;
    }
    
    return true;
}

function processData(data) {
    // Process validated data
    if (validateInput(data)) {
        return data.trim().toLowerCase();
    }
    return null;
}
EOF

echo "📊 Creating validation script..."
cd ../results

cat > validate_mvp.py << 'EOF'
#!/usr/bin/env python3
"""
🚀 PaniniFS MVP Validation Script
Analyse sémantique rapide sur échantillon concentré
"""

import time
import json
from pathlib import Path
from collections import Counter
import re

class PaniniFSMVP:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.start_time = time.time()
        self.results = {}
        
    def simple_semantic_analysis(self, text):
        """Analyse sémantique basique mais efficace"""
        # Nettoyage et normalisation
        text = text.lower()
        text = re.sub(r'[^a-z\s]', ' ', text)
        
        # Extraction concepts clés
        words = text.split()
        # Filtrer mots vides basiques
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        meaningful_words = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Comptage fréquence
        word_freq = Counter(meaningful_words)
        
        # Signature sémantique basique
        signature = {
            'top_concepts': dict(word_freq.most_common(10)),
            'concept_count': len(word_freq),
            'total_words': len(words),
            'semantic_density': len(word_freq) / len(words) if words else 0
        }
        
        return signature
    
    def calculate_similarity(self, sig1, sig2):
        """Calcul similarité sémantique basique"""
        concepts1 = set(sig1['top_concepts'].keys())
        concepts2 = set(sig2['top_concepts'].keys())
        
        if not concepts1 or not concepts2:
            return 0.0
            
        intersection = len(concepts1.intersection(concepts2))
        union = len(concepts1.union(concepts2))
        
        jaccard = intersection / union if union > 0 else 0
        
        # Bonus pour densité sémantique similaire
        density_diff = abs(sig1['semantic_density'] - sig2['semantic_density'])
        density_bonus = max(0, 1 - density_diff * 2)
        
        return (jaccard * 0.7 + density_bonus * 0.3)
    
    def test_cross_linguistic(self):
        """Test: Romeo EN vs Romeo FR"""
        print("🌐 Testing cross-linguistic similarity...")
        
        romeo_en = (self.base_dir / 'gutenberg' / 'romeo_en.txt').read_text()
        romeo_fr = (self.base_dir / 'gutenberg' / 'romeo_fr.txt').read_text()
        
        sig_en = self.simple_semantic_analysis(romeo_en)
        sig_fr = self.simple_semantic_analysis(romeo_fr)
        
        similarity = self.calculate_similarity(sig_en, sig_fr)
        
        self.results['cross_linguistic'] = {
            'romeo_en_fr_similarity': similarity,
            'target': 0.60,
            'status': 'PASS' if similarity >= 0.60 else 'FAIL',
            'concepts_en': list(sig_en['top_concepts'].keys())[:5],
            'concepts_fr': list(sig_fr['top_concepts'].keys())[:5]
        }
        
        print(f"  Romeo EN/FR similarity: {similarity:.1%}")
        return similarity
    
    def test_multi_format(self):
        """Test: formats différents, contenu similaire"""
        print("📁 Testing multi-format detection...")
        
        md_content = (self.base_dir / 'formats' / 'demo_doc.md').read_text()
        txt_content = (self.base_dir / 'formats' / 'demo_doc.txt').read_text()
        
        sig_md = self.simple_semantic_analysis(md_content)
        sig_txt = self.simple_semantic_analysis(txt_content)
        
        similarity = self.calculate_similarity(sig_md, sig_txt)
        
        self.results['multi_format'] = {
            'md_txt_similarity': similarity,
            'target': 0.70,
            'status': 'PASS' if similarity >= 0.70 else 'FAIL',
            'concepts_common': list(set(sig_md['top_concepts'].keys()).intersection(set(sig_txt['top_concepts'].keys())))
        }
        
        print(f"  MD/TXT similarity: {similarity:.1%}")
        return similarity
    
    def test_algorithm_equivalence(self):
        """Test: même algorithme, langages différents"""
        print("⚙️  Testing algorithm equivalence...")
        
        py_content = (self.base_dir / 'formats' / 'demo_algo.py').read_text()
        js_content = (self.base_dir / 'formats' / 'demo_algo.js').read_text()
        
        sig_py = self.simple_semantic_analysis(py_content)
        sig_js = self.simple_semantic_analysis(js_content)
        
        similarity = self.calculate_similarity(sig_py, sig_js)
        
        self.results['algorithm_equivalence'] = {
            'py_js_similarity': similarity,
            'target': 0.50,
            'status': 'PASS' if similarity >= 0.50 else 'FAIL'
        }
        
        print(f"  Python/JS similarity: {similarity:.1%}")
        return similarity
    
    def generate_report(self):
        """Génération rapport complet"""
        elapsed = time.time() - self.start_time
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r['status'] == 'PASS')
        
        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'elapsed_seconds': round(elapsed, 2),
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': success_rate,
            'overall_status': 'SUCCESS' if success_rate >= 0.75 else 'PARTIAL' if success_rate >= 0.5 else 'FAILED',
            'detailed_results': self.results
        }
        
        # Sauvegarde JSON
        with open(self.base_dir / 'results' / 'mvp_validation.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Rapport console
        print(f"\n🚀 PANINIFS MVP VALIDATION REPORT")
        print(f"=" * 50)
        print(f"⏱️  Processing Time: {elapsed:.1f}s")
        print(f"📊 Success Rate: {success_rate:.0%} ({passed_tests}/{total_tests})")
        print(f"🎯 Overall Status: {report['overall_status']}")
        print(f"\n📋 Test Details:")
        
        for test_name, result in self.results.items():
            status_emoji = "✅" if result['status'] == 'PASS' else "❌"
            print(f"   {status_emoji} {test_name}: {result.get('romeo_en_fr_similarity', result.get('md_txt_similarity', result.get('py_js_similarity', 0))):.1%}")
        
        print(f"\n💡 Next Steps:")
        if success_rate >= 0.75:
            print("   🚀 Ready to expand dataset")
            print("   📈 Begin performance optimization")
        elif success_rate >= 0.5:
            print("   🔧 Improve failing algorithms")
            print("   📊 Add more test cases")
        else:
            print("   ⚠️  Review core semantic analysis")
            print("   🔍 Debug similarity calculations")
            
        return report

def main():
    mvp = PaniniFSMVP('/tmp/paninifs_mvp')
    
    # Exécution tests
    mvp.test_cross_linguistic()
    mvp.test_multi_format()
    mvp.test_algorithm_equivalence()
    
    # Génération rapport
    report = mvp.generate_report()
    
    print(f"\n📄 Full report saved: /tmp/paninifs_mvp/results/mvp_validation.json")

if __name__ == "__main__":
    main()
EOF

chmod +x validate_mvp.py

# Résumé final
end_time=$(date +%s)
elapsed=$((end_time - start_time))

echo ""
echo "✅ PaniniFS MVP Dataset Setup Complete!"
echo "⏱️  Setup time: ${elapsed}s"
echo "📁 Location: $MVP_DIR" 
echo "💾 Total size: $(du -sh "$MVP_DIR" | cut -f1)"
echo ""
echo "🚀 Next steps:"
echo "   cd $MVP_DIR/results"
echo "   python3 validate_mvp.py"
echo ""
echo "🎯 Expected results in <5 minutes!"
