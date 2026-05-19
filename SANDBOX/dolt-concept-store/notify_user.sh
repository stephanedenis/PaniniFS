#!/bin/bash
# Script de notification utilisateur (son système + KDE Connect)
# Usage: ./notify_user.sh "Message" ["Titre optionnel"]

MESSAGE="${1:-Intervention requise}"
TITLE="${2:-Panini-FS Dolt Setup}"

# Son système (essaie plusieurs méthodes)
if command -v paplay &> /dev/null && [ -f /usr/share/sounds/freedesktop/stereo/complete.oga ]; then
    paplay /usr/share/sounds/freedesktop/stereo/complete.oga &
elif command -v paplay &> /dev/null && [ -f /usr/share/sounds/freedesktop/stereo/bell.oga ]; then
    paplay /usr/share/sounds/freedesktop/stereo/bell.oga &
elif command -v beep &> /dev/null; then
    beep -f 800 -l 200 &
else
    # Fallback: beep terminal
    echo -e "\a" &
fi

# KDE Connect notification (trouve le device automatiquement)
if command -v kdeconnect-cli &> /dev/null; then
    # Récupère le premier device connecté
    DEVICE_ID=$(kdeconnect-cli -a --id-only 2>/dev/null | head -n1)
    
    if [ -n "$DEVICE_ID" ]; then
        kdeconnect-cli -d "$DEVICE_ID" --ping-msg "$TITLE: $MESSAGE" 2>/dev/null &
    fi
fi

# Notification desktop (notify-send)
if command -v notify-send &> /dev/null; then
    notify-send -u critical "$TITLE" "$MESSAGE" &
fi

echo "🔔 $TITLE: $MESSAGE"
