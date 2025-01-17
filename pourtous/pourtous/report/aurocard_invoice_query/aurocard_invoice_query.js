// Copyright (c) 2025, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Aurocard Invoice Query"] = {
	"filters": [
		{
			"fieldname": "remarks",
			"label": __("Aurocard Transaction ID"),
			"fieldtype": "Data",
			"width": "80px",
		},
	]
};
