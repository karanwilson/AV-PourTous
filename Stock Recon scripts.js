frappe.listview_settings['Stock Reconciliation'] = {
    refresh(listview) {
        listview.page.add_inner_button("Process DraftRecon Batches", () => {
            setTimeout(() => {
                frappe.call({
                    method: 'pourtous.api.fetch_pending_stock_recons',
                });
                frappe.show_alert({message: __('Initiated Background Submits of stock recons'), indicator: 'green'});
            }, 0);
        });
    }
};