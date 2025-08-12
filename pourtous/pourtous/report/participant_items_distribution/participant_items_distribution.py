# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not (filters.custom_fs_account_number and filters.voucher_type and filters.from_date and filters.to_date): # don't execute until filters are set
		return [], []

	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)

	if not data:
		msgprint(_('No records found'))
		return columns, data

	return columns, data


def get_columns(filters):
	if filters.voucher_type == "Checkout Notes":
		return [
			{
				"fieldname": "invoice_name",
				"label": "Checkout Note",
				"fieldtype": "Link",
				"options": "Sales Invoice",
				"width": "150"
			},
			{
				"fieldname": "customer_name",
				"label": "Family Name",
				"fieldtype": "Link",
				"options": "Customer",
				"width": "150"
			},
			{
				"fieldname": "posting_date",
				"label": "Date",
				"fieldtype": "Date",
				"width": "100"
			},
			{
				"fieldname": "item_code",
				"label": "Item Code",
				"fieldtype": "Data",
				"width": "100"
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
				"width": "100"
			},
			{
				"fieldname": "rate",
				"label": "Rate",
				"fieldtype": "Currency",
				"width": "100"
			},
			{
				"fieldname": "amount",
				"label": "Amount",
				"fieldtype": "Currency",
				"width": "100"
			}
		]

	else:
		return [
			{
				"fieldname": "order_name",
				"label": "Order",
				"fieldtype": "Link",
				"options": "Sales Order",
				"width": "150"
			},
			{
				"fieldname": "customer_name",
				"label": "Family Name",
				"fieldtype": "Link",
				"options": "Customer",
				"width": "150"
			},
			{
				"fieldname": "transaction_date",
				"label": "Date",
				"fieldtype": "Date",
				"width": "100"
			},
			{
				"fieldname": "item_code",
				"label": "Item Code",
				"fieldtype": "Data",
				"width": "100"
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
				"width": "100"
			},
			{
				"fieldname": "rate",
				"label": "Rate",
				"fieldtype": "Currency",
				"width": "100"
			},
			{
				"fieldname": "amount",
				"label": "Amount",
				"fieldtype": "Currency",
				"width": "100"
			}
		]


def get_data(filters):
	if filters.voucher_type == "Checkout Notes":
		query = frappe.db.sql(
			"""
			SELECT s.name AS invoice_name, s.customer_name, s.posting_date, item_code, item_name, qty, rate, amount
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
			SELECT so.name AS order_name, so.customer_name, so.transaction_date, item_code, item_name, qty, rate, amount
			FROM `tabSales Order` so, `tabSales Order Item` soi
			WHERE
				so.docstatus = 1
				AND so.status not in ("Closed", "On Hold")
				AND so.per_billed < 99.99
				AND so.custom_fs_account_number = '{0}'
				AND so.transaction_date BETWEEN '{1}' AND '{2}'
				AND soi.parent = so.name
			ORDER BY
				customer
			""".format(filters.custom_fs_account_number, filters.from_date, filters.to_date),
			as_dict=True,
		)

	return query
