# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not (filters): # don't execute until filters are set
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
		{
			"fieldname": "so_reserved",
			"label": "SO Reserved",
			"fieldtype": "Float",
			"width": "115"
		},
		{
			"fieldname": "balance_qty",
			"label": "Stall Balance",
			"fieldtype": "Float",
			"width": "115"
		}
	]


def get_data(filters):
	query = frappe.db.sql(
		"""
		SELECT table1.*,
		IF((table1.so_reserved != "NULL"), (table1.stall_qty - table1.so_reserved), (table1.stall_qty - 0)) AS balance_qty
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
			SELECT SUM(qty)
			FROM `tabSales Order Item`, `tabSales Order`
			WHERE parent = `tabSales Order`.name AND `tabSales Order`.docstatus = 1
			AND parent NOT IN ( SELECT sales_order FROM `tabSales Invoice Item` WHERE sales_order != "NULL" )
			AND `tabSales Order Item`.item_code = tabItem.item_code
			GROUP BY item_code
		) AS so_reserved
		FROM tabItem, `tabItem Supplier`
		WHERE tabItem.item_code = `tabItem Supplier`.parent
		AND `tabItem Supplier`.supplier = '{2}'
		) table1
		""".format("Stores%", "Stall%", filters.supplier),
		as_dict=True
	)

	return query