# Copyright (c) 2024, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
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
			"label": "Invoice ID",
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
			"fieldname": "item_group",
			"label": "Item Group",
			"fieldtype": "Data",
			"width": "150"
		},

		{
			"fieldname": "price_list_rate",
			"label": "Price",
			"fieldtype": "Currency",
			"width": "150"
		},
	]


def get_data(filters):

	query = frappe.db.sql(
		"""

		""",
		as_dict=True
	)

	return query