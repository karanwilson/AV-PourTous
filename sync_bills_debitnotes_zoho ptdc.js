frappe.listview_settings['Purchase Invoice'] = {
    refresh(listview) {
        listview.page.add_inner_button("Add ERP bills in ZB", () => {
            setTimeout(() => {
                frappe.call({
                    method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.fetch_erp_bills_list',
                });
                frappe.show_alert({message: __('Initiated Background Push of Purchase Invoices to Zoho Books'), indicator: 'green'});
            }, 0);
        }, __("Sync with ZB"));


        listview.page.add_inner_button("Add ERP debitnotes in ZB", () => {
            setTimeout(() => {
                frappe.call({
                    method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.fetch_erp_debitnotes_list',
                    // async: false,
                });
            }, 0);
            frappe.show_alert({message: __('Initiated Background Push of Purchase Returns to Zoho Books'), indicator: 'green'});
        }, __("Sync with ZB"));
    },
};