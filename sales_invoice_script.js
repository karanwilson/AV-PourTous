frappe.ui.form.on('Sales Invoice', {
	refresh(frm) {
        frm.set_value('taxes_and_charges', 'Output GST In-state - PTPS')
            .then(() => {
                frm.refresh_field('taxes_and_charges');
            });
	},
});
