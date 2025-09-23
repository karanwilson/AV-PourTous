# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	# if not (filters.name or filters.item_code): # don't execute until filters are set
	# 	return [], []

	columns, data = [], []

	columns = get_columns()
	data = get_data()

	if not data:
		msgprint(_('No records found'))
		return columns, data

	return columns, data


def get_columns():
	return [
		{
			"fieldname": "item_code",
			"label": "Item Code",
			"fieldtype": "Data",
			"width": "90"
		},
		{
			"fieldname": "gst_hsn_code",
			"label": "HSN Code",
			"fieldtype": "Data",
			"width": "90"
		},
		{
			"fieldname": "item_name",
			"label": "Item Name",
			"fieldtype": "Data",
			"width": "350"
		},
		{
			"fieldname": "supplier",
			"label": "Supplier",
			"fieldtype": "Data",
			"width": "300"
		},
		{
			"fieldname": "item_tax_template",
			"label": "Item Tax",
			"fieldtype": "Link",
			"options": "Item Tax Template",
			"width": "150"
		},
	]


def get_data():
	query = frappe.db.sql(
		"""
		SELECT i.item_code, i.gst_hsn_code, i.item_name, its.supplier, it.item_tax_template
		FROM tabItem i, `tabItem Supplier` its, `tabItem Tax` it
		WHERE its.parent = i.item_code
		AND it.parent = i.item_code
		""",
		as_dict=True
	)

	return query