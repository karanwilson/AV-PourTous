// Copyright (c) 2025, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Push Consol Sales-Inv ZB-API"] = {
	filters: [
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
		{
			"fieldname": "custom_fs_account_number",
			"label": __("PT/FS Account No."),
			"fieldtype": "Data",
			"width": "60px",
		},
		{
			"fieldname": "is_return",
			"label": __("Returns"),
			"fieldtype": "Check",
			"width": "60px",
		}
	],

	onload(report) {
		//create_push_button();
		report.page.add_inner_button(
			__("Push to Zoho"),
			function () {
				//frappe.msgprint("Test Message");
				const to_date = frappe.query_report.get_filter_value('to_date');
				const is_return = frappe.query_report.get_filter_value('is_return');
				const custom_fs_account_number = frappe.query_report.get_filter_value('custom_fs_account_number');
				console.log("frappe.query_report.get_filter_value('from_date'): ", frappe.query_report.get_filter_value("from_date"));
				console.log("frappe.query_report.get_filter_value('to_date'): ", to_date);
				console.log("frappe.query_report.get_filter_value('is_return'): ", is_return);
				frappe.call({
					method: `pourtous.pourtous.report.push_consol_sales_inv_zb_api.push_consol_sales_inv_zb_api.get_participant_monthly_distribution`,
					args: {
						from_date: frappe.query_report.get_filter_value("from_date"),
						to_date: to_date,
						custom_fs_account_number: custom_fs_account_number,
						is_return: is_return
					},
				});
				frappe.show_alert({message: __('Initiated Background Push of Invoices to Zoho Books'), indicator: 'green'});
			}
		);
	}
}
