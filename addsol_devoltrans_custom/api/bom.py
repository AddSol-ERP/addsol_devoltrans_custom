import frappe
from frappe.utils import escape_html
from erpnext.manufacturing.doctype.bom.bom import get_bom_items_as_dict
from erpnext.stock.utils import get_bin


def get_existing_requested_qty(bom, project, exclude_mr=None):
    """
    Returns:
        { item_code: total_requested_qty }
    For Purchase Material Requests against same BOM + Project
    """

    conditions = """
        mr.material_request_type = 'Purchase'
        AND mr.docstatus != 2
        AND mri.bom_no = %(bom)s
    """

    params = {"bom": bom}

    if project:
        conditions += " AND mri.project = %(project)s"
        params["project"] = project

    if exclude_mr:
        conditions += " AND mr.name != %(exclude_mr)s"
        params["exclude_mr"] = exclude_mr

    rows = frappe.db.sql(
        f"""
        SELECT
            mri.item_code,
            SUM(mri.qty) AS requested_qty
        FROM `tabMaterial Request Item` mri
        INNER JOIN `tabMaterial Request` mr
            ON mr.name = mri.parent
        WHERE {conditions}
        GROUP BY mri.item_code
        """,
        params,
        as_dict=True,
    )

    return {row.item_code: row.requested_qty for row in rows}


@frappe.whitelist()
def get_bom_items_for_mr(
    bom,
    company,
    warehouse,
    exclude_mr=None,
):
    """
    FINAL API for popup dialog:
    - Compact single-line grid rows
    - Expandable detail section
    - Project derived from BOM
    """

    # ---- BOM as source of truth ----
    bom_doc = frappe.get_doc("BOM", bom)
    bom_project = bom_doc.project

    # ---- Exploded BOM items ----
    bom_items = get_bom_items_as_dict(
        bom,
        company=company,
        fetch_exploded=1,
    )

    # ---- Already requested qty ----
    requested_map = get_existing_requested_qty(
        bom=bom,
        project=bom_project,
        exclude_mr=exclude_mr,
    )

    result = []

    for item in bom_items.values():
        item_code = item["item_code"]
        item_name = item.get("item_name") or ""
        uom = item.get("uom") or item.get("stock_uom")

        # ---- Warehouse stock ----
        available_qty = 0
        if warehouse:
            bin_data = get_bin(item_code, warehouse)
            available_qty = bin_data.actual_qty if bin_data else 0

        required_qty = item["qty"]
        already_requested = requested_map.get(item_code, 0)

        remaining_qty = max(
            required_qty - available_qty - already_requested, 0
        )

        # ---- ITEM (single line) ----
        item_html = f"""{item_code} {escape_html(item_name)}"""

        # ---- REQUIREMENT SUMMARY (single line) ----
        requirement_html = f"""Req:{required_qty} | Stk:{available_qty} | MR:{already_requested}"""

        # ---- STATUS ----
        if already_requested > 0:
            status_html = 'Already Requested'
        elif available_qty >= required_qty:
            status_html = 'Available'
        else:
            status_html = 'To Purchase'

        # ---- EXPANDABLE DETAILS ----
        details_html = f"""
        <div class="text-muted" style="
            padding: 8px 0;
            font-size: 12px;
            line-height: 1.5;
        ">
            <div><b>Required Qty:</b> {required_qty}</div>
            <div><b>Available Stock:</b> {available_qty}</div>
            <div><b>Already Requested:</b> {already_requested}</div>
            <div><b>UOM:</b> {uom}</div>
            <div><b>BOM:</b> {bom}</div>
            <div><b>Project:</b> {bom_project or '-'}</div>
        </div>
        """

        result.append(
            {
                # 🔑 hidden data (logic)
                "item_code": item_code,
                "uom": uom,
                "bom_no": bom,
                "project": bom_project,

                # visible UI
                "is_selected": 0,
                "item": item_html,
                "requirement": requirement_html,
                "request_qty": remaining_qty,
                "status": status_html,
                "details": details_html,
            }
        )

    return result
