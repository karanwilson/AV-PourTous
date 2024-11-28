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

        listview.page.add_inner_button("Process FS Credit Bills", () => {
            frappe.call({
                method: 'payments.payment_gateways.doctype.fs_settings.fs_settings.fetch_fs_credit_bills',
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Number of Credit Bills to process: ", length);
                        let transfers = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'payments.payment_gateways.doctype.fs_settings.fs_settings.add_transfer_fs_credit_bill',
                                    args: { bill: r.message[i][0] },
                                    async: false,
                                    callback: (r) => {
                                        if (r.message == "OK")
                                            transfers++;
                                    }
                                });
                                const count = i+1;
                                const message = "Loading "+count+" of "+length;
                                frappe.show_progress("Processing FS Credit Bills", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        });

        /* listview.page.add_inner_button("Exception Process FS Credit Bills", () => {
            frappe.call({
                method: 'payments.payment_gateways.doctype.fs_settings.fs_settings.exception_add_transfer_fs_credit_bills',
                freeze: true,
                freeze_message: "Processing Exception FS Credit Bills",
                callback: (r) => {
                    //this.refresh();
                    location.reload();
                }
            });
        }); */
    },
};