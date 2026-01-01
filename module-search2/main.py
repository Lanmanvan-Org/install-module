#!/usr/bin/env python3
"""
Module: module-search
Simple Metasploit-style module searcher (filename & module.yaml content only)
Highlights matches with background color
"""

import os
import sys
import fnmatch
import re

# ANSI Colors - Metasploit style (red text + yellow background highlight for matches)
RED = '\033[91m'
YELLOW_BG = '\033[43m'   # Yellow background for highlighted match
BOLD = '\033[1m'
RESET = '\033[0m'
GREEN = '\033[92m'
CYAN = '\033[96m'

HOME = os.path.expanduser("~")
MODULES_DIR = os.path.join(HOME, "lanmanvan", "modules")

def highlight_match(text, keyword, case_sensitive=False):
    """Highlight exact match with yellow background"""
    if not keyword:
        return text
    flags = 0 if case_sensitive else re.IGNORECASE
    pattern = re.compile(f"({re.escape(keyword)})", flags)
    return pattern.sub(f"{YELLOW_BG}{RED}{BOLD}\\1{RESET}", text)

def search_in_module_yaml(filepath, keyword, case_sensitive=False):
    """Check only module.yaml files for keyword in content (simple match)"""
    if not os.path.basename(filepath) == "module.yaml":
        return False, None

    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                if re.search(keyword, line, flags):
                    clean_line = line.rstrip()
                    highlighted = highlight_match(clean_line, keyword, case_sensitive)
                    return True, f"line {line_num}: {highlighted}"
        return False, None
    except:
        return False, None

def main():
    keyword = os.getenv('ARG_KEYWORD')
    if not keyword:
        print(f"{RED}[!] Missing required: ARG_KEYWORD{RESET}")
        sys.exit(1)

    case_sensitive = os.getenv('ARG_CASE_SENSITIVE', 'false').lower() == 'true'

    print(f"{CYAN}[*] Searching modules for: {RED}{BOLD}{keyword}{RESET}")
    print(f"{CYAN}    Case sensitive: {case_sensitive}{RESET}")
    print(f"{CYAN}{'-' * 60}{RESET}")

    if not os.path.exists(MODULES_DIR):
        print(f"{RED}[!] Modules directory not found: {MODULES_DIR}{RESET}")
        sys.exit(0)

    found = False

    for root, dirs, files in os.walk(MODULES_DIR):
        rel_root = os.path.relpath(root, MODULES_DIR)

        # 1. Match in directory or filenames
        matched_paths = []

        # Check directory name
        dir_name = os.path.basename(root)
        dir_match = keyword if case_sensitive else keyword.lower()
        if dir_match in (dir_name if case_sensitive else dir_name.lower()):
            rel_path = rel_root if rel_root != '.' else ''
            path_display = f"{rel_path}/" if rel_path else './'
            matched_paths.append(f"{CYAN}[DIR]{RESET}  {highlight_match(path_display, keyword, case_sensitive)}")

        # Check filenames
        for f in files:
            name_match = f if case_sensitive else f.lower()
            if dir_match in name_match or fnmatch.fnmatch(f, f"*{keyword}*"):
                rel_path = os.path.join(rel_root, f) if rel_root != '.' else f
                matched_paths.append(f"{GREEN}[FILE]{RESET} {highlight_match(rel_path, keyword, case_sensitive)}")

        # Print path matches in Metasploit-like grouped style
        if matched_paths:
            found = True
            for line in matched_paths:
                print(line)
            print()  # spacing

        # 2. Search inside module.yaml only
        yaml_path = os.path.join(root, "module.yaml")
        if os.path.isfile(yaml_path):
            rel_yaml = os.path.relpath(yaml_path, MODULES_DIR)
            matched, context = search_in_module_yaml(yaml_path, keyword, case_sensitive)
            if matched:
                found = True
                print(f"{RED}[MATCH]{RESET} {rel_yaml}")
                print(f" └> {context}")
                print()

    if not found:
        print(f"{RED}[!] No modules found matching '{keyword}'{RESET}")
    else:
        print(f"{CYAN}[+] Search complete.{RESET}")

if __name__ == '__main__':
    main()
