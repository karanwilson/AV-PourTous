frappe.listview_settings['Purchase Invoice'] = {
    refresh(listview) {
        listview.page.add_inner_button("Update Batch Prices", () => {
            frappe.call({
                method: 'pourtous.api.fetch_pur_inv_list',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Number of Invoices: ", length);
						console.log("Invoice List: ", r.message);
                        // console.log("r.message[0]['name']: ", r.message[0]["name"]);
                        let updated = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.api.update_batch_price_pur_inv_rec',
                                    args: {
                                        doctype: 'Purchase Invoice',
                                        doc_name: r.message[i]["name"],
                                    },
                                    async: false,
                                }).then(r => {
                                    if (r.message == "UPDATED")
                                        updated++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Updated ", updated, ", of ", length);
                                });
                                const count = i+1;
                                const message = "Updated "+count+" of "+length;
                                frappe.show_progress("Updating Batch Prices", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        });


        // listview.page.add_inner_button("Add ERP bills in ZB", () => {
        //     frappe.call({
        //         method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.fetch_erp_bills_list',
        //         async: false,
        //         callback: (r) => {
        //             if (r.message) {
        //                 const length = r.message.length;
        //                 console.log("Number of Bills to add: ", length);
		// 				console.log("Bills List: ", r.message);
        //                 //console.log("r.message[0]['name']: ", r.message[0]["name"]);
        //                 let added = 0;
        //                 for (let i = 0; i < length; i++) {
        //                     setTimeout(() => {
        //                         frappe.call({
        //                             method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.add_erp_bill_debitnote_in_zoho',
        //                             args: {
        //                                 bill: r.message[i]["name"]
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
        //                         frappe.show_progress("Pushing Bills to Zoho Books", count, length, message);
        //                     }, 0);
        //                 }
        //             }
        //         }
        //     });
        // }, __("Sync with ZB"));

        listview.page.add_inner_button("Add ERP bills in ZB (in background)", () => {
            setTimeout(() => {
                frappe.call({
                    method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.fetch_erp_bills_list',
                });
                frappe.show_alert({message: __('Initiated Background Push of Purchase Invoices to Zoho Books'), indicator: 'green'});
            }, 0);
        }, __("Sync with ZB"));

        listview.page.add_inner_button("Push bill attachments to ZB", () => {
            frappe.call({
                method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.fetch_file_attachments_in_bills',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Number of Bill-Attachments to push: ", length);
						console.log("Attachments List: ", r.message);
                        //console.log("r.message[0]['name']: ", r.message[0]["name"]);
                        let added = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.attach_file_to_bill',
                                    args: {
                                        file_docname: r.message[i]["name"],
                                        bill_id: r.message[i]["custom_zoho_bill_id"],
                                        file_name: r.message[i]["file_name"],
                                        file_url: r.message[i]["file_url"]
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
                                frappe.show_progress("Pushing Bill Attachments to Zoho Books", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        }, __("Sync with ZB"));


        // listview.page.add_inner_button("Add ERP debitnotes in ZB", () => {
        //     frappe.call({
        //         method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.fetch_erp_debitnotes_list',
        //         async: false,
        //         callback: (r) => {
        //             if (r.message) {
        //                 const length = r.message.length;
        //                 console.log("Number of Bills to add: ", length);
		// 				console.log("Contacts List: ", r.message);
        //                 //console.log("r.message[0]['name']: ", r.message[0]["name"]);
        //                 let added = 0;
        //                 for (let i = 0; i < length; i++) {
        //                     setTimeout(() => {
        //                         frappe.call({
        //                             method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.add_erp_bill_debitnote_in_zoho',
        //                             args: {
        //                                 bill: r.message[i]["name"]
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
        //                         frappe.show_progress("Pushing Debitnotes to Zoho Books", count, length, message);
        //                     }, 0);
        //                 }
        //             }
        //         }
        //     });
        // }, __("Sync with ZB"));

        listview.page.add_inner_button("Add ERP debitnotes in ZB (in background)", () => {
            setTimeout(() => {
                frappe.call({
                    method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.fetch_erp_debitnotes_list',
                    // async: false,
                });
            }, 0);
            frappe.show_alert({message: __('Initiated Background Push of Purchase Returns to Zoho Books'), indicator: 'green'});
        }, __("Sync with ZB"));

        /* listview.page.add_inner_button("Set Vendor Bills unique", () => {
            frappe.call({
                method: 'pourtous.api.fetch_purchase_invoices',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Number of Bills to add: ", length);
						console.log("Bills List: ", r.message);
                        console.log("r.message[0]['name']: ", r.message[0]["name"]);
                        let added = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.api.set_vendor_bills_unique',
                                    args: {
                                        bill: r.message[i]["name"]
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
                                frappe.show_progress("Pushing Bills to Zoho Books", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        }); */

        /* listview.page.add_inner_button("Delete specific bills in ZB", () => {
            frappe.call({
                method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.fetch_bills_to_delete',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Number of bills to sync: ", length);
						console.log("Bills List: ", r.message);
                        //console.log("r.message[0]['name']: ", r.message[0]["name"]);
                        let deleted = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.delete_bills_in_zoho',
                                    args: {
                                        bill: r.message[i]["name"],
                                        custom_zoho_bill_id: r.message[i]["custom_zoho_bill_id"]
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
                                frappe.show_progress("Deleting Bills in Zoho Books", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        }, __("Sync with ZB")); */
    },
};