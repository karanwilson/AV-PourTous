# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not (filters.from_date and filters.to_date): # don't execute until filters are set
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
			"fieldname": "gst_hsn_code",
			"label": "HSN Code",
			"fieldtype": "Link",
			"options": "GST HSN Code",
			"width": "100"
		},
		{
			"fieldname": "description",
			"label": "Description",
			"fieldtype": "Data",
			"width": "300"
		},
		{
			"fieldname": "uom",
			"label": "UOM",
			"fieldtype": "Data",
			"width": "70"
		},
		{
			"fieldname": "total_qty",
			"label": "Total Qty",
			"fieldtype": "Float",
			"width": "125"
		},
		{
			"fieldname": "item_tax_template",
			"label": "Item Tax Template",
			"fieldtype": "Link",
			"options": "Item Tax Template",
			"width": "125"
		},
		{
			"fieldname": "cgst_amount",
			"label": "CGST Amount",
			"fieldtype": "Currency",
			"width": "125"
		},
		{
			"fieldname": "sgst_amount",
			"label": "SGST Amount",
			"fieldtype": "Currency",
			"width": "125"
		},
		{
			"fieldname": "total_tax",
			"label": "Total Tax",
			"fieldtype": "Currency",
			"width": "100"
		},
	]


def get_data(filters):
	itemised_hsn_query = frappe.db.sql(
		"""
		SELECT tabItem.gst_hsn_code, `tabGST HSN Code`.description, `tabSales Invoice Item`.uom,
		SUM(`tabSales Invoice Item`.net_amount) AS total_qty, `tabSales Invoice Item`.item_tax_template,
		SUM(`tabSales Invoice Item`.cgst_amount) AS cgst_amount, SUM(`tabSales Invoice Item`.sgst_amount) AS sgst_amount,
		(SUM(`tabSales Invoice Item`.cgst_amount) + SUM(`tabSales Invoice Item`.sgst_amount)) AS total_tax

		FROM tabItem, `tabGST HSN Code`, `tabSales Invoice Item`, `tabSales Invoice`

		WHERE `tabSales Invoice`.docstatus = 1 AND `tabSales Invoice Item`.docstatus = 1
		AND tabItem.gst_hsn_code = `tabGST HSN Code`.hsn_code
		AND tabItem.item_code = `tabSales Invoice Item`.item_code
		AND `tabSales Invoice Item`.parent = `tabSales Invoice`.name
		AND posting_date BETWEEN '{0}' AND '{1}'

		GROUP BY tabItem.gst_hsn_code
		""".format(filters.from_date, filters.to_date),
		as_dict=True
	)

	return itemised_hsn_query