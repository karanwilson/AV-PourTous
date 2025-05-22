# Copyright (c) 2024, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	columns, data = [], []

	columns = get_columns()
	data = get_data(filters)

	if not data:
		msgprint(_('No records found'))
		return columns, data

	return columns, data


def get_columns():
	return [
		{
			"fieldname": "name",
			"label": "Invoice ID",
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": "150"
		},

		{
			"fieldname": "customer_name",
			"label": "Customer",
			"fieldtype": "Data",
			"width": "300"
		},

		{
			"fieldname": "posting_date",
			"label": "Posting Date",
			"fieldtype": "Date",
			"width": "150"
		},

		{
			"fieldname": "status",
			"label": "Status",
			"fieldtype": "Data",
			"width": "150"
		},

		{
			"fieldname": "custom_fs_transfer_status",
			"label": "FS Transfer Status",
			"fieldtype": "Data",
			"width": "150"
		},

		{
			"fieldname": "grand_total",
			"label": "Total",
			"fieldtype": "Currency",
			"width": "150"
		},
	]


def get_data(filters):

	query = frappe.db.sql(
		"""
		SELECT name, customer_name, posting_date, status, custom_fs_transfer_status, grand_total
		FROM `tabSales Invoice`
		WHERE docstatus = 1 AND outstanding_amount > 0 AND status IN
		("Unpaid", "Unpaid and Discounted", "Partly Paid", "Partly Paid and Discounted", "Overdue", "Overdue and Discounted")
		""",
		as_dict=True
		#AND custom_fs_transfer_status = "Insufficient Funds"
	)

	return query