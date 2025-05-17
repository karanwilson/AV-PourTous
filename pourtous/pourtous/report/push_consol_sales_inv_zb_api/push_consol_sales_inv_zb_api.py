# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not (filters.from_date and filters.to_date): # don't execute until filters are set
		return [], []

	columns, data = [], []

	columns = get_columns()
	data = get_data(from_date=filters.from_date, to_date = filters.to_date)

	if not data:
		msgprint(_('No records found'))
		return columns, data

	return columns, data


def get_columns():
	return [
		{
			"fieldname": "name",
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
			"fieldname": "custom_fs_account_number",
			"label": "PT Account",
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
		}
	]


def get_data(from_date, to_date):
	query = frappe.db.sql(
		"""
		SELECT s.name, s.customer_name, s.custom_fs_account_number, s.posting_date, item_code, item_name, qty, rate
		FROM `tabSales Invoice Item` si, `tabSales Invoice` s
		WHERE s.docstatus = 1 AND si.parent = s.name AND s.is_return = 0
		AND s.posting_date BETWEEN '{0}' AND '{1}'
		AND s.custom_zoho_invoice_id IS NULL AND s.custom_zb_consol_inv_id IS NULL
		""".format(from_date, to_date),
		as_dict=True
	)

	return query


def update_sync_status(from_date, to_date):
	query = frappe.db.sql(
		"""
		SELECT name FROM `tabSales Invoice`
		WHERE docstatus = 1 AND is_return = 0
		AND posting_date BETWEEN '{0}' AND '{1}'
		AND custom_zoho_invoice_id IS NULL AND custom_zb_consol_inv_id IS NULL
		""".format(from_date, to_date),
		as_dict=True
	)

	return query


@frappe.whitelist()
def get_participant_monthly_distribution(from_date, to_date):
	return get_data(from_date, to_date)