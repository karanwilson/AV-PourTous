# Copyright (c) 2024, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
from erpnext.stock.doctype.batch.batch import get_batch_qty


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
	#if frappe.defaults.get_user_default("company") == "Pour Tous Purchasing Service":
	if frappe.get_value("Item", filters.name, "has_batch_no"):
		return [
			{
				"fieldname": "item_code",
				"label": "Item Code",
				"fieldtype": "Data",
				"width": "70"
			},
			{
				"fieldname": "item_name",
				"label": "Item Name",
				"fieldtype": "Data",
				"width": "200"
			},
			{
				"fieldname": "supplier",
				"label": "Supplier",
				"fieldtype": "Data",
				"width": "150"
			},
			{
				"fieldname": "batch_no",
				"label": "Batch",
				"fieldtype": "Link",
				"options": "Batch",
				"width": "100"
			},
			{
				"fieldname": "serial_and_batch_bundle",
				"label": "SrBatch Bundle",
				"fieldtype": "Link",
				"options": "Serial and Batch Bundle",
				"width": "150"
			},
			{
				"fieldname": "warehouse",
				"label": "Store",
				"fieldtype": "Link",
				"options": "Warehouse",
				"width": "110"
			},
			{
				"fieldname": "qty",
				"label": "Qty",
				"fieldtype": "Float",
				"width": "70"
			},
			{
				"fieldname": "buying_price",
				"label": "Last Buy.Price",
				"fieldtype": "Currency",
				"width": "120"
			},
			{
				"fieldname": "batch_buying_price",
				"label": "Batch B.Price",
				"fieldtype": "Currency",
				"width": "110"
			},
			{
				"fieldname": "item_tax_template",
				"label": "Item Tax",
				"fieldtype": "Link",
				"options": "Item Tax Template",
				"width": "110"
			},			
			{
				"fieldname": "selling_price",
				"label": "S Price",
				"fieldtype": "Currency",
				"width": "80"
			},
			{
				"fieldname": "manufacturing_date",
				"label": "Batch Date",
				"fieldtype": "Date",
				"width": "100"
			},
			{
				"fieldname": "expiry_date",
				"label": "Exp Date",
				"fieldtype": "Date",
				"width": "100"
			},
			{
				"fieldname": "custom_barcode",
				"label": "Batch Barcode",
				"fieldtype": "Data",
				"width": "150"
			},
			{
				"fieldname": "barcode",
				"label": "Item Barcode",
				"fieldtype": "Data",
				"width": "150"
			},
		]

	else:
		return [
			{
				"fieldname": "item_code",
				"label": "Item Code",
				"fieldtype": "Data",
				"width": "80"
			},
			{
				"fieldname": "item_name",
				"label": "Item Name",
				"fieldtype": "Data",
				"width": "200"
			},
			{
				"fieldname": "supplier",
				"label": "Supplier",
				"fieldtype": "Data",
				"width": "150"	
			},
			{
				"fieldname": "stores_qty",
				"label": "Stores",
				"fieldtype": "Float",
				"width": "100"
			},
			{
				"fieldname": "stall_qty",
				"label": "Stall",
				"fieldtype": "Float",
				"width": "100"
			},
			{
				"fieldname": "store_1_qty",
				"label": "Store1",
				"fieldtype": "Float",
				"width": "80"
			},
			{
				"fieldname": "store_2_qty",
				"label": "Store2",
				"fieldtype": "Float",
				"width": "80"
			},
			{
				"fieldname": "store_3_qty",
				"label": "Store3",
				"fieldtype": "Float",
				"width": "80"
			},
			{
				"fieldname": "buying_price",
				"label": "B Price",
				"fieldtype": "Currency",
				"width": "80"
			},
			{
				"fieldname": "selling_price",
				"label": "S Price",
				"fieldtype": "Currency",
				"width": "80"
			},
			{
				"fieldname": "barcode",
				"label": "Item Barcode",
				"fieldtype": "Data",
				"width": "150"
			}
		]
	
	# elif frappe.defaults.get_user_default("company") == "Pour Tous Distribution Center":
	# 	if frappe.get_value("Item", filters.name, "has_batch_no"):
	# 		return [
	# 			{
	# 				"fieldname": "item_code",
	# 				"label": "Item Code",
	# 				"fieldtype": "Data",
	# 				"width": "70"
	# 			},
	# 			{
	# 				"fieldname": "item_name",
	# 				"label": "Item Name",
	# 				"fieldtype": "Data",
	# 				"width": "200"
	# 			},
	# 			{
	# 				"fieldname": "supplier",
	# 				"label": "Supplier",
	# 				"fieldtype": "Data",
	# 				"width": "150"
	# 			},
	# 			{
	# 				"fieldname": "batch_no",
	# 				"label": "Batch",
	# 				"fieldtype": "Link",
	# 				"options": "Batch",
	# 				"width": "100"
	# 			},
	# 			{
	# 				"fieldname": "serial_and_batch_bundle",
	# 				"label": "SrBatch Bundle",
	# 				"fieldtype": "Link",
	# 				"options": "Serial and Batch Bundle",
	# 				"width": "150"
	# 			},
	# 			{
	# 				"fieldname": "manufacturing_date",
	# 				"label": "Batch Date",
	# 				"fieldtype": "Date",
	# 				"width": "100"
	# 			},
	# 			{
	# 				"fieldname": "warehouse",
	# 				"label": "Store",
	# 				"fieldtype": "Link",
	# 				"width": "110"
	# 			},
	# 			{
	# 				"fieldname": "qty",
	# 				"label": "Qty",
	# 				"fieldtype": "Float",
	# 				"width": "80"
	# 			},
	# 			{
	# 				"fieldname": "buying_price",
	# 				"label": "Last Buy.Price",
	# 				"fieldtype": "Currency",
	# 				"width": "120"
	# 			},
	# 			{
	# 				"fieldname": "batch_buying_price",
	# 				"label": "Batch B.Price",
	# 				"fieldtype": "Currency",
	# 				"width": "110"
	# 			},
	# 			{
	# 				"fieldname": "selling_price",
	# 				"label": "S Price",
	# 				"fieldtype": "Currency",
	# 				"width": "80"
	# 			},
	# 			{
	# 				"fieldname": "custom_barcode",
	# 				"label": "Batch Barcode",
	# 				"fieldtype": "Data",
	# 				"width": "150"
	# 			},
	# 			{
	# 				"fieldname": "barcode",
	# 				"label": "Item Barcode",
	# 				"fieldtype": "Data",
	# 				"width": "150"
	# 			},
	# 			{
	# 				"fieldname": "qty",
	# 				"label": "Qty",
	# 				"fieldtype": "Float",
	# 				"width": "70"
	# 			}
	# 		]

	# 	else:
	# 		return [
	# 			{
	# 				"fieldname": "item_code",
	# 				"label": "Item Code",
	# 				"fieldtype": "Data",
	# 				"width": "80"
	# 			},
	# 			{
	# 				"fieldname": "item_name",
	# 				"label": "Item Name",
	# 				"fieldtype": "Data",
	# 				"width": "200"
	# 			},
	# 			{
	# 				"fieldname": "supplier",
	# 				"label": "Supplier",
	# 				"fieldtype": "Data",
	# 				"width": "150"	
	# 			},
	# 			{
	# 				"fieldname": "warehouse",
	# 				"label": "Store",
	# 				"fieldtype": "Link",
	# 				"width": "110"
	# 			},
	# 			{
	# 				"fieldname": "qty",
	# 				"label": "Qty",
	# 				"fieldtype": "Float",
	# 				"width": "80"
	# 			},
	# 			{
	# 				"fieldname": "buying_price",
	# 				"label": "B Price",
	# 				"fieldtype": "Currency",
	# 				"width": "80"
	# 			},
	# 			{
	# 				"fieldname": "selling_price",
	# 				"label": "S Price",
	# 				"fieldtype": "Currency",
	# 				"width": "80"
	# 			},
	# 			{
	# 				"fieldname": "barcode",
	# 				"label": "Item Barcode",
	# 				"fieldtype": "Data",
	# 				"width": "150"
	# 			},
	# 			{
	# 				"fieldname": "qty",
	# 				"label": "Qty",
	# 				"fieldtype": "Float",
	# 				"width": "70"
	# 			}
	# 		]

def get_data(filters):
	#if frappe.defaults.get_user_default("company") == "Pour Tous Purchasing Service":
	if frappe.get_value("Item", filters.name, "has_batch_no"):
		query = get_batch_qty(item_code=filters.name)
		for row in query:
			query2 = frappe.db.sql(
				"""
				SELECT sle.item_code, tabBatch.item_name, `tabItem Supplier`.supplier,
				sle.serial_and_batch_bundle, tabBatch.manufacturing_date,
				(
					SELECT price_list_rate FROM `tabItem Price`
					WHERE `tabItem Price`.item_code = sle.item_code
					AND price_list = "Standard Buying"
				) AS buying_price,
				tabBatch.custom_buying_price AS batch_buying_price, it.item_tax_template,
				tabBatch.posa_batch_price AS selling_price, tabBatch.custom_barcode,
				(
					SELECT barcode FROM `tabItem Barcode`
					WHERE `tabItem Barcode`.parent = tabItem.item_code
					AND tabItem.item_code = '{0}'
					limit 1
				) AS barcode
				FROM `tabStock Ledger Entry` sle, `tabItem Supplier`, tabBatch, tabItem
				LEFT JOIN `tabItem Tax` it ON it.parent = tabItem.name
				WHERE sle.is_cancelled = 0
				AND tabBatch.name = '{1}'
				AND `tabItem Supplier`.parent = sle.item_code
				AND sle.item_code = tabItem.item_code
				AND sle.item_code = '{0}'
				""".format(filters.name, row.batch_no),
				as_dict=True
			)

			row.update(query2[0])

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
			) AS stores_qty,
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
			) AS store_1_qty,
			(
				select `tabStock Ledger Entry`.qty_after_transaction from `tabStock Ledger Entry`
				where (`tabStock Ledger Entry`.item_code = tabItem.item_code) and `tabStock Ledger Entry`.is_cancelled=0
				and warehouse like '{3}'
				order by posting_date desc, posting_time desc, creation desc
				limit 1
			) AS store_2_qty,
			(
				select `tabStock Ledger Entry`.qty_after_transaction from `tabStock Ledger Entry`
				where (`tabStock Ledger Entry`.item_code = tabItem.item_code) and `tabStock Ledger Entry`.is_cancelled=0
				and warehouse like '{4}'
				order by posting_date desc, posting_time desc, creation desc
				limit 1
			) AS store_3_qty,
			(
				SELECT price_list_rate FROM `tabItem Price`
				WHERE `tabItem Price`.item_code = tabItem.item_code
				AND price_list = "Standard Buying"
			) AS buying_price,
			(
				SELECT price_list_rate FROM `tabItem Price`
				WHERE `tabItem Price`.item_code = tabItem.item_code
				AND price_list = "Standard Selling"
			) AS selling_price,
			(
				SELECT barcode FROM `tabItem Barcode`
				WHERE `tabItem Barcode`.parent = tabItem.item_code
				AND tabItem.item_code = '{5}'
				limit 1
			) AS barcode
			FROM tabItem, `tabItem Supplier`
			WHERE tabItem.item_code = `tabItem Supplier`.parent
			AND tabItem.item_code = '{5}'
			""".format("Stores%", "Stall%", "Store 1%", "Store 2%", "Store 3%", filters.name),
			as_dict=True
		)

	return query

	# elif frappe.defaults.get_user_default("company") == "Pour Tous Distribution Center":
	# 	if frappe.get_value("Item", filters.name, "has_batch_no"):
	# 		query = frappe.db.sql(
	# 			"""
	# 			SELECT `tabStock Ledger Entry`.item_code, tabBatch.item_name, `tabItem Supplier`.supplier,
	# 			`tabStock Ledger Entry`.batch_no, tabBatch.manufacturing_date,
	# 			(
	# 				SELECT SUM(actual_qty) FROM `tabStock Ledger Entry`
	# 				WHERE is_cancelled = 0 AND warehouse LIKE '{0}'
	# 				AND batch_no = tabBatch.name
	# 			) AS stores_qty,
	# 			(
	# 				SELECT SUM(actual_qty) FROM `tabStock Ledger Entry`
	# 				WHERE is_cancelled = 0 AND warehouse LIKE '{1}'
	# 				AND batch_no = tabBatch.name
	# 			) AS sunship_qty,
	# 			(
	# 				SELECT price_list_rate FROM `tabItem Price`
	# 				WHERE `tabItem Price`.item_code = `tabStock Ledger Entry`.item_code
	# 				AND price_list = "Standard Buying"
	# 			) AS buying_price,
	# 			tabBatch.custom_buying_price AS batch_buying_price,
	# 			tabBatch.posa_batch_price AS selling_price, tabBatch.custom_barcode,
	# 			(
	# 				SELECT barcode FROM `tabItem Barcode`
	# 				WHERE `tabItem Barcode`.parent = tabItem.item_code
	# 				AND tabItem.item_code = '{2}'
	# 				limit 1
	# 			) AS barcode
	# 			FROM `tabStock Ledger Entry`, `tabItem Supplier`, tabBatch, tabItem
	# 			WHERE `tabStock Ledger Entry`.is_cancelled = 0
	# 			AND tabBatch.name = `tabStock Ledger Entry`.batch_no
	# 			AND `tabItem Supplier`.parent = `tabStock Ledger Entry`.item_code
	# 			AND (
	# 			(
	# 				SELECT SUM(actual_qty) FROM `tabStock Ledger Entry`
	# 				WHERE is_cancelled = 0 AND warehouse LIKE '{0}'
	# 				AND batch_no = tabBatch.name
	# 			) != 0
	# 			OR
	# 			(
	# 				SELECT SUM(actual_qty) FROM `tabStock Ledger Entry`
	# 				WHERE is_cancelled = 0 AND warehouse LIKE '{1}'
	# 				AND batch_no = tabBatch.name
	# 			) != 0
	# 			)
	# 			AND `tabStock Ledger Entry`.item_code = tabItem.item_code
	# 			AND `tabStock Ledger Entry`.item_code = '{2}'
	# 			GROUP BY `tabStock Ledger Entry`.batch_no
	# 			""".format("Stores%", "Sunship%", filters.name),
	# 			as_dict=True
	# 		)

	# 	else:
	# 		query = frappe.db.sql(
	# 			"""
	# 			SELECT tabItem.item_code, tabItem.item_name, `tabItem Supplier`.supplier,
	# 			(
	# 				select `tabStock Ledger Entry`.qty_after_transaction from `tabStock Ledger Entry`
	# 				where (`tabStock Ledger Entry`.item_code = tabItem.item_code) and `tabStock Ledger Entry`.is_cancelled=0
	# 				and warehouse like '{0}'
	# 				order by posting_date desc, posting_time desc, creation desc
	# 				limit 1
	# 			) AS stores_qty,
	# 			(
	# 				select `tabStock Ledger Entry`.qty_after_transaction from `tabStock Ledger Entry`
	# 				where (`tabStock Ledger Entry`.item_code = tabItem.item_code) and `tabStock Ledger Entry`.is_cancelled=0
	# 				and warehouse like '{1}'
	# 				order by posting_date desc, posting_time desc, creation desc
	# 				limit 1
	# 			) AS sunship_qty,
	# 			(
	# 				SELECT price_list_rate FROM `tabItem Price`
	# 				WHERE `tabItem Price`.item_code = tabItem.item_code
	# 				AND price_list = "Standard Buying"
	# 			) AS buying_price,
	# 			(
	# 				SELECT price_list_rate FROM `tabItem Price`
	# 				WHERE `tabItem Price`.item_code = tabItem.item_code
	# 				AND price_list = "Standard Selling"
	# 			) AS selling_price,
	# 			(
	# 				SELECT barcode FROM `tabItem Barcode`
	# 				WHERE `tabItem Barcode`.parent = tabItem.item_code
	# 				AND tabItem.item_code = '{2}'
	# 				limit 1
	# 			) AS barcode
	# 			FROM tabItem, `tabItem Supplier`
	# 			WHERE tabItem.item_code = `tabItem Supplier`.parent
	# 			AND tabItem.item_code = '{2}'
	# 			""".format("Stores%", "Sunship%", filters.name),
	# 			as_dict=True
	# 		)
