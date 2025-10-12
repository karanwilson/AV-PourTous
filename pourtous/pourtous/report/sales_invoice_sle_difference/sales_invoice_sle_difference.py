# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not (filters.from_date and filters.to_date): # don't execute until filters are set
		return [], []

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
			"fieldname": "invoice",
			"label": "Invoice",
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": "150"
		},
		{
			"fieldname": "customer_name",
			"label": "Customer Name",
			"fieldtype": "Data",
			"width": "200"
		},
		{
			"fieldname": "custom_fs_account_number",
			"label": "FS Account",
			"fieldtype": "Data",
			"width": "100"
		},
		{
			"fieldname": "invoice_item_rows",
			"label": "Invoice Rows",
			"fieldtype": "Data",
			"width": "120"
		},
		{
			"fieldname": "sle_item_rows",
			"label": "SLE Rows",
			"fieldtype": "Data",
			"width": "100"
		},
		{
			"fieldname": "si_sle_difference",
			"label": "Difference",
			"fieldtype": "Data",
			"width": "100"
		}			
	]


def get_data(filters):
	if filters.sales_invoice:
		query = frappe.db.sql(
			"""
			select table1.*, (table1.invoice_item_rows - table1.sle_item_rows) AS si_sle_difference
			from
			(
			select si.name as invoice, si.customer_name, si.custom_fs_account_number,
			( select count(sii.item_code) from `tabSales Invoice Item` sii where sii.parent = si.name ) AS invoice_item_rows,
			( select count(sle.item_code) from `tabStock Ledger Entry` sle where sle.voucher_no = si.name ) AS sle_item_rows
			from `tabSales Invoice` si
			where si.docstatus = 1
			and si.posting_date between '{0}' and '{1}'
			and si.name = '{2}'
			) table1
			""".format(filters.from_date, filters.to_date, filters.sales_invoice),
			as_dict=True
		)
		return query


	else:
		query = frappe.db.sql(
			"""
			select table1.*, (table1.invoice_item_rows - table1.sle_item_rows) AS si_sle_difference
			from
			(
			select si.name as invoice, si.customer_name, si.custom_fs_account_number,
			( select count(sii.item_code) from `tabSales Invoice Item` sii where sii.parent = si.name ) AS invoice_item_rows,
			( select count(sle.item_code) from `tabStock Ledger Entry` sle where sle.voucher_no = si.name ) AS sle_item_rows
			from `tabSales Invoice` si
			where si.docstatus = 1
			and si.posting_date between '{0}' and '{1}'
			) table1
			""".format(filters.from_date, filters.to_date),
			as_dict=True
		)
		return query