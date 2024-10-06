frappe.listview_settings['Sales Invoice'] = {
    refresh(listview) {
        listview.page.add_inner_button("Submit Offline FS Bills", () => {
            frappe.call({
                method: 'payments.payment_gateways.doctype.fs_settings.fs_settings.add_transfer_fs_draft_bills',
                freeze: true,
                freeze_message: "Processing Offline FS Bills",
                callback: (r) => {
                    //this.refresh();
                    location.reload();
                }
            });
        });
    },
};