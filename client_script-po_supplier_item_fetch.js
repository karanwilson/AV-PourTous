frappe.ui.form.on('Purchase Order', {
	//refresh(frm) {
		// your code here
	//}
	supplier(frm) {
		frappe.call('pourtous.api.supplier_items', {
		    supplier: frm.doc.supplier
		}).then(r => {
		    r.message.forEach(item => {
		        frm.add_child('custom_supplier_item_data', {
		            item_code: '',
		            item_name: '',
		            item_group: '',
		            buying_price: '',
		            selling_price: '',
		            ordered_qty: '',
		            current_qty: '',
		            sold_last_month: '',
		            sold_this_month: ''
		        });
		    });
		});
	},
	custom_add_to_items(frm) {
	    let selected = frm.get_selected('custom_supplier_item_data');
	    selected.forEach(item => {
	        frm.add_child('items', {
	            item_code: item.item_code,
	            qty: item.to_buy
	        });
	    });
	}
});