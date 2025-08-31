frappe.ui.form.on('Sales Invoice', {
	//refresh(frm) {
		// your code here
	//},

	// before_save(frm) {
	// 	if (!frm.doc.amended_from)
    //         frappe.throw(__("Please submit Sales Invoices from the POS"));
	// },

	before_submit(frm) {
		if (!frm.doc.amended_from)
            frappe.throw(__("Please submit Sales Invoices from the POS"));
	},
});