// Copyright (c) 2025, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Push Consol Sales-Inv ZB-API"] = {
	filters: [
		{
			"fieldname": "from_date",
			"label": __("From Date*"),
			"fieldtype": "Date",
			"width": "60px",
		},
		{
			"fieldname": "to_date",
			"label": __("To Date*"),
			"fieldtype": "Date",
			"width": "60px",
		}
	],

	onload(report) {
		//create_push_button();
		report.page.add_inner_button(
			__("Push to Zoho"),
			function () {
				//frappe.msgprint("Test Message");
				const to_date = frappe.query_report.get_filter_value('to_date')
				console.log("frappe.query_report.get_filter_value('from_date'): ", frappe.query_report.get_filter_value("from_date"));
				console.log("frappe.query_report.get_filter_value('to_date'): ", to_date);
				frappe.call({
					method: `pourtous.pourtous.report.push_consol_sales_inv_zb_api.push_consol_sales_inv_zb_api.get_participant_monthly_distribution`,
					args: {
						from_date: frappe.query_report.get_filter_value("from_date"),
						to_date: to_date,
					},
					async: false,
					callback: function (r) {
						if (r.message) {
							const length = Object.keys(r.message).length;
							//console.log("typeof(r.message): ", typeof(r.message));
							console.log("Number of PT invoices to sync: ", length);
							console.log("Invoice List: ", r.message);

							//if (counter == 100)
							//	break;

							let added = 0;
							let counter = 0;
							for (const key in r.message) {
								//console.log("key: ", key);
								//console.log("r.message[key]: ", r.message[key]);

								setTimeout(() => {
									frappe.call({
										method: 'pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.sync_pt_consol_inv_with_zb',
										args: {
											consol_inv_pt_account: key,
											line_items_dict: r.message[key],
											date: to_date
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
									//const count = counter+1;
									counter++
									const message = "Adding "+counter+" of "+length;
									frappe.show_progress("Pushing PT Invoices to Zoho Books", counter, length, message);
								}, 0);
							}
						}
					},
				});
			}
		);
	}
}
