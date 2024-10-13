// Copyright (c) 2024, Karan and contributors
// For license information, please see license.txt

frappe.ui.form.on('FS Bulk Transfer', {
	// refresh: function(frm) {
	// }
	after_save(frm) {
        console.log("frm.doc: ", frm.doc);
        switch(frm.doc.export_transfers) {
            case "Pending":
                frappe.call({
                    method: 'payments.payment_gateways.doctype.fs_settings.fs_settings.add_transfer_fs_draft_bills',
		    		args: {
			    		'doc_name': frm.doc.name,
				    	'year': frm.doc.year,
    				},
                    freeze: true,
                    freeze_message: "Processing Offline FS Bills",
                    callback: (r) => {
                        frm.refresh_field(frm.doc.transaction_logs)
                        //location.reload();
                    }
                });
                break;

            case "Insufficient Funds":
                frappe.call({
                    method: 'payments.payment_gateways.doctype.fs_settings.fs_settings.add_transfer_fs_credit_bills',
                    args: {
                        'doc_name': frm.doc.name,
                        'year': frm.doc.year,
                    },
                    freeze: true,
                    freeze_message: "Processing FS Credit Bills",
                    callback: (r) => {
                        frm.refresh_field(frm.doc.transaction_logs)
                        //location.reload();
                    }
                });
                break;
		}
	}
});
