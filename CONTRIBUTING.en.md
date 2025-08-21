# 🤝 Contributing Guide - PaniniFS

*[Version française](CONTRIBUTING.md) | **English Version***

Thank you for your interest in PaniniFS! This guide explains how to contribute effectively to the project.

## 🎯 **Contribution Types**

### **🤖 AI Copiloting (Strongly Recommended)**
**PaniniFS has been primarily developed through collaborative human-AI copiloting.**
- **GitHub Copilot**: Real-time assisted code development
- **Continuous collaboration**: Constant developer ↔ AI dialogue
- **Rapid iteration**: Short feedback cycles and continuous improvement
- **Living documentation**: Code and docs evolve together

*Copiloting is our preferred contribution method - we strongly encourage this approach!*

### **🔬 Research & Theory**
- Validation of the 7 informational dhātu
- New semantic compression approaches
- Linguistic analysis and experiments
- Academic publications and articles

### **💻 Development**
- Rust Core (compression engine)
- APIs and integrations
- CLI tools and interfaces
- Tests and benchmarks

### **📚 Documentation**
- User guides
- Technical documentation
- Tutorials and examples
- Translations

### **🌐 Ecosystem**
- Cloud integrations (Azure, Google Drive, etc.)
- Automation tools
- Extensions and plugins
- Autonomous missions

## 🛠️ **Development Environment Setup**

### **Prerequisites**
```bash
# Rust (stable version)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Python 3.8+ (for ecosystem tools)
python3 --version

# Git configuration
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### **Project Installation**
```bash
# Clone and setup
git clone https://github.com/stephanedenis/PaniniFS.git
cd PaniniFS

# Build Rust core
cd CORE/panini-fs
cargo build
cargo test

# Setup Python ecosystem
cd ../../ECOSYSTEM
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **Project Structure**
```
PaniniFS/
├── CORE/              # 🦀 Rust - Main engine
├── ECOSYSTEM/         # 🐍 Python - Tools and integrations  
├── DOCUMENTATION/     # 📚 User and dev documentation
├── RESEARCH/          # 🔬 Experiments and datasets
├── OPERATIONS/        # ⚙️ DevOps, monitoring, deployment
├── GOVERNANCE/        # 🏛️ Processes and governance
└── SANDBOX/           # 🧪 Prototypes and experiments
```

## 📝 **Code Standards**

### **Rust (CORE/)**
```rust
// Style: rustfmt with default config
cargo fmt

// Linting: clippy strict level
cargo clippy -- -D warnings

// Tests: coverage >80%
cargo test
cargo tarpaulin --out Html
```

### **Python (ECOSYSTEM/)**
```python
# Style: Black formatter
black .

# Linting: flake8 + mypy
flake8 .
mypy .

# Tests: pytest with coverage
pytest --cov=. --cov-report=html
```

### **Commits**
```bash
# Format: type(scope): description
#
# Types: feat, fix, docs, test, refactor, perf, ci, build
# Examples:
git commit -m "feat(core): add bidirectional dhātu compression"
git commit -m "fix(ecosystem): correct GitHub API integration"
git commit -m "docs(research): publish dhātu validation results"
```

## 🔄 **Contribution Workflow**

### **🤖 Copiloting Workflow** (Preferred Method)
```bash
# AI-assisted development recommended
# GitHub Copilot, Claude, ChatGPT, etc.

# 1. Collaborative human-AI session
AI_ASSISTANT="github-copilot"  # or other
git checkout -b feature/copilot-assisted-compression

# 2. Iterative development with continuous feedback
# - Constant dialogue with AI
# - Real-time validation
# - Collaboratively generated documentation

# 3. Regular documented commits
git commit -m "feat(core): copilot-assisted dhātu optimization

Co-authored-by: GitHub Copilot
Collaborative session: Human + AI iterative development
Validation: AI-suggested tests + human review"

# 4. PR with collaboration context
# Document the copiloting process used
```

### **👥 Traditional Workflow**

#### **1. Issues & Planning**
- Check [open issues](https://github.com/stephanedenis/PaniniFS/issues)
- Comment to signal your interest
- Create issue for new feature

#### **2. Fork & Branch**
```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR-USERNAME/PaniniFS.git
cd PaniniFS

# Create descriptive branch
git checkout -b feature/dhatu-compression-optimization
# or
git checkout -b fix/github-api-authentication  
# or
git checkout -b docs/installation-guide-update
```

#### **3. Development**
```bash
# Develop your contribution
# Test locally
cargo test      # For Rust
pytest          # For Python

# Regular commits with clear messages
git add .
git commit -m "feat(core): implement dhātu compression algorithm"
```

#### **4. Pull Request**
```bash
# Push your branch
git push origin feature/dhatu-compression-optimization

# Create PR on GitHub with:
# - Clear description of changes
# - References to related issues
# - Added/modified tests
# - Updated documentation if necessary
```

## ✅ **PR Checklist**

### **Code**
- [ ] Code follows style standards (rustfmt/black)
- [ ] Linting passes without warnings (clippy/flake8)
- [ ] Tests added for new features
- [ ] All existing tests pass
- [ ] Performance verified (benchmarks if applicable)

### **Documentation**
- [ ] README updated if necessary
- [ ] Code documentation (rustdoc/docstrings)
- [ ] CHANGELOG.md updated for notable changes
- [ ] Usage examples provided

### **Process**
- [ ] Branch up to date with master
- [ ] Atomic commits with clear messages
- [ ] Complete PR description
- [ ] CI/CD tests pass

## 🔬 **Research Contribution**

### **dhātu Validation**
- Experiments with linguistic datasets
- Compression validation across different languages
- Performance and quality metrics
- Results publication in RESEARCH/

### **New Approaches**
- Innovative compression algorithms
- AI/ML integrations
- Performance optimizations
- Cross-linguistic applications

## 🌐 **Ecosystem Contribution**

### **Cloud Integrations**
- External service connectors
- APIs and webhooks
- Automation and orchestration
- Monitoring and observability

### **User Tools**
- Ergonomic CLI
- Graphical interfaces
- Editor extensions
- System plugins

## 📊 **Review Process**

### **Typical Timeline**
- **Initial feedback**: 24-48h
- **Technical review**: 2-5 days
- **Merge**: After approval + green CI

### **Review Criteria**
- **Functional**: Contribution works as described
- **Quality**: Maintainable and tested code
- **Consistency**: Integrates with existing architecture
- **Documentation**: Sufficiently documented

## 🤝 **Community**

### **Communication**
- **GitHub Issues**: Technical discussions and bugs
- **Discussions**: General questions and ideas
- **Commits/PR**: Detailed async communication

### **Code of Conduct**
- Respectful and inclusive
- Constructive in criticism
- Focus on technical and research aspects
- No marketing or self-promotion

## 🆘 **Need Help?**

### **Getting Started**
- Check [good first issues](https://github.com/stephanedenis/PaniniFS/labels/good%20first%20issue)
- Read documentation in DOCUMENTATION/
- Explore examples in CORE/examples/

### **Questions**
- Open a [GitHub discussion](https://github.com/stephanedenis/PaniniFS/discussions)
- Comment on corresponding issue
- Consult DOCUMENTATION/developer-docs/

### **Bugs**
- Check existing issues
- Use bug-report template
- Provide minimal reproduction

---

## 🎯 **Project Goals**

**PaniniFS aims to revolutionize data compression through deep linguistic analysis, leveraging Sanskrit dhātu to create a universally efficient generative file system.**

**Every contribution, whether code, research, or documentation, brings us closer to this ambitious goal.**

**Thank you for being part of this adventure! 🚀**
