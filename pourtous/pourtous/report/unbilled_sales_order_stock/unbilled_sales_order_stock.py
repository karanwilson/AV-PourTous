# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	#if not (filters.from_date and filters.to_date): # don't execute until filters are set
	#	return [], []

	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)

	if not data:
		msgprint(_('No records found'))
		return columns, data

	return columns, data


def get_columns(filters):
	if frappe.defaults.get_user_default("company") == 'Pour Tous Purchasing Service' and filters.show_details:
		return [
			{
				"fieldname": "sales_order",
				"label": "Sales Order",
				"fieldtype": "Link",
				"options": "Sales Order",
				"width": "180"
			},
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
				"width": "200"
			},
			{
				"fieldname": "stock_uom",
				"label": "UOM",
				"fieldtype": "Data",
				"width": "80"
			},
			{
				"fieldname": "rate",
				"label": "Price",
				"fieldtype": "Currency",
				"width": "100"
			},
			{
				"fieldname": "order_qty",
				"label": "Order Qty",
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
				"fieldname": "qty_needed",
				"label": "Qty Needed",
				"fieldtype": "Float",
				"width": "100"
			}
		]

	elif frappe.defaults.get_user_default("company") == 'Pour Tous Purchasing Service' and not filters.show_details:
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
				"width": "200"
			},
			{
				"fieldname": "stock_uom",
				"label": "UOM",
				"fieldtype": "Data",
				"width": "80"
			},
			{
				"fieldname": "order_qty",
				"label": "Order Qty",
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
				"fieldname": "qty_needed",
				"label": "Qty Needed",
				"fieldtype": "Float",
				"width": "100"
			}
		]

	elif filters.show_details:
		return [
			{
				"fieldname": "sales_order",
				"label": "Sales Order",
				"fieldtype": "Link",
				"options": "Sales Order",
				"width": "180"
			},
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
				"width": "200"
			},
			{
				"fieldname": "stock_uom",
				"label": "UOM",
				"fieldtype": "Data",
				"width": "80"
			},
			{
				"fieldname": "rate",
				"label": "Price",
				"fieldtype": "Currency",
				"width": "100"
			},
			{
				"fieldname": "order_qty",
				"label": "Order Qty",
				"fieldtype": "Float",
				"width": "100"
			},
			{
				"fieldname": "stores_qty",
				"label": "Stores Qty",
				"fieldtype": "Float",
				"width": "100"
			},
			{
				"fieldname": "qty_needed",
				"label": "Qty Needed",
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
				"width": "200"
			},
			{
				"fieldname": "stock_uom",
				"label": "UOM",
				"fieldtype": "Data",
				"width": "80"
			},
			{
				"fieldname": "order_qty",
				"label": "Order Qty",
				"fieldtype": "Float",
				"width": "100"
			},
			{
				"fieldname": "stores_qty",
				"label": "Stores Qty",
				"fieldtype": "Float",
				"width": "100"
			},
			{
				"fieldname": "qty_needed",
				"label": "Qty Needed",
				"fieldtype": "Float",
				"width": "100"
			}
		]


def get_data(filters):
	if frappe.defaults.get_user_default("company") == 'Pour Tous Purchasing Service' and filters.show_details:
		query = frappe.db.sql(
			"""
			SELECT table1.*,
			IF ((table1.order_qty > table1.stall_qty), (table1.order_qty - table1.stall_qty), 0) AS qty_needed

			FROM
			(SELECT s.name AS sales_order, i.item_code, i.item_name, i.stock_uom, i.rate, i.stock_qty AS order_qty,
			(
				SELECT `tabStock Ledger Entry`.qty_after_transaction from `tabStock Ledger Entry`
				WHERE (`tabStock Ledger Entry`.item_code = i.item_code) AND `tabStock Ledger Entry`.is_cancelled=0
				AND warehouse like '{0}'
				ORDER BY posting_date desc, posting_time desc, creation desc
				LIMIT 1
			) AS stall_qty
			FROM `tabSales Order Item` i , `tabSales Order` s

			where s.status not in ("Closed", "On Hold")
			AND s.per_billed < 99.99
			AND s.name = i.parent and i.docstatus = 1) table1
			""".format("Stall%"),
			as_dict=True
		)

	elif frappe.defaults.get_user_default("company") == 'Pour Tous Purchasing Service' and not filters.show_details:
		query = frappe.db.sql(
			"""
			SELECT table1.*,
			IF ((table1.order_qty > table1.stall_qty), (table1.order_qty - table1.stall_qty), 0) AS qty_needed

			FROM
			(SELECT i.item_code, i.item_name, i.stock_uom, SUM(i.stock_qty) AS order_qty,
			(
				SELECT `tabStock Ledger Entry`.qty_after_transaction from `tabStock Ledger Entry`
				WHERE (`tabStock Ledger Entry`.item_code = i.item_code) AND `tabStock Ledger Entry`.is_cancelled=0
				AND warehouse like '{0}'
				ORDER BY posting_date desc, posting_time desc, creation desc
				LIMIT 1
			) AS stall_qty
			FROM `tabSales Order Item` i , `tabSales Order` s

			where s.status not in ("Closed", "On Hold")
			AND s.per_billed < 99.99
			AND s.name = i.parent and i.docstatus = 1

			GROUP BY i.item_code) table1
			""".format("Stall%"),
			as_dict=True
		)

	elif filters.show_details:
		query = frappe.db.sql(
			"""
			SELECT table1.*,
			IF ((table1.order_qty > table1.stores_qty), (table1.order_qty - table1.stores_qty), 0) AS qty_needed

			FROM
			(SELECT s.name AS sales_order, i.item_code, i.item_name, i.stock_uom, i.rate, i.stock_qty AS order_qty,
			(
				SELECT `tabStock Ledger Entry`.qty_after_transaction from `tabStock Ledger Entry`
				WHERE (`tabStock Ledger Entry`.item_code = i.item_code) AND `tabStock Ledger Entry`.is_cancelled=0
				ORDER BY posting_date desc, posting_time desc, creation desc
				LIMIT 1
			) AS stores_qty
			FROM `tabSales Order Item` i , `tabSales Order` s

			where s.status not in ("Closed", "On Hold")
			AND s.per_billed < 99.99
			AND s.name = i.parent and i.docstatus = 1) table1
			""",
			as_dict=True
		)

	else:
		query = frappe.db.sql(
			"""
			SELECT table1.*,
			IF ((table1.order_qty > table1.stores_qty), (table1.order_qty - table1.stores_qty), 0) AS qty_needed

			FROM
			(SELECT i.item_code, i.item_name, i.stock_uom, SUM(i.stock_qty) AS order_qty,
			(
				SELECT `tabStock Ledger Entry`.qty_after_transaction from `tabStock Ledger Entry`
				WHERE (`tabStock Ledger Entry`.item_code = i.item_code) AND `tabStock Ledger Entry`.is_cancelled=0
				ORDER BY posting_date desc, posting_time desc, creation desc
				LIMIT 1
			) AS stores_qty
			FROM `tabSales Order Item` i , `tabSales Order` s

			where s.status not in ("Closed", "On Hold")
			AND s.per_billed < 99.99
			AND s.name = i.parent and i.docstatus = 1

			GROUP BY i.item_code) table1
			""",
			as_dict=True
		)


	return query