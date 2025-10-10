// Copyright (c) 2025, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Invoice SLE difference"] = {
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
			"fieldname": "sales_invoice",
			"label": __("Sales Invoice"),
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": "60px",
		},
	]
};
