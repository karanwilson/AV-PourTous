frappe.ui.form.on('Stock Entry', {
	before_submit(frm) {
		if (frm.doc.stock_entry_type == "Repack") {
			frm.doc.items.forEach((item) => {
				if (!item.custom_selling_price) {
					frappe.throw(__("Please enter the Selling Price for '{0}': '{1}'", [item.item_code, item.item_name]));
				}
			});
		}
	}
	// custom_batch_barcode(frm) {
	// 	if (frm.doc.custom_batch_barcode) {
	// 		const batch_no = frm.doc.custom_batch_barcode.slice(3,12);
	// 		console.log('batch_no: ', batch_no);
	// 		frm.set_value('scan_barcode', batch_no);
	// 	}
	// 	frm.set_value('custom_batch_barcode', '');
	// }
});