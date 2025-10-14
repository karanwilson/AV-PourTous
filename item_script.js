frappe.ui.form.on('Item', {
    before_save(frm) {
		if (frappe.defaults.get_user_default("company") == "Pour Tous Purchasing Service" && frm.doc.custom_item_add_on) {
            frappe.throw(__("'Item Add On' is set - please remove it, or inform support team to enable this feature"));
        }
	},
});