frappe.ui.form.on('Sales Invoice', {
	onload(frm) {
		frappe.msgprint(__('Please use this Sales Invoice form only to consolidate B2B Sales Orders; for regular B2C Invoices please use the POS.'));
		/* let sales_order;
		frappe.call({
			method: 'pourtous.api.get_so_item_batch',
			args: {
				sales_order: "SAL-ORD-2025-00062",
			},
			callback: (r) => {
				if (r.message) {
					console.log(r.message.name);
					sales_order = r.message;
					//sales_order_name = r.message
					console.log(sales_order);
				}
			}
		}); */
	},

	before_save(frm) {
		frappe.call({
			method: 'pourtous.api.get_warehouse_name',
			async: true,
			callback: (r) => {
				if (r.message) {
					frm.set_value('update_stock', 1);
					frm.set_value('set_warehouse', r.message);
					let sales_order_name = "";
					let sales_order;
					let idx = 0;
					frm.doc.items.forEach((item) => {
						if (item.sales_order && item.sales_order != sales_order_name) {
							frappe.call({
								method: 'pourtous.api.get_so_item_batch',
								args: {
									sales_order: item.sales_order,
								},
								callback: (r) => {
									if (r.message) {
										sales_order_name = r.message.name;
										sales_order = r.message;
									}
								}
							});
						}
						item.batch_no = sales_order.items[idx];
						idx++;
					});
				}
			}
		});
	}
});