import frappe

def after_insert_project(doc, event):
    """
    Rename Project as <project_id>: <project_name> immediately after creation.
    Ensures safe renaming with merge=False.
    """
    # Run only for the Project doctype
    if doc.doctype != "Project":
        return

    project_id = doc.name            # value created by naming series
    project_name = doc.project_name  # field user fills in UI

    if not project_id or not project_name:
        return

    new_name = f"{project_id}: {project_name}".strip()

    # Avoid duplicate rename
    if doc.name == new_name:
        return

    # rename document, this changes id
    # frappe.rename_doc("Project", doc.name, new_name, force=True, merge=False)

    # ALSO update the "Project Name" field in DB
    frappe.db.set_value("Project", doc.name, "project_name", new_name)

    # Because rename overrides doc.name, update local instance
    doc.name = new_name
