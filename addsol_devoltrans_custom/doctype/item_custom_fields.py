import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def create_item_custom_fields():
    """
    Create custom fields for the Item DocType.
    Run this in your app's after_install or via:
        bench --site yoursite.local execute addsol_devoltrans_custom.custom.item_custom_fields.create_item_custom_fields
    """
    custom_fields = {
        "Item": [
          {
                "fieldname": "tc_required",
                "label": "Test Certificate Required",
                "fieldtype": "Check",
                "insert_after": "stock_uom",
                "in_list_view": 0,
                "description": "Is test certificate from supplier required?"
            },
            {
                "fieldname": "remarks",
                "label": "Remarks",
                "fieldtype": "Text Editor",
                "insert_after": "description",
                "reqd": 0,
                "unique": 0,
                "translatable": 0,
                "in_list_view": 0,
                "description": "Remark for the item, if any"
            },
            {
                "fieldname": "material_grade",
                "label": "Material Grade",
                "fieldtype": "Select",
                "options": "\nCRGO\nCRNGO\nM4\nM5\nM6",
                "insert_after": "customer_part_no",
                "in_list_view": 0
            },
            {
                "fieldname": "section_make_partno",
                "label": "Make and Part No.",
                "fieldtype": "Section Break",
                "insert_after": "remarks",
            },
            {
                "fieldname": "make",
                "label": "Make",
                "fieldtype": "Data",
                "insert_after": "section_make_partno",
                "in_list_view": 0
            },
            {
                "fieldname": "column_break_make_partno",
                "fieldtype": "Column Break",
                "insert_after": "make",
            },
            {
                "fieldname": "part_number",
                "label": "Part Number",
                "fieldtype": "Data",
                "insert_after": "column_break_make_partno",
                "in_list_view": 0
            },
            {
                "fieldname": "drawing_ref",
                "label": "Drawing Reference",
                "fieldtype": "Data",
                "insert_after": "part_number",
                "in_list_view": 0
            },
        ]
    }

    create_custom_fields(custom_fields)
    frappe.clear_cache(doctype="Item")
    frappe.msgprint("Custom Item fields added successfully.")
