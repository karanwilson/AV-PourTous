frappe.ui.form.on('Sales Order', {
	refresh(frm) {
        if (frm.doc.docstatus === 0 && !frm.doc.taxes_and_charges) {
            frappe.call('pourtous.api.get_sales_tax_template')
            .then(r => {
                frm.set_value('taxes_and_charges', r.message[0].name)
                    .then(() => {
                        frm.refresh_field('taxes_and_charges');
                    });
            });
            /* if (frm.doc.customer && (frm.doc.advances.length === 0 && frm.doc.is_return === 0)) {
                //console.log("trigerring get_advances");
                frm.trigger('get_advances');
            } */
        }
	},
});
