// Copyright (c) 2024, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Unpaid Invoices"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			width: "60px",
		},

		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			width: "60px",
		},

		{
			fieldname: "custom_fs_account_number",
			label: __("FS Account"),
			fieldtype: "Data",
			width: "60px",
		}
	],

// onload(report) {
// 	report.filters = [];
// }
};
