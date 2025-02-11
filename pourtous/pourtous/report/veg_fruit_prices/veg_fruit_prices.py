# Copyright (c) 2024, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not (filters.item_group and filters.price_list): # don't execute until both filters are set
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
			"fieldname": "price_list_rate",
			"label": "Price",
			"fieldtype": "Currency",
			"width": "80"
		},
	]


def get_data(filters):
	query = frappe.db.sql(
		"""
			select `tabItem Price`.item_code, `tabItem Price`.item_name, `tabItem Price`.price_list_rate
			from `tabItem Price`, tabItem
			where `tabItem Price`.price_list = '{0}'
			and `tabItem Price`.item_code = tabItem.item_code
			and tabItem.item_group = '{1}'
			AND tabItem.has_batch_no = 0
		""".format(filters.price_list, filters.item_group),
		as_dict=True
	)
	return query