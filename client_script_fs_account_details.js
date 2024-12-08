frappe.listview_settings['FS Account Details'] = {
    refresh(listview) {
        listview.page.add_inner_button("Fetch FS Accounts", () => {
            frappe.call({
                method: 'payments.payment_gateways.doctype.fs_settings.fs_settings.fetch_fs_accounts_detail',
                freeze: true,
                freeze_message: "Fetching FS Accounts",
                callback: (r) => {
                    //this.refresh();
					console.log(r.message);
                    //location.reload();
                }
            });
        });
    },
};