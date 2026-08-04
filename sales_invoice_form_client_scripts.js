frappe.ui.form.on('Sales Invoice', {
	custom_fs_account_number(frm) {
		if (!frm.doc.customer) {
			frappe.call({
				method: 'pourtous.api.set_customer_from_fs_account',
				args: { 'custom_fs_account_number': frm.doc.custom_fs_account_number },
				callback: (r) => {
					frm.set_value('customer', r.message);
				}
			});
		}
	},

	customer(frm) {
		frm.set_value('update_stock', 1);
		frm.set_value('set_warehouse', 'Stall - PTPS');
		frm.refresh_field("update_stock");
		frm.refresh_field("set_warehouse");
	},

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
				frappe.throw("Please request the executives to cancel Invoice");
			}
		}
		else if (frappe.defaults.get_user_default("company") == "Pour Tous Purchasing Service") {
			if (frappe.session.user == "Administrator" ||
				frappe.session.user == "kumaran@auroville.org.in" ||
				frappe.session.user == "iyyappan@auroville.org.in" ||
				frappe.session.user == "karan.wilson@auroville.org.in") {
				}
			else {
				frappe.throw("Please request the executives to cancel Invoice");
			}
		}
	}
});