# Copyright (c) 2024, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not (filters.name or filters.item_code): # don't execute until filters are set
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
			"width": "350"
		},
		{
			"fieldname": "supplier",
			"label": "Supplier",
			"fieldtype": "Data",
			"width": "300"
		},
		{
			"fieldname": "store_qty",
			"label": " Store Qty",
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
	if filters.name:
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
			) AS stall_qty
			FROM tabItem, `tabItem Supplier`
			WHERE tabItem.item_code = `tabItem Supplier`.parent
			AND tabItem.item_code = '{2}'
			""".format("Stores%", "Stall%", filters.name),
			as_dict=True
		)

	elif filters.item_code:
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
			) AS stall_qty
			FROM tabItem, `tabItem Supplier`
			WHERE tabItem.item_code = `tabItem Supplier`.parent
			AND tabItem.item_code = '{2}'
			""".format("Stores%", "Stall%", filters.item_code),
			as_dict=True
		)

	return query