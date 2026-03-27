frappe.ui.form.on('Sales Invoice', {
	//refresh(frm) {
		// your code here
	//},

	// before_save(frm) {
	// 	if (!frm.doc.amended_from)
    //         frappe.throw(__("Please submit Sales Invoices from the POS"));
	// },

	before_submit(frm) {
		if (!frm.doc.amended_from) {
			if (frappe.defaults.get_user_default("company") == "Pour Tous Purchasing Service") {
				if (frappe.session.user == "Administrator" ||
					frappe.session.user == "kumaran@auroville.org.in" ||
					frappe.session.user == "iyyappan@auroville.org.in" ||
					frappe.session.user == "karan.wilson@auroville.org.in") {
					}
				else {
					frappe.throw(__("Please submit Sales Invoices from the POS"));
				}
			}
			else if (frappe.defaults.get_user_default("company") == "Pour Tous Distribution Center") {
				if (frappe.session.user == "Administrator" ||
					frappe.session.user == "anandi@auroville.org.in" ||
					frappe.session.user == "arulkumarsankar@auroville.org.in" ||
					frappe.session.user == "karan.wilson@auroville.org.in") {
					}
				else {
					frappe.throw(__("Please submit Sales Invoices from the POS"));
				}
			}
		}
	},

	before_cancel(frm) {
		if (frappe.defaults.get_user_default("company") == "Pour Tous Distribution Center") {
			if (frappe.session.user == "Administrator" ||
				frappe.session.user == "anandi@auroville.org.in" ||
				frappe.session.user == "arulkumarsankar@auroville.org.in" ||
				frappe.session.user == "karan.wilson@auroville.org.in") {
				}
			else {
				frappe.throw("Please request the executives to cancell Invoice");
			}
		}
	}
});