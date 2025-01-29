# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)

	if not data:
		msgprint(_('No records found'))
		return columns, data

	return columns, data


def get_columns(filters):
	if filters.view_so:
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
				"fieldname": "qty",
				"label": "Quantity",
				"fieldtype": "Float",
				"width": "100"
			},
			{
				"fieldname": "sales_order",
				"label": "Sales Order",
				"fieldtype": "Link",
				"options": "Sales Order",
				"width": "200"
			},
			{
				"fieldname": "customer",
				"label": "Customer ID",
				"fieldtype": "Link",
				"options": "Customer",
				"width": "150"
			},
			{
				"fieldname": "customer_name",
				"label": "Customer Name",
				"fieldtype": "Data",
				"width": "200"
			}
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
				"width": "350"
			},
			{
				"fieldname": "qty",
				"label": "Quantity",
				"fieldtype": "Float",
				"width": "100"
			}
		]


def get_data(filters):
	if filters.item and filters.view_so:
		query = frappe.db.sql(
			"""
			SELECT item_code, item_name, qty, parent AS sales_order,
			`tabSales Order`.customer, `tabSales Order`.customer_name
			FROM `tabSales Order Item`, `tabSales Order`
			WHERE parent = `tabSales Order`.name AND `tabSales Order`.docstatus = 1
			AND item_code = '{0}'
			AND parent NOT IN ( SELECT sales_order FROM `tabSales Invoice Item` WHERE sales_order != "NULL" )
			""".format(filters.item),
			as_dict=True
		)

		return query
	
	elif filters.item and not filters.view_so:
		query = frappe.db.sql(
			"""
			SELECT item_code, item_name, SUM(qty) AS qty
			FROM `tabSales Order Item`, `tabSales Order`
			WHERE parent = `tabSales Order`.name AND `tabSales Order`.docstatus = 1
			AND item_code = '{0}'
			AND parent NOT IN ( SELECT sales_order FROM `tabSales Invoice Item` WHERE sales_order != "NULL" )
			GROUP BY item_code
			""".format(filters.item),
			as_dict=True
		)

		return query

	elif not filters.item and filters.view_so:
		query = frappe.db.sql(
			"""
			SELECT item_code, item_name, qty, parent AS sales_order,
			`tabSales Order`.customer, `tabSales Order`.customer_name
			FROM `tabSales Order Item`, `tabSales Order`
			WHERE parent = `tabSales Order`.name AND `tabSales Order`.docstatus = 1
			AND parent NOT IN ( SELECT sales_order FROM `tabSales Invoice Item` WHERE sales_order != "NULL" )
			""".format(filters.item),
			as_dict=True
		)

		return query

	else:
		query = frappe.db.sql(
			"""
			SELECT item_code, item_name, SUM(qty) AS qty
			FROM `tabSales Order Item`, `tabSales Order`
			WHERE parent = `tabSales Order`.name AND `tabSales Order`.docstatus = 1
			AND parent NOT IN ( SELECT sales_order FROM `tabSales Invoice Item` WHERE sales_order != "NULL" )
			GROUP BY item_code
			""",
			as_dict=True
		)

		return query