# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not (filters.warehouse): # don't execute until filters are set
		return [], []

	columns, data = [], []

	abbr = frappe.get_value("Company", frappe.defaults.get_user_default("company"), 'abbr')
	# get company abbreviation

	columns = get_columns(filters, abbr)
	data = get_data(filters, abbr)

	if not data:
		msgprint(_('No records found'))
		return columns, data

	return columns, data


def get_columns(filters, abbr):
	if filters.warehouse == "Stall - "+abbr:
		return [
			{
				"fieldname": "item_code",
				"label": "Item Code",
				"fieldtype": "Data",
				"width": "100"
			},
			{
				"fieldname": "item_name",
				"label": "Item Name",
				"fieldtype": "Data",
				"width": "500"
			},
			{
				"fieldname": "item_group",
				"label": "Item Group",
				"fieldtype": "Data",
				"width": "250"
			},
			{
				"fieldname": "qty",
				"label": filters.warehouse,
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
				"label": "Balance Qty",
				"fieldtype": "Float",
				"width": "100"
			}
		]

	else:
		return [
			{
				"fieldname": "item_code",
				"label": "Item Code",
				"fieldtype": "Data",
				"width": "100"
			},
			{
				"fieldname": "item_name",
				"label": "Item Name",
				"fieldtype": "Data",
				"width": "500"
			},
			{
				"fieldname": "item_group",
				"label": "Item Group",
				"fieldtype": "Data",
				"width": "250"
			},
			{
				"fieldname": "qty",
				"label": filters.warehouse,
				"fieldtype": "Float",
				"width": "100"
			}
		]


def get_data(filters, abbr):
	if filters.warehouse == "Stall - "+abbr and filters.item_group:
		query = frappe.db.sql(
			"""
			SELECT table1.*,
			IF((table1.so_reserved != "NULL"), (table1.qty - table1.so_reserved), (table1.qty - 0)) AS balance_qty
			FROM

			(
			SELECT tabItem.item_code, tabItem.item_name, tabItem.item_group,
			(
				SELECT `tabStock Ledger Entry`.qty_after_transaction FROM `tabStock Ledger Entry`
				WHERE (`tabStock Ledger Entry`.item_code = tabItem.item_code) AND `tabStock Ledger Entry`.is_cancelled=0
				AND warehouse = '{0}'
				ORDER BY posting_date desc, posting_time desc, creation desc
				LIMIT 1
			) AS qty,
			(
				SELECT SUM(qty)
				FROM `tabSales Order Item`, `tabSales Order`
				WHERE parent = `tabSales Order`.name AND `tabSales Order`.docstatus = 1
				AND parent NOT IN ( SELECT sales_order FROM `tabSales Invoice Item` WHERE sales_order != "NULL" )
				AND `tabSales Order Item`.item_code = tabItem.item_code
				GROUP BY item_code
			) AS so_reserved
			FROM tabItem WHERE tabItem.item_group = '{1}'
			) table1

			WHERE table1.qty > 0
			""".format(filters.warehouse, filters.item_group),
			as_dict=True
		)
		return query


	elif filters.warehouse == "Stall - "+abbr and not filters.item_group:
		query = frappe.db.sql(
			"""
			SELECT table1.*,
			IF((table1.so_reserved != "NULL"), (table1.qty - table1.so_reserved), (table1.qty - 0)) AS balance_qty
			FROM

			(
			SELECT tabItem.item_code, tabItem.item_name, tabItem.item_group,
			(
				SELECT `tabStock Ledger Entry`.qty_after_transaction FROM `tabStock Ledger Entry`
				WHERE (`tabStock Ledger Entry`.item_code = tabItem.item_code) AND `tabStock Ledger Entry`.is_cancelled=0
				AND warehouse = '{0}'
				ORDER BY posting_date desc, posting_time desc, creation desc
				LIMIT 1
			) AS qty,
			(
				SELECT SUM(qty)
				FROM `tabSales Order Item`, `tabSales Order`
				WHERE parent = `tabSales Order`.name AND `tabSales Order`.docstatus = 1
				AND parent NOT IN ( SELECT sales_order FROM `tabSales Invoice Item` WHERE sales_order != "NULL" )
				AND `tabSales Order Item`.item_code = tabItem.item_code
				GROUP BY item_code
			) AS so_reserved
			FROM tabItem
			) table1

			WHERE table1.qty > 0
			""".format(filters.warehouse),
			as_dict=True
		)
		return query


	elif filters.warehouse != "Stall - "+abbr and filters.item_group:
		query = frappe.db.sql(
			"""
			SELECT table1.*,
			IF((table1.so_reserved != "NULL"), (table1.qty - table1.so_reserved), (table1.qty - 0)) AS balance_qty
			FROM

			(
			SELECT tabItem.item_code, tabItem.item_name, tabItem.item_group,
			(
				SELECT `tabStock Ledger Entry`.qty_after_transaction FROM `tabStock Ledger Entry`
				WHERE (`tabStock Ledger Entry`.item_code = tabItem.item_code) AND `tabStock Ledger Entry`.is_cancelled=0
				AND warehouse = '{0}'
				ORDER BY posting_date desc, posting_time desc, creation desc
				LIMIT 1
			) AS qty,
			(
				SELECT SUM(qty)
				FROM `tabSales Order Item`, `tabSales Order`
				WHERE parent = `tabSales Order`.name AND `tabSales Order`.docstatus = 1
				AND parent NOT IN ( SELECT sales_order FROM `tabSales Invoice Item` WHERE sales_order != "NULL" )
				AND `tabSales Order Item`.item_code = tabItem.item_code
				GROUP BY item_code
			) AS so_reserved
			FROM tabItem WHERE tabItem.item_group = '{1}'
			) table1

			WHERE table1.qty > 0
			""".format(filters.warehouse, filters.item_group),
			as_dict=True
		)
		return query


	else:
		query = frappe.db.sql(
			"""
			SELECT table1.*
			FROM

			(SELECT tabItem.item_code, tabItem.item_name, tabItem.item_group,
			(
				SELECT `tabStock Ledger Entry`.qty_after_transaction FROM `tabStock Ledger Entry`
				WHERE (`tabStock Ledger Entry`.item_code = tabItem.item_code) AND `tabStock Ledger Entry`.is_cancelled=0
				AND warehouse = '{0}'
				ORDER BY posting_date desc, posting_time desc, creation desc
				LIMIT 1
			) AS qty FROM tabItem
			) table1

			WHERE table1.qty > 0
			""".format(filters.warehouse),
			as_dict=True
		)
		return query