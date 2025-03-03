# Copyright (c) 2024, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not (filters.voucher_type and filters.posting_date): # don't execute until filters are set
		return [], []

	columns, data = [], []

	columns = get_columns(filters)

	if filters.from_time and filters.to_time:
		data = get_data1(filters)
	else:
		data = get_data2(filters)

	if not data:
		msgprint(_('No records found'))
		return columns, data

	return columns, data


def get_columns(filters):
	if filters.voucher_type == "Purchase Receipt":
		return [
			{
				"fieldname": "voucher_name",
				"label": "Voucher ID",
				"fieldtype": "Link",
				"options": "Purchase Receipt",
				"width": "135"
			},

			{
				"fieldname": "supplier",
				"label": "Supplier",
				"fieldtype": "Data",
				"width": "150"
			},

			{
				"fieldname": "item_code",
				"label": "Item Code",
				"fieldtype": "Data",
				"width": "90"
			},

			{
				"fieldname": "batch_no",
				"label": "Batch",
				"fieldtype": "Link",
				"options": "Batch",
				"width": "120"
			},

			{
				"fieldname": "custom_barcode",
				"label": "Barcode",
				"fieldtype": "Data",
				"width": "150"
			},

			{
				"fieldname": "item_name",
				"label": "Item Name",
				"fieldtype": "Data",
				"width": "250"
			},

			{
				"fieldname": "qty",
				"label": "Qty",
				"fieldtype": "Float",
				"width": "90"
			},

			{
				"fieldname": "custom_selling_price",
				"label": "S Price",
				"fieldtype": "Currency",
				"width": "100"
			},

			{
				"fieldname": "rate",
				"label": "Rate (Old PR)",
				"fieldtype": "Currency",
				"width": "120"
			},
		]

	else:
		return [
			{
				"fieldname": "voucher_type",
				"label": "Voucher Type",
				"fieldtype": "Data",
				"width": "135"
			},

			{
				"fieldname": "voucher_name",
				"label": "Voucher ID",
				"fieldtype": "Link",
				"options": "Stock Entry",
				"width": "200"
			},

			{
				"fieldname": "item_code",
				"label": "Item Code",
				"fieldtype": "Data",
				"width": "90"
			},

			{
				"fieldname": "batch_no",
				"label": "Batch",
				"fieldtype": "Link",
				"options": "Batch",
				"width": "130"
			},

			{
				"fieldname": "item_name",
				"label": "Item Name",
				"fieldtype": "Data",
				"width": "250"
			},

			{
				"fieldname": "qty",
				"label": "Quantity",
				"fieldtype": "Float",
				"width": "100"
			},
		]


def get_data1(filters):
	# with Time based filter

	if filters.voucher_type == "Purchase Receipt":
		query = frappe.db.sql(
			"""
			SELECT `tabPurchase Receipt`.name AS voucher_name, `tabPurchase Receipt`.title AS supplier,
			`tabPurchase Receipt Item`.item_code, `tabPurchase Receipt Item`.batch_no,
			tabBatch.custom_barcode, `tabPurchase Receipt Item`.item_name, `tabPurchase Receipt Item`.qty, `tabPurchase Receipt Item`.custom_selling_price,
			IF((`tabPurchase Receipt Item`.custom_selling_price = 0), `tabPurchase Receipt Item`.rate, 0) AS rate
			FROM `tabPurchase Receipt Item`
			INNER JOIN `tabPurchase Receipt` ON `tabPurchase Receipt Item`.parent = `tabPurchase Receipt`.name
			AND `tabPurchase Receipt`.docstatus = 1
			AND `tabPurchase Receipt`.posting_date = '{0}'
			AND `tabPurchase Receipt`.posting_time BETWEEN '{1}' AND '{2}'
			LEFT JOIN tabBatch
			ON `tabPurchase Receipt Item`.batch_no = tabBatch.name
			""".format(filters.posting_date, filters.from_time, filters.to_time),
			as_dict=True
		)

	else:
		abbr = frappe.get_value("Company", frappe.defaults.get_user_default("company"), 'abbr')
		# get company abbreviation
		warehouse = "Sales Order Reserve - " + abbr
		query = frappe.db.sql(
			"""
				SELECT stock_entry_type AS voucher_type, `tabStock Entry`.name AS voucher_name,
				item_code, batch_no, `tabStock Entry Detail`.item_name, qty
				FROM `tabStock Entry Detail`, `tabStock Entry`
				WHERE `tabStock Entry Detail`.parent = `tabStock Entry`.name
				AND `tabStock Entry Detail`.t_warehouse != '{1}'
				AND `tabStock Entry`.docstatus = 1
				AND `tabStock Entry`.posting_date = '{0}'
				AND `tabStock Entry`.posting_time BETWEEN '{2}' AND '{3}'
			""".format(filters.posting_date, warehouse, filters.from_time, filters.to_time),
			as_dict=True
		)

	return query


def get_data2(filters):
	# without Time based filter

	if filters.voucher_type == "Purchase Receipt":
		query = frappe.db.sql(
			"""
			SELECT `tabPurchase Receipt`.name AS voucher_name, `tabPurchase Receipt`.title AS supplier,
			`tabPurchase Receipt Item`.item_code, `tabPurchase Receipt Item`.batch_no,
			tabBatch.custom_barcode, `tabPurchase Receipt Item`.item_name, `tabPurchase Receipt Item`.qty, `tabPurchase Receipt Item`.custom_selling_price,
			IF((`tabPurchase Receipt Item`.custom_selling_price = 0), `tabPurchase Receipt Item`.rate, 0) AS rate
			FROM `tabPurchase Receipt Item`
			INNER JOIN `tabPurchase Receipt` ON `tabPurchase Receipt Item`.parent = `tabPurchase Receipt`.name
			AND `tabPurchase Receipt`.docstatus = 1
			AND `tabPurchase Receipt`.posting_date = '{0}'
			LEFT JOIN tabBatch
			ON `tabPurchase Receipt Item`.batch_no = tabBatch.name
			""".format(filters.posting_date),
			as_dict=True
		)

	else:
		abbr = frappe.get_value("Company", frappe.defaults.get_user_default("company"), 'abbr')
		# get company abbreviation
		warehouse = "Sales Order Reserve - " + abbr
		query = frappe.db.sql(
			"""
				SELECT stock_entry_type AS voucher_type, `tabStock Entry`.name AS voucher_name,
				item_code, batch_no, `tabStock Entry Detail`.item_name, qty
				FROM `tabStock Entry Detail`, `tabStock Entry`
				WHERE `tabStock Entry Detail`.parent = `tabStock Entry`.name
				AND `tabStock Entry Detail`.t_warehouse != '{1}'
				AND `tabStock Entry`.docstatus = 1
				AND `tabStock Entry`.posting_date = '{0}'
			""".format(filters.posting_date, warehouse),
			as_dict=True
		)

	return query