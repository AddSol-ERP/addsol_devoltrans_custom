import frappe

def delete_custom_fields():
    # List of all custom fields your app creates
    item_group_fields = [
        "project_mandatory"
    ]

    item_fields = [
        "tc_required",
        "linked_project",
        "remarks",
        "section_make_partno",
        "make",
        "material_grade",
        "column_break_make_partno",
        "part_number",
        "drawing_ref",
    ]

    for fieldname in item_group_fields:
        frappe.db.delete("Custom Field", {"fieldname": fieldname, "dt": "Item Group"})

    for fieldname in item_fields:
        frappe.db.delete("Custom Field", {"fieldname": fieldname, "dt": "Item"})

    frappe.clear_cache()
    frappe.msgprint("Custom fields removed during uninstall")
