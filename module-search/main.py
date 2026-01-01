#!/usr/bin/env python3
"""
Module: module-search
Description: Search for keywords in LanManVan modules with color-highlighted results.
"""

import os
import sys
import fnmatch
import re

# ANSI Colors
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

HOME = os.path.expanduser("~")
MODULES_DIR = os.path.join(HOME, "lanmanvan", "modules")

def is_text_file(filepath):
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
            return b'\0' not in chunk
    except:
        return False

def search_in_file(filepath, keyword, case_sensitive=False):
    flags = 0 if case_sensitive else re.IGNORECASE
    pattern = re.compile(f"({re.escape(keyword)})", flags)
    
    try:
        for encoding in ['utf-8', 'latin1', 'cp1252']:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    for line_num, line in enumerate(f, 1):
                        match = pattern.search(line)
                        if match:
                            highlighted = pattern.sub(
                                f"{Colors.RED}{Colors.BOLD}\\1{Colors.RESET}", line.rstrip()
                            )
                            return True, line_num, highlighted
                break
            except UnicodeDecodeError:
                continue
    except:
        pass
    return False, None, None

def main():
    keyword = os.getenv('ARG_KEYWORD')
    if not keyword:
        print(f"{Colors.RED}[!] Missing required option: ARG_KEYWORD{Colors.RESET}")
        sys.exit(1)

    case_sensitive = os.getenv('ARG_CASE_SENSITIVE', 'false').lower() == 'true'
    search_content = os.getenv('ARG_SEARCH_CONTENT', 'true').lower() == 'true'
    max_results = int(os.getenv('ARG_MAX_RESULTS', '100'))

    print(f"{Colors.YELLOW}[*] Searching for '{Colors.RED}{Colors.BOLD}{keyword}{Colors.RESET}{Colors.YELLOW}' in LanManVan modules...{Colors.RESET}")
    print(f"    Case sensitive: {case_sensitive} | Search content: {search_content} | Max results: {max_results}")
    print("-" * 80)

    if not os.path.exists(MODULES_DIR):
        print(f"{Colors.RED}[!] Modules directory not found: {MODULES_DIR}{Colors.RESET}")
        sys.exit(0)

    results = []
    count = 0

    for root, dirs, files in os.walk(MODULES_DIR):
        if count >= max_results:
            break

        rel_root = os.path.relpath(root, MODULES_DIR)

        # Directory matches
        for d in dirs:
            if count >= max_results:
                break
            path = os.path.join(rel_root, d) if rel_root != '.' else d
            name = d if case_sensitive else d.lower()
            key = keyword if case_sensitive else keyword.lower()

            if key in name or fnmatch.fnmatch(d, f"*{keyword}*"):
                results.append(f"{Colors.CYAN}[DIR]  {path}/{Colors.RESET}")
                count += 1

        # File name matches
        for f in files:
            if count >= max_results:
                break
            path = os.path.join(rel_root, f) if rel_root != '.' else f
            name = f if case_sensitive else f.lower()
            key = keyword if case_sensitive else keyword.lower()

            if key in name or fnmatch.fnmatch(f, f"*{keyword}*"):
                results.append(f"{Colors.GREEN}[FILE] {path}{Colors.RESET}")
                count += 1

        # Content search
        if search_content:
            for f in files:
                if count >= max_results:
                    break
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, MODULES_DIR)

                if not is_text_file(full_path):
                    continue

                found, line_num, highlighted_line = search_in_file(full_path, keyword, case_sensitive)
                if found:
                    preview = highlighted_line[:120] + ("..." if len(highlighted_line) > 120 else "")
                    results.append(f"{Colors.YELLOW}[TEXT] {rel_path} (line {line_num}){Colors.RESET}\n       └> {preview}")
                    count += 1

    # Output results
    if not results:
        print(f"{Colors.RED}[!] No matches found for '{keyword}'{Colors.RESET}")
    else:
        for res in results[:max_results]:
            print(res)
        if count > max_results:
            print(f"\n{Colors.YELLOW}[+] ... and {count - max_results} more results truncated (increase ARG_MAX_RESULTS){Colors.RESET}")

    print(f"\n{Colors.CYAN}[+] Search complete. Found {count} match(es).{Colors.RESET}")

if __name__ == '__main__':
    main()
