# Copyright (c) 2024, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	""" if not (filters.item_group): # don't execute until both filters are set
		return [], [] """

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
			"width": "150"
		},

		{
			"fieldname": "item_name",
			"label": "Item Name",
			"fieldtype": "Data",
			"width": "300"
		},

		{
			"fieldname": "buying_price",
			"label": "B.Price",
			"fieldtype": "Currency",
			"width": "80"
		},
		{
			"fieldname": "selling_price",
			"label": "S.Price",
			"fieldtype": "Currency",
			"width": "80"
		},
	]


def get_data():
	query = frappe.db.sql(
		"""
		SELECT tabItem.item_code, tabItem.item_name, 
		(
			SELECT price_list_rate
			FROM `tabItem Price`
			WHERE `tabItem Price`.item_code = tabItem.item_code
			AND price_list = 'Standard Buying'
		) AS buying_price,
		(
			SELECT price_list_rate
			from `tabItem Price`
			WHERE `tabItem Price`.item_code = tabItem.item_code
			AND price_list = 'Standard Selling'
		) AS selling_price
		FROM tabItem
		WHERE tabItem.has_batch_no = 0
		""",
		as_dict=True
	)
	return query