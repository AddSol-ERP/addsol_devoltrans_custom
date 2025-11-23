import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def add_custom_fields():
    create_item_group_custom_fields()
    create_item_custom_fields()
    
def create_item_group_custom_fields():
    if frappe.db.exists("Custom Field", "Item Group-project_mandatory"):
        return

    frappe.get_doc({
        "doctype": "Custom Field",
        "dt": "Item Group",
        "fieldname": "project_mandatory",
        "fieldtype": "Check",
        "label": "Project Mandatory",
        "description": "Is project manadatory for this group of items?",
        "insert_after": "is_group",
        "default": "1"
    }).insert(ignore_permissions=True)

    frappe.clear_cache(doctype="Item Group")

def create_item_custom_fields():
    # Group 1: Fields after stock_uom (no internal chaining)
    group1 = {
        "Item": [
            {
                "fieldname": "tc_required",
                "label": "Test Certificate Required",
                "fieldtype": "Check",
                "insert_after": "stock_uom",
                "description": "Is test certificate from supplier required?",
                "translatable": 0,
            },
            {
                "fieldname": "linked_project",
                "label": "Project",
                "fieldtype": "Link",
                "options": "Project",
                "insert_after": "stock_uom",  # Both after stock_uom for simplicity
                "translatable": 0,
            },
        ]
    }
    create_custom_fields(group1, ignore_validate=True)

    # Group 2: Standalone remarks after description
    group2 = {
        "Item": [
            {
                "fieldname": "remarks",
                "label": "Remarks",
                "fieldtype": "Text Editor",
                "insert_after": "description",
                "description": "Remark for the item, if any",
                "translatable": 0,
            },
        ]
    }
    create_custom_fields(group2, ignore_validate=True)

    # Group 3a: Create section first (standalone)
    group3a = {
        "Item": [
            {
                "fieldname": "section_make_partno",
                "label": "Make and Part No.",
                "fieldtype": "Section Break",
                "insert_after": "stock_uom",  # Place after stock_uom, near the other new fields
            },
        ]
    }
    create_custom_fields(group3a, ignore_validate=True)

    # Group 3b: Now chain fields inside the section (section now exists)
    group3b = {
        "Item": [
            {
                "fieldname": "make",
                "label": "Make",
                "fieldtype": "Data",
                "insert_after": "section_make_partno",
            },
            {
                "fieldname": "material_grade",
                "label": "Material Grade",
                "fieldtype": "Select",
                "options": "CRGO\nCRNGO\nM4\nM5\nM6",  # No leading newline—options start directly
                "insert_after": "make",
            },
            {
                "fieldname": "column_break_make_partno",
                "fieldtype": "Column Break",
                "insert_after": "material_grade",
            },
            {
                "fieldname": "part_number",
                "label": "Part Number",
                "fieldtype": "Data",
                "insert_after": "column_break_make_partno",
            },
            {
                "fieldname": "drawing_ref",
                "label": "Drawing Reference",
                "fieldtype": "Data",
                "insert_after": "part_number",
            },
        ]
    }
    create_custom_fields(group3b, ignore_validate=True)

    # Reload doctype
    frappe.clear_cache(doctype="Item")
    frappe.db.commit()

if __name__ == "__main__":
    create_item_custom_fields()
    print("Custom Item fields added successfully in phases.")