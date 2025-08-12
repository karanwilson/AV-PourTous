frappe.listview_settings['Sales Invoice'] = {
    refresh(listview) {
        listview.page.add_inner_button("Orders to Invoices", () => {
            frappe.call({
                method: 'pourtous.api.fetch_orders_to_invoice',
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
                                    method: 'pourtous.api.process_orders_to_invoice_ptdc',
                                    args: {
                                        order: r.message[i][0],
                                        pos_profile: r.message[i][1],
                                        order_date: r.message[i][2],
                                        order_time: r.message[i][3]
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
    }
};