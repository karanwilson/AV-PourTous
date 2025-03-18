// Copyright (c) 2025, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Consolidated Sales Zoho API"] = {
	"filters": [

	],

	onload(report) {
		report.page.add_inner_button(
					__("Push to Zoho"),
					function () {
						frappe.msgprint("Test Message");
					});
	}
};
