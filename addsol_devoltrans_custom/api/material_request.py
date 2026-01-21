# addsol_devoltrans_custom/api/material_request.py

import frappe
from erpnext.manufacturing.doctype.bom.bom import get_bom_items_as_dict

@frappe.whitelist()
def validate_mr_qty_against_bom(mr_name):
    mr = frappe.get_doc("Material Request", mr_name)

    errors = []

    for row in mr.items:
        if not row.bom_no:
            continue

        bom_items = get_bom_items_as_dict(
            row.bom_no,
            company=mr.company,
            fetch_exploded=1
        )

        bom_item = bom_items.get(row.item_code)
        if not bom_item:
            continue

        bom_qty = bom_item["qty"]

        if row.qty > bom_qty:
            errors.append(
                f"Item {row.item_code}: Requested Qty ({row.qty}) "
                f"exceeds BOM Qty ({bom_qty})"
            )

    if errors:
        frappe.throw(
            "<br>".join(errors),
            title="Quantity exceeds BOM"
        )
