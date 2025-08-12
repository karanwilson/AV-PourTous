// Copyright (c) 2025, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Participant Usage"] = {
	"filters": [
		{
			"fieldname": "custom_fs_account_number",
			"label": __("PT/FS Account No."),
			"fieldtype": "Data",
			"width": "60px",
		},
		{
			"fieldname": "from_date",
			"label": __("From Date*"),
			"fieldtype": "Date",
			"width": "60px",
		},
		{
			"fieldname": "to_date",
			"label": __("To Date*"),
			"fieldtype": "Date",
			"width": "60px",
		},
		/* {
			"fieldname": "show_breakup",
			"label": __("Show Contribution Breakup"),
			"fieldtype": "Check",
			"width": "60px",
		} */
	]
};
