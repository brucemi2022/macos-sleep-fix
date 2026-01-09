# MacOS Sleep & Optimize Toolkit 🛠️

A lightweight collection of Python tools designed to diagnose performance issues and fix common **Sleep/Wake crashes** (Black Screen on Wake) on MacOS 12 Monterey and later.

## 🚀 Features

This toolkit contains two main scripts:

### 1. `fix_sleep_crash.py` (The Repair Tool)
Specifically designed to fix the "Black Screen / Frozen System" issue after waking from sleep.
*   **Diagnoses**: Checks risky power settings (`hibernatemode 3`, Power Nap, TCP KeepAlive) and scans logs for crash signatures.
*   **Fixes**: Safely switches to **Hibernate Mode 25** (Deep Sleep), disables Power Nap, and stops network wake-ups.
*   **Safety**: Automatically backs up your `pmset` settings before making changes.

### 2. `macos_troubleshoot.py` (The Optimiser)
A general system health check tool.
*   **Monitors**: CPU Load, Memory Pressure, Disk Usage, and Internet connectivity.
*   **Fixes**: One-click DNS Flush and Memory Purge.
*   **Inspects**: Finds applications preventing your Mac from sleeping (`pmset` assertions).

---

## 📦 Installation

Clone this repository to your local machine:

```bash
git clone https://github.com/brucemi2022/macos-sleep-fix.git
cd macos-sleep-fix
```

## 📖 Usage

### Fixing Sleep Crashes (Recommended First Step)
If your Mac freezes when you open the lid:

```bash
sudo python3 fix_sleep_crash.py
```
*Requires password for `sudo` to apply power setting fixes.*

### General Diagnostics
To check why your Mac is running hot or slow:

```bash
python3 macos_troubleshoot.py --check
```

To run interactive fixes (DNS/Memory):
```bash
python3 macos_troubleshoot.py --fix
```

---

## ⚙️ Requirements
*   **OS**: MacOS 12 (Monterey) or newer (Tested on MacOS 12.7.6).
*   **Python**: Python 3.x (Pre-installed on macOS).

## ⚠️ Disclaimer
This tool modifies system power settings (`pmset`). While it backs up settings and uses standard, safe commands, please use it at your own risk. Always ensure your data is backed up.
