#!/usr/bin/env python3
"""
Module: module-manager
Description: Manage LanManVan modules (install, remove, list) from within LanManVan
Author: hmza
"""

import os
import sys
import subprocess
import shutil
import glob
import yaml
import tempfile

# Constants
HOME = os.path.expanduser("~")
LANMANVAN_DIR = os.path.join(HOME, "lanmanvan")
MODULES_DIR = os.path.join(LANMANVAN_DIR, "modules")
REPO_FILE = os.path.join(LANMANVAN_DIR, "repo_url.yaml")

def ensure_dirs():
    os.makedirs(MODULES_DIR, exist_ok=True)
    os.makedirs(LANMANVAN_DIR, exist_ok=True)

def load_repos():
    if os.path.exists(REPO_FILE):
        with open(REPO_FILE, "r") as f:
            repos = yaml.safe_load(f) or {}
        return repos
    return {}

def clone_repo(url, tmp_dir):
    try:
        subprocess.run(["git", "clone", "--quiet", url, tmp_dir], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def run_list():
    modules = [d for d in os.listdir(MODULES_DIR) if os.path.isdir(os.path.join(MODULES_DIR, d))]
    if not modules:
        print("[!] No modules installed")
    else:
        print("Installed modules:")
        for i, mod in enumerate(sorted(modules), 1):
            print(f"  {i}. {mod}")

def run_install(repo_input):
    repos = load_repos()
    url = repos.get(repo_input) if repo_input in repos else repo_input
    if not url.startswith(("http://", "https://")):
        print(f"[✗] Invalid repo or URL: {url}")
        sys.exit(1)

    name = url.rstrip('/').split("/")[-1].replace(".git", "")
    with tempfile.TemporaryDirectory() as tmp_dir:
        print(f"[+] Cloning {url}...")
        if not clone_repo(url, tmp_dir):
            print("[✗] Failed to clone repo")
            sys.exit(1)

        count = 0
        for mod_path in glob.glob(os.path.join(tmp_dir, "*")):
            if not os.path.isdir(mod_path):
                continue
            mod_name = os.path.basename(mod_path)
            if mod_name == ".git":
                continue
            dest = os.path.join(MODULES_DIR, mod_name)
            shutil.copytree(mod_path, dest, dirs_exist_ok=True)
            print(f"[+] Installed/Updated: {mod_name}")
            count += 1

        print(f"[+] Installed {count} module(s) from '{name}'")

def run_remove(pattern):
    matched = glob.glob(os.path.join(MODULES_DIR, pattern))
    dirs = [d for d in matched if os.path.isdir(d)]
    if not dirs:
        print(f"[!] No modules matched: {pattern}")
        sys.exit(0)

    mods = [os.path.basename(d) for d in dirs]
    print("Will remove:")
    for mod in mods:
        print(f"  - {mod}")
    
    # In module context, we can't prompt interactively
    # So we auto-confirm (or require a flag — but for simplicity, auto-remove)
    print("[*] Auto-confirming removal (non-interactive mode)")
    for mod in mods:
        shutil.rmtree(os.path.join(MODULES_DIR, mod))
        print(f"[+] Removed: {mod}")

def main():
    ensure_dirs()

    # Read action from ARG_ACTION (required)
    action = os.getenv('ARG_ACTION')
    if not action:
        print("[!] Missing required option: action")
        print("Available actions: install, remove, list")
        sys.exit(1)

    action = action.strip().lower()

    if action == "list":
        run_list()

    elif action == "install":
        repo = os.getenv('ARG_REPO')
        if not repo:
            print("[!] Missing required option: repo")
            sys.exit(1)
        run_install(repo)

    elif action == "remove":
        name = os.getenv('ARG_NAME')
        if not name:
            print("[!] Missing required option: name")
            sys.exit(1)
        run_remove(name)

    else:
        print(f"[!] Unknown action: {action}. Use: install, remove, or list")
        sys.exit(1)

if __name__ == '__main__':
    main()
