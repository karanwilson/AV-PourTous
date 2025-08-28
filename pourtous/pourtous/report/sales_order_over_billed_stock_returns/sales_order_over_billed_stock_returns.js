// Copyright (c) 2025, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Order Over-billed Stock Returns"] = {
	"filters": [
		{
			"fieldname": "item",
			"label": __("Item Code"),
			"fieldtype": "Data",
			"width": "60px",
		},
		{
			"fieldname": "view_so",
			"label": __("Check: Shows SalesOrder ID, Uncheck: Shows Item Qty Aggregates"),
			"fieldtype": "Check",
			"width": "60px",
		},
	]
};
