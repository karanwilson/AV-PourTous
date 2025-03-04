// Copyright (c) 2025, Karan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Zoho Books API', {
	// refresh: function(frm) {
	// }
	login(frm) {
		frm.call('request_access_token', { throw_if_missing: true })
		.then(r => {
			if (r.message) {
				console.log(r.message);	
			}
		})
	}
});
