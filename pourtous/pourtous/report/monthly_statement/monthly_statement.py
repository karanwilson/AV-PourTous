# Copyright (c) 2024, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not (filters.from_date and filters.to_date and filters.custom_fs_account_number): # don't execute until filters are set
		return [], []

	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)

	if not data:
		msgprint(_('No records found'))
		return columns, data

	return columns, data


def get_columns(filters):
	if filters.items_view:
		return [
			{
				"fieldname": "invoice_name",
				"label": "Invoice",
				"fieldtype": "Link",
				"options": "Sales Invoice",
				"width": "120"
			},
			{
				"fieldname": "customer_name",
				"label": "Customer",
				"fieldtype": "Link",
				"options": "Customer",
				"width": "120"
			},
			{
				"fieldname": "custom_fs_account_number",
				"label": "FS Account",
				"fieldtype": "Data",
				"width": "100"
			},
			{
				"fieldname": "posting_date",
				"label": "Date",
				"fieldtype": "Date",
				"width": "100"
			},
			{
				"fieldname": "item_code",
				"label": "Code",
				"fieldtype": "Data",
				"width": "75"
			},
			{
				"fieldname": "item_name",
				"label": "Item Name",
				"fieldtype": "Data",
				"width": "200"
			},
			{
				"fieldname": "qty",
				"label": "Quanity",
				"fieldtype": "Float",
				"width": "80"
			},
			{
				"fieldname": "rate",
				"label": "Rate",
				"fieldtype": "Currency",
				"width": "80"
			},
			{
				"fieldname": "amount",
				"label": "Amount",
				"fieldtype": "Currency",
				"width": "80"
			}
		]

	else:
		return [
			{
				"fieldname": "name",
				"label": "Invoice",
				"fieldtype": "Link",
				"options": "Sales Invoice",
				"width": "150"
			},

			{
				"fieldname": "customer_name",
				"label": "Customer",
				"fieldtype": "Data",
				"width": "130"
			},

			{
				"fieldname": "custom_fs_account_number",
				"label": "FS Account",
				"fieldtype": "Data",
				"width": "130"
			},

			{
				"fieldname": "posting_date",
				"label": "Posting Date",
				"fieldtype": "Date",
				"width": "130"
			},

			{
				"fieldname": "total",
				"label": "Net Total",
				"fieldtype": "Currency",
				"width": "100"
			},

			{
				"fieldname": "total_taxes_and_charges",
				"label": "Total Tax",
				"fieldtype": "Currency",
				"width": "100"
			},

			{
				"fieldname": "grand_total",
				"label": "Grand Total",
				"fieldtype": "Currency",
				"width": "100"
			},

			{
				"fieldname": "return_against",
				"label": "Return Against",
				"fieldtype": "Link",
				"options": "Sales Invoice",
				"width": "130"
			},

		]


def get_data(filters):
	if filters.items_view:
		query = frappe.db.sql(
			"""
			SELECT s.name AS invoice_name, s.customer_name, s.custom_fs_account_number, s.posting_date, si.item_code, si.item_name, si.qty, si.rate, si.amount
			FROM `tabSales Invoice Item` si, `tabSales Invoice` s
			WHERE s.docstatus = 1 AND s.custom_fs_account_number = '{0}'
			AND s.posting_date BETWEEN '{1}' AND '{2}'
			AND si.parent = s.name
			""".format(filters.custom_fs_account_number, filters.from_date, filters.to_date),
			as_dict=True
		)

	else:
		query = frappe.db.sql(
			"""
			SELECT name, customer_name, custom_fs_account_number, posting_date, total, total_taxes_and_charges,
			grand_total, return_against

			FROM `tabSales Invoice` WHERE docstatus = 1
			AND posting_date between '{0}' and '{1}'
			AND custom_fs_account_number = '{2}'
			""".format(filters.from_date, filters.to_date, filters.custom_fs_account_number),
			as_dict=True
		)

	return query

