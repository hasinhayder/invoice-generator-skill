# Invoice API JSON schema

`POST {API}/invoices` (multipart): field `data` = this JSON, optional field `logo` = PNG/JPEG file (≤ 2 MB).

| Field | Req | Notes |
|---|---|---|
| `template` | no | `professional` (default), `studio`, `sidebar`, `classic`, `modern`, `minimal`, `bold`, `elegant`, `compact` |
| `invoice_number` | no | auto-generated if omitted |
| `currency` | no | symbol or code, default `$`. Use `USD`, `EUR`, `€`, `£`. Non-Latin symbols (₹, ৳) are rendered as codes (INR, BDT); prefer codes |
| `biller` | yes | `{name, address, email?, phone?, tax_id?}`; address may contain `\n` |
| `client` | yes | `{name, address, email?, phone?, tax_id?}` |
| `items` | yes | ≥1 of `{description, quantity (>0), unit_price (≥0)}` — unit price, not line total |
| `tax` | no | `{type: "percent"\|"amount", value}`; default none. Applied after discount |
| `discount` | no | same shape; applied to subtotal |
| `issue_date` | yes | `YYYY-MM-DD` |
| `due_date` | yes | `YYYY-MM-DD`, not before issue_date |
| `notes` | no | free text |
| `payment_details` | no | bank/payment instructions |

Totals are computed by the server: subtotal → minus discount → plus tax → total.

Errors: HTTP 422 with `detail: [{loc, msg}]` — map `loc` to the missing/invalid field and ask the user.

Example:
```json
{
  "template": "professional",
  "currency": "USD",
  "biller": {"name": "Acme Studio", "address": "1 Main St\nDhaka 1207", "email": "hi@acme.test"},
  "client": {"name": "Globex Ltd", "address": "99 Long Road\nLondon", "tax_id": "GB123"},
  "items": [
    {"description": "Website redesign", "quantity": 1, "unit_price": 2500},
    {"description": "Hosting setup (hours)", "quantity": 3, "unit_price": 80}
  ],
  "tax": {"type": "percent", "value": 20},
  "discount": {"type": "percent", "value": 10},
  "issue_date": "2026-10-27",
  "due_date": "2026-11-26",
  "payment_details": "Bank transfer: IBAN GB00 0000 0000"
}
```
