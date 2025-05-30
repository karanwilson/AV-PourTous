frappe.ui.form.on('Delivery Note', {
	refresh(frm) {
		// your code here
        frappe.call('pourtous.api.get_sales_tax_template_form_script')
            .then(r => {
                frm.set_value('taxes_and_charges', r.message[0].name)
                    .then(() => {
                        frm.refresh_field('taxes_and_charges');
                    });
            });
	},
});