frappe.listview_settings['Sales Invoice'] = {
    refresh(listview) {
        listview.page.add_inner_button("Submit Offline FS Bills", () => {
            frappe.call('payments.payment_gateways.doctype.fs_settings.fs_settings.add_transfer_draft_fs_bills');
        });
    },
};