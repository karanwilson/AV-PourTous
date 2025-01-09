# Copyright (c) 2024, Karan and contributors
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
			"fieldname": "voucher_id",
			"label": "Voucher ID",
			"fieldtype": "Data",
			"width": "200"
		},
		{
			"fieldname": "posting_date",
			"label": "Posting Date",
			"fieldtype": "Date",
			"width": "100"
		},
		{
			"fieldname": "item_code",
			"label": "Item Code",
			"fieldtype": "Data",
			"width": "90"
		},
		{
			"fieldname": "item_name",
			"label": "Item Name",
			"fieldtype": "Data",
			"width": "300"
		},
		{
			"fieldname": "warehouse",
			"label": "warehouse",
			"fieldtype": "Float",
			"width": "100"
		},
		{
			"fieldname": "quantity_difference",
			"label": "Qty Difference",
			"fieldtype": "Float",
			"width": "100"
		},
		{
			"fieldname": "amount_difference",
			"label": "Amt Difference",
			"fieldtype": "Currency",
			"width": "100"
		},
		{
			"fieldname": "custom_comments",
			"label": "Comments",
			"fieldtype": "Data",
			"width": "180"
		},
	]


def get_data(filters):
	query = frappe.db.sql(
		"""
		SELECT `tabStock Reconciliation Item`.parent AS voucher_id, `tabStock Reconciliation`.posting_date,
		`tabStock Reconciliation Item`.item_code, `tabStock Reconciliation Item`.item_name,
		`tabStock Reconciliation Item`.warehouse, `tabStock Reconciliation Item`.quantity_difference,
		`tabStock Reconciliation Item`.amount_difference, `tabStock Reconciliation Item`.custom_comments

		FROM `tabStock Reconciliation`, `tabStock Reconciliation Item`
		WHERE parenttype = "Stock Reconciliation"
		AND `tabStock Reconciliation Item`.parent = `tabStock Reconciliation`.name
		AND `tabStock Reconciliation Item`.docstatus = 1
		AND (`tabStock Reconciliation`.posting_date >= '{0}')
		AND (`tabStock Reconciliation`.posting_date <= '{1}')
		""".format(filters.from_date, filters.to_date),
		as_dict=True
	)

	return query