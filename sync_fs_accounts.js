frappe.listview_settings['Customer'] = {
    refresh(listview) {
        listview.page.add_inner_button("Update FS Accounts", () => {
            frappe.call({
                method: 'payments.payment_gateways.doctype.fs_settings.fs_settings.fetch_fs_accounts_detail',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message["RecordCount"];
                        console.log("Number of FS Accounts: ", length);
                        console.log("credit_limit_av_account: ", r.message["credit_limit_av_account"]);
                        let added = 0, updated = 0, credit_limit_UPDATED = 0, credit_limit = 0;

                        for (let i = 0; i < length; i++) {
                            if (i>0 && r.message["Accounts"]["R"+i+"_Number"] == r.message["Accounts"]["R"+(i-1)+"_Number"]) {
                                //console.log(["R"+i+"_Number"], ["R"+(i-1)+"_Number"]);
                                continue;
                            }

                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.api.update_fs_accounts',
                                    args: {
                                        fs_account: r.message["Accounts"]["R"+i+"_Number"],
                                        name: r.message["Accounts"]["R"+i+"_Name"],
                                        disable: r.message["Accounts"]["R"+i+"_Disable"],
                                        credit_limit_av_account: r.message["credit_limit_av_account"]
                                    },
                                    async: false,
                                }).then(r => {
                                    if (r.message == "NEW")
                                        added++;
                                    else if (r.message == "_UPDATED")
                                        updated++;
                                    else if (r.message == "credit_limit_UPDATED")
                                        credit_limit_UPDATED++;
                                    else if (r.message == "credit_limit")
                                        credit_limit++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Added ", added, " Accounts; Updated ", updated, " Accounts");
                                    console.log("UPDATED+credit_limit_UPDATED: ", credit_limit_UPDATED, ", credit_limit updated: ", credit_limit);
                                    //console.log("Updated ", updated, " Accounts");
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

        /* listview.page.add_inner_button("Fetch FS Accounts", () => {
            frappe.call({
                method: 'payments.payment_gateways.doctype.fs_settings.fs_settings.fetch_fs_accounts_detail',
                freeze: true,
                freeze_message: "Fetching FS Accounts",
                callback: (r) => {
                    //this.refresh();
                    //console.log("r: ", r);
                    console.log(r.message["Accounts"]);
                    console.log(r.message["Accounts"]["R0_Number"]);
                    console.log(r.message["Accounts"]["R"+0+"_Number"]);
                    //location.reload();
                }
            });
        });

        listview.page.add_inner_button("Sync FS Accounts", () => {
            frappe.call({
                method: 'pourtous.api.sync_fs_accounts',
                freeze: true,
                freeze_message: "Syncing FS Accounts",
                callback: (r) => {
                    //this.refresh();
                    location.reload();
                }
            });
        }); */
    },
};