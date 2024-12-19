# Copyright (c) 2024, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not (filters.name): # don't execute until filters are set
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
			"width": "90"
		},
		{
			"fieldname": "item_name",
			"label": "Item Name",
			"fieldtype": "Data",
			"width": "300"
		},
		{
			"fieldname": "supplier",
			"label": "Supplier",
			"fieldtype": "Data",
			"width": "300"	
		},
		{
			"fieldname": "batch",
			"label": "Batch No.",
			"fieldtype": "Data",
			"width": "150"
		},
		{
			"fieldname": "price",
			"label": "Batch Price",
			"fieldtype": "Currency",
			"width": "100"
		},
	]


def get_data(filters):
	if frappe.get_value("Item", filters.name, "has_batch_no"):
		query = frappe.db.sql(
			"""
			SELECT item as item_code, item_name, supplier,
			tabBatch.name AS batch, posa_batch_price AS price
			FROM tabBatch, `tabStock Ledger Entry`
			WHERE item = `tabStock Ledger Entry`.item_code
			AND `tabStock Ledger Entry`.is_cancelled = 0
			AND batch_qty != 0
			AND item_code = '{0}'
			GROUP BY tabBatch.name
			""".format(filters.name),
			as_dict=True
		)

	else:
		query = frappe.db.sql(
			"""
			SELECT tabItem.item_code, tabItem.item_name, `tabItem Supplier`.supplier,
			`tabItem Price`.price_list_rate AS price
			FROM tabItem, `tabItem Supplier`, `tabItem Price`
			WHERE tabItem.item_code = `tabItem Supplier`.parent
			AND `tabItem Price`.item_code = tabItem.item_code
			AND `tabItem Price`.price_list = "Standard Selling"
			AND tabItem.item_code = '{0}'
			""".format(filters.name),
			as_dict=True
		)

	return query