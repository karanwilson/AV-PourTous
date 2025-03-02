frappe.ui.form.on('Sales Invoice', {
	onload(frm) {
		if (frm.doc.docstatus === 0 && !frm.doc.is_return)
			frappe.msgprint(__('Please use this Sales Invoice form only to consolidate B2B Sales Orders; for regular B2C Invoices please use the POS.'));
		/* let sales_order_name = "";
		let sales_order;
		let idx = 1; // idx column in Items tables start from 1
		frappe.call({
			method: 'pourtous.api.get_so_item_batch',
			args: {
				sales_order: "SAL-ORD-2025-00085",
			},
			async: false,
			callback: (r) => {
				if (r.message) {
					sales_order_name = r.message.name;
					sales_order = r.message;
					console.log(sales_order_name);
					console.log(sales_order);
					idx = 1; // each time a Sales Order doc is pulled from backend, reset idx to starting value of 1.
				}
			}
		});
		console.log(sales_order.items);
		console.log(sales_order.items[idx-1]);
		console.log(sales_order.items[idx-1].custom_batch_no);
		idx++; */
	},
	//(array === undefined || array.length == 0)
	refresh(frm) {
		if (frm.doc.customer && (frm.doc.advances.length === 0)) {
			//console.log("trigerring get_advances");
			frm.trigger('get_advances');
		}
	},

	get_advances(frm) {
		if(!frm.doc.is_return) {
			frm.call({
				method: "set_advances",
				doc: frm.doc,
				callback: function(r, rt) {
					refresh_field("advances");
					frm.dirty();
				}
			});
		}
	},

	before_save(frm) {
		if (!frm.doc.is_return) {
			frappe.call({
				method: 'pourtous.api.get_warehouse_name',
				args: { customer: frm.doc.customer },
				async: true,
				callback: (r) => {
					if (r.message["customer_type"] == "Company") {
						//frm.trigger('get_advances');
						frm.set_value('update_stock', 1);
						frm.set_value('set_warehouse', r.message["warehouse"]);
						let sales_order_name = "";
						let sales_order;
						let idx = 1; // idx column in Items tables start from 1
						frm.doc.items.forEach((item) => {
							if (item.sales_order && item.sales_order != sales_order_name) {
								frappe.call({
									method: 'pourtous.api.get_so_item_batch',
									args: {
										sales_order: item.sales_order,
									},
									async: false,
									callback: (r) => {
										if (r.message) {
											sales_order_name = r.message.name;
											sales_order = r.message;
											idx = 1; // each time a Sales Order doc is pulled from backend, reset idx to starting value of 1.
										}
									}
								});
							}
							item.batch_no = sales_order.items[idx-1].custom_batch_no; // Python array index values start from 0, where idx starts from 1
							//console.log(item.batch_no);
							idx++;
						});
					}
				}
			});
		}
	},
});