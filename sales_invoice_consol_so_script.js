frappe.ui.form.on('Sales Invoice', {
	refresh(frm) {
		frm.set_value('update_stock', 1);
	},

	before_save(frm) {
		frm.doc.items.forEach((item) => {
			if (item.sales_order) {
				item.warehouse = "Sales Order Reserve - PTPS";
				// from March the warehouse field can be directly pulled from the frappe.call statement below,
				// as it is being set in the Sales Order Items, from 20 Feb onward.
				frappe.call({
					method: 'pourtous.api.get_so_item_batch',
					args: {
						sales_order: item.sales_order,
						item_code: item.item_code
					},
					callback: (r) => {
						if (r.message)
							item.batch_no = r.message;
					}
				});
			}
		});
	}
});