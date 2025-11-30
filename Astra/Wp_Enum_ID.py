#!/usr/bin/env python3
import argparse
import requests
import re
import sys

def fetch_author_enum(url, author_id):
    """Request ?author=X and extract username from redirect or page source."""
    try:
        resp = requests.get(f"{url}/?author={author_id}", allow_redirects=True, timeout=10)

        # Check redirect path
        if resp.history:
            for r in resp.history:
                loc = r.headers.get("Location", "")
                match = re.search(r"/author/([^/]+)", loc)
                if match:
                    return match.group(1)

        # Check page source like the grep pattern:
        match = re.search(r'View all posts by ([a-zA-Z0-9\.\-]+)', resp.text)
        if match:
            return match.group(1)

    except Exception as e:
        print(f"[!] Error: {e}")

    return None


def main():
    parser = argparse.ArgumentParser(description="WordPress Author Enumeration Tool")
    parser.add_argument("-u", "--url", required=True, help="Target WordPress site (example: https://example.com)")
    parser.add_argument("-r", "--range", help="Range of IDs, e.g. 1-10")

    args = parser.parse_args()

    targets = []

    # Author ID from CLI

    # Range: "1-10"
    if args.range:
        try:
            a, b = args.range.split("-")
            targets.extend(list(range(int(a), int(b) + 1)))
        except:
            print("[!] Invalid range format. Use: -r 1-10")
            sys.exit(1)

    # File input

    if not targets:
        print("[!] No author IDs or list provided.")
        sys.exit(1)

    # Run enumeration
    found = {}
    usernames = []
    for t in targets:
        print(f"[*] Scanning author: {t}")
        username = fetch_author_enum(args.url, t)
        if username:
            found[t] = username
            usernames.append(username)
            print(f"[+] Found username: {username}")
        else:
            print("[-] No username found.")

    with open("username", "w") as f:
        for user in usernames:
            f.write(user + "\n")

    print("\n=== Summary ===")
    for aid, uname in found.items():
        print(f"{aid} → {uname}")


if __name__ == "__main__":
    main()
