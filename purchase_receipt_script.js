frappe.ui.form.on('Purchase Receipt', {
	refresh(frm) {
		console.log("(Refresh) frappe.session.user_fullname: ", frappe.session.user_fullname);
		if (frappe.session.user_fullname != 'Administrator' && frappe.session.user_fullname != 'Kalki')
			{
				frm.set_query('supplier', () => {
					return {
						filters: {
							supplier_name: frappe.session.user_fullname
						}	
					};
				});
			}

        frm.set_value('taxes_and_charges', 'Input GST In-state - M')
            .then(() => {
                frm.refresh_field('taxes_and_charges');
            });
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
