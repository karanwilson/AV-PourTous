// Copyright (c) 2024, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Batch Price"] = {
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
