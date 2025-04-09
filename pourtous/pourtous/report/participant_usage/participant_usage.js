// Copyright (c) 2025, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Participant Usage"] = {
	"filters": [
		{
			"fieldname": "name",
			"label": __("Participant"),
			"fieldtype": "Link",
			"options": "Customer",
			"width": "60px",
		},
	]
};
