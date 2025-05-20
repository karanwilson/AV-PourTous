frappe.ui.form.on('Purchase Receipt', {
	refresh(frm) {
        frappe.call('pourtous.api.get_tax_template')
            .then(r => {
                frm.set_value('taxes_and_charges', r.message[0].name)
                    .then(() => {
                        frm.refresh_field('taxes_and_charges');
                    });
            });
        frm.set_value('disable_rounded_total', 0);
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
