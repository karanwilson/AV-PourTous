// Copyright (c) 2025, Karan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Participant Contribution Template', {
	// refresh: function(frm) {
	// }
	before_save(frm) {
		frm.set_value('total_contribution', frm.doc.in_kind_scheme + frm.doc.lunch_scheme + frm.doc.monthly_contribution);
	}
});
