// Copyright (c) 2024, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Custom Sales Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"fieldtype": "Date",
			"label": "From Date",
			"mandatory": 0,
			"wildcard_filter": 0
		},

		{
			"fieldname": "to_date",
			"fieldtype": "Date",
			"label": "To Date",
			"mandatory": 0,
			"wildcard_filter": 0
		},

		{
			"fieldname": "current_date",
			"fieldtype": "Check",
			"label": "Current Date",
			"mandatory": 0,
			"wildcard_filter": 0
		}
	]
};
