frappe.listview_settings['Sales Invoice'] = {
    refresh(listview) {
        listview.page.add_inner_button("Add FS Acc to Inv", () => {
            frappe.call({
                method: 'pourtous.api.fetch_invoice_list',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Number of FS Accounts to add to Inv: ", length);
                        console.log("Invoice list: ", r.message);
                        console.log("r.message[0].name: ", r.message[0].name);
                        console.log("r.message[0].customer: ", r.message[0].customer);

                        let added = 0;

                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.api.add_fs_accounts',
                                    args: {
                                        invoice: r.message[i].name,
                                        customer: r.message[i].customer
                                    },
                                    async: false,
                                }).then(r => {
                                    if (r.message == "ADDED")
                                        added++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Added ", added, " Accounts");
                                });
                                const count = i+1; // i starts from 0, but length counts from 1
                                const message = "Synching Account "+count+" of "+length;
                                frappe.show_progress("Loading FS Accounts", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        });
    },
};