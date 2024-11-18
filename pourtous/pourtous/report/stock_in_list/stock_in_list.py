# Copyright (c) 2024, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not (filters.posting_date): # don't execute until filters are set
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
			"fieldname": "item_code",
			"label": "Item Code",
			"fieldtype": "Data",
			"width": "150"
		},

		{
			"fieldname": "item_name",
			"label": "Item Name",
			"fieldtype": "Data",
			"width": "300"
		},

		{
			"fieldname": "qty",
			"label": "Quantity",
			"fieldtype": "Float",
			"width": "150"
		},

		{
			"fieldname": "rate",
			"label": "Price",
			"fieldtype": "Currency",
			"width": "150"
		},
	]


def get_data(filters):

	query = frappe.db.sql(
		"""
			SELECT item_code, item_name, qty, rate
			FROM `tabPurchase Receipt Item`, `tabPurchase Receipt`
			WHERE `tabPurchase Receipt Item`.parent = `tabPurchase Receipt`.name
			AND `tabPurchase Receipt`.posting_date = '{0}'
		""".format(filters.posting_date),
		as_dict=True
	)

	return query