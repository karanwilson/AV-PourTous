// Copyright (c) 2024, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock-In List"] = {
	"filters": [
		{
			"fieldname": "voucher_type",
			"label": __("Voucher Type"),
			"fieldtype": "Select",
			"options": ["", "Purchase Receipt", "Stock Entry"],
			"width": "60px",
		},
		{
			"fieldname": "posting_date",
			"label": __("Date"),
			"fieldtype": "Date",
			"width": "60px",
		},
	]
};
