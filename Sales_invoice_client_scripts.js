frappe.listview_settings['Sales Invoice'] = {
    refresh(listview) {

        listview.page.add_inner_button("FS Inv to ZB", () => {
            frappe.call({
                method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.fetch_unsynced_erp_fs_invoice_list',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Number of FS invoices to sync: ", length);
                        console.log("Invoice List: ", r.message);
                        //console.log("r.message[0]['name']: ", r.message[0]["name"]);
                        let added = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.sync_fs_inv_with_zoho_books',
                                    args: {
                                        invoice: r.message[i]["name"],
                                        customer: r.message[i]["customer"],
                                    },
                                    async: false,
                                }).then(r => {
                                    if (r.message == "ADDED")
                                        added++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Added ", added, ", of ", length);
                                });
                                const count = i+1;
                                const message = "Adding "+count+" of "+length;
                                frappe.show_progress("Pushing FS Invoices to Zoho Books", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        }, __("Sync with ZB"));


        listview.page.add_inner_button("Aurocard Inv to ZB", () => {
            frappe.call({
                method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.fetch_unsynced_erp_aurocard_invoice_list',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Number of Aurocard invoices to sync: ", length);
                        console.log("Invoice List: ", r.message);
                        //console.log("r.message[0]['name']: ", r.message[0]["name"]);
                        let added = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.sync_aurocard_inv_with_zoho_books',
                                    args: {
                                        invoice: r.message[i]["name"],
                                    },
                                    async: false,
                                }).then(r => {
                                    if (r.message == "ADDED")
                                        added++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Added ", added, ", of ", length);
                                });
                                const count = i+1;
                                const message = "Adding "+count+" of "+length;
                                frappe.show_progress("Pushing Aurocard Invoices to Zoho Books", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        }, __("Sync with ZB"));


        listview.page.add_inner_button("UPI Inv to ZB", () => {
            frappe.call({
                method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.fetch_unsynced_erp_upi_invoice_list',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Number of UPI invoices to sync: ", length);
                        console.log("Invoice List: ", r.message);
                        //console.log("r.message[0]['name']: ", r.message[0]["name"]);
                        let added = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.sync_upi_inv_with_zoho_books',
                                    args: {
                                        invoice: r.message[i]["name"],
                                    },
                                    async: false,
                                }).then(r => {
                                    if (r.message == "ADDED")
                                        added++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Added ", added, ", of ", length);
                                });
                                const count = i+1;
                                const message = "Adding "+count+" of "+length;
                                frappe.show_progress("Pushing UPI Invoices to Zoho Books", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        }, __("Sync with ZB"));


        listview.page.add_inner_button("Adv Inv to ZB", () => {
            frappe.call({
                method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.fetch_unsynced_erp_adv_payment_invoice_list',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Number of Adv invoices to sync: ", length);
                        console.log("Invoice List: ", r.message);
                        //console.log("r.message[0]['name']: ", r.message[0]["name"]);
                        let added = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.sync_adv_payment_inv_with_zoho_books',
                                    args: {
                                        invoice: r.message[i]["name"],
                                        customer: r.message[i]["customer"],
                                    },
                                    async: false,
                                }).then(r => {
                                    if (r.message == "ADDED")
                                        added++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Added ", added, ", of ", length);
                                });
                                const count = i+1;
                                const message = "Adding "+count+" of "+length;
                                frappe.show_progress("Pushing UPI Invoices to Zoho Books", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        }, __("Sync with ZB"));


        listview.page.add_inner_button("CreditNotes to ZB", () => {
            frappe.call({
                method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.fetch_unsynced_erp_return_invoice_list',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Number of Return invoices to sync: ", length);
                        console.log("Invoice List: ", r.message);
                        //console.log("r.message[0]['name']: ", r.message[0]["name"]);
                        let added = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.sync_return_inv_with_zoho_books',
                                    args: {
                                        invoice: r.message[i]["name"],
                                        customer: r.message[i]["customer"]
                                    },
                                    async: false,
                                }).then(r => {
                                    if (r.message == "ADDED")
                                        added++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Added ", added, ", of ", length);
                                });
                                const count = i+1;
                                const message = "Adding "+count+" of "+length;
                                frappe.show_progress("Pushing Return Invoices to Zoho Books", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        }, __("Sync with ZB"));


        listview.page.add_inner_button("Orders to Invoices", () => {
            frappe.call({
                method: 'pourtous.api.fetch_orders_to_invoice',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message[0].length;
                        console.log("Number of SO to process: ", length);
						console.log("Sales Orders to Invoice: ", r.message);
						console.log("SO to SI: ", r.message[0][0]);
                        /* console.log("r.message[0][0][0]: ", r.message[0][0][0]);
                        console.log("r.message[0][0][1]: ", r.message[0][0][1]);
                        console.log("r.message[0][10][2]: ", r.message[0][10][0]);
                        console.log("r.message[0][10][3]: ", r.message[0][10][1]);
                        console.log("is_tax_inclusive: ", r.message[1]); */
                        let done = 0, error = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.api.process_orders_to_invoice',
                                    args: {
                                        order: r.message[0][i][0],
                                        pos_profile: r.message[0][i][1],
                                        order_date: r.message[0][i][2],
                                        order_time: r.message[0][i][3],
                                        is_tax_inclusive: r.message[1],
                                    },
                                    async: false,
                                }).then(r => {
                                    if (r.message == "DONE")
                                        done++;
                                    else if (r.message == "ERROR")
                                        error++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Created Invoices: ", done, "; Error: ", error, "; of total ", length, " Sales Orders");
                                });
                                const count = i+1;
                                const message = "Loading "+count+" of "+length;
                                frappe.show_progress("Processing Sales Orders to Invoices", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        });

        listview.page.add_inner_button("Process FS Credits", () => {
            frappe.call({
                method: 'payments.payment_gateways.doctype.fs_settings.fs_settings.fetch_fs_credit_bills',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Number of Credit Bills to process: ", length);
                        //console.log('r.message[0]: ', r.message[0]);
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
        })

        /* listview.page.add_inner_button("DelZBInvP", () => {
            frappe.call({
                method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.fetch_invoices_to_delete',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Number of invoices to delete: ", length);
                        console.log("Invoice List: ", r.message);
                        //console.log("r.message[0][0]: ", r.message[0][0]);
                        let deleted = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.delete_invoice_ids_in_erp',
                                    args: {
                                        invoice: r.message[i]["name"],
                                        //custom_zoho_invoice_id: r.message[i]["custom_zoho_invoice_id"]
                                    },
                                    async: false,
                                }).then(r => {
                                    if (r.message == "DELETED")
                                        deleted++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Deleted ", deleted, ", of ", length);
                                });
                                const count = i+1;
                                const message = "Deleting "+count+" of "+length;
                                frappe.show_progress("Deleting Invoice IDs in ERP", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        }, __("Sync with ZB")); */


        /* listview.page.add_inner_button("Delete ZB Payments CN CN-Refunds", () => {
            frappe.call({
                method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.fetch_payments_cn_refunds_to_delete',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Number of payments to delete: ", length);
                        console.log("Payments List: ", r.message);
                        //console.log("r.message[0]['name']: ", r.message[0]["name"]);
                        let deleted = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.delete_customer_payments_cn_refunds_in_zb',
                                    args: {
                                        invoice: r.message[i]["name"],
                                        custom_zoho_payment_id: r.message[i]["custom_zoho_payment_id"],
                                        //custom_zb_creditnote_id: r.message[i]["custom_zb_creditnote_id"],
                                        //custom_zb_creditnote_refund_id: r.message[i]["custom_zb_creditnote_refund_id"],
                                    },
                                    async: false,
                                }).then(r => {
                                    if (r.message == "DELETED")
                                        deleted++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Deleted ", deleted, ", of ", length);
                                });
                                const count = i+1;
                                const message = "Deleting "+count+" of "+length;
                                frappe.show_progress("Deleting Payments in Zoho Books", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        }, __("Sync with ZB")); */

        /* listview.page.add_inner_button("Update ERP Invoices in ZB", () => {
            frappe.call({
                method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.fetch_erp_invoice_list_to_update',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Number of ERP invoices to update: ", length);
                        console.log("Invoice List: ", r.message);
                        //console.log("r.message[0]['name']: ", r.message[0]["name"]);
                        let added = 0;
                        for (let i = 0; i < 2; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.update_erp_inv_with_zoho_books',
                                    args: {
                                        invoice: r.message[i]["name"],
                                    },
                                    async: false,
                                }).then(r => {
                                    if (r.message == "ADDED")
                                        added++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Added ", added, ", of ", length);
                                });
                                const count = i+1;
                                const message = "Adding "+count+" of "+length;
                                frappe.show_progress("Updating ERP Invoices in Zoho Books", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        }, __("Sync with ZB"));


        listview.page.add_inner_button("TaxExc Process Orders to Invoices", () => {
            frappe.call({
                method: 'pourtous.api.tax_exception_fetch_orders_to_invoice',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Number of SO to process: ", length);
						console.log("Sales Orders to Invoice: ", r.message);
                        //console.log("r.message[0][0]: ", r.message[0][0]);
                        let done = 0, error = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.api.tax_exception_process_orders_to_invoice',
                                    args: { order: r.message[i][0] },
                                    async: false,
                                }).then(r => {
                                    if (r.message == "DONE")
                                        done++;
                                    else if (r.message == "ERROR")
                                        error++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Created Invoices: ", done, "; Error: ", error, "; of total ", length, " Sales Orders");
                                });
                                const count = i+1;
                                const message = "Loading "+count+" of "+length;
                                frappe.show_progress("Processing Sales Orders to Invoices", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        }); */
    }
};