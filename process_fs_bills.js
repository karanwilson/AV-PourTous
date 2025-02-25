frappe.listview_settings['Sales Invoice'] = {
    refresh(listview) {
        listview.page.add_inner_button("Process FS Credit Bills", () => {
            frappe.call({
                method: 'payments.payment_gateways.doctype.fs_settings.fs_settings.fetch_fs_credit_bills',
                async: false,
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
                                }).then(r => {
                                    if (r.message == "OK")
                                        transfers++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Received transfers for ", transfers, " of ", length, " Invoices");
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


        listview.page.add_inner_button("Sync with Zoho Books", () => {
            frappe.call({
                method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.fetch_unsynced_sales_invoice_list',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Number of Sales Invoices to sync: ", length);
                        let transfers = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.sync_with_zoho_books',
                                    args: { bill: r.message[i][0] },
                                    async: false,
                                }).then(r => {
                                    if (r.message == "OK")
                                        transfers++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Synced ", transfers, " of ", length, " Invoices");
                                });
                                const count = i+1;
                                const message = "Syncing "+count+" of "+length;
                                frappe.show_progress("Syncing with Zoho Books", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        });


        listview.page.add_inner_button("Get Zoho Books Auth Code", () => {
            frappe.call({
                method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.generate_grant_token',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        console.log(r.message);
                    }
                }
            });
        });

        /* listview.page.add_inner_button("Exception Process FS Credit Bills", () => {
            frappe.call({
                method: 'payments.payment_gateways.doctype.fs_settings.fs_settings.fetch_exception_fs_credit_bills',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Number of Exception Credit Bills to process: ", length);
                        let transfers = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'payments.payment_gateways.doctype.fs_settings.fs_settings.add_transfer_exception_fs_credit_bill',
                                    args: { bill: r.message[i][0] },
                                    async: false,
                                }).then(r => {
                                    if (r.message == "OK")
                                        transfers++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Received transfers for ", transfers, " of ", length, " Invoices");
                                });
                                const count = i+1;
                                const message = "Loading "+count+" of "+length;
                                frappe.show_progress("Processing Exception FS Credit Bills", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        }); */
    },
};