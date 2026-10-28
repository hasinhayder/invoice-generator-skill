#!/usr/bin/env bash
# Usage: generate_invoice.sh <invoice.json> [--logo FILE] [--out DIR]
# API:   https://invoice-api.tyrolabs.dev
# Prints the saved PDF path on success; prints API error JSON to stderr and exits 1 otherwise.
set -euo pipefail

API="https://invoice-api.tyrolabs.dev"
json="${1:?usage: generate_invoice.sh <invoice.json> [--logo FILE] [--out DIR]}"; shift
logo=""; out="."
while [ $# -gt 0 ]; do
  case "$1" in
    --logo) logo="$2"; shift 2 ;;
    --out) out="$2"; shift 2 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

[ -f "$json" ] || { echo "no such file: $json" >&2; exit 2; }
curl -fsS "$API/health" >/dev/null 2>&1 || { echo "Invoice API not reachable at $API" >&2; exit 3; }

mkdir -p "$out"
tmp_pdf="$(mktemp)"; tmp_hdr="$(mktemp)"
args=(-sS -o "$tmp_pdf" -D "$tmp_hdr" -w '%{http_code}' -F "data=<$json")
[ -n "$logo" ] && args+=(-F "logo=@$logo")
code="$(curl "${args[@]}" "$API/invoices")"

if [ "$code" != "200" ]; then
  cat "$tmp_pdf" >&2; echo >&2
  rm -f "$tmp_pdf" "$tmp_hdr"; exit 1
fi
name="$(sed -n 's/^[Cc]ontent-[Dd]isposition:.*filename="\([^"]*\)".*/\1/p' "$tmp_hdr" | tr -d '\r')"
dest="$out/${name:-invoice.pdf}"
mv "$tmp_pdf" "$dest"; rm -f "$tmp_hdr"
head -c 4 "$dest" | grep -q '%PDF' || { echo "response was not a PDF" >&2; exit 1; }
echo "$dest"
