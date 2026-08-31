#!/usr/bin/env python3
"""Inject Billing Validation demo scenario (PO 4500198872) into static Orbis JSON."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "api"

PO = "4500198872"
SO = "SO-2026-07741"
DR = "DN-88231"
CONTRACT = "MSA-NW-APX-2024-017"
DRAFT = "BD-2026-5599"
INVOICE = "APX-INV-2026-05590"
CUSTOMER_ID = "C-200114"
GENERATED = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

PAYMENT_TERMS = (
    "Net 45 days from invoice date; 2% discount if paid within 10 days"
)
CUSTOMER_NAME = "Nordwind Turbines GmbH"
BILL_TO = (
    "Accounts Payable, Nordwind Turbines GmbH, Postfach 44, "
    "20095 Hamburg, Germany"
)
SHIP_TO = (
    "Nordwind Turbines GmbH, Plant 2 Goods-In, Ottensener Str. 9, "
    "22765 Hamburg, Germany"
)

LINES = [
    {
        "line": 1,
        "item_number": "AX-PMP-320",
        "item_description": "Centrifugal Pump Assembly, 320mm impeller, SS316",
        "item_class": "ROTATING-EQUIP",
        "uom": "EA",
        "quantity_to_bill": 12,
        "unit_price": 1850.0,
        "line_amount": 22200.0,
    },
    {
        "line": 2,
        "item_number": "AX-SEAL-88",
        "item_description": "Mechanical Seal Kit, tungsten carbide faces",
        "item_class": "SPARES",
        "uom": "EA",
        "quantity_to_bill": 24,
        "unit_price": 145.0,
        "line_amount": 3480.0,
    },
    {
        "line": 3,
        "item_number": "AX-BRG-540",
        "item_description": "High-load Bearing Set, sealed, Class 5",
        "item_class": "SPARES",
        "uom": "SET",
        "quantity_to_bill": 12,
        "unit_price": 410.0,
        "line_amount": 4920.0,
    },
    {
        "line": 4,
        "item_number": "AX-GSKT-12",
        "item_description": "Gasket & Fastener Pack (per pump)",
        "item_class": "SPARES",
        "uom": "PK",
        "quantity_to_bill": 12,
        "unit_price": 62.5,
        "line_amount": 750.0,
    },
]

GOODS_SUBTOTAL = 31350.0
FREIGHT_TOTAL = 480.0
TOTAL_PAYABLE = 31830.0

HEADER = {
    "draft_number": DRAFT,
    "proposed_invoice_number": INVOICE,
    "status": "PENDING_VALIDATION",
    "sales_order": SO,
    "customer_po_number": PO,
    "contract_number": CONTRACT,
    "delivery_number": DR,
    "customer_id": CUSTOMER_ID,
    "invoice_date": "2026-06-20",
    "prepared_on": "2026-06-18",
    "prepared_by": "BPO O2C Billing Desk",
    "billing_type": "Delivery-based (goods)",
    "currency": "EUR",
    "payment_terms": PAYMENT_TERMS,
    "incoterms": "DAP Hamburg Plant 2 (Incoterms 2020)",
    "tax_code": "EU-RC-0",
    "tax_treatment": "REVERSE_CHARGE",
    "tax_rate": 0.0,
    "customer_tax_registration": "DE 118 456 221",
    "exemption_certificate": None,
    "operating_unit": "GEAM_OU_EUR_IND_EU_TRB_WBO",
    "legal_entity": "Apex Precision Manufacturing Inc.",
    "notes": "Billing Validation demo — Nordwind PO 4500198872 / DR DN-88231.",
    "customer_name": CUSTOMER_NAME,
    "order_status": "AWAITING_BILLING",
    "order_invoiced_date": None,
    "order_on_hold": False,
    "bill_to_name": CUSTOMER_NAME,
    "bill_to_site_use_id": "BT-DEMO-NW-1",
    "bill_to_address_1": "Accounts Payable",
    "bill_to_address_2": "Nordwind Turbines GmbH",
    "bill_to_address_3": "-",
    "bill_to_address_4": "Postfach 44",
    "bill_to_city": "20095 Hamburg",
    "bill_to_state": "",
    "bill_to_postal_code": "",
    "bill_to_country": "Germany",
    "ship_to_name": CUSTOMER_NAME,
    "ship_to_site_use_id": "ST-DEMO-NW-1",
    "ship_to_address_1": "Nordwind Turbines GmbH",
    "ship_to_address_2": "Plant 2 Goods-In",
    "ship_to_address_3": "-",
    "ship_to_address_4": "Ottensener Str. 9",
    "ship_to_city": "22765 Hamburg",
    "ship_to_state": "",
    "ship_to_postal_code": "",
    "ship_to_country": "Germany",
    "goods_subtotal": GOODS_SUBTOTAL,
    "surcharge_total": 0.0,
    "freight_total": FREIGHT_TOTAL,
    "net_subtotal": TOTAL_PAYABLE,
    "tax_amount": 0.0,
    "total_payable": TOTAL_PAYABLE,
}


def flat_rows() -> list[dict]:
    rows = []
    for line in LINES:
        rows.append(
            {
                **HEADER,
                **line,
                "line_type": "GOODS",
                "line_tax_code": "EU-RC-0",
                "line_tax_rate": 0.0,
                "line_tax_amount": 0.0,
                "line_total_incl_tax": line["line_amount"],
                "line_source": "DELIVERY",
                "line_source_reference": DR,
                "hs_code": "8413.70",
                "taxable_item": True,
                "ref_item_list_price": line["unit_price"],
                "ref_contract_price": line["unit_price"],
                "ref_contract_discount_pct": 0.0,
                "ref_ordered_quantity": line["quantity_to_bill"],
                "ref_shipped_quantity": line["quantity_to_bill"],
                "ref_backordered_quantity": 0,
                "ref_order_unit_selling_price": line["unit_price"],
                "ref_order_extended_amount": line["line_amount"],
                "ref_contract_payment_terms": PAYMENT_TERMS,
                "ref_contract_incoterms": "DAP Hamburg Plant 2 (Incoterms 2020)",
                "ref_contract_currency": "EUR",
                "ref_contract_freight_terms": "PREPAID_AND_ADD",
                "ref_contract_surcharge_allowed": False,
                "ref_contract_po_required": True,
                "ref_contract_price_tolerance_pct": 0.0,
                "ref_contract_qty_tolerance_pct": 2.0,
                "ref_customer_tax_code": "EU-RC-0",
                "ref_customer_tax_rate": 0.0,
                "ref_customer_tax_treatment": "REVERSE_CHARGE",
                "ref_po_valid_to": "2027-05-31",
                "ref_po_status": "OPEN",
                "ref_po_amount_limit": 35000.0,
                "ref_proof_of_delivery_date": "2026-06-18",
            }
        )
    return rows


def envelope(object_name: str, data: list | dict, **extra) -> dict:
    payload = {
        "source_system": "ORBIS ERP",
        "object": object_name,
        "generated_at": GENERATED,
        **extra,
    }
    if isinstance(data, list):
        payload["count"] = len(data)
        payload["data"] = data
    else:
        payload["data"] = data
    return payload


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def prepend_row(rows: list[dict], row: dict, key: str) -> None:
    rows[:] = [row] + [r for r in rows if r.get(key) != row.get(key)]


def main() -> None:
    flat = flat_rows()
    flat_note = (
        "One row per draft line with every header field denormalised onto it. "
        "Columns prefixed ref_ are joined from the source objects."
    )

    save_json(
        API / "billing-draft-lines" / f"{PO}.json",
        envelope("Billing Draft Line (flat)", flat, note=flat_note),
    )

    all_flat_path = API / "billing-draft-lines.json"
    all_flat = load_json(all_flat_path)
    all_flat["data"] = flat + [
        r for r in all_flat["data"] if r.get("customer_po_number") != PO
    ]
    all_flat["count"] = len(all_flat["data"])
    all_flat["generated_at"] = GENERATED
    save_json(all_flat_path, all_flat)

    draft_header = {
        **{k: v for k, v in HEADER.items() if not k.startswith(("bill_to_", "ship_to_"))},
        "line_count": len(LINES),
        "goods_line_count": len(LINES),
        "total_quantity": sum(l["quantity_to_bill"] for l in LINES),
        "bill_to_name": HEADER["bill_to_name"],
        "bill_to_city": "Hamburg",
        "bill_to_state": "HH",
        "bill_to_postal_code": "20095",
        "ship_to_name": HEADER["ship_to_name"],
        "ship_to_city": "Hamburg",
        "ship_to_state": "HH",
        "ship_to_postal_code": "22765",
    }

    drafts_path = API / "billing-drafts.json"
    drafts = load_json(drafts_path)
    prepend_row(drafts["data"], draft_header, "draft_number")
    drafts["count"] = len(drafts["data"])
    drafts["generated_at"] = GENERATED
    save_json(drafts_path, drafts)

    draft_detail = {
        **HEADER,
        "bill_to": {
            "site_use_id": HEADER["bill_to_site_use_id"],
            "name": CUSTOMER_NAME,
            "address_1": "Accounts Payable",
            "address_2": "Nordwind Turbines GmbH",
            "address_3": "-",
            "address_4": "Postfach 44",
            "city": "Hamburg",
            "state": "HH",
            "postal_code": "20095",
            "country": "DE",
        },
        "ship_to": {
            "site_use_id": HEADER["ship_to_site_use_id"],
            "name": CUSTOMER_NAME,
            "address_1": "Nordwind Turbines GmbH",
            "address_2": "Plant 2 Goods-In",
            "address_3": "-",
            "address_4": "Ottensener Str. 9",
            "city": "Hamburg",
            "state": "HH",
            "postal_code": "22765",
            "country": "DE",
        },
        "lines": [
            {
                "line": l["line"],
                "item_number": l["item_number"],
                "description": l["item_description"],
                "line_type": "GOODS",
                "uom": l["uom"],
                "quantity_to_bill": l["quantity_to_bill"],
                "unit_price": l["unit_price"],
                "amount": l["line_amount"],
                "tax_code": "EU-RC-0",
                "tax_rate": 0.0,
                "tax_amount": 0.0,
                "source": "DELIVERY",
                "source_reference": DR,
            }
            for l in LINES
        ],
        "totals": {
            "goods_subtotal": GOODS_SUBTOTAL,
            "surcharge_total": 0.0,
            "freight_total": FREIGHT_TOTAL,
            "tax_amount": 0.0,
            "total_payable": TOTAL_PAYABLE,
            "currency": "EUR",
        },
        "documents": [],
    }
    save_json(
        API / "billing-drafts" / f"{DRAFT}.json",
        {"source_system": "ORBIS ERP", "object": "Billing Draft", "data": draft_detail},
    )

    po_row = {
        "po_number": PO,
        "customer_id": CUSTOMER_ID,
        "customer_name": CUSTOMER_NAME,
        "contract_number": CONTRACT,
        "po_date": "2026-05-12",
        "valid_to": "2027-05-31",
        "status": "OPEN",
        "currency": "EUR",
        "po_amount_limit": 35000.0,
        "released_amount": TOTAL_PAYABLE,
        "sales_order": SO,
        "buyer_name": "Katrin Bauer",
    }
    pos = load_json(API / "purchase-orders.json")
    prepend_row(pos["data"], po_row, "po_number")
    pos["count"] = len(pos["data"])
    save_json(API / "purchase-orders.json", pos)

    po_detail = {
        "po_number": PO,
        "customer_id": CUSTOMER_ID,
        "customer_name": CUSTOMER_NAME,
        "contract_number": CONTRACT,
        "po_date": "2026-05-12",
        "valid_from": "2026-05-12",
        "valid_to": "2027-05-31",
        "status": "OPEN",
        "currency": "EUR",
        "po_amount_limit": 35000.0,
        "released_amount": TOTAL_PAYABLE,
        "buyer_name": "Katrin Bauer",
        "buyer_email": "k.bauer@nordwind-turbines.de",
        "payment_terms": PAYMENT_TERMS,
        "incoterms": "DAP Hamburg Plant 2 (Incoterms 2020)",
        "sales_order": SO,
        "lines": [
            {
                "po_line": l["line"],
                "item_number": l["item_number"],
                "description": l["item_description"],
                "uom": l["uom"],
                "quantity": l["quantity_to_bill"],
                "unit_price": l["unit_price"],
                "amount": l["line_amount"],
            }
            for l in LINES
        ],
        "document_id": f"DOC-PO-{PO}",
        "documents": [],
    }
    save_json(
        API / "purchase-orders" / f"{PO}.json",
        {"source_system": "ORBIS ERP", "object": "Customer Purchase Order", "data": po_detail},
    )

    so_row = {
        "order_number": SO,
        "customer_po_number": PO,
        "contract_number": CONTRACT,
        "customer_id": CUSTOMER_ID,
        "status": "AWAITING_BILLING",
        "entered_date": "2026-05-13",
        "invoiced_date": None,
        "delivery_number": DR,
        "payment_terms": PAYMENT_TERMS,
        "currency": "EUR",
        "order_total": TOTAL_PAYABLE,
        "operating_unit": HEADER["operating_unit"],
        "customer_name_bill_to": CUSTOMER_NAME,
        "customer_name_ship_to": CUSTOMER_NAME,
        "state_bill_to": "HH",
        "state_ship_to": "HH",
        "on_hold": False,
        "line_count": len(LINES),
        "transaction_originator": "Order Management, Apex Precision",
    }
    sos = load_json(API / "sales-orders.json")
    prepend_row(sos["data"], so_row, "order_number")
    sos["count"] = len(sos["data"])
    save_json(API / "sales-orders.json", sos)

    so_detail = {
        "order_number": SO,
        "customer_po_number": PO,
        "contract_number": CONTRACT,
        "operating_unit": HEADER["operating_unit"],
        "legal_entity": HEADER["legal_entity"],
        "order_type": "Standard Order",
        "order_source": "Manual Entry",
        "status": "AWAITING_BILLING",
        "entered_date": "2026-05-13",
        "booked_date": "2026-05-13",
        "requested_ship_date": "2026-06-18",
        "invoiced_date": None,
        "transaction_originator": "Order Management, Apex Precision",
        "caller_name": "Katrin Bauer",
        "caller_email": "k.bauer@nordwind-turbines.de",
        "caller_phone": "+49 40 4711 220",
        "customer_id": CUSTOMER_ID,
        "customer_name_bill_to": CUSTOMER_NAME,
        "customer_name_ship_to": CUSTOMER_NAME,
        "bill_to": draft_detail["bill_to"],
        "ship_to": draft_detail["ship_to"],
        "currency": "EUR",
        "payment_terms": PAYMENT_TERMS,
        "incoterms": "DAP Hamburg Plant 2 (Incoterms 2020)",
        "freight_terms": "PREPAID_AND_ADD",
        "tax_code": "EU-RC-0",
        "tax_treatment": "REVERSE_CHARGE",
        "tax_registration_customer": "DE 118 456 221",
        "exemption_certificate": None,
        "price_list": "EU-IND-2026",
        "delivery_number": DR,
        "holds": [],
        "lines": [
            {
                "line": l["line"],
                "item_number": l["item_number"],
                "description": l["item_description"],
                "line_type": "GOODS",
                "uom": l["uom"],
                "ordered_quantity": l["quantity_to_bill"],
                "shipped_quantity": l["quantity_to_bill"],
                "unit_list_price": l["unit_price"],
                "unit_selling_price": l["unit_price"],
                "discount_pct": 0.0,
                "extended_amount": l["line_amount"],
                "tax_code": "EU-RC-0",
                "tax_rate": 0.0,
                "tax_amount": 0.0,
                "gl_account": "4100-PRODUCT-REVENUE",
            }
            for l in LINES
        ],
        "goods_total": GOODS_SUBTOTAL,
        "surcharge_total": 0.0,
        "freight_amount": FREIGHT_TOTAL,
        "tax_amount": 0.0,
        "order_total": TOTAL_PAYABLE,
        "documents": [],
    }
    save_json(
        API / "sales-orders" / f"{SO}.json",
        {"source_system": "ORBIS ERP", "object": "Sales Order", "data": so_detail},
    )

    dr_row = {
        "delivery_number": DR,
        "sales_order": SO,
        "customer_id": CUSTOMER_ID,
        "ship_date": "2026-06-18",
        "carrier": "DHL Freight",
        "waybill": "DHL-DEMO-88231",
        "proof_of_delivery_date": "2026-06-18",
        "incoterms": "DAP Hamburg Plant 2 (Incoterms 2020)",
    }
    deliveries = load_json(API / "deliveries.json")
    prepend_row(deliveries["data"], dr_row, "delivery_number")
    deliveries["count"] = len(deliveries["data"])
    save_json(API / "deliveries.json", deliveries)

    dr_detail = {
        **dr_row,
        "lines": [
            {
                "line": l["line"],
                "item_number": l["item_number"],
                "uom": l["uom"],
                "shipped_quantity": l["quantity_to_bill"],
                "ordered_quantity": l["quantity_to_bill"],
                "backordered_quantity": 0,
            }
            for l in LINES
        ],
        "documents": [],
    }
    save_json(
        API / "deliveries" / f"{DR}.json",
        {"source_system": "ORBIS ERP", "object": "Delivery", "data": dr_detail},
    )

    contract_row = {
        "contract_number": CONTRACT,
        "contract_type": "MSA",
        "customer_id": CUSTOMER_ID,
        "status": "ACTIVE",
        "effective_date": "2024-06-01",
        "expiry_date": "2027-05-31",
        "currency": "EUR",
        "payment_terms": PAYMENT_TERMS + ". Invoices payable in EUR.",
        "incoterms": "All deliveries are made DAP Hamburg Plant 2 (Incoterms 2020). "
        "Title and risk pass to the Buyer on delivery at the named place. "
        "Freight for DAP deliveries is billable to the Buyer at cost.",
        "discount_pct": 0.0,
        "qty_tolerance_pct": 2.0,
    }
    contracts = load_json(API / "contracts.json")
    prepend_row(contracts["data"], contract_row, "contract_number")
    contracts["count"] = len(contracts["data"])
    save_json(API / "contracts.json", contracts)

    contract_detail = deepcopy(contract_row)
    contract_detail.update(
        {
            "price_list": "EU-IND-2026",
            "freight_terms": "PREPAID_AND_ADD",
            "billing_method": "DELIVERY_BASED",
            "tax_treatment": "REVERSE_CHARGE",
            "surcharge_allowed": False,
            "po_required": True,
            "price_tolerance_pct": 0.0,
            "price_list_lines": [
                {
                    "item_number": l["item_number"],
                    "uom": l["uom"],
                    "list_price": l["unit_price"],
                    "discount_pct": 0.0,
                    "contract_price": l["unit_price"],
                    "currency": "EUR",
                }
                for l in LINES
            ],
            "orders": [SO],
            "documents": [],
        }
    )
    save_json(
        API / "contracts" / f"{CONTRACT}.json",
        {"source_system": "ORBIS ERP", "object": "Contract", "data": contract_detail},
    )

    pkg_index_row = {
        "draft_number": DRAFT,
        "url": f"api/validation-packages/{DRAFT}.json",
        "sales_order": SO,
        "customer_id": CUSTOMER_ID,
        "total_payable": TOTAL_PAYABLE,
        "currency": "EUR",
        "document_count": 0,
    }
    pkgs = load_json(API / "validation-packages.json")
    prepend_row(pkgs["data"], pkg_index_row, "draft_number")
    pkgs["count"] = len(pkgs["data"])
    save_json(API / "validation-packages.json", pkgs)

    index = load_json(API / "index.json")
    index["generated_at"] = GENERATED
    counts = index.setdefault("counts", {})
    counts["purchase_orders"] = len(pos["data"])
    counts["sales_orders"] = len(sos["data"])
    counts["deliveries"] = len(deliveries["data"])
    counts["billing_drafts"] = len(drafts["data"])
    save_json(API / "index.json", index)

    print(f"Injected demo PO {PO} ({len(flat)} ERP lines)")
    print(f"  Per-PO API: api/billing-draft-lines/{PO}.json")
    print(f"  Bill-to maps to: {BILL_TO}")
    print(f"  Ship-to maps to: {SHIP_TO}")


if __name__ == "__main__":
    main()
