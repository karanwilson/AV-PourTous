# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	# if not (filters): # don't execute until filters are set
	# 	return [], []
	columns, data = [], []

	columns = get_columns()
	data = get_data(filters)

	if not data:
		msgprint(_('No records found'))
		return columns, data

	return columns, data


def get_columns():
	if frappe.defaults.get_user_default("company") == "Pour Tous Purchasing Service":
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
				"width": "250"
			},
			{
				"fieldname": "item_group",
				"label": "Item Group",
				"fieldtype": "Data",
				"width": "200"
			},
			{
				"fieldname": "supplier",
				"label": "Supplier",
				"fieldtype": "Data",
				"width": "200"
			},
			{
				"fieldname": "stores_qty",
				"label": "Stores",
				"fieldtype": "Float",
				"width": "90"
			},
			{
				"fieldname": "stall_qty",
				"label": "Stall",
				"fieldtype": "Float",
				"width": "80"
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
		]
	
	else:
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
				"width": "250"
			},
			{
				"fieldname": "item_group",
				"label": "Item Group",
				"fieldtype": "Data",
				"width": "200"
			},
			{
				"fieldname": "supplier",
				"label": "Supplier",
				"fieldtype": "Data",
				"width": "200"
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
		]


def get_data(filters):
	if frappe.defaults.get_user_default("company") == "Pour Tous Purchasing Service":
		if filters.supplier:
			query = frappe.db.sql(
				"""
				SELECT table1.*
				FROM

				(
				SELECT tabItem.item_code, tabItem.item_name, tabItem.item_group, `tabItem Supplier`.supplier,
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
				) AS store_3_qty
				FROM tabItem, `tabItem Supplier`
				WHERE tabItem.item_code = `tabItem Supplier`.parent
				AND `tabItem Supplier`.supplier = '{5}'
				) table1
				""".format("Stores%", "Stall%", "Store 1%", "Store 2%", "Store 3%", filters.supplier),
				as_dict=True
			)

		else:
			query = frappe.db.sql(
				"""
				SELECT table1.*
				FROM

				(
				SELECT tabItem.item_code, tabItem.item_name, tabItem.item_group, `tabItem Supplier`.supplier,
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
				) AS store_3_qty
				FROM tabItem, `tabItem Supplier`
				WHERE tabItem.item_code = `tabItem Supplier`.parent
				) table1
				""".format("Stores%", "Stall%", "Store 1%", "Store 2%", "Store 3%"),
				as_dict=True
			)

		return query
	
	else:
		if filters.supplier:
			query = frappe.db.sql(
				"""
				SELECT table1.*
				FROM

				(
				SELECT tabItem.item_code, tabItem.item_name, tabItem.item_group, `tabItem Supplier`.supplier,
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
				FROM tabItem, `tabItem Supplier`
				WHERE tabItem.item_code = `tabItem Supplier`.parent
				AND `tabItem Supplier`.supplier = '{3}'
				) table1
				""".format("Stores%", "Stall%", filters.supplier),
				as_dict=True
			)

		else:
			query = frappe.db.sql(
				"""
				SELECT table1.*
				FROM

				(
				SELECT tabItem.item_code, tabItem.item_name, tabItem.item_group, `tabItem Supplier`.supplier,
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
				FROM tabItem, `tabItem Supplier`
				WHERE tabItem.item_code = `tabItem Supplier`.parent
				) table1
				""".format("Stores%", "Stall%"),
				as_dict=True
			)

		return query