// Copyright (c) 2024, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Reconciliation Report"] = {
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
			"fieldname": "is_waste",
			"label": __("Is Waste"),
			"fieldtype": "Check",
			"width": "60px",
		},
	]
};
