// Add Upload BOM Excel button to Project
frappe.ui.form.on("Project", {
	refresh(frm) {
		if (!frm.is_new()) {
			const group_label = __("BOM Actions");
			frm.add_custom_button('<i class="fa fa-file-excel-o text-success"></i> Download BOM Template', () => {
				window.location.href = `/api/method/addsol_devoltrans_custom.api.project_bom_template_download.download_bom_template?project=${encodeURIComponent(frm.doc.name)}`;
            // frappe.call({
            //     method: "addsol_devoltrans_custom.api.project_bom_upload.download_bom_template",
            //     callback: (r) => {
            //         // if (!r.exc) {
            //         //     const blob = new Blob([r.message], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
            //         //     const url = window.URL.createObjectURL(blob);
            //         //     const a = document.createElement("a");
            //         //     a.href = url;
            //         //     a.download = "BOM_Template.xlsx";
            //         //     a.click();
            //         //     window.URL.revokeObjectURL(url);
            //         // }
            //     }
            // });
        }, group_label).addClass('bom-action-btn-secondary');
			frm.add_custom_button( 
				'<i class="fa fa-upload text-primary"></i> Upload BOM Excel',
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
				}, group_label).addClass('bom-action-btn-primary')
			;
		}
	},
});
