# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not (filters): # don't execute until filters are set
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
			"fieldname": "name",
			"label": "Invoice ID",
			"fieldtype": "Data",
			"width": "150"
		},
		{
			"fieldname": "customer",
			"label": "Customer",
			"fieldtype": "Data",
			"width": "150"
		},
		{
			"fieldname": "customer_name",
			"label": "Customer Name",
			"fieldtype": "Small Text",
			"width": "150"
		},
		{
			"fieldname": "grand_total",
			"label": "Grand Total",
			"fieldtype": "Float",
			"width": "100"
		},
		{
			"fieldname": "remarks",
			"label": "Remarks",
			"fieldtype": "Small Text",
			"width": "300"
		},
	]


def get_data(filters):
	query = frappe.db.sql(
		"""
		SELECT name, customer, customer_name, grand_total, remarks
		FROM `tabSales Invoice`
		WHERE remarks LIKE '%Aurocard Transaction ID:%{0}%'
		""".format(filters.remarks),
		as_dict=True
	)

	return query