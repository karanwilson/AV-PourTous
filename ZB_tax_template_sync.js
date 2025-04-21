frappe.listview_settings['Item Tax Template'] = {
    refresh(listview) {
        listview.page.add_inner_button("Sync ZB taxes with ERP", () => {
            frappe.call({
                method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.get_zb_tax_list',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Length of the ZB tax List: ", length);
						console.log("Tax List: ", r.message);
                        console.log("r.message[0]['taxes']: ", r.message[0]);
                        console.log("r.message[0]['tax_id']: ", r.message[0]["tax_id"]);
                        console.log("r.message[0]['tax_name']: ", r.message[0]["tax_name"]);
                        let updated = 0, no_match = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.sync_zb_tax_id_with_erp',
                                    args: {
                                        tax_id: r.message[i]["tax_id"],
                                        tax_name: r.message[i]["tax_name"],
                                        tax_percentage: r.message[i]["tax_percentage"],
                                        tax_type: r.message[i]["tax_type"],
                                        tax_specific_type: r.message[i]["tax_specific_type"]
                                    },
                                    async: false,
                                }).then(r => {
                                    if (r.message == "UPDATED")
                                        updated++;
                                    else if (r.message == "NO-MATCH")
                                        no_match++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Tax IDs Updated: ", updated, "; No-Matches: ", no_match);
                                });
                                const count = i+1;
                                const message = "Updating "+count+" of "+length;
                                frappe.show_progress("Syncing Zoho Books Tax IDs with ERP", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        });


        /* listview.page.add_inner_button("Sync ERP taxes with ZB", () => {
            frappe.call({
                method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.fetch_erp_tax_list',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Length of the ERP tax List: ", length);
						console.log("Tax List: ", r.message);
                        console.log("r.message[0]: ", r.message[0]);
                        //console.log("r.message[0]['tax_id']: ", r.message[0]["tax_id"]);
                        //console.log("r.message[0]['tax_name']: ", r.message[0]["tax_name"]);
                        let updated = 0, no_match = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.sync_erp_taxes_to_zoho',
                                    args: {
                                        erp_tax: r.message[i]["name"]
                                    },
                                    async: false,
                                }).then(r => {
                                    if (r.message == "UPDATED")
                                        updated++;
                                    else if (r.message == "NO-MATCH")
                                        no_match++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Tax IDs Updated: ", updated, "; No-Matches: ", no_match);
                                });
                                const count = i+1;
                                const message = "Updating "+count+" of "+length;
                                frappe.show_progress("Syncing Zoho Books Tax IDs with ERP", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        }); */

    },
};