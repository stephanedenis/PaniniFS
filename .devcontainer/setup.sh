#!/bin/bash
# 🎌 PaniniFS DevContainer Setup Script

echo "🔧 Setting up PaniniFS Research Environment..."

# Rust setup
echo "🦀 Configuring Rust..."
rustup update
rustup component add clippy rustfmt
cargo install cargo-watch cargo-tarpaulin

# Python dependencies
echo "🐍 Installing Python research dependencies..."
pip install --upgrade pip
pip install jupyter pandas numpy matplotlib seaborn
pip install nltk spacy transformers
pip install requests beautifulsoup4 
pip install pytest pytest-cov black isort

# Download language models
echo "📚 Downloading language models..."
python -m spacy download en_core_web_sm
python -m spacy download fr_core_news_sm

# Build PaniniFS Core
echo "🏗️ Building PaniniFS Core..."
cd /workspaces/PaniniFS-1/CORE/panini-fs
cargo build
cargo test

# Setup git configuration
echo "📝 Configuring git..."
git config --global core.autocrlf input
git config --global init.defaultBranch main

# Create research workspace
echo "🔬 Setting up research workspace..."
mkdir -p /workspaces/research-temp
mkdir -p /workspaces/datasets-cache

# Install additional tools
echo "🛠️ Installing additional tools..."
cargo install ripgrep fd-find bat
pip install rich typer

echo "✅ PaniniFS Environment Setup Complete!"
echo ""
echo "🎯 Quick Start:"
echo "  📊 Research: cd RESEARCH/ && jupyter lab"
echo "  🦀 Core Dev: cd CORE/panini-fs && cargo watch -x test"
echo "  🔍 Validate: cd CORE/semantic-analyzer && python dhatu-detector/dhatu_detector.py"
echo ""
echo "🎌 Ready for semantic compression research!"
