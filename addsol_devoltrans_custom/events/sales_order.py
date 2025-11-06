import frappe


# on Sales Order Submit create a peoject
def on_submit(doc, method):
    # If Auto generation flag is set
    if doc.custom_auto_generate_project and not doc.project:
        project = frappe.get_doc({
            "doctype": "Project",
            "project_name": f"Project for {doc.name} - {doc.customer_name}",
            "customer": doc.customer,
            "sales_order": doc.name,
            "expected_start_date": doc.transaction_date,
            "expected_end_date": doc.delivery_date,
            "status": "Open"
        })

        # Bypass ALL validate hooks (safe for auto-creation)
        # project.flags.ignore_validate = True
        project.insert(ignore_permissions=True)

        # Rename project to be more descriptive
        new_name = f"{project.name} : {doc.customer_name} : {doc.name}"
        project.db_set("project_name", new_name)

        # Link back to Sales Order
        doc.db_set("project", project.name)

        frappe.msgprint(
            f"Project <b>{project.name}</b> created for Sales Order <b>{doc.name}</b>", indicator="green")

