# ORBIS — Order & Revenue Billing Information System

A dummy SAP/Oracle-style pre-billing system for a **billing validation POC**. It holds everything an
invoice is assembled from, plus source documents, plus the pre-invoice **billing drafts** your
validation tool is meant to check.

| Path | What it is |
|---|---|
| `erp/` | ORBIS ERP — transactional UI (drafts, orders, contracts, POs, deliveries, masters, documents) |
| `analytics/` | ORBIS Insight — Qlik-style analytics sheet with governing selections |
| `api/` | Static JSON API, served by GitHub Pages with `Access-Control-Allow-Origin: *` |
| `docs/` | 80 source PDFs: contracts, customer POs, order acknowledgements, delivery notes |
| `sql/` | MySQL schema + seed with identical data |
| `generate.py` | Regenerates everything, deterministically |

## Deploy

```bash
git init && git add . && git commit -m "ORBIS pre-billing system"
git branch -M main
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```

Settings → Pages → Deploy from a branch → `main` / `(root)`.

Locally: `python3 -m http.server 8080` then open <http://localhost:8080>. `file://` will not work —
the apps fetch JSON.

## Data model

```
customer ──< contract ──< price_list
    │           │
    │           ├──< purchase_order ──< po_line
    │           │
    └──────────< sales_order ──< so_line
                    │
                    ├──< delivery ──< delivery_line      (what actually shipped)
                    │
                    └──< billing_draft ──< billing_draft_line   (what we intend to invoice)
```

Join keys:

| From | To |
|---|---|
| `billing_draft.sales_order` | `sales_order.order_number` |
| `sales_order.customer_po_number` | `purchase_order.po_number` |
| `sales_order.contract_number` | `contract.contract_number` |
| `sales_order.delivery_number` | `delivery.delivery_number` |
| `draft line item + contract` | `price_list.contract_price` |
| `billing_draft.tax_code` | `tax_rule.tax_code` |

## Billing draft shape

The draft is a header with lines, so it is published two ways:

| Endpoint | Shape | Use it for |
|---|---|---|
| `api/billing-drafts.json` | one row per draft, ~50 header fields including full bill-to and ship-to blocks, all four subtotals, tax registration and exemption certificate, order status and invoiced date | header-level checks, worklists |
| `api/billing-drafts/{draft_number}.json` | header plus nested `lines[]` and `totals` | working a single draft |
| `api/billing-draft-lines.json` | **one row per draft line, 93 columns** — every header field denormalised onto each line, plus `ref_` columns | field-by-field validation, CSV export, spreadsheet review |

Columns prefixed `ref_` on the flat endpoint are joined from the source objects — contract price and
discount, ordered and shipped quantity, PO validity and authorised value, contract payment terms,
incoterms, currency, freight terms, surcharge permission, tolerances, expected tax code/rate/treatment,
and proof of delivery date. They are what the draft *should* agree with. Drop them if you would rather
your validator fetch the truth itself from the source endpoints.

## Contents

10 customers across two operating units (US life sciences in USD, EU industrial in EUR),
10 contracts, 24 customer POs, 24 sales orders (90 lines), 22 deliveries, 20 billing drafts,
80 PDFs, 24 validated invoice fields, 14 seeded defects.

Line types are separated deliberately — `GOODS`, `SURCHARGE`, `FREIGHT` — because whether a
surcharge or freight line may be billed at all is a contract question, not a pricing question.

## What makes this useful for validation

`api/field-map.json` is the specification for your rule set: each invoice field, its authoritative
source, the precedence order when sources disagree, and the match rule.

| Field group | Authoritative source |
|---|---|
| Unit price, discount | `contract.price_list` → contract price, within `price_tolerance_pct` |
| Quantity billed | `delivery.shipped_quantity` — never the ordered quantity |
| PO number, validity, authorised value | `purchase_order` |
| Payment terms, incoterms, currency, billing rule | `contract` |
| Freight billable? Surcharge billable? | `contract.freight_terms`, `contract.surcharge_allowed` |
| Tax code, rate, treatment | `tax_rules` + `customer.tax_code` |
| Bill-to / ship-to | `customer` master sites |
| Duplicate check | `sales_order.invoiced_date` must be null |

## Seeded defects (answer key: `api/mismatches.json`)

| Finding | Draft | Severity |
|---|---|---|
| `price_off_contract` | BD-2026-5501 | critical |
| `qty_exceeds_shipped` | BD-2026-5503 | critical |
| `po_expired` | BD-2026-5505 | high |
| `po_limit_exceeded` | BD-2026-5506 | high |
| `missing_po` | BD-2026-5507 | high |
| `tax_treatment_wrong` | BD-2026-5509 | critical |
| `bill_to_address_stale` | BD-2026-5510 | medium |
| `surcharge_not_allowed` | BD-2026-5511 | high |
| `freight_not_billable` | BD-2026-5512 | high |
| `payment_terms_off_contract` | BD-2026-5513 | medium |
| `currency_mismatch` | BD-2026-5515 | critical |
| `total_math_error` | BD-2026-5516 | critical |
| `billing_before_delivery` | BD-2026-5517 | medium |
| `duplicate_billing` | BD-2026-5519 | critical |

Negative controls are in there on purpose: drafts BD-2026-5514 and BD-2026-5518 bill **less** than the
ordered quantity because those orders shipped partially. A rule that compares billed quantity to
*ordered* quantity will flag them and lose precision; comparing to *shipped* quantity is correct.

## Regenerating

```bash
pip install reportlab
python3 generate.py
```

Edit `DEFECT_PLAN` to change which drafts break and how. Everything else — JSON, PDFs, SQL — follows.

## Connecting your validation tool

Read-only JSON over static hosting. No auth, no keys, no rate limits, and GitHub Pages returns
`Access-Control-Allow-Origin: *` on every file including the PDFs, so browser clients work too.

### Recommended entry point

`api/validation-packages/{draft_number}.json` returns a billing draft **with every upstream object
already joined** — sales order, purchase order, contract with its price list, delivery, customer,
tax rules, item master, and the URLs of all four source PDFs. One request instead of six.

```python
import requests

BASE = "https://<you>.github.io/<repo>"

# 1. list the drafts that need validating
drafts = requests.get(f"{BASE}/api/validation-packages.json").json()["data"]

# 2. pull one complete package
pkg = requests.get(f"{BASE}/api/validation-packages/{drafts[0]['draft_number']}.json").json()

draft    = pkg["billing_draft"]     # what we intend to invoice
order    = pkg["sales_order"]       # what was ordered, plus holds and invoiced_date
po       = pkg["purchase_order"]    # validity window and authorised value
contract = pkg["contract"]          # terms, tolerances, price_list_lines
delivery = pkg["delivery"]          # shipped and backordered quantities
customer = pkg["customer"]          # bill-to / ship-to sites, tax registration
taxes    = pkg["tax_rules"]         # expected rate and treatment
items    = pkg["items"]             # list price, UOM, taxability per item on the draft

# 3. fetch a source document
pdf = requests.get(f"{BASE}/{pkg['documents'][0]['url']}").content
```

### Other access patterns

| Need | Endpoint |
|---|---|
| Pull the whole model once and validate offline | `api/bundle.json` (~340 KB, every object) |
| Introspect the API | `api/openapi.json` (OpenAPI 3.1) |
| Discover paths, join keys, counts | `api/index.json` |
| Every draft line as a flat table (one row per line, header denormalised) | `api/billing-draft-lines.json` |
| Individual objects | `api/{object}.json` and `api/{object}/{key}.json` |
| Source PDFs | `docs/{file_name}` — URLs are listed in `api/documents.json` |

Document URLs are relative to the site root; join them with your base URL.

### Caching

Files are static, so ETags and `If-None-Match` work normally. The dataset only changes when you
re-run `generate.py` and push, so a client can cache aggressively.
