// Copyright (c) 2026, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Customer Credit Balance Custom"] = {
	"filters": [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			reqd: 1,
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer",
		},
		{
			fieldname: "custom_fs_account_number",
			label: __("FS Account"),
			fieldtype: "Data"
		},
	]
};
