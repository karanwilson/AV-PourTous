frappe.listview_settings['Sales Invoice'] = {
    refresh(listview) {
        listview.page.add_inner_button("Initialise Participant Monthly Balance", () => {
            frappe.call({
                method: 'pourtous.api.fetch_participant_list',
                async: false,
                callback: (r) => {
                    if (r.message) {
                        const length = r.message.length;
                        console.log("Initialising Balances for " + length + " Participants");
                        let balances = 0;
                        for (let i = 0; i < length; i++) {
                            setTimeout(() => {
                                frappe.call({
                                    method: 'pourtous.api.process_pt_monthly_balances',
                                    args: { participant: "" },
                                    async: false,
                                }).then(r => {
                                    if (r.message == "OK")
                                        balances++;
                                }).then(r => {
                                    // placing this statement block here as it does not work outside of the main frappe.call block
                                    // though it prints on console for each loop iteration (comes in only one line, with the loop count),
                                    // it shows an accurate result in the end. This design works.
                                    console.log("Initialised Balances for ", balances, " of ", length, " Participants");
                                });
                                const count = i+1;
                                const message = "Initialising "+count+" of "+length;
                                frappe.show_progress("Initialising Participant Balances", count, length, message);
                            }, 0);
                        }
                    }
                }
            });
        });
    },
};