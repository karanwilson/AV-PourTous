// Copyright (c) 2025, Karan Wilson and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Zoho Sync Pending"] = {
	"filters": [
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
		}
	]
};
