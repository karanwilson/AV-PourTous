frappe.listview_settings['Customer'] = {
    refresh(listview) {
        listview.page.add_inner_button("Fetch FS Accounts", () => {
            frappe.call({
                method: 'payments.payment_gateways.doctype.fs_settings.fs_settings.fetch_fs_accounts_detail',
                freeze: true,
                freeze_message: "Fetching FS Accounts",
                callback: (r) => {
                    //this.refresh();
                    location.reload();
                }
            });
        });

        listview.page.add_inner_button("Sync FS Accounts", () => {
            frappe.call({
                method: 'pourtous.api.sync_fs_accounts',
                freeze: true,
                freeze_message: "Syncing FS Accounts",
                callback: (r) => {
                    //this.refresh();
                    location.reload();
                }
            });
        });
    },
};