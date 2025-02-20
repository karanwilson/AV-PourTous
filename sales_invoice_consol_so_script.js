frappe.ui.form.on('Sales Invoice', {
	refresh(frm) {
		// your code here
        frappe.call('pourtous.api.set_so_warehouse')
            .then(r => {
                frm.set_value('', r.message)
                    .then(() => {
                        frm.refresh_field('');
                    });
            });
	},

	/* before_save(frm) {
		frm.doc.items.forEach((row) => {
			row.stock_qty = row.qty;
		});
		frm.refresh_field('items');
	} */
});