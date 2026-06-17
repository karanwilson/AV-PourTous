frappe.listview_settings['Purchase Receipt'] = {
    refresh(listview) {
        listview.page.add_inner_button("Add ERP bills in ZB", () => {
            frappe.call({
                method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.fetch_erp_bills_list',
                // async: true,
                // freeze: true,
                // timeout: 0,
                // callback: (r) => {
                //     console.log("r: ", r);

                //     frappe.realtime.on("zb_bills_push_progress_update", (data) => {
                //         console.log("frappe.realtime.on data: ", data);
                //         // let progress = (data.count / data.total) * 100;
                //         // report.dashboard.show_progress(data.title, (data.count / data.total) * 100, data.message);
                //         frappe.show_progress(data.title, (data.count / data.total) * 100, data.message);
                //     })

                //     if (r.message == "Completed") {
                //         frappe.show_alert({message: __('Push Complete'), indicator: 'green'});
				// 	}

                //     if (r.message) {
                //         const length = r.message.length;
                //         console.log("Number of Bills to add: ", length);
				// 		console.log("Bills List: ", r.message);
                //         //console.log("r.message[0]['name']: ", r.message[0]["name"]);
                //         let added = 0;
                //         for (let i = 0; i < length; i++) {
                //             setTimeout(() => {
                //                 frappe.call({
                //                     method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.add_erp_bill_debitnote_in_zoho',
                //                     args: {
                //                         bill: r.message[i]["name"]
                //                     },
                //                     async: false,
                //                 }).then(r => {
                //                     if (r.message == "ADDED")
                //                         added++;
                //                 }).then(r => {
                //                     // placing this statement block here as it does not work outside of the main frappe.call block
                //                     // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                //                     // it shows an accurate result in the end. This design works.
                //                     console.log("Added ", added, ", of ", length);
                //                 });
                //                 const count = i+1;
                //                 const message = "Adding "+count+" of "+length;
                //                 frappe.show_progress("Pushing Bills to Zoho Books", count, length, message);
                //             }, 0);
                //         }
                //     }
                // }
            });
            frappe.show_alert({message: __('Initiated Background Push of Invoices to Zoho Books'), indicator: 'green'});
        }, __("Sync with ZB"));


        listview.page.add_inner_button("Add ERP debitnotes in ZB", () => {
            frappe.call({
                method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.fetch_erp_debitnotes_list',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Number of Bills to add: ", length);
						console.log("Contacts List: ", r.message);
                        //console.log("r.message[0]['name']: ", r.message[0]["name"]);
                        let added = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.add_erp_bill_debitnote_in_zoho',
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
                                frappe.show_progress("Pushing Debitnotes to Zoho Books", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        }, __("Sync with ZB"));
    },
};