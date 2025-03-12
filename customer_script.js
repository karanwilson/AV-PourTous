frappe.ui.form.on('Customer', {
	//refresh(frm) {
	//},

    before_save(frm) {
        frm.set_value("custom_update_zoho_contact", 1);
    },
});
