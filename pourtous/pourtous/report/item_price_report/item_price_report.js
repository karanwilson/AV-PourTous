// Copyright (c) 2025, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item Price Report"] = {
	"filters": [
		{
			"fieldname": "has_batch_no",
			"label": __("Has Batch No."),
			"fieldtype": "Check",
			"width": "60px",
		},
	]
};
