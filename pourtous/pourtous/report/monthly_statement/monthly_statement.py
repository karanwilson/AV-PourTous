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
				"fieldname": "branch",
				"label": "Branch",
				"fieldtype": "Data",
				"width": "100"
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
				"fieldname": "branch",
				"label": "Branch",
				"fieldtype": "Data",
				"width": "100"
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
			}
		]


def get_data(filters):
	#frappe.throw(str(filters))
	if filters.items_view and filters.branch:
		query = frappe.db.sql(
			"""
			SELECT si.name AS invoice_name, si.branch, si.customer_name, si.custom_fs_account_number, si.posting_date,
			sii.item_code, sii.item_name, sii.qty, sii.rate, sii.amount
			FROM `tabSales Invoice Item` sii, `tabSales Invoice` si
			WHERE si.docstatus = 1
			AND sii.parent = si.name
			AND si.branch = '{0}'
			AND si.custom_fs_account_number = '{1}'
			AND si.posting_date BETWEEN '{2}' AND '{3}'
			""".format(filters.branch, filters.custom_fs_account_number, filters.from_date, filters.to_date),
			as_dict=True
		)

	elif filters.items_view and not filters.branch:
		query = frappe.db.sql(
			"""
			SELECT si.name AS invoice_name, si.branch, si.customer_name, si.custom_fs_account_number, si.posting_date,
			sii.item_code, sii.item_name, sii.qty, sii.rate, sii.amount
			FROM `tabSales Invoice Item` sii, `tabSales Invoice` si
			WHERE si.docstatus = 1
			AND sii.parent = si.name
			AND si.branch IS NULL
			AND si.custom_fs_account_number = '{1}'
			AND si.posting_date BETWEEN '{2}' AND '{3}'
			""".format(filters.branch, filters.custom_fs_account_number, filters.from_date, filters.to_date),
			as_dict=True
		)

	elif filters.branch:
		query = frappe.db.sql(
			"""
			SELECT si.name AS invoice_name, si.branch, si.customer_name, si.custom_fs_account_number, si.posting_date,
			sii.item_code, sii.item_name, sii.qty, sii.rate, sii.amount
			FROM `tabSales Invoice Item` sii, `tabSales Invoice` si
			WHERE si.docstatus = 1
			AND sii.parent = si.name
			AND si.branch = '{0}'
			AND si.custom_fs_account_number = '{1}'
			AND si.posting_date BETWEEN '{2}' AND '{3}'
			""".format(filters.branch, filters.custom_fs_account_number, filters.from_date, filters.to_date),
			as_dict=True
		)

	else:
		query = frappe.db.sql(
			"""
			SELECT si.name, si.branch, si.customer_name, si.custom_fs_account_number, si.posting_date, si.total, si.total_taxes_and_charges,
			si.grand_total, si.return_against
			FROM `tabSales Invoice` si, `tabSales Invoice Item` sii
			LEFT JOIN `tabSales Order` so 
			ON so.docstatus = 1
			AND so.name = sii.sales_order
			WHERE si.docstatus = 1
			AND sii.parent = si.name
			AND si.branch IS NULL
			AND si.posting_date between '{1}' and '{2}'
			AND si.custom_fs_account_number = '{3}'
			GROUP BY si.name
			""".format(filters.branch, filters.from_date, filters.to_date, filters.custom_fs_account_number),
			as_dict=True
		)

	return query

