frappe.ui.form.on('Purchase Invoice', {
	refresh(frm) {
		// your code here
		frm.set_value('taxes_and_charges', 'Input GST In-state - PTPS')
			.then(() => {
				frm.refresh_field('taxes_and_charges');
			});
	},

	before_save(frm) {
		frm.doc.items.forEach((row) => {
			row.stock_qty = row.qty;
		});
		frm.refresh_field('items');
	}
});