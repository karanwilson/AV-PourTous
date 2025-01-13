frappe.listview_settings['Batch'] = {
    refresh(listview) {
        listview.page.add_inner_button("Sync Batch Prices", () => {
            frappe.call({
                method: 'pourtous.api.fetch_batch_list',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Number of Batch prices to update: ", length);
                        let transfers = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.api.sync_batch_prices',
                                    args: { batch: r.message[i][1] },
                                    //async: false,
                                }).then(r => {
                                    if (r.message == "OK")
                                        transfers++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Updated prices for ", transfers, " of ", length, " Batches");
                                });
                                const count = i+1;
                                const message = "Updating Batch "+count+" of "+length;
                                frappe.show_progress("Updating Batch Prices", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        });
    },
};