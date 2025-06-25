// Copyright (c) 2024, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["GST Sales Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "60px",
		},

		{
			"fieldname": "to_date",
			"label": __("To Date"),
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

		{
			"fieldname": "customer_type",
			"label": __("Participant Type"),
			"fieldtype": "Select",
			"options": "\nIndividual\nCompany",
			"width": "60px",
		},

		{
			"fieldname": "customer_group",
			"label": __("Participant Group"),
			"fieldtype": "Link",
			"options": "Customer Group",
			"width": "60px",
		},
	]
};
