// Copyright (c) 2024, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["GST Sales Report"] = {
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
		},

		{
			"fieldname": "mop",
			"label": __("Mode Of Payment"),
			// "fieldtype": "Link",
			// "options": "Mode of Payment",
			"fieldtype": "Select",
			"options": "\nFS\nAurocard\nUPI\nCash\nCards\nNEFT",
			"width": "60px",
		}
	]
};
