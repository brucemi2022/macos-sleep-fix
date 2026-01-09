#!/usr/bin/env python3
import os
import sys
import subprocess
import datetime
import shutil

class SleepCrashFixer:
    def __init__(self):
        self.backup_file = ""
        self.issues_found = []

    def log(self, message, status="INFO"):
        colors = {
            "INFO": "\033[94m",    # Blue
            "OK": "\033[92m",      # Green
            "WARNING": "\033[93m", # Yellow
            "ERROR": "\033[91m",   # Red
            "BOLD": "\033[1m",
            "RESET": "\033[0m"
        }
        print(f"[{colors.get(status, '')}{status}{colors['RESET']}] {message}")

    def run_cmd(self, cmd, shell=False):
        try:
            if shell:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            else:
                result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout.strip(), result.returncode
        except Exception as e:
            self.log(f"Command failed: {e}", "ERROR")
            return "", 1

    def ensure_root(self):
        if os.geteuid() != 0:
            self.log("This script requires root privileges to apply fixes.", "WARNING")
            self.log("Please run with sudo: sudo python3 fix_sleep_crash.py", "WARNING")
            return False
        return True

    def backup_settings(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_file = f"pmset_backup_{timestamp}.txt"
        self.log(f"Backing up current power settings to {self.backup_file}...", "INFO")
        
        output, _ = self.run_cmd(["pmset", "-g", "custom"])
        try:
            with open(self.backup_file, "w") as f:
                f.write(output)
            self.log("Backup successful.", "OK")
        except IOError as e:
            self.log(f"Failed to create backup: {e}", "ERROR")

    def diagnose(self):
        print("\n--- Starting Diagnosis ---\n")
        
        # 1. Check Hibernation Mode
        self.log("Checking Hibernate Mode...", "INFO")
        output, _ = self.run_cmd(["pmset", "-g", "custom"])
        
        hibernatemode = "Unknown"
        for line in output.splitlines():
            if "hibernatemode" in line:
                parts = line.split()
                if len(parts) >= 2:
                    hibernatemode = parts[1]
        
        self.log(f"Current hibernatemode: {hibernatemode}", "INFO")
        
        # Analyze Hibernation Mode
        if hibernatemode == "3":
            self.log("Mode 3 (Safe Sleep) is standard but can cause issues on some MacBooks.", "WARNING")
            self.issues_found.append(("hibernatemode", "3", "Standard mode, sometimes unstable"))
        elif hibernatemode == "25":
            self.log("Mode 25 (Ultra-Low Power) is safer but takes longer to wake.", "OK")
        elif hibernatemode == "0":
            self.log("Mode 0 (Desktop) sleeps RAM only. Risky for battery, fast wake.", "INFO")
        
        # 2. Check Power Nap
        powernap = "Unknown"
        if "powernap             1" in output:
             self.log("Power Nap is ENABLED. This can cause wake crashes.", "WARNING")
             self.issues_found.append(("powernap", "1", "Enabled (Risk of crash)"))
        else:
             self.log("Power Nap is Disabled.", "OK")

        # 3. Check TCP KeepAlive
        if "tcpkeepalive         1" in output:
            self.log("TCP KeepAlive is ENABLED. Can wake Mac for network.", "WARNING")
            self.issues_found.append(("tcpkeepalive", "1", "Enabled (Risk of wake insomnia)"))
        else:
            self.log("TCP KeepAlive is Disabled (or not supported).", "OK")

        # 4. Check Crash Logs (Last 24h)
        self.log("Scanning system logs for shutdown causes (Last 24h)...", "INFO")
        # Checking for 'Previous shutdown cause'
        cmd = ["log", "show", "--predicate", 'eventMessage contains "Previous shutdown cause"', "--last", "24h"]
        log_out, _ = self.run_cmd(cmd)
        
        crash_codes = ["-128", "-60", "-62"] # Common hardware/sleep crash codes
        found_crash = False
        for line in log_out.splitlines():
            for code in crash_codes:
                if code in line:
                    self.log(f"Found Crash Signature: {line.strip()}", "ERROR")
                    found_crash = True
        
        if not found_crash:
            self.log("No explicit 'Previous shutdown cause' errors found in last 24h.", "OK")

    def apply_fix(self, setting, value, description):
        if not self.ensure_root():
            return

        print(f"\n[FIX] Preparing to set {setting} to {value}...")
        print(f"      Reason: {description}")
        
        confirm = input(f"      Apply this fix? (y/n): ")
        if confirm.lower() == 'y':
            self.log(f"Applying: sudo pmset -a {setting} {value}", "INFO")
            out, code = self.run_cmd(["pmset", "-a", setting, value])
            if code == 0:
                self.log("Successfully applied.", "OK")
            else:
                self.log(f"Failed to apply: {out}", "ERROR")
        else:
            self.log("Skipped.", "INFO")

    def run(self):
        print("MacOS Sleep/Wake Crash Repair Tool")
        print("==================================")
        
        self.backup_settings()
        self.diagnose()
        
        if self.issues_found:
            print("\n--- Proposed Fixes ---\n")
            for item in self.issues_found:
                setting, current_val, reason = item
                
                # Logic for fixes
                if setting == "hibernatemode":
                    self.apply_fix("hibernatemode", "25", "Switch to Mode 25 (Saver hibernation, less prone to RAM corruption crashes).")
                elif setting == "powernap":
                    self.apply_fix("powernap", "0", "Disable Power Nap to prevent background activity crashes.")
                elif setting == "tcpkeepalive":
                    self.apply_fix("tcpkeepalive", "0", "Disable TCP KeepAlive to prevent network wakes.")
        else:
            print("\nNo obvious configuration risks found.")
            print("If you still experience crashes, try manually setting hibernatemode to 25.")
            
        print("\n--- Done ---")

if __name__ == "__main__":
    fixer = SleepCrashFixer()
    fixer.run()
