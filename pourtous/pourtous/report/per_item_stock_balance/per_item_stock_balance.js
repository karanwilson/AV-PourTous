// Copyright (c) 2026, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Per Item Stock Balance"] = {
	"filters": [
		{
			"fieldname": "name",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item",
			"width": "60px",
		},
	]
};
