// Add Upload BOM Excel button to Project
frappe.ui.form.on("Project", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(
				"Upload BOM Excel",
				async function () {
					// Show file uploader dialog
					const d = new frappe.ui.Dialog({
						title: "📦 Upload BOM Excel",
						fields: [
							{
								fieldname: "bom_excel",
								fieldtype: "Attach",
								label: "Select Excel File",
								reqd: 1,
							},
						],
						primary_action_label: "Upload",
						primary_action(values) {
							frappe.call({
								method: "addsol_devoltrans_custom.api.project_bom_upload.upload_bom_excel",
								args: {
									project: frm.doc.name,
									file_url: values.bom_excel,
								},
								freeze: true,
								freeze_message: "Processing Excel...",
								callback: (r) => {
									if (!r.exc) {
										frappe.msgprint(r.message || "BOM Uploaded Successfully!");
										frm.reload_doc();
									}
								},
							});
							d.hide();
						},
					});
					d.show();
				},
				__("Actions")
			);
		}
	},
});
