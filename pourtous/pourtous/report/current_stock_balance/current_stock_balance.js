// Copyright (c) 2024, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Current Stock Balance"] = {
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
