frappe.ui.form.on('Payment Entry', {
	//refresh(frm) {
		// your code here
	//},

	custom_fs_account_number(frm) {
		frappe.call({
			method: 'pourtous.api.set_customer_from_fs_account',
			args: { 'custom_fs_account_number': frm.doc.custom_fs_account_number },
			callback: (r) => {
				frm.set_value('party', r.message);
			}
		});
	},

	before_save(frm) {
		if (frm.doc.custom_receive_from_fs_api && frm.doc.mode_of_payment == "FS") {
			frm.set_value("reference_no", "Temp ref no: pre-fs-transaction");
			frm.set_value("reference_date", frappe.datetime.get_today());
		}
	},

	/* before_submit(frm) {
		if (frm.doc.custom_receive_from_fs_api && frm.doc.mode_of_payment == "FS") {
			if (frm.doc.references.length == 1) {
				frappe.call({
					method: 'payments.payment_gateways.doctype.fs_settings.fs_settings.add_transfer_fs_credit_bill',
					args: {
						bill: frm.doc.references[0].reference_name,
						pe: frm.doc.name
					},
					callback: (r) => {
						if (r.message) {
							if (r.message['custom_fs_transfer_status'] == "OK" || r.message['custom_fs_transfer_status'] == "OK - Paid") {
								// frm.set_value('custom_fs_transfer_status', r.message['Result']);
								// frm.set_value('reference_no', r.message['reference_no']);
								// frm.set_value('custom_remarks', 1);
								// frm.set_value('remarks', r.message['Message']);
								frm.set_value({
									custom_fs_transfer_status: r.message['custom_fs_transfer_status'],
									reference_no: r.message['reference_no'],
									custom_remarks: 1,
									remarks: r.message['remarks']
								});
							}
							else frappe.throw(r.message['custom_fs_transfer_status']);
						}
						else frappe.throw("No Response");
					}
				});
			}
			else frappe.throw("Receiving Payment via FS API is configured for a single Invoice/Order only");
		}
	}, */

	// on_submit(frm) { // update custom_fs_transfer_status
	// 	frm.doc.references.forEach((reference) => {
	// 		doc = frappe.get_doc(reference.reference_doctype, reference.reference_name);
	// 		if (doc.custom_fs_account_number && doc.status == "Paid" && doc.custom_fs_transfer_status.match("Paid").length == 0) {			
	// 			frappe.db.set_value(reference.reference_doctype, reference.reference_name, "custom_fs_transfer_status", doc.status);
	// 		}
	// 	});
	// }

});