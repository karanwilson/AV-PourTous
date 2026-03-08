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
			"fieldname": "custom_fs_account_number",
			"label": "FS Account",
			"fieldtype": "Data",
			"width": "120"
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
	query = """
			SELECT si.name, si.customer_name, si.custom_fs_account_number, posting_date, status, custom_fs_transfer_status, grand_total
			FROM `tabSales Invoice` si, tabCustomer c
			WHERE si.docstatus = 1 AND si.outstanding_amount > 0
			AND si.custom_fs_account_number IS NOT NULL
			AND si.customer = c.name AND c.customer_group != "Credit Customers"
			AND status IN
			("Unpaid", "Unpaid and Discounted", "Partly Paid", "Partly Paid and Discounted", "Overdue", "Overdue and Discounted")
			"""

	# Date filter is optional.
	if filters.get("from_date") and filters.get("to_date"):
		query += "AND posting_date between %(from_date)s and %(to_date)s"

	# custom_fs_account_number filter is optional.
	if filters.get("custom_fs_account_number"):
		query += " AND custom_fs_account_number = %(custom_fs_account_number)s"

	return frappe.db.sql(query, filters, as_dict=1)