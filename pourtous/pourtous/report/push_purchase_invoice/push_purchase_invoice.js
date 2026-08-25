// Copyright (c) 2026, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Push Purchase Invoice"] = {
	"filters": [
		{
			"fieldname": "is_return",
			"label": __("Is Return*"),
			"fieldtype": "Select",
			"options": ["", "No", "Yes"],
			"width": "60px",
		},
		{
			"fieldname": "from_posting_date",
			"label": __("From Posting Date*"),
			"fieldtype": "Date",
			"width": "60px",
		},
		{
			"fieldname": "to_posting_date",
			"label": __("To Posting Date*"),
			"fieldtype": "Date",
			"width": "60px",
		},
		{
			"fieldname": "from_bill_date",
			"label": __("From bill Date*"),
			"fieldtype": "Date",
			"width": "60px",
		},
		{
			"fieldname": "to_bill_date",
			"label": __("To Bill Date*"),
			"fieldtype": "Date",
			"width": "60px",
		},
	],

	onload(report) {
		report.page.add_inner_button(
			__("Push to Zoho"),
			function () {
				// frappe.msgprint("Test Message");

				const from_posting_date = frappe.query_report.get_filter_value('from_posting_date');
				const to_posting_date = frappe.query_report.get_filter_value('to_posting_date');
				const from_bill_date = frappe.query_report.get_filter_value('from_bill_date');
				const to_bill_date = frappe.query_report.get_filter_value('to_bill_date');
				const is_return = frappe.query_report.get_filter_value('is_return');

				console.log("from_posting_date: ", from_posting_date);
				console.log("to_posting_date: ", to_posting_date);
				console.log("from_posting_date: ", from_bill_date);
				console.log("to_posting_date: ", to_bill_date);
				console.log("is_return: ", is_return);

				frappe.call({
					method: `pourtous.pourtous.report.push_purchase_invoice.push_purchase_invoice.get_purchase_invoices`,
					args: {
						from_posting_date: from_posting_date,
						to_posting_date: to_posting_date,
						from_bill_date: from_bill_date,
						to_bill_date: to_bill_date,
						is_return: is_return
					},
				});

				frappe.show_alert({message: __('Initiated Background Push of Purchase Invoices to Zoho Books'), indicator: 'green'});
			}
		);
	}

};
