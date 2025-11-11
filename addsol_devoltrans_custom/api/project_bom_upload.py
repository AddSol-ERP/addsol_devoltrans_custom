import frappe
from frappe import _
import pandas as pd
from frappe.utils.file_manager import get_file_path

# --------------------------------------------------------------------------- #
#  UPLOAD BOM EXCEL
# --------------------------------------------------------------------------- #

EXPECTED_COLUMNS = [
    "Item Code", "Item Name", "Description", "Make", "Part no.",
    "Qty", "UOM", "Item Group", "Remarks", "Specification Link", "Sub BOM Sheet",
]


@frappe.whitelist()
def upload_bom_excel(project: str, file_url: str):
    """
    Upload and process a multi-level BOM Excel file.
    Supports:
      - Operations in row 3
      - Item data from row 5 onward
      - Nested BOM via 'Sub BOM Sheet'
      - Auto creation of missing Items
    """
    file_name = file_url.split("/")[-1]
    file_path = get_file_path(file_name)
    if not file_path:
        frappe.throw(_("File not found on server."))

    try:
        created_boms = _process_bom_sheet(project, file_path, "BOM")
        frappe.logger("bom_upload").info(f"{len(created_boms)} BOMs created for project {project}")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "BOM Upload Failed")
        frappe.throw(_("Error while processing BOM Excel: {0}").format(str(e)))

    return _(f"✅ Successfully created {len(created_boms)} BOM(s) for project {project}.")


# --------------------------------------------------------------------------- #
#  INTERNAL IMPLEMENTATION
# --------------------------------------------------------------------------- #

def _process_bom_sheet(project, file_path, sheet_name, parent_bom=None, visited=None):
    if visited is None:
        visited = set()

    if sheet_name in visited:
        frappe.throw(_(f"Circular reference detected in BOM sheets: {sheet_name}"))
    visited.add(sheet_name)

    # ---- 1. Read operations from row 3 ----
    operations = _read_operations(file_path, sheet_name)

    # ---- 2. Read BOM items from row 5 ----
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=4)
    except Exception as e:
        frappe.throw(_(f"Unable to read sheet '{sheet_name}': {e}"))

    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        frappe.throw(_(f"Missing columns in sheet '{sheet_name}': {', '.join(missing)}"))

    if df.empty:
        frappe.throw(_(f"Sheet '{sheet_name}' has no BOM item data."))

    created_boms = []

    for _, row in df.iterrows():
        item_code = str(row["Item Code"]).strip()
        if not item_code:
            frappe.throw(_(f"Blank Item Code found in sheet '{sheet_name}'."))

        _ensure_item_exists(row)

        qty = row.get("Qty", 1)
        uom = row.get("UOM") or "Nos"
        sub_bom_sheet = str(row.get("Sub BOM Sheet") or "").strip()

        bom_doc = frappe.new_doc("BOM")
        bom_doc.update({
            "item": item_code,
            "quantity": qty,
            "project": project,
            "is_active": 1,
            "is_default": 0
        })

        for idx, op_name in enumerate(operations, start=1):
            bom_doc.append("operations", {
                "operation": op_name,
                "sequence_id": idx
            })

        if sub_bom_sheet:
            child_boms = _process_bom_sheet(project, file_path, sub_bom_sheet, parent_bom=bom_doc.name, visited=visited)
            for child_bom_name in child_boms:
                bom_doc.append("items", {
                    "item_code": item_code,
                    "qty": qty,
                    "uom": uom,
                    "bom_no": child_bom_name
                })
        else:
            bom_doc.append("items", {
                "item_code": item_code,
                "qty": qty,
                "uom": uom
            })

        try:
            bom_doc.insert(ignore_permissions=True)
            created_boms.append(bom_doc.name)
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "BOM Creation Error")
            frappe.throw(_(f"Failed to create BOM for item '{item_code}' in sheet '{sheet_name}': {e}"))

    return created_boms


def _read_operations(file_path, sheet_name):
    try:
        ops_df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, nrows=3)
    except Exception as e:
        frappe.throw(_(f"Unable to read operations from sheet '{sheet_name}': {e}"))

    if ops_df.shape[0] < 3:
        frappe.throw(_(f"Row 3 missing in sheet '{sheet_name}' for operations."))

    ops_row = ops_df.iloc[2].dropna().tolist()
    operations = [
        str(op).strip()
        for op in ops_row
        if str(op).strip().lower() not in ["", "operations", "operation"]
    ]

    if not operations:
        frappe.throw(_(f"No operations defined on row 3 in sheet '{sheet_name}'."))

    invalid_ops = [op for op in operations if not frappe.db.exists("Operation", {"operation_name": op})]
    if invalid_ops:
        frappe.throw(_(f"Unknown operations in sheet '{sheet_name}': {', '.join(invalid_ops)}"))

    return operations


def _ensure_item_exists(row):
    item_code = str(row["Item Code"]).strip()
    if frappe.db.exists("Item", item_code):
        return

    try:
        item_doc = frappe.new_doc("Item")
        item_doc.update({
            "item_code": item_code,
            "item_name": row.get("Item Name") or item_code,
            "description": row.get("Description") or "",
            "stock_uom": row.get("UOM") or "Nos",
            "make": row.get("Make") or "",
            "part_no": row.get("Part no.") or "",
            "include_item_in_manufacturing": 1,
            "is_stock_item": 1,
            "disabled": 0,
        })

        if row.get("Specification Link"):
            item_doc.db_set("specification_link", str(row["Specification Link"]), commit=False)

        item_doc.insert(ignore_permissions=True)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Item Creation Error")
        frappe.throw(_(f"Failed to create Item '{item_code}': {e}"))
