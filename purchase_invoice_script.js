frappe.ui.form.on('Purchase Invoice', {
	refresh(frm) {
		// your code here
        frappe.call('pourtous.api.get_tax_template')
            .then(r => {
                frm.set_value('taxes_and_charges', r.message[0].name)
                    .then(() => {
                        frm.refresh_field('taxes_and_charges');
                    });
            });
		frm.set_value('disable_rounded_total', 0);
	},

	/* before_save(frm) {
		frm.doc.items.forEach((row) => {
			row.stock_qty = row.qty;
		});
		frm.refresh_field('items');
	} */
});