---
name: invoice-generator
description: Create a PDF invoice from the user's invoice details (usually a text/notes file) using the Invoice Builder API. Use when the user asks to create, generate, build, or make an invoice or bill, or points to a file containing invoice information.
---

# Invoice Generator

Turns the user's free-form invoice notes into a PDF by calling the Invoice Builder API.
Full field reference: `reference/schema.md`. Example input: `reference/example-input.txt`.

API: `https://invoice-api.tyrolabs.dev` (hosted; no setup or token needed).

## Workflow

### 1. Read the input
Read the text file the user points to (or the details pasted in chat). If no file or details are given, ask where they are.

### 2. Extract into the JSON schema
Map the text to the fields in `reference/schema.md`:
- biller (who is sending the invoice) and client (who pays): name + address required
- line items: `description`, `quantity`, `unit_price`. Convert "3 hours at 80/hour" → quantity 3, unit_price 80. If only a line total is given, use quantity 1.
- `tax` and `discount`: decide `percent` vs `amount` explicitly ("10%" → percent, "$50 off" → amount)
- `issue_date`, `due_date` as `YYYY-MM-DD`. Resolve relative terms ("due in 30 days") from the issue date. Today's date comes from the environment.
- optional: invoice number, currency, notes, payment details, logo path

**Never invent** names, addresses, prices, quantities or dates. Optional things that are simply absent (tax, discount, notes) are left out.

### 3. Ask about what is missing — before calling the API
Required: biller name+address, client name+address, ≥1 item with quantity and price, issue date, due date.
Also confirm, in the **same single message**:
- any required field that is missing or ambiguous (e.g. unclear whether a number is % or an amount)
- the **template** (offer the list from `GET $API/templates`: classic, modern, minimal, bold, elegant, compact; default classic if the user has no preference)
- whether they want a **logo** (ask for a PNG/JPEG path; skip if they say no)

Do not ask about things the file already answers. Wait for the reply, then proceed.

### 4. Generate
1. Write the JSON to a temp file (not into the user's project unless asked).
2. Run the helper (it checks the API is up, posts, saves the PDF, validates `%PDF`). `scripts/` is in **this skill's directory**, not the user's project, so call it by its absolute path (e.g. `~/.commandcode/skills/invoice-generator/scripts/generate_invoice.sh`, `~/.claude/skills/...`, wherever this SKILL.md was loaded from) and keep the current directory unchanged:
   ```bash
   <skill-dir>/scripts/generate_invoice.sh /tmp/invoice.json --logo /path/logo.png --out .
   ```
   Omit `--logo` if none. The PDF is saved as `invoice-<number>.pdf` in `--out` (default: current directory; use the directory the user's file is in if sensible).
3. If exit code 3: the API is unreachable. Check `curl -s https://invoice-api.tyrolabs.dev/health` once more; if it is still down, tell the user the server is not responding and stop.
4. If the API returns HTTP 422: the error JSON lists `loc`/`msg` per field. Fix what you can from the input; otherwise ask the user about those fields and retry.

Equivalent raw call:
```bash
curl -fS -o invoice.pdf -F 'data=<invoice.json' -F 'logo=@logo.png' https://invoice-api.tyrolabs.dev/invoices
```

### 5. Report
Tell the user the absolute path of the PDF, the template used, and the computed total (subtotal, discount, tax) so they can sanity-check. Offer to regenerate in another template.
