import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def create_item_custom_fields():

    custom_fields = {
        "Item": [
            # 1. Test Certificate Required
            {
                "fieldname": "tc_required",
                "label": "Test Certificate Required",
                "fieldtype": "Check",
                "insert_after": "stock_uom",
                "in_list_view": 0,
                "description": "Is test certificate from supplier required?"
            },

            # 2. Project Link
            {
                "fieldname": "linked_project",
                "label": "Project",
                "fieldtype": "Link",
                "options": "Project",
                "insert_after": "tc_required",
                "in_list_view": 0,
            },

            # 3. Remarks
            {
                "fieldname": "remarks",
                "label": "Remarks",
                "fieldtype": "Text Editor",
                "insert_after": "description",
                "in_list_view": 0,
                "description": "Remark for the item, if any"
            },

            # 4. Section Break (Make & Part No Section)
            {
                "fieldname": "section_make_partno",
                "label": "Make and Part No.",
                "fieldtype": "Section Break",
                "insert_after": "remarks",
            },

            # 5. Make
            {
                "fieldname": "make",
                "label": "Make",
                "fieldtype": "Data",
                "insert_after": "section_make_partno",
                "in_list_view": 0,
            },

            # 6. Material Grade
            {
                "fieldname": "material_grade",
                "label": "Material Grade",
                "fieldtype": "Select",
                "options": "CRGO\nCRNGO\nM4\nM5\nM6",
                "insert_after": "make",
                "in_list_view": 0,
            },

            # 7. Column Break
            {
                "fieldname": "column_break_make_partno",
                "fieldtype": "Column Break",
                "insert_after": "material_grade",
            },

            # 8. Part Number
            {
                "fieldname": "part_number",
                "label": "Part Number",
                "fieldtype": "Data",
                "insert_after": "column_break_make_partno",
                "in_list_view": 0,
            },

            # 9. Drawing Reference
            {
                "fieldname": "drawing_ref",
                "label": "Drawing Reference",
                "fieldtype": "Data",
                "insert_after": "part_number",
                "in_list_view": 0,
            },
        ]
    }

    create_custom_fields(custom_fields)
    frappe.clear_cache(doctype="Item")
    frappe.msgprint("Custom Item fields added successfully.")
