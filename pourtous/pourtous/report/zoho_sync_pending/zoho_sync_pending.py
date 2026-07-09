# Copyright (c) 2024, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not (filters.voucher_type and filters.from_date and filters.to_date): # don't execute until filters are set
		return [], []

	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)

	if not data:
		msgprint(_('No records found'))
		return columns, data

	return columns, data


def get_columns(filters):
	if filters.voucher_type == "Purchase Invoice":
		return [
			{
				"fieldname": "name",
				"label": "Purchase Invoice",
				"fieldtype": "Link",
				"options": "Purchase Invoice",
				"width": "150"
			},
			{
				"fieldname": "bill_no",
				"label": "Supplier Bill",
				"fieldtype": "Data",
				"width": "150"
			},
			{
				"fieldname": "bill_date",
				"label": "Suppl Bill Dt",
				"fieldtype": "Date",
				"width": "120"
			},
			{
				"fieldname": "posting_date",
				"label": "Posting Date",
				"fieldtype": "Date",
				"width": "120"
			},
			{
				"fieldname": "posting_time",
				"label": "Posting Time",
				"fieldtype": "Time",
				"width": "120"
			},
			{
				"fieldname": "supplier",
				"label": "Supplier",
				"fieldtype": "Data",
				"width": "150"
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
				"label": "Return?",
				"fieldtype": "Link",
				"options": "Sales Invoice",
				"width": "100"
			}
		]


	elif filters.voucher_type == "Sales Invoice":
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
				"fieldname": "custom_customer_group",
				"label": "Customer Group",
				"fieldtype": "Link",
				"options": "Customer Group",
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
				"label": "Return?",
				"fieldtype": "Link",
				"options": "Sales Invoice",
				"width": "100"
			}
		]


def get_data(filters):
	if filters.voucher_type == "Purchase Invoice":
		query = frappe.db.sql(
			"""
			SELECT name, bill_no, bill_date, posting_date, posting_time, total_taxes_and_charges, grand_total, supplier, is_return
			FROM `tabPurchase Invoice`
			WHERE docstatus = 1
			AND custom_zoho_bill_id IS NULL AND custom_zb_vendor_credit_id IS NULL
			AND posting_date between '{0}' and '{1}'
			""".format(filters.from_date, filters.to_date),
			as_dict=True
		)

	elif filters.voucher_type == "Sales Invoice":
		query = frappe.db.sql(
			"""
			SELECT si.name, si.customer_name, si.custom_customer_group, si.custom_fs_account_number, si.posting_date, si.total,
			si.total_taxes_and_charges, si.grand_total, si.is_return
			FROM `tabSales Invoice` si
			WHERE si.docstatus = 1
			AND si.custom_zoho_invoice_id IS NULL AND si.custom_zb_creditnote_id IS NULL
			AND si.posting_date between '{0}' and '{1}'
			""".format(filters.from_date, filters.to_date),
			as_dict=True
		)

	return query
