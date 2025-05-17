// Copyright (c) 2025, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Participant Items Distribution"] = {
	filters: [
		{
			"fieldname": "custom_fs_account_number",
			"label": __("PT/FS Account No."),
			"fieldtype": "Data",
			"width": "60px",
		},
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

	/* onload(report) {
		report.page.add_inner_button(
					__("Push to Zoho"),
					function () {
						frappe.msgprint("Test Message");
						console.log("frappe.query_reports['Participant Items Distribution']: ", frappe.query_reports["Participant Items Distribution"]);
						console.log("frappe.query_reports['Participant Items Distribution'].filters: ", frappe.query_reports["Participant Items Distribution"].filters);
						frappe.call({
							method: "pourtous.pourtous.report.participant_items_distribution.get_participant_monthly_distribution",
							args: { filters: frappe.query_reports["Participant Items Distribution"].filters },
							async: false,
							callback: (r) => {
								if (r.message) {
									console.log("r.message: ", r.message);
								}
							}
						});
					}
		)
	} */
}
