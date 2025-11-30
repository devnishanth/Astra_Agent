import argparse
import requests
import sys


def normalize_url(u):
    if not u.startswith('http'):
        u = 'http://' + u
    return u.rstrip('/')


def probe_rest_list(url, timeout=10):
    path = f"{url}/wp-json/wp/v2/users?per_page=100"
    try:
        r = requests.get(path, timeout=timeout)
        if 'application/json' in r.headers.get('Content-Type',''):
            return r.json()
        return None
    except Exception as e:
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument('-u','--url', required=True)
    args = p.parse_args()
    u = normalize_url(args.url)
    data = probe_rest_list(u)

    usernames = []
    if not data:
        print('[-] No JSON returned or endpoint blocked')
        sys.exit(0)
    for item in data:
        user=item.get('slug') or item.get('name')
        print(user)
        usernames.append(user)
    with open("username", "w") as f:
        for user in usernames:
            f.write(user + "\n")

if __name__=='__main__':
    main()

