// Copyright (c) 2025, Karan Wilson and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Monthly Statement"] = {
	"filters": [
		{
			"fieldname": "custom_fs_account_number",
			"label": __("FS Account No."),
			"fieldtype": "Data",
			"width": "60px",
		},

		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "60px",
		},

		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "60px",
		},

		{
			"fieldname": "items_view",
			"label": __("Check: Shows Itemised Breakup, Uncheck: Shows Invoice Aggregates"),
			"fieldtype": "Check",
			"width": "60px",
		},
	]
};
