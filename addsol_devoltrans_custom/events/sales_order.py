import frappe

# After Insert
def after_insert(doc, event):
    '''
    Append Project ID to Sales Order name
    '''
    if doc.doctype != "Sales Order":
        return

    # -----------------------------
    # 1. Append Project ID to Sales Order name
    # -----------------------------
    project = doc.project

    if not project:
        return  # should not happen, because mandatory

    # Fetch project document
    project = frappe.get_doc("Project", doc.project)
    project_id = project.name

    # Already renamed?
    if project_id in doc.name:
        return

    # new name format → SO-####-<ProjectID>
    new_name = f"{project_id}: {doc.name}"

    # rename Sales Order safely
    frappe.rename_doc(
        doctype="Sales Order",
        old=doc.name,
        new=new_name,
        force=True,
        merge=False
    )

    # update in-memory instance
    doc.name = new_name

    # -----------------------------
    # 2. Link Sales Order back to Project
    # -----------------------------
    project = frappe.get_doc("Project", project_id)

    updated = False

    # Set Sales Order reference on Project (optional field — use custom field or default field)
    # If you already have a field: 'sales_order'
    if hasattr(project, "sales_order"):
        if not project.sales_order:
            project.sales_order = doc.name
            updated = True
    else:
        # If field doesn't exist, add a comment instead so link still exists
        if not frappe.db.exists("Communication", {"reference_doctype": "Project", "reference_name": project_id, "subject": doc.name}):
            project.add_comment("Info", f"Linked Sales Order: {doc.name}")

    # -----------------------------
    # 3. Link Customer to Project (if not already linked)
    # -----------------------------
    # Project usually has a field called 'customer' (ERPNext Standard)
    if hasattr(project, "customer"):
        if not project.customer:
            project.customer = doc.customer
            updated = True

    # -----------------------------
    # 4. Save only if fields were updated
    # -----------------------------
    if updated:
        project.save(ignore_permissions=True)



def on_submit_sales_order(doc, method):
    '''
    Get list of memebers from Email Group 'Sales Order Notification List' 
    and send email to them on Sales Order Submit
    '''
    # ------- Prepare message --------
    project_code = doc.project or "Not Assigned"
    delivery_date = doc.delivery_date or "Not Set"

    # HTML email template
    message = f"""
    <div style="font-family: Arial, sans-serif; max-width: 650px; margin: 0 auto;
        border: 1px solid #e5e5e5; border-radius: 8px; background: #ffffff;">

        <div style="background: #e81a1a; padding: 16px; border-radius: 8px 8px 0 0;">
            <h2 style="margin: 0; color: #ffffff; font-size: 20px;">
                📄 New Sales Order Received
            </h2>
        </div>

        <div style="padding: 20px; font-size: 14px; color: #333333;">
            <p style="font-size: 15px; margin-bottom: 20px;">
                Hello Team,<br>
                We have received a <b>new order</b>. Please find the attached document for more information.
            </p>

            <div style="background: #f9f9f9; padding: 15px; border-radius: 6px; margin-bottom: 20px;">
                <p style="margin: 6px 0;"><b>Sales Order:</b> {doc.name}</p>
                <p style="margin: 6px 0;"><b>Customer:</b> {doc.customer_name}</p>
                <p style="margin: 6px 0;"><b>Project:</b> {project_code}</p>
                <p style="margin: 6px 0;"><b>Delivery Date:</b> {delivery_date}</p>
            </div>

            <p style="margin-top: 15px; font-size: 14px;">
                Please take necessary action.
            </p>
        </div>

        <div style="background: #e81a1a; padding: 10px; border-radius: 0 0 8px 8px; text-align:center;">
            <p style="color: #ffffff; margin: 0; font-size: 13px;">ERPNext Auto Notification</p>
        </div>
    </div>
    """

    # ------- Generate PDF from print format --------
    pdf_dict = frappe.attach_print(
        doctype="Sales Order",
        name=doc.name,
        print_format="Sales Order Without Price"
    )
    pdf_data = pdf_dict["fcontent"]

    # ------- Send Email --------
    # Get members of Email Group 'Sales Order Notification List'
    email_group_members = frappe.get_all("Email Group Member", 
        filters={"email_group": "Sales Order Notification List"},
        fields=["email"]
    )
    recipients = [member.email for member in email_group_members if member.email]
    # recipients = ["ed@devoltrans.com", "sanjay@devoltrans.com", "amit@devoltrans.com", "pramod@devoltrans.com", "sagar@devoltrans.com", "sudin@devoltrans.com"]
    #recipients = ["sanketvyapari@gmail.com"]
    frappe.sendmail(
        recipients=recipients,
        subject=f"New Order Recieved: {doc.name}",
        message=message,
        attachments=[{
            "fname": f"{doc.name}.pdf",
            "fcontent": pdf_data
        }],
        now=True
    )
