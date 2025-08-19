#!/bin/bash

# Script pour configurer Google Drive API OAuth2 correctement

echo "🔧 Configuration Google Drive API - Fix OAuth2"
echo "=============================================="

echo ""
echo "❌ Erreur détectée: redirect_uri_mismatch"
echo "   - Type actuel: web"
echo "   - Type requis: desktop/installed application"

echo ""
echo "🛠️  Correction nécessaire dans Google Cloud Console:"
echo ""
echo "1. Aller sur: https://console.cloud.google.com/"
echo "2. Projet: generated-area-469517-n9"
echo "3. APIs & Services > Credentials"
echo "4. Supprimer l'OAuth 2.0 Client ID existant"
echo "5. Créer un nouveau OAuth 2.0 Client ID:"
echo "   - Application type: Desktop application"
echo "   - Name: PaniniFS Desktop Client"
echo "6. Télécharger le nouveau JSON"
echo "7. Remplacer le fichier credentials.json"

echo ""
echo "✅ Alternative rapide - Upload manuel:"
echo "   1. Compresser le package:"
echo "      tar -czf remarkable_study_pack.tar.gz remarkable_study_pack/"
echo ""
echo "   2. Upload sur Google Drive:"
echo "      - Créer dossier: Panini/Bibliographie/Study_Pack_Remarkable/"
echo "      - Uploader remarkable_study_pack.tar.gz"
echo ""
echo "   3. Extraire sur reMarkable ou localement"

echo ""
echo "📁 Contenu du package prêt pour upload:"
ls -la remarkable_study_pack/ 2>/dev/null || echo "   Package non trouvé - vérifier le chemin"

echo ""
echo "🎯 Recommandation: Upload manuel pour accès immédiat"
echo "Configuration API pour automatisation future"
