frappe.listview_settings['Customer'] = {
    refresh(listview) {
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