frappe.listview_settings['Item'] = {
    refresh(listview) {
        listview.page.add_inner_button("Update Item-Code Barcodes", () => {
            frappe.call({
                method: 'pourtous.api.fetch_items_list_for_barcode',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Number of Item-Code Barcodes to Add/Update: ", length);
						console.log("List of Items: ", r.message);
                        console.log("r.message[0]['name']: ", r.message[0]["name"]);
                        let updated = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.api.update_item_barcode',
                                    args: {
                                        item_code: r.message[i]["name"]
                                    },
                                    async: false,
                                }).then(r => {
                                    if (r.message == "Updated")
                                        updated++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Updated ", updated, ", of ", length);
                                });
                                const count = i+1;
                                const message = "Updating "+count+" of "+length;
                                frappe.show_progress("Updating Item-Code Barcodes", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        });
    },
};