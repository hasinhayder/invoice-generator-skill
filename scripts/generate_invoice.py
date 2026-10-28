#!/usr/bin/env python3
"""Generate a PDF invoice through the hosted Invoice API.

Usage: generate_invoice.py INVOICE.json [--logo FILE] [--out DIR]

Prints the saved PDF path on success.
Exit codes: 0 ok, 1 API rejected the request (error JSON on stderr),
            2 bad arguments or input file, 3 API unreachable.
Needs only Python 3.7+ (standard library, no packages).
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
import uuid

API = "https://invoice-api.tyrolabs.dev"
HEADERS = {"User-Agent": "invoice-generator-skill/1.0"}


def fail(msg, code):
    print(msg, file=sys.stderr)
    sys.exit(code)


def multipart(fields, files):
    boundary = uuid.uuid4().hex
    body = b""
    for name, value in fields.items():
        body += (f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n').encode()
        body += value.encode("utf-8") + b"\r\n"
    for name, (filename, content, ctype) in files.items():
        body += (f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"; '
                 f'filename="{filename}"\r\nContent-Type: {ctype}\r\n\r\n').encode()
        body += content + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    return body, f"multipart/form-data; boundary={boundary}"


def main():
    ap = argparse.ArgumentParser(description="Generate a PDF invoice via the Invoice API")
    ap.add_argument("json_file")
    ap.add_argument("--logo")
    ap.add_argument("--out", default=".")
    args = ap.parse_args()

    try:
        with open(args.json_file, encoding="utf-8-sig") as f:
            data = f.read()
        json.loads(data)
    except (OSError, ValueError) as e:
        fail(f"cannot read invoice JSON {args.json_file}: {e}", 2)

    files = {}
    if args.logo:
        try:
            with open(args.logo, "rb") as f:
                content = f.read()
        except OSError as e:
            fail(f"cannot read logo {args.logo}: {e}", 2)
        ctype = "image/png" if content.startswith(b"\x89PNG") else "image/jpeg"
        files["logo"] = (os.path.basename(args.logo), content, ctype)

    try:
        urllib.request.urlopen(urllib.request.Request(API + "/health", headers=HEADERS), timeout=20).read()
    except Exception:
        fail(f"Invoice API not reachable at {API}", 3)

    body, ctype = multipart({"data": data}, files)
    req = urllib.request.Request(API + "/invoices", data=body, method="POST",
                                 headers={**HEADERS, "Content-Type": ctype})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            pdf = resp.read()
            disp = resp.headers.get("Content-Disposition", "")
    except urllib.error.HTTPError as e:
        fail(e.read().decode("utf-8", "replace"), 1)
    except Exception as e:
        fail(f"Invoice API not reachable at {API}: {e}", 3)

    if not pdf.startswith(b"%PDF"):
        fail("response was not a PDF", 1)
    name = "invoice.pdf"
    if 'filename="' in disp:
        name = os.path.basename(disp.split('filename="', 1)[1].split('"', 1)[0]) or name
    os.makedirs(args.out, exist_ok=True)
    dest = os.path.abspath(os.path.join(args.out, name))
    with open(dest, "wb") as f:
        f.write(pdf)
    print(dest)


if __name__ == "__main__":
    main()
