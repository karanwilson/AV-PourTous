frappe.listview_settings['Sales Order'] = {
    refresh(listview) {
        listview.page.add_inner_button("Process SO FS-Payments", () => {
            frappe.call({
                method: 'payments.payment_gateways.doctype.fs_settings.fs_settings.fetch_unpaid_sales_orders',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Number of SO Payments to process: ", length);
                        let transfers = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'payments.payment_gateways.doctype.fs_settings.fs_settings.add_transfer_sales_order',
                                    args: { order: r.message[i][0] },
                                    async: false,
                                }).then(r => {
                                    if (r.message == "OK")
                                        transfers++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Received transfers for ", transfers, " of ", length, " Sales Orders");
                                });
                                const count = i+1;
                                const message = "Loading "+count+" of "+length;
                                frappe.show_progress("Processing Sales Order Payments", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        });

        /* listview.page.add_inner_button("Old SO Batch Update", () => {
            frappe.call({
                method: 'pourtous.api.fetch_old_so_list',
                //async: false,
                callback: (r) => {
                    if (r.message) {
                        //console.log("r.message: ", r.message);
                        r.message.forEach((sales_order_name) => {
                            console.log(sales_order_name[0]);
                            frappe.call({
                                method: 'pourtous.api.update_old_so_item_batch',
                                args: { sales_order_name: sales_order_name[0] },
                                //async: false,
                            }).then(r => {
                                console.log(r.message);
                            });
                        });
                    }
                }
            });
        }); */
    },
};