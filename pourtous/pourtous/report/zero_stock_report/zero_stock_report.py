# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
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
			"width": "90"
		},
		{
			"fieldname": "item_name",
			"label": "Item Name",
			"fieldtype": "Data",
			"width": "300"
		},
		{
			"fieldname": "stock_uom",
			"label": "UOM",
			"fieldtype": "Link",
			"options": "UOM",
			"width": "90"
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


def get_data():
	query = frappe.db.sql(
		"""
		SELECT tabItem.item_code, tabItem.item_name, tabItem.stock_uom,
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
		FROM tabItem
		WHERE
		(
		(
			select `tabStock Ledger Entry`.qty_after_transaction from `tabStock Ledger Entry`
			where (`tabStock Ledger Entry`.item_code = tabItem.item_code) and `tabStock Ledger Entry`.is_cancelled=0
			and warehouse like '{0}'
			order by posting_date desc, posting_time desc, creation desc
			limit 1
		) > 0
		OR
		(
			select `tabStock Ledger Entry`.qty_after_transaction from `tabStock Ledger Entry`
			where (`tabStock Ledger Entry`.item_code = tabItem.item_code) and `tabStock Ledger Entry`.is_cancelled=0
			and warehouse like '{1}'
			order by posting_date desc, posting_time desc, creation desc
			limit 1
		) > 0
		)
		""".format("Stores%", "Stall%"),
		as_dict=True
	)

	return query