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
	}
});