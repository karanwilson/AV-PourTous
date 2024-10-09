frappe.ui.form.on('Purchase Order', {
	//refresh(frm) {
		// your code here
	//}
	supplier(frm) {
		frm.clear_table('items');
		frappe.call({
			method: 'pourtous.api.supplier_batch_items',
			args: {
				supplier: frm.doc.supplier
			},
			callback: (r) => {
				if (r.message.length > 0) {
					frm.clear_table('custom_supplier_items_data');
					for (const row of r.message) {
						let item_row = frm.add_child('custom_supplier_items_data');
						item_row.item_code = row["item_code"];
						item_row.item_name = row["item_name"];
						item_row.buying_price = row["buying_price"];
						item_row.selling_price = row["selling_price"];
						item_row.ordered_qty = row["ordered_qty"];
						item_row.current_qty = row["current_qty"];
						item_row.sold_last_month = row["sold_last_month"];
						item_row.sold_this_month = row["sold_this_month"];
						console.log("row: ", row);
					}
				}
				else {
					console.log("No batch data");
					frappe.call({
						method: 'pourtous.api.supplier_items',
						args: {
							supplier: frm.doc.supplier
						},
						callback: (r) => {
							frm.clear_table('custom_supplier_items_data');
							for (const row of r.message) {
								let item_row = frm.add_child('custom_supplier_items_data');
								item_row.item_code = row["item_code"];
								item_row.item_name = row["item_name"];
								item_row.buying_price = row["buying_price"];
								item_row.selling_price = row["selling_price"];
								item_row.ordered_qty = row["ordered_qty"];
								item_row.current_qty = row["current_qty"];
								item_row.sold_last_month = row["sold_last_month"];
								item_row.sold_this_month = row["sold_this_month"];
								console.log("row: ", row);
							}
						}
					})
				}
				frm.refresh_field('custom_supplier_items_data');
			}
		});
		frm.set_query('item_code', 'items', () => {
			return {
				query: 'pourtous.api.supplier_items_filter',
				txt: frm.doc.supplier
			}
		})
	},
	custom_add_to_items(frm) {
		//frm.clear_table('items');
	    let selected = frm.get_selected();
	    selected.custom_supplier_items_data.forEach((row) => {
			const item = locals["PO Supplier Items"][row];
	        let item_row = frm.add_child('items');
	        //frappe.model.set_value triggers a form event that loads other Item data fields like rate, etc.
	        frappe.model.set_value(item_row.doctype, item_row.name, 'item_code', item.item_code);
	        item_row.qty = item.to_buy;
	    });
		frm.refresh_field('items');
		//frm.clear_table('custom_supplier_items_data');
		frm.refresh_field('custom_supplier_items_data');
	},
	before_submit(frm) {
		frm.clear_table('custom_supplier_items_data');
	}
});