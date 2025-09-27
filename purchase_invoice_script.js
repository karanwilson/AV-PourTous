frappe.ui.form.on('Purchase Invoice', {
	/* supplier(frm) {
        frappe.call({
			method: 'pourtous.api.get_tax_template',
			args: {
				company: frm.doc.company,
				supplier: frm.doc.supplier
			},
			callback: (r) => {
				console.log("r.message: ", r.message);
				console.log("r.message[0].name: ", r.message[0].name);
				frm.set_value('taxes_and_charges', r.message[0].name);
				frm.refresh_field('taxes_and_charges');
			}
		})
	}, */

	before_save(frm) {
		frm.set_value('disable_rounded_total', 0);

		/* frm.doc.items.forEach((row) => {
			row.stock_qty = row.qty;
		});
		frm.refresh_field('items'); */
	},

	onload(frm) {
		frm.set_query("batch_no", "items", function (doc, cdt, cdn) {
			var item = locals[cdt][cdn];
			return {
				filters: {
					item: item.item_code,
					batch_qty: ["!=", 0]
				},
			};
		});
	},
});