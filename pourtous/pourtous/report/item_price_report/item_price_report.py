# Copyright (c) 2024, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	#if not (filters.name): # don't execute until filters are set
	#	return [], []

	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)

	if not data:
		msgprint(_('No records found'))
		return columns, data

	return columns, data


def get_columns(filters):
	#if frappe.get_value("Item", filters.name, "has_batch_no"):
	if filters.has_batch_no == 1:
		return [
			{
				"fieldname": "item_code",
				"label": "Code",
				"fieldtype": "Data",
				"width": "70"
			},
			{
				"fieldname": "item_name",
				"label": "Item Name",
				"fieldtype": "Data",
				"width": "250"
			},
			{
				"fieldname": "supplier",
				"label": "Supplier",
				"fieldtype": "Data",
				"width": "200"
			},
			{
				"fieldname": "batch_no",
				"label": "Batch No.",
				"fieldtype": "Link",
				"options": "Batch",
				"width": "100"
			},
			{
				"fieldname": "store_qty",
				"label": "Store Qty",
				"fieldtype": "Float",
				"width": "90"
			},
			{
				"fieldname": "stall_qty",
				"label": "Stall Qty",
				"fieldtype": "Float",
				"width": "80"
			},
			{
				"fieldname": "so_reserve",
				"label": "SO Reserve",
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
				"fieldname": "batch_buying_price",
				"label": "Batch B.Price",
				"fieldtype": "Currency",
				"width": "110"
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
				"fieldname": "so_reserve",
				"label": "SO Reserve",
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
	#if frappe.get_value("Item", filters.name, "has_batch_no"):
	if filters.has_batch_no == 1:
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
				SELECT SUM(actual_qty) FROM `tabStock Ledger Entry`
				WHERE is_cancelled = 0 AND warehouse LIKE '{2}'
				AND batch_no = tabBatch.name
			) AS so_reserve,
			tabBatch.custom_buying_price AS batch_buying_price,
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
			OR
			(
				SELECT SUM(actual_qty) FROM `tabStock Ledger Entry`
				WHERE is_cancelled = 0 AND warehouse LIKE '{2}'
				AND batch_no = tabBatch.name
			) != 0
			)
			GROUP BY `tabStock Ledger Entry`.item_code
			""".format("Stores%", "Stall%", "Sales Order Reserve%"),
			as_dict=True
			# GROUP BY `tabStock Ledger Entry`.batch_no
			# GROUP BY `tabStock Ledger Entry`.item_code
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
				select `tabStock Ledger Entry`.qty_after_transaction from `tabStock Ledger Entry`
				where (`tabStock Ledger Entry`.item_code = tabItem.item_code) and `tabStock Ledger Entry`.is_cancelled=0
				and warehouse like '{2}'
				order by posting_date desc, posting_time desc, creation desc
				limit 1
			) AS so_reserve,
			(
				SELECT price_list_rate FROM `tabItem Price`
				WHERE `tabItem Price`.item_code = tabItem.item_code
				AND price_list = "Standard Buying"
				limit 1
			) AS buying_price,
			(
				SELECT price_list_rate FROM `tabItem Price`
				WHERE `tabItem Price`.item_code = tabItem.item_code
				AND price_list = "Standard Selling"
				limit 1
			) AS selling_price
			FROM tabItem, `tabItem Supplier`
			WHERE tabItem.item_code = `tabItem Supplier`.parent
			AND tabItem.has_batch_no = 0
			""".format("Stores%", "Stall%", "Sales Order Reserve%"),
			as_dict=True
		)
		# SELECT tabItem.item_code, tabItem.item_name, `tabItem Supplier`.supplier,
		# FROM tabItem, `tabItem Supplier`
		# WHERE tabItem.item_code = `tabItem Supplier`.parent
		# AND tabItem.item_code = '{3}'

	return query