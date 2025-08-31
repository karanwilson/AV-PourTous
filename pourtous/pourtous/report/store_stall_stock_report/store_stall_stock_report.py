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
	if filters.warehouse == "Stall - " + abbr:
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
				"width": "200"
			},
			{
				"fieldname": "so_reserve",
				"label": "SO Reserve",
				"fieldtype": "Float",
				"width": "115"
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
				"width": "200"
			}
		]


def get_data(filters, abbr):
	if filters.warehouse == "Stall - " + abbr and filters.item_group:
		query = frappe.db.sql(
			"""
			SELECT table1.*
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
				select `tabStock Ledger Entry`.qty_after_transaction from `tabStock Ledger Entry`
				where (`tabStock Ledger Entry`.item_code = tabItem.item_code) and `tabStock Ledger Entry`.is_cancelled=0
				and warehouse like '{1}'
				order by posting_date desc, posting_time desc, creation desc
				limit 1
			) AS so_reserve
			FROM tabItem WHERE tabItem.item_group = '{2}'
			) table1
			""".format(filters.warehouse, "Sales Order Reserve - "+abbr, filters.item_group),
			as_dict=True
			#WHERE table1.qty > 0
		)
		return query


	elif filters.warehouse == "Stall - " + abbr and not filters.item_group:
		query = frappe.db.sql(
			"""
			SELECT table1.*
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
				select `tabStock Ledger Entry`.qty_after_transaction from `tabStock Ledger Entry`
				where (`tabStock Ledger Entry`.item_code = tabItem.item_code) and `tabStock Ledger Entry`.is_cancelled=0
				and warehouse like '{1}'
				order by posting_date desc, posting_time desc, creation desc
				limit 1
			) AS so_reserve
			FROM tabItem
			) table1
			""".format(filters.warehouse, "Sales Order Reserve - "+abbr),
			as_dict=True
			#WHERE table1.qty > 0
		)
		return query


	elif not filters.warehouse == "Stall - " + abbr and filters.item_group:
		query = frappe.db.sql(
			"""
			SELECT table1.*
			FROM

			(
			SELECT tabItem.item_code, tabItem.item_name, tabItem.item_group,
			(
				SELECT `tabStock Ledger Entry`.qty_after_transaction FROM `tabStock Ledger Entry`
				WHERE (`tabStock Ledger Entry`.item_code = tabItem.item_code) AND `tabStock Ledger Entry`.is_cancelled=0
				AND warehouse = '{0}'
				ORDER BY posting_date desc, posting_time desc, creation desc
				LIMIT 1
			) AS qty
			FROM tabItem WHERE tabItem.item_group = '{1}'
			) table1
			""".format(filters.warehouse, filters.item_group),
			as_dict=True
			#WHERE table1.qty > 0
		)
		return query


	else:
		query = frappe.db.sql(
			"""
			SELECT table1.*
			FROM

			(
			SELECT tabItem.item_code, tabItem.item_name, tabItem.item_group,
			(
				SELECT `tabStock Ledger Entry`.qty_after_transaction FROM `tabStock Ledger Entry`
				WHERE (`tabStock Ledger Entry`.item_code = tabItem.item_code) AND `tabStock Ledger Entry`.is_cancelled=0
				AND warehouse = '{0}'
				ORDER BY posting_date desc, posting_time desc, creation desc
				LIMIT 1
			) AS qty
			FROM tabItem
			) table1
			""".format(filters.warehouse),
			as_dict=True
			#WHERE table1.qty > 0
		)
		return query