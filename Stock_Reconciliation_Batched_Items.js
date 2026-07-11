frappe.ui.form.on('Stock Reconciliation', {
	//refresh(frm) {
		// your code here
	//},

	onload: function (frm) {
		frm.set_query("batch_no", "items", function (doc, cdt, cdn) {
			var item = locals[cdt][cdn];
			return {
				filters: {
					item: item.item_code,
					batch_qty: ["!=", 0]
				},
			};
		});
	},
});

frappe.ui.form.on('Stock Reconciliation Item', {
	item_code: function (frm, cdt, cdn) {
		var d = locals[cdt][cdn];

		frappe.call({
			method: 'pourtous.api.stock_recon_total_store_qty',
			args: {
				item_code: d.item_code,
				warehouse: d.warehouse
			},
			async: false,
			callback: (r) => {
				if (r.message) {
					console.log('r.message[0]["custom_total_qty"] : ', r.message[0]["custom_total_qty"]);
					frappe.model.set_value(cdt, cdn, "custom_total_qty", r.message[0]["custom_total_qty"]);
				}
			}
		});

		// frappe.db.get_value("tabStock Ledger Entry", { 
		// 	item_code: d.item_code,
		// 	is_cancelled: 0,
		// 	warehouse: ["LIKE", d.warehouse+"%"]
		//  }, "qty_after_transaction", (r) => {
		// 	frappe.model.set_value(cdt, cdn, "fieldname", r.fieldname);
		// });
	},
});
// Templated from: apps/erpnext/erpnext/stock/doctype/purchase_receipt/purchase_receipt.js
// and apps/erpnext/erpnext/selling/doctype/sales_order/sales_order.js
// and apps/erpnext/erpnext/controllers/website_list_for_contact.py