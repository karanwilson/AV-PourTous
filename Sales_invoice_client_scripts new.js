frappe.listview_settings['Sales Invoice'] = {
    refresh(listview) {

        // listview.page.add_inner_button("Sales Inv to ZB", () => {
        //     frappe.call('pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.fetch_unsynced_erp_invoice_list');
        //     frappe.show_alert({message: __('Initiated Background Push of Invoices to Zoho Books'), indicator: 'green'});

        //     // frappe.call({
        //     //     method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.fetch_unsynced_erp_invoice_list',
        //     //     async: true,
        //     //     callback: (r) => {
        //     //         if (!r.exc) {
        //     //             frappe.show_alert({message: __('Initiated Background Push of Invoices to Zoho Books'), indicator: 'green'});
        //     //         }
        //     //     }
        //     // });
        // }, __("Sync with ZB"));


        // listview.page.add_inner_button("CreditNotes to ZB", () => {
        //     frappe.call({
        //         method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.fetch_unsynced_erp_return_invoice_list',
        //         async: false,
        //         callback: (r) => {
        //             if (r.message) {
        //                 const length = r.message.length;
        //                 console.log("Number of Return invoices to sync: ", length);
        //                 console.log("Invoice List: ", r.message);
        //                 //console.log("r.message[0]['name']: ", r.message[0]["name"]);
        //                 let added = 0;
        //                 for (let i = 0; i < length; i++) {
        //                     setTimeout(() => {
        //                         frappe.call({
        //                             method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.sync_return_inv_with_zoho_books',
        //                             args: {
        //                                 invoice: r.message[i]["name"],
        //                                 customer: r.message[i]["customer"]
        //                             },
        //                             async: false,
        //                         }).then(r => {
        //                             if (r.message == "ADDED")
        //                                 added++;
        //                         }).then(r => {
        //                             // placing this statement block here as it does not work outside of the main frappe.call block
        //                             // though it prints on console for each loop iteration (comes in only one line, with the loop count),
        //                             // it shows an accurate result in the end. This design works.
        //                             console.log("Added ", added, ", of ", length);
        //                         });
        //                         const count = i+1;
        //                         const message = "Adding "+count+" of "+length;
        //                         frappe.show_progress("Pushing Return Invoices to Zoho Books", count, length, message);
        //                     }, 0);
        //                 }
        //             }
        //         }
        //     });
        // }, __("Sync with ZB"));


        listview.page.add_inner_button("Process FS Credits", () => {
            frappe.call({
                method: 'payments.payment_gateways.doctype.fs_settings.fs_settings.fetch_fs_credit_bills',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Number of Credit Bills to process: ", length);
                        console.log('r.message: ', r.message);
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
        }, __("FS Credit Bills"));


        // listview.page.add_inner_button("Process FS Credits in background", () => {
        //     frappe.call('payments.payment_gateways.doctype.fs_settings.fs_settings.process_fs_credit_bills');
        //     frappe.show_alert({message: __('Initiated Background Process of FS Credit Bills'), indicator: 'green'});

        //     // frappe.call({
        //     //     method: 'payments.payment_gateways.doctype.fs_settings.fs_settings.process_fs_credit_bills',
        //     //     async: true,
        //     //     callback: (r) => {
        //     //         if (!r.exc) {
        //     //             frappe.show_alert({message: __('Initiated Background Process of FS Credit Bills'), indicator: 'green'});
        //     //         }
        //     //     }
        //     // });
        // }, __("FS Credit Bills"));

    }
};