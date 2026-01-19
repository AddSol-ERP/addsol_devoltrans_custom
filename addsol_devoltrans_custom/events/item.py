# Items related customization
import frappe
from frappe import _
import uuid

# Temporary assign code to bypass duplicate validation 
def before_insert_item(doc, method):
    """Assign a temporary unique code to bypass duplicate checks."""
    original_code = (doc.item_code or "").strip()
    project = (doc.linked_project or "").strip()

    if not project:
        return

    # save original code for later rename
    doc._original_item_code = original_code

    # temporary unique name to avoid duplicates
    temp_code = f"TEMP-{uuid.uuid4().hex[:8]}"
    doc.item_code = temp_code



# Checks if item belongs to specified groups. If yes check if Project field is populated, and then adds project id to item code
def after_insert_item(doc, method):
    """Runs only after new Item is inserted."""

    item_group = (doc.item_group or "").strip()
    project = (doc.linked_project or "").strip()

    # Groups where project is needed
    # required_groups = ["Finished Goods", "Raw Material"]
    # Fetch the Item Group doc
    item_group_doc = frappe.get_cached_doc("Item Group", doc.item_group)

    # 1️⃣ Validate Mandatory Project for marked Item Groups
    # if item_group in required_groups and not project:
    #     frappe.throw(_("Project is mandatory for Item Group: {0}").format(item_group))

    if item_group_doc.project_mandatory and not project:
        frappe.throw(_("Project is mandatory for Item Group: {0}").format(doc.item_group))

    if not project:
        return  # nothing more to do

    # Read original_item_code saved earlier
    original_code = getattr(doc, "_original_item_code", None)
    if not original_code:
        return  # nothing to rename

    # 2️⃣ Get Project ID / Name to append
    project_doc = frappe.get_doc("Project", project)
    project_id = project_doc.name  # using project.name, which holds ID

    # 3️⃣ Append project id to Item Code → ITEMCODE-PROJECTID
    new_item_code = f"{project_id}: {original_code}"

    if new_item_code == doc.item_code:
        return  # avoid double-appending

    # Frappe safe rename
    frappe.rename_doc(
        doctype="Item",
        old=doc.name,
        new=new_item_code,
        force=True,      # allow rename even if linked (safe on insert)
        show_alert=False,
        merge=False,
    )

    # Update reference inside doc object so UI reloads properly
    doc.name = new_item_code
    doc.item_code = new_item_code
