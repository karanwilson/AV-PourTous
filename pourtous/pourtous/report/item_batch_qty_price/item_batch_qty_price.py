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
				"width": "250"
			},
			{
				"fieldname": "batch_no",
				"label": "Batch No.",
				"fieldtype": "Data",
				"width": "130"
			},
			{
				"fieldname": "store_qty",
				"label": "Store Qty",
				"fieldtype": "Float",
				"width": "100"
			},
			{
				"fieldname": "stall_qty",
				"label": "Stall Qty",
				"fieldtype": "Float",
				"width": "100"
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
				"width": "250"	
			},
			{
				"fieldname": "store_qty",
				"label": "Store Qty",
				"fieldtype": "Float",
				"width": "100"
			},
			{
				"fieldname": "stall_qty",
				"label": "Stall Qty",
				"fieldtype": "Float",
				"width": "100"
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


def get_data(filters):
	if frappe.get_value("Item", filters.name, "has_batch_no"):
		query = frappe.db.sql(
			"""
			SELECT `tabStock Ledger Entry`.item_code, tabBatch.item_name, `tabItem Supplier`.supplier, `tabStock Ledger Entry`.batch_no,
			(
				SELECT SUM(actual_qty) FROM `tabStock Ledger Entry`
				WHERE is_cancelled = 0 AND warehouse LIKE '{0}'
				AND batch_no = tabBatch.name
			) AS store_qty,
			(
				SELECT SUM(actual_qty) FROM `tabStock Ledger Entry`
				WHERE is_cancelled = 0 AND warehouse LIKE '{1}'
				AND batch_no = tabBatch.name
			) AS stall_qty,
			(
				SELECT price_list_rate FROM `tabItem Price`
				WHERE `tabItem Price`.item_code = `tabStock Ledger Entry`.item_code
				AND price_list = "Standard Buying"
			) AS buying_price,
			tabBatch.posa_batch_price AS selling_price
			FROM `tabStock Ledger Entry`, `tabItem Supplier`, tabBatch
			WHERE `tabStock Ledger Entry`.is_cancelled = 0
			AND tabBatch.name = `tabStock Ledger Entry`.batch_no
			AND `tabItem Supplier`.parent = `tabStock Ledger Entry`.item_code
			AND (
			(
				SELECT SUM(actual_qty) FROM `tabStock Ledger Entry`
				WHERE is_cancelled = 0 AND warehouse LIKE '{0}'
				AND batch_no = tabBatch.name
			) != 0
			OR
			(
				SELECT SUM(actual_qty) FROM `tabStock Ledger Entry`
				WHERE is_cancelled = 0 AND warehouse LIKE '{1}'
				AND batch_no = tabBatch.name
			) != 0
			)
			AND `tabStock Ledger Entry`.item_code = '{2}'
			GROUP BY `tabStock Ledger Entry`.batch_no
			""".format("Stores%", "Stall%", filters.name),
			as_dict=True
		)

	else:
		query = frappe.db.sql(
			"""
			SELECT tabItem.item_code, tabItem.item_name, `tabItem Supplier`.supplier,
			(
				select `tabStock Ledger Entry`.qty_after_transaction from `tabStock Ledger Entry`
				where (`tabStock Ledger Entry`.item_code = tabItem.item_code) and `tabStock Ledger Entry`.is_cancelled=0
				and warehouse like '{0}'
				order by posting_date desc, posting_time desc, creation desc
				limit 1
			) AS store_qty,
			(
				select `tabStock Ledger Entry`.qty_after_transaction from `tabStock Ledger Entry`
				where (`tabStock Ledger Entry`.item_code = tabItem.item_code) and `tabStock Ledger Entry`.is_cancelled=0
				and warehouse like '{1}'
				order by posting_date desc, posting_time desc, creation desc
				limit 1
			) AS stall_qty,
			(
				SELECT price_list_rate FROM `tabItem Price`
				WHERE `tabItem Price`.item_code = tabItem.item_code
				AND price_list = "Standard Buying"
			) AS buying_price,
			(
				SELECT price_list_rate FROM `tabItem Price`
				WHERE `tabItem Price`.item_code = tabItem.item_code
				AND price_list = "Standard Selling"
			) AS selling_price
			FROM tabItem, `tabItem Supplier`
			WHERE tabItem.item_code = `tabItem Supplier`.parent
			AND tabItem.item_code = '{2}'
			""".format("Stores%", "Stall%", filters.name),
			as_dict=True
		)

	return query