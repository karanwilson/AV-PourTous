frappe.listview_settings['Payment Entry'] = {
    refresh(listview) {
        listview.page.add_inner_button("Process Monthly Balances", () => {
            frappe.call({
                method: 'pourtous.api.fetch_monthly_contributions',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        if (r.message.length >0) {
                            console.log("r.message: ", r.message);
                            /* console.log("contact: ", r.message[0]["contact"]);
                            console.log("customer: ", r.message[0]["customer"]);
                            console.log("custom_in_kind_scheme: ", r.message[0]["custom_in_kind_scheme"]);
                            console.log("custom_lunch_scheme: ", r.message[0]["custom_lunch_scheme"]);
                            console.log("custom_monthly_contribution: ", r.message[0]["custom_monthly_contribution"]);
                            console.log("custom_ptdc_maintenance: ", r.message[0]["custom_ptdc_maintenance"]); */
                            const length = r.message.length;
                            console.log("Processing Balances for " + length + " Participants");
                            let balances = 0;
                            for (let i = 0; i < length; i++) {
                                setTimeout(() => {
                                    frappe.call({
                                        method: 'pourtous.api.process_pt_monthly_balances',
                                        args: {
                                            contact: r.message[i]["contact"],
                                            customer: r.message[i]["customer"],
                                            custom_in_kind_scheme: r.message[i]["custom_in_kind_scheme"],
                                            custom_lunch_scheme: r.message[i]["custom_lunch_scheme"],
                                            custom_monthly_contribution: r.message[i]["custom_monthly_contribution"],
                                            custom_ptdc_maintenance: r.message[i]["custom_ptdc_maintenance"]
                                        },
                                        async: false,
                                    }).then(r => {
                                        if (r.message == "OK")
                                            balances++;
                                        else if (r.message = "EXISTS")
                                            frappe.throw("Payment Exists for this month");
                                    }).then(r => {
                                        // placing this statement block here as it does not work outside of the main frappe.call block
                                        // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                        // it shows an accurate result in the end. This design works.
                                        console.log("Processed Balances for ", balances, " of ", length, " Participants");
                                    });
                                    const count = i+1;
                                    const message = "Processing "+count+" of "+length;
                                    frappe.show_progress("Processing Participant Monthly Balances", count, length, message);
                                }, 0);
                            }
                        }
                        else {
                            console.log("No Records");
                            frappe.msgprint(__("No Contribution Details Found or Monthly Balances already processed for this month"));
                        }
                    }
                }
            });
        });

        listview.page.add_inner_button("Process Extra Contributions", () => {
            frappe.call({
                method: 'pourtous.api.fetch_extra_contributions',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        if (r.message.length >0) {
                            /* console.log("r.message: ", r.message);
                            console.log("contact: ", r.message[0]["contact"]);
                            console.log("customer: ", r.message[0]["customer"]);
                            console.log("custom_extra_contribution: ", r.message[0]["custom_extra_contribution"]); */
                            const length = r.message.length;
                            console.log("Processing Extra Contributions for " + length + " Participants");
                            let extra_contributions = 0;
                            for (let i = 0; i < length; i++) {
                                setTimeout(() => {
                                    frappe.call({
                                        method: 'pourtous.api.process_pt_extra_contributions',
                                        args: {
                                            contact: r.message[i]["contact"],
                                            customer: r.message[i]["customer"],
                                            custom_extra_contribution: r.message[i]["custom_extra_contribution"]
                                        },
                                        async: false,
                                    }).then(r => {
                                        if (r.message == "OK")
                                            extra_contributions++;
                                    }).then(r => {
                                        // placing this statement block here as it does not work outside of the main frappe.call block
                                        // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                        // it shows an accurate result in the end. This design works.
                                        console.log("Processed Extra Contributions for ", extra_contributions, " of ", length, " Participants");
                                    });
                                    const count = i+1;
                                    const message = "Processing "+count+" of "+length;
                                    frappe.show_progress("Processing Extra Contributions", count, length, message);
                                }, 0);
                            }
                        }
                        else {
                            console.log("No Records");
                            frappe.msgprint(__("No Extra Contributions Found"));
                        }
                    }
                }
            });
        });
    },
};