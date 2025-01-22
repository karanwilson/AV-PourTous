frappe.ui.form.on('Purchase Order', {
	//refresh(frm) {
		// your code here
	//}

	supplier(frm) {
		frm.clear_table('items');
	},

	custom_batch_items_fetch(frm) {
		frm.clear_table('custom_batch_items_data');
		frappe.call({
			method: 'pourtous.api.supplier_batch_items',
			args: {
				supplier: frm.doc.supplier
			},
			callback: (r) => {
				if (r.message.length > 0) {
					for (const row of r.message) {
						let item_row = frm.add_child('custom_batch_items_data');
						item_row.item_code = row["item_code"];
						item_row.item_name = row["item_name"];
						item_row.buying_price = row["buying_price"];
						item_row.ordered_qty = row["ordered_qty"];
						item_row.store_qty = row["store_qty"];
						item_row.stall_qty = row["stall_qty"];
						item_row.sold_last_month = row["sold_last_month"];
						item_row.sold_this_month = row["sold_this_month"];
						item_row.to_buy = 0;
						//console.log("row: ", row);
					}
				}
				else frappe.msgprint({
					title: __('Notification'),
					indicator: 'red',
					message: __('No Data')
				});
				frm.refresh_field('custom_batch_items_data');
			}
		});
		/* frm.set_query('item_code', 'items', () => {
			return {
				query: 'pourtous.api.supplier_items_filter',
				txt: frm.doc.supplier
			}
		}) */
	},

	custom_add_batch_items(frm) {
	    let selected = frm.get_selected();
	    selected.custom_batch_items_data.forEach((row) => {
			const itemToAdd = locals["PO Supplier Batch Items"][row];
			let added = false;
			for (const item of frm.doc.items) {
				if (item.item_code == itemToAdd.item_code) {
					item.qty += itemToAdd.to_buy;
					added = true;
					break;
				}
			}
			if (!added) {
				let item_row = frm.add_child('items');
				//frappe.model.set_value triggers a form event that loads other Item data fields like rate, etc.
				frappe.model.set_value(item_row.doctype, item_row.name, 'item_code', itemToAdd.item_code);
				item_row.qty = itemToAdd.to_buy;
			}
	    });
		frm.refresh_field('items');
		//frm.refresh_field('custom_batch_items_data');
	},

	custom_non_batch_items_fetch(frm) {
		frm.clear_table('custom_non_batch_items_data');
		frappe.call({
			method: 'pourtous.api.supplier_non_batch_items',
			args: {
				supplier: frm.doc.supplier
			},
			callback: (r) => {
				if (r.message.length > 0) {
					for (const row of r.message) {
						let item_row = frm.add_child('custom_non_batch_items_data');
						item_row.item_code = row["item_code"];
						item_row.item_name = row["item_name"];
						item_row.buying_price = row["buying_price"];
						item_row.ordered_qty = row["ordered_qty"];
						item_row.store_qty = row["store_qty"];
						item_row.stall_qty = row["stall_qty"];
						item_row.sold_last_month = row["sold_last_month"];
						item_row.sold_this_month = row["sold_this_month"];
						item_row.to_buy = 0;
						//console.log("row: ", row);
					}
				}
				else frappe.msgprint({
					title: __('Notification'),
					indicator: 'red',
					message: __('No Data')
				});
				frm.refresh_field('custom_non_batch_items_data');
			}
		});
	},

	custom_add_non_batch_items(frm) {
	    let selected = frm.get_selected();
	    selected.custom_non_batch_items_data.forEach((row) => {
			const itemToAdd = locals["PO Supplier Non Batch Items"][row];
			let added = false;
			for (const item of frm.doc.items) {
				if (item.item_code == itemToAdd.item_code) {
					item.qty += itemToAdd.to_buy;
					added = true;
					break;
				}
			}
			if (!added) {
				let item_row = frm.add_child('items');
				//frappe.model.set_value triggers a form event that loads other Item data fields like rate, etc.
				frappe.model.set_value(item_row.doctype, item_row.name, 'item_code', itemToAdd.item_code);
				item_row.qty = itemToAdd.to_buy;
			}
	    });
		frm.refresh_field('items');
		//frm.refresh_field('custom_non_batch_items_data');
	},

	before_submit(frm) {
		frm.clear_table('custom_batch_items_data');
		frm.clear_table('custom_non_batch_items_data');
	}
});