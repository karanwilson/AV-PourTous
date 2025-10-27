frappe.listview_settings['Item'] = {
    refresh(listview) {
        /* listview.page.add_inner_button("Sync ZB ItemIDs with ERP", () => {
            frappe.call({
                method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.get_zb_item_list',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Length of the ZB Item List: ", length);
						console.log("Item List: ", r.message);
                        let updated = 0, no_match = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.sync_zb_item_id_with_erp',
                                    args: {
                                        item_id: r.message[i]["item_id"],
                                        item_name: r.message[i]["item_name"],
                                    },
                                    async: false,
                                }).then(r => {
                                    if (r.message == "UPDATED")
                                        updated++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Item IDs Updated: ", updated);
                                });
                                const count = i+1;
                                const message = "Updating "+count+" of "+length;
                                frappe.show_progress("Syncing Zoho Books Item IDs with ERP", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        }, __("Sales Invoice")); */


        listview.page.add_inner_button("Delete ERP Items in ZB", () => {
            frappe.call({
                method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.custom_fetch_erp_items_list_from_file',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Length of the ERP Items List: ", length);
						console.log("Items List: ", r.message);
                        //console.log("Item[0]: ", r.message[0]);
                        //length = 1000;
                        //console.log("Limiting Length to: ", length);
                        let deleted = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.custom_delete_item_in_zoho',
                                    args: {
                                        //erp_item: r.message[i]["name"],
                                        //custom_zoho_item_id: r.message[i]["custom_zoho_item_id"],
                                        custom_zoho_item_id: r.message[i],
                                    },
                                    async: false,
                                }).then(r => {
                                    if (r.message == "DELETED")
                                        deleted++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Items Deleted: ", deleted);
                                });
                                const count = i+1;
                                const message = "Deleted "+count+" of "+length;
                                frappe.show_progress("Deleting ERP Items in Zoho Books", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        }, __("Sync with ZB"));


        listview.page.add_inner_button("Update ERP Items in ZB", () => {
            frappe.call({
                method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.custom_fetch_erp_items_list',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Length of the ERP Items List: ", length);
						console.log("Items List: ", r.message);
                        //console.log("Item: ", r.message[0]);
                        let added = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.custom_update_erp_item_in_zb',
                                    args: {
                                        erp_item: r.message[i]["name"],
                                        custom_zoho_item_id: r.message[i]["custom_zoho_item_id"],
                                        //custom_zoho_item_id: r.message[i],
                                        //gst_hsn_code: r.message[i]["gst_hsn_code"],
                                    },
                                    async: false,
                                }).then(r => {
                                    if (r.message == "ADDED")
                                        added++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Items Added: ", added);
                                });
                                const count = i+1;
                                const message = "Updating "+count+" of "+length;
                                frappe.show_progress("Adding ERP Items in Zoho Books", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        }, __("Sync with ZB"));
    },
};