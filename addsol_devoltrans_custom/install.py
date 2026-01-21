import frappe


def add_custom_fields():
    create_item_group_custom_fields()
    create_item_custom_fields()


# -------------------------
# Item Group Custom Fields
# -------------------------
def create_item_group_custom_fields():
    if frappe.db.exists("Custom Field", "Item Group-project_mandatory"):
        return

    frappe.get_doc({
        "doctype": "Custom Field",
        "dt": "Item Group",
        "fieldname": "project_mandatory",
        "fieldtype": "Check",
        "label": "Project Mandatory",
        "description": "Is project mandatory for this group of items?",
        "insert_after": "is_group",
        "default": "1",
        "module": "Addsol Devoltrans Custom"
    }).insert(ignore_permissions=True)

    frappe.clear_cache(doctype="Item Group")


# -------------------------
# Item Custom Fields
# -------------------------
def create_item_custom_fields():

    data_fields = [
        {
            "fieldname": "tc_required",
            "label": "Test Certificate Required",
            "fieldtype": "Check",
            "insert_after": "stock_uom",
            "description": "Is test certificate from supplier required?",
        },
        {
            "fieldname": "linked_project",
            "label": "Project",
            "fieldtype": "Link",
            "options": "Project",
            "insert_after": "tc_required",
        },
        {
            "fieldname": "design_remarks",
            "label": "Design Remarks",
            "fieldtype": "Text Editor",
            "insert_after": "description",
            "description": "Remark for the item, if any",
        },

        # Column 1
        {
            "fieldname": "item_make",
            "label": "Item Make",
            "fieldtype": "Data",
            "insert_after": "design_remarks",
        },
        {
            "fieldname": "material_grade",
            "label": "Material Grade",
            "fieldtype": "Select",
            "options": "CRGO\nCRNGO\nM4\nM5\nM6",
            "insert_after": "item_make",
        },

        # Column 2
        {
            "fieldname": "part_number",
            "label": "Part Number",
            "fieldtype": "Data",
            "insert_after": "material_grade",
        },
        {
            "fieldname": "drawing_ref",
            "label": "Drawing Reference",
            "fieldtype": "Data",
            "insert_after": "part_number",
        },
    ]

    for field in data_fields:
        name = f"Item-{field['fieldname']}"
        if frappe.db.exists("Custom Field", name):
            continue

        frappe.get_doc({
            "doctype": "Custom Field",
            "dt": "Item",
            "module": "Addsol Devoltrans Custom",
            **field
        }).insert(ignore_permissions=True)

    frappe.clear_cache(doctype="Item")


if __name__ == "__main__":
    add_custom_fields()
    print("Custom fields for Item and Item Group added successfully.")
