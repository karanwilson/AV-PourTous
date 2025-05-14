// Copyright (c) 2024, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock-In List"] = {
	"filters": [
		{
			"fieldname": "voucher_type",
			"label": __("Voucher Type"),
			"fieldtype": "Select",
			"options": ["", "Purchase Invoice", "Purchase Receipt", "Stock Entry"],
			"width": "60px",
		},
		{
			"fieldname": "posting_date",
			"label": __("Date"),
			"fieldtype": "Date",
			"width": "60px",
		},
		{
			"fieldname": "from_time",
			"label": __("From Time"),
			"fieldtype": "Time",
			"width": "60px",
		},
		{
			"fieldname": "to_time",
			"label": __("To Time"),
			"fieldtype": "Time",
			"width": "60px",
		},
	]
};
