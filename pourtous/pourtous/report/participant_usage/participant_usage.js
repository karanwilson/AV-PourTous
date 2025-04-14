// Copyright (c) 2025, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Participant Usage"] = {
	"filters": [
		/* {
			"fieldname": "customer",
			"label": __("Participant"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": "60px",
		}, */
		{
			"fieldname": "show_breakup",
			"label": __("Show Breakup"),
			"fieldtype": "Check",
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
	]
};
