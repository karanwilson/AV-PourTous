frappe.ui.form.on('Stock Entry', {
	custom_batch_barcode(frm) {
		if (frm.doc.custom_batch_barcode) {
			const batch_no = frm.doc.custom_batch_barcode.slice(3,12);
			console.log('batch_no: ', batch_no);
			frm.set_value('scan_barcode', batch_no);
		}
		frm.set_value('custom_batch_barcode', '');
	}
});