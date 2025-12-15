frappe.ui.form.on('Purchase Order', {
	supplier(frm) {
		frm.clear_table('items');
	},

	custom_items_fetch(frm) {
		frm.clear_table('custom_items_data');
		frappe.call({
			method: 'pourtous.api.supplier_items',
			args: {
				supplier: frm.doc.supplier
			},
			callback: (r) => {
				if (r.message.length > 0) {
					for (const row of r.message) {
						let item_row = frm.add_child('custom_items_data');
						item_row.item_code = row["item_code"];
						item_row.item_name = row["item_name"];
						item_row.store_qty = row["store_qty"];
						item_row.stall_qty = row["stall_qty"];
						item_row.str1_qty = row["str1_qty"];
						item_row.str2_qty = row["str2_qty"];
						item_row.str3_qty = row["str3_qty"];
						item_row.sold_last_month = row["sold_last_month"];
						item_row.sold_this_month = row["sold_this_month"];
						item_row.last_buy_price = row["last_buy_price"];
						item_row.last_order_qty = row["last_order_qty"];
						item_row.to_buy = 0;
						//console.log("row: ", row);
					}
				}
				else frappe.msgprint({
					title: __('Notification'),
					indicator: 'red',
					message: __('No Data')
				});
				frm.refresh_field('custom_items_data');
			}
		});
		/* frm.set_query('item_code', 'items', () => {
			return {
				query: 'pourtous.api.supplier_items_filter',
				txt: frm.doc.supplier
			}
		}) */
	},

	custom_add_items(frm) {
	    let selected = frm.get_selected();
	    selected.custom_items_data.forEach((row) => {
			const itemToAdd = locals["PO Supplier Items"][row];
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
		//frm.refresh_field('custom_items_data');
	},
});