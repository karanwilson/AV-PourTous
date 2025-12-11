# Copyright (c) 2024, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not (filters.from_date and filters.to_date): # don't execute until filters are set
		return [], []

	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)

	if not data:
		msgprint(_('No records found'))
		return columns, data

	return columns, data


def get_columns(filters):
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
			"width": "150"
		},
		{
			"fieldname": "custom_fs_account_number",
			"label": "FS Account",
			"fieldtype": "Data",
			"width": "100"
		},
		{
			"fieldname": "posting_date",
			"label": "Posting Date",
			"fieldtype": "Date",
			"width": "120"
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
			"fieldname": "is_return",
			"label": "Is Return",
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": "100"
		}
	]


def get_data(filters):
	query = frappe.db.sql(
		"""
		SELECT si.name, si.customer_name, si.custom_fs_account_number, si.posting_date, si.total,
		si.total_taxes_and_charges, si.grand_total, si.is_return
		FROM `tabSales Invoice` si
		WHERE si.docstatus = 1
		AND (si.custom_zoho_invoice_id IS NULL AND si.custom_zb_creditnote_id IS NULL)
		AND si.posting_date between '{0}' and '{1}'
		""".format(filters.from_date, filters.to_date),
		as_dict=True
	)

	return query

