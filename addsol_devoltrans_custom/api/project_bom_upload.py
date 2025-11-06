import frappe
from frappe import _
import pandas as pd
from frappe.utils.file_manager import get_file_path


@frappe.whitelist()
def upload_bom_excel(project: str, file_url: str):
    """
    Process uploaded Excel and create BOM(s)
    :param project: Project name (link)
    :param file_url: URL of uploaded Excel file
    """
    # Locate file path
    file_path = get_file_path(file_url.split('/')[-1])
    if not file_path:
        frappe.throw(_("File not found on server."))

    # Read Excel
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        frappe.throw(_("Unable to read Excel: {0}").format(str(e)))

    # Basic validation
    if 'Item Code' not in df.columns:
        frappe.throw(_("Excel must contain 'Item Code' column."))

    # Example logic: create BOM for each item
    created_boms = []
    for _, row in df.iterrows():
        item_code = row['Item Code']
        quantity = row.get('Quantity', 1)
        bom_doc = frappe.get_doc({
            "doctype": "BOM",
            "item": item_code,
            "quantity": quantity,
            "project": project,
            "is_active": 1,
            "is_default": 0
        })
        bom_doc.insert(ignore_permissions=True)
        created_boms.append(item_code)

    return _(f"Created {len(created_boms)} BOMs for project {project}.")
