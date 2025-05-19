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
				console.log("frappe.query_report.get_filter_value('from_date'): ", frappe.query_report.get_filter_value("from_date"));
				console.log("frappe.query_report.get_filter_value('to_date'): ", frappe.query_report.get_filter_value('to_date'));
				frappe.call({
					method: `pourtous.pourtous.report.push_consol_sales_inv_zb_api.push_consol_sales_inv_zb_api.get_participant_monthly_distribution`,
					args: {
						from_date: frappe.query_report.get_filter_value("from_date"),
						to_date: frappe.query_report.get_filter_value("to_date"),
					},
					callback: function (r) {
						if (r.message) {
							//console.log("r.message: ", r.message);
							const length = r.message.length;
							console.log("Number of FS invoices to sync: ", length);
							console.log("Invoice List: ", r.message);
						}
					},
				});
			}
		);
	}
}
