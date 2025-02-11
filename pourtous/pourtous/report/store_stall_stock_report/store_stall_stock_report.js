// Copyright (c) 2025, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Store Stall Stock report"] = {
	"filters": [
		{
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": "60px"
		},

		{
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group",
			"width": "60px"
		},
	]
};
