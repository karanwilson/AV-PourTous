frappe.ui.form.on('Purchase Order', {
	//refresh(frm) {
		// your code here
	//}
	supplier(frm) {
		frappe.call({
			method: 'pourtous.api.supplier_items',
			args: {
				supplier: frm.doc.supplier
			},
			callback: (r) => {
				frm.clear_table('custom_supplier_items_data');
				for (const row of r.message) {
					let item_row = frm.add_child('custom_supplier_items_data');
					item_row.item_code = row[0];
					item_row.item_name = row[1];
					item_row.buying_price = row[2];
					item_row.selling_price = row[3];
					item_row.ordered_qty = row[4];
					item_row.current_qty = row[6];
					item_row.sold_last_month = row[7];
					item_row.sold_this_month = row[8];
				}
				frm.refresh_field('custom_supplier_items_data');
			}
		});
	},
	custom_add_to_items(frm) {
		frm.clear_table('items');
	    let selected = frm.get_selected();
	    selected.custom_supplier_items_data.forEach((row) => {
			const item = locals["PO Supplier Items"][row];
	        let item_row = frm.add_child('items');
	        //frappe.model.set_value triggers a form event that loads other Item data fields like rate, etc.
	        frappe.model.set_value(item_row.doctype, item_row.name, 'item_code', item.item_code);
	        item_row.qty = item.to_buy;
	    });
		frm.refresh_field('items');
		frm.clear_table('custom_supplier_items_data');
		frm.refresh_field('custom_supplier_items_data');
	}
});