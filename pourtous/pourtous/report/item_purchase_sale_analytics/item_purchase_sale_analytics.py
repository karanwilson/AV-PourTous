# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not (filters.supplier and filters.from_date and filters.to_date and (
		filters.voucher_type == "Purchase Receipt" or filters.voucher_type == "Purchase Invoice")):
		# don't execute until filters are set
		return [], []

	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)

	if not data:
		msgprint(_('No records found'))
		return columns, data

	return columns, data


def get_columns(filters):
	return [
		{
			"fieldname": "voucher_name",
			"label": "Voucher ID",
			"fieldtype": "Link",
			"options": filters.voucher_type,
			"width": "135"
		},

		{
			"fieldname": "item_code",
			"label": "Item Code",
			"fieldtype": "Data",
			"width": "130"
		},

		{
			"fieldname": "item_name",
			"label": "Item Name",
			"fieldtype": "Data",
			"width": "300"
		},

		{
			"fieldname": "item_group",
			"label": "Item Group",
			"fieldtype": "Data",
			"width": "250"
		},

		{
			"fieldname": "stock_uom",
			"label": "UOM",
			"fieldtype": "Data",
			"width": "80"
		},

		{
			"fieldname": "qty_purchased",
			"label": "Qty Purchased",
			"fieldtype": "float",
			"width": "130"
		},

		{
			"fieldname": "qty_sold",
			"label": "Qty Sold",
			"fieldtype": "float",
			"width": "130"
		},
	]


def get_data(filters):

	gst_sales_query = frappe.db.sql(
		"""
		select `tabStock Ledger Entry`.item_code, tabItem.item_name, tabItem.item_group, tabItem.stock_uom,
		(
			select SUM(actual_qty) from `tabStock Ledger Entry`
			where item_code = `tabItem Supplier`.parent
			AND `tabStock Ledger Entry`.voucher_type = "{3}"
			AND `tabStock Ledger Entry`.posting_date BETWEEN '{1}' AND '{2}'
		) AS qty_purchased,

		(
			select SUM(actual_qty) from `tabStock Ledger Entry`
			where item_code = `tabItem Supplier`.parent
			AND voucher_type = "Sales Invoice"
			AND `tabStock Ledger Entry`.posting_date BETWEEN '{1}' AND '{2}'
		) AS qty_sold
		FROM `tabStock Ledger Entry`, `tabItem Supplier`, tabItem
		WHERE `tabStock Ledger Entry`.is_cancelled = 0
		AND `tabStock Ledger Entry`.item_code = `tabItem Supplier`.parent
		AND `tabStock Ledger Entry`.item_code = tabItem.item_code
		AND`tabItem Supplier`.supplier = '{0}'
		GROUP BY `tabStock Ledger Entry`.item_code
		""".format(filters.supplier, filters.from_date, filters.to_date, filters.voucher_type),
		as_dict=True
	)

	return gst_sales_query