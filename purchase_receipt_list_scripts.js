frappe.listview_settings['Purchase Receipt'] = {
    refresh(listview) {

        listview.page.add_inner_button("Update Batch Prices", () => {
            frappe.call({
                method: 'pourtous.api.fetch_pur_rec_list',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Number of Invoices: ", length);
						console.log("Receipt List: ", r.message);
                        console.log("r.message[0]['name']: ", r.message[0]["name"]);
                        let updated = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.api.update_batch_price_pur_inv_rec',
                                    args: {
                                        doctype: 'Purchase Receipt',
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
    },
};