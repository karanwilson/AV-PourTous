# Copyright (c) 2024, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not (filters.name): # don't execute until filters are set
		return [], []

	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)

	if not data:
		msgprint(_('No records found'))
		return columns, data

	return columns, data


def get_columns(filters):
	if frappe.get_value("Item", filters.name, "has_batch_no"):
		return [
			{
				"fieldname": "item_code",
				"label": "Code",
				"fieldtype": "Data",
				"width": "80"
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
				"fieldname": "batch_no",
				"label": "Batch No.",
				"fieldtype": "Data",
				"width": "130"
			},
			{
				"fieldname": "qty",
				"label": "Qty",
				"fieldtype": "Float",
				"width": "80"
			},
			{
				"fieldname": "price",
				"label": "Price",
				"fieldtype": "Currency",
				"width": "80"
			},
		]
		""" {
			"fieldname": "warehouse",
			"label": "Warehouse",
			"fieldtype": "Data",
			"width": "120"
		}, """

	else:
		return [
			{
				"fieldname": "item_code",
				"label": "Code",
				"fieldtype": "Data",
				"width": "80"
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
				"fieldname": "price",
				"label": "Price",
				"fieldtype": "Currency",
				"width": "80"
			},
		]		


def get_data(filters):
	if frappe.get_value("Item", filters.name, "has_batch_no"):
		query = frappe.db.sql(
			"""
			select `tabStock Ledger Entry`.item_code, tabBatch.item_name, tabBatch.supplier,
			`tabStock Ledger Entry`.batch_no, `tabStock Ledger Entry`.warehouse,
			SUM(`tabStock Ledger Entry`.actual_qty) as qty, tabBatch.posa_batch_price AS price
			from `tabStock Ledger Entry`, tabBatch
			where `tabStock Ledger Entry`.is_cancelled = 0
			and `tabStock Ledger Entry`.batch_no = tabBatch.name
			AND tabBatch.batch_qty != 0
			and `tabStock Ledger Entry`.item_code = '{0}'
			group by `tabStock Ledger Entry`.batch_no
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