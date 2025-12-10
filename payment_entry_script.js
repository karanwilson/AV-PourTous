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

	before_submit(frm) {
		if (frm.doc.custom_receive_from_fs_api && frm.doc.mode_of_payment == "FS") {
			frappe.call({
				method: 'payments.payment_gateways.doctype.fs_settings.fs_settings.add_transfer_fs_credit_bill',
				args: {
					bill: frm.pass
				},
				callback: (r) => {
					//frm.set_value('party', r.message);
				}
			});
		}
	}

});