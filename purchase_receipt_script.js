frappe.ui.form.on('Purchase Receipt', {
	refresh(frm) {
        frm.set_value('taxes_and_charges', 'Input GST In-state - PTPS')
            .then(() => {
                frm.refresh_field('taxes_and_charges');
            })
	},

/*     supplier(frm) {
        frm.set_query('item_code', 'items', () => {
            return {
                query: 'pourtous.api.supplier_items_filter',
                txt: frm.doc.supplier
            };
        });
    },

    after_save(frm) {
        let custom_rate_with_tax = 0;
        frm.doc.items.forEach((item) => {
            custom_rate_with_tax = (item.amount + item.cgst_amount + item.sgst_amount)/item.qty;
            item.custom_rate_with_tax = custom_rate_with_tax;
            frm.refresh_field(frm.doc.items);
        });
    } */
});
