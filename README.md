# 🔐 Network Keylogger

> **⚠️ Disclaimer:** This project was developed strictly for educational purposes. It must only be used in controlled, authorized lab environments. Unauthorized use against real systems is illegal and unethical.

---

## 📋 Overview

A real-time keylogger that captures and transmits keystrokes from a victim machine to an attacker-controlled server over a network share. Built to simulate a real-world cyberattack within an ethical hacking framework, demonstrating key penetration testing phases and the security vulnerabilities they exploit.

Both machines ran **Kali Linux** on an isolated local network.

---

## 🧠 Ethical Hacking Phases Covered

| Phase | What was done |
|---|---|
| **Reconnaissance** | Identified and configured both machines on a shared local network |
| **Gaining Access** | Set up an SMB/CIFS share between attacker and victim without credentials |
| **Maintaining Access** | Ran a persistent Python keylogger that logs continuously to the shared drive |
| **Covering Tracks** | No local log files on victim; all data written directly to attacker's machine |

---

## 🛠️ Tools & Technologies

- **Python 3** — keylogger script
- **pynput** — keyboard event interception library
- **Samba (SMB/CIFS)** — network file sharing protocol for real-time log transfer
- **cifs-utils** — mounting the SMB share on the victim machine
- **Kali Linux** — used on both attacker and victim machines

---

## 🏗️ System Architecture

```
┌─────────────────────────────┐          ┌──────────────────────────────┐
│        VICTIM MACHINE       │          │       ATTACKER MACHINE       │
│      IP: <VICTIM_IP>        │          │      IP: <ATTACKER_IP>       │
│                             │          │                              │
│  keylogger.py               │  SMB/    │  /srv/logs_from_victim/      │
│  └─ captures keystrokes ────┼─ CIFS ──►│  └─ keylog.txt              │
│  └─ writes to mount point   │          │  └─ tail -f keylog.txt       │
│     /mnt/attacker_logs/     │          │     (live monitoring)        │
└─────────────────────────────┘          └──────────────────────────────┘
```

---

## ✨ Features

- ⏱️ **Timestamps** — every keystroke logged with `[HH:MM:SS]`
- 🔄 **Auto-reconnect** — if the SMB share drops, the script retries automatically
- 📁 **Log rotation** — log file capped at 5 MB with 3 rotating backups
- 🏷️ **Session markers** — clear `SESSION STARTED / SESSION ENDED` blocks per run
- 🔤 **Readable key output** — special keys shown as `SPACE`, `[ENTER]`, `[BKSP]` etc.
- 🛡️ **Graceful error handling** — OS, permission, and write errors caught without crashing

---

## 📂 Project Structure

```
csci369-keylogger-lab/
├── README.md
├── attacker/
│   └── setup_attacker.sh     # Samba share setup script
└── victim/
    ├── keylogger.py          # Main keylogger script
    └── setup_victim.sh       # Dependency install + mount script
```

---

## 🚀 Setup & Usage

### 1. Attacker Machine

```bash
git clone https://github.com/<your-username>/csci369-keylogger-lab.git
cd csci369-keylogger-lab/attacker
bash setup_attacker.sh
```

Then monitor keystrokes in real time:

```bash
tail -f /srv/logs_from_victim/keylog.txt
```

### 2. Victim Machine

Edit `setup_victim.sh` and replace `<ATTACKER_IP>` with the attacker's actual IP address, then:

```bash
cd victim
bash setup_victim.sh
python3 keylogger.py
```

---

## 📊 Sample Log Output

```
==================================================
SESSION STARTED: 2025-06-22 14:03:11
==================================================

[14:03:15] h
[14:03:15] e
[14:03:15] l
[14:03:15] l
[14:03:15] o
[14:03:16] SPACE
[14:03:17] w
[14:03:17] o
[14:03:17] r
[14:03:17] l
[14:03:17] d
[14:03:18] [ENTER]

==================================================
SESSION ENDED: 2025-06-22 14:05:44
==================================================
```

---

## 🛡️ Mitigation Recommendations

- Enforce strict access controls on all shared network directories — never allow guest write access
- Deploy an **Intrusion Detection System (IDS)** to flag unusual outbound SMB traffic
- Audit installed Python packages regularly on all endpoints
- Educate users to recognize suspicious system behavior (unexpected CPU/network spikes)
- Block SMB traffic at the network perimeter unless explicitly required

---

## 🧪 Test Cases

| Scenario | Expected Result |
|---|---|
| Victim types regular text | Characters appear in `keylog.txt` with timestamps |
| Special key pressed (e.g. Enter) | Logged as `[ENTER]` with a newline |
| SMB share disconnects | Script retries mount automatically every 10 seconds |
| Attacker removes write permission | Script fails silently, resumes when access restored |
| Log file reaches 5 MB | Automatically rotated; old log saved as `keylog.txt.1` |

---

## 📚 References

- Daniel G. Graham, *Ethical Hacking: A Hands-on Introduction to Breaking In*, No Starch Press, 2021
- [pynput documentation](https://pypi.org/project/pynput/)

---

## ⚖️ Legal Notice

This tool is provided for **educational and research purposes only**. The author is not responsible for any misuse. Always obtain explicit written permission before conducting any penetration testing on systems you do not own.
