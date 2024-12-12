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
			"width": "150"
		},
		{
			"fieldname": "batch_no",
			"label": " Batch No.",
			"fieldtype": "Data",
			"width": "100"
		},
		{
			"fieldname": "batch_qty",
			"label": "Quantity",
			"fieldtype": "Float",
			"width": "100"
		},
		{
			"fieldname": "posa_batch_price",
			"label": "Batch Price",
			"fieldtype": "Currency",
			"width": "100"
		},
		{
			"fieldname": "price_list_rate",
			"label": "Item Price",
			"fieldtype": "Currency",
			"width": "100"
		},
	]


def get_data(filters):
	query = frappe.db.sql(
		"""
		SELECT tabItem.item_code, tabItem.item_name, `tabItem Supplier`.supplier,
		tabBatch.name AS Batch, tabBatch.batch_qty AS Qty,
		IF(tabBatch.posa_batch_price > 0, tabBatch.posa_batch_price, `tabItem Price`.price_list_rate) AS Price
		FROM tabItem, `tabItem Supplier`, tabBatch, `tabItem Price`
		WHERE tabItem.item_code = `tabItem Supplier`.parent AND tabBatch.item = tabItem.item_code and tabBatch.batch_qty > 0
		AND `tabItem Price`.item_code = tabItem.item_code AND `tabItem Price`.price_list = "Standard Selling"
		AND tabItem.item_code = '{0}'
		""".format(filters.name),
		as_dict=True
	)

	return query