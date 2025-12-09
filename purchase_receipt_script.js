frappe.ui.form.on('Purchase Receipt', {
	before_save(frm) {
		frm.set_value('disable_rounded_total', 0);

        frm.doc.items.forEach((item) => {
			frappe.call('pourtous.api.set_item_default_warehouse', {
				item_code: item.item_code,
				warehouse: item.warehouse
			});
		});
	}
    /* supplier(frm) {
        frm.set_query('item_code', 'items', () => {
            return {
                query: 'pourtous.api.supplier_items_filter',
                txt: frm.doc.supplier
            };
        });
    }, */
});
