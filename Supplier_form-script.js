frappe.ui.form.on('Supplier', {
	//refresh(frm) {
		// your code here
	//},
	before_save(frm) {
		if (!frm.doc.gstin)
			frm.set_value('is_reverse_charge_applicable', 1);
        else frm.set_value('is_reverse_charge_applicable', 0);
	},
});