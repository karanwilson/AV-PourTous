frappe.listview_settings['Customer'] = {
    refresh(listview) {
        listview.page.add_inner_button("Sync FS Accounts", () => {
            frappe.call('pourtous.api.sync_fs_accounts');
        });
    },
};