frappe.ui.form.on('Purchase Receipt', {
	before_save(frm) {
		frm.set_value('disable_rounded_total', 0);

		if (frm.doc.items && frappe.defaults.get_user_default("company") == "Pour Tous Purchasing Service") {
			if (!frm.doc.is_return) {
				frm.doc.items.forEach((item) => {
					if (item.warehouse == "Stores - PTPS") {
						frappe.throw(__("We are migrating stock from the common '{0}' to segregated stores: please set the correct Store/Warehouse", [item.warehouse]));
					}
					else {
						frappe.call('pourtous.api.set_item_default_warehouse', {
							item_code: item.item_code,
							warehouse: item.warehouse
						});
					}
				});
			}
		}
		if (frm.doc.discount_amount < 0 || frm.doc.additional_discount_percentage < 0) {
			frappe.throw(__("Discount Amount/Percentage should be positive"));
		}
	},
    /* supplier(frm) {
        frm.set_query('item_code', 'items', () => {
            return {
                query: 'pourtous.api.supplier_items_filter',
                txt: frm.doc.supplier
            };
        });
    }, */
});
