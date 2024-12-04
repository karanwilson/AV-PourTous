// Copyright (c) 2024, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["GST Sales Report"] = {
	"filters": [
		{
			"fieldname": "query_date",
			"label": __("Date"),
			"fieldtype": "Date",
			"width": "60px",
		},

		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": "60px",
		},
	]
};
