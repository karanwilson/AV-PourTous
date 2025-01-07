// Copyright (c) 2025, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Supplier Stock Report"] = {
	"filters": [
		{
			"fieldname": "supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
			"width": "60px",
		},
	]
};
