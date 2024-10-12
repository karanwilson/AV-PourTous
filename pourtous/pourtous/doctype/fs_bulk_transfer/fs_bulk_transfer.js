// Copyright (c) 2024, Karan and contributors
// For license information, please see license.txt

frappe.ui.form.on('FS Bulk Transfer', {
	// refresh: function(frm) {
	// }
	initiate(frm) {
		if (frm.doc.export_transfers == "Pending") {
            frappe.call({
                method: 'payments.payment_gateways.doctype.fs_settings.fs_settings.add_transfer_fs_draft_bills',
				args: {
					'name': frm.doc.name,
					'from_date': frm.doc.from_date,
					'to_date': frm.doc.to_date
				},
                freeze: true,
                freeze_message: "Processing Offline FS Bills",
                callback: (r) => {
                    frm.refresh_field(frm.doc.transaction_logs)
                    //location.reload();
                }
            });
		}
		else if (frm.doc.export_transfers == "Insufficient Funds") {
            frappe.call({
                method: 'payments.payment_gateways.doctype.fs_settings.fs_settings.add_transfer_fs_credit_bills',
				args: {
					'name': frm.doc.name,
					'from_date': frm.doc.from_date,
					'to_date': frm.doc.to_date
				},
                freeze: true,
                freeze_message: "Processing FS Credit Bills",
                callback: (r) => {
                    frm.refresh_field(frm.doc.transaction_logs)
                    //location.reload();
                }
            });
		}
	}
});
