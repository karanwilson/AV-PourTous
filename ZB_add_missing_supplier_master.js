frappe.listview_settings['Supplier'] = {
    refresh(listview) {

        listview.page.add_inner_button("Add missing Suppliers in ZB", () => {
            frappe.call({
                method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.fetch_erp_supplier_list',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Number of Suppliers to add: ", length);
						console.log("Supplier List: ", r.message);
                        console.log("r.message[0]['name']: ", r.message[0]["name"]);
                        let added = 0;
                        //let updated = 0;
                        for (let i = 0; i < 10; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.add_supplier_to_zb',
                                    args: { supplier: r.message[i]["name"] },
                                    async: false,
                                }).then(r => {
                                    if (r.message == "ADDED")
                                        added++;
                                    //else if (r.message == "UPDATED")
                                    //    updated++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Added ", added, " of ", length, " Suppliers");
                                });
                                const count = i+1;
                                const message = "Adding "+count+" of "+length;
                                frappe.show_progress("Adding missing Suppliers in Zoho Books", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        });

    },
};