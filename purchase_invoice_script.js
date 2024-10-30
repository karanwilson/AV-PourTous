frappe.ui.form.on('Purchase Invoice', {
	//refresh(frm) {
		// your code here
	//}

	before_save(frm) {
		frm.doc.items.forEach((row) => {
			row.stock_qty = row.qty;
		});
		frm.refresh_field('items');
	}
});