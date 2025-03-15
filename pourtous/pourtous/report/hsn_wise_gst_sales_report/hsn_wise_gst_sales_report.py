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
			"fieldname": "total_qty",
			"label": "Total Units",
			"fieldtype": "Float",
			"width": "100"
		},
		{
			"fieldname": "taxable_value",
			"label": "Taxable Value",
			"fieldtype": "Currency",
			"width": "125"
		},

		{
			"fieldname": "gst_5",
			"label": "GST - 5%",
			"fieldtype": "Currency",
			"width": "100"
		},

		{
			"fieldname": "gst_12",
			"label": "GST - 12%",
			"fieldtype": "Currency",
			"width": "100"
		},

		{
			"fieldname": "gst_18",
			"label": "GST - 18%",
			"fieldtype": "Currency",
			"width": "100"
		},

		{
			"fieldname": "gst_28",
			"label": "GST - 28%",
			"fieldtype": "Currency",
			"width": "100"
		},

		{
			"fieldname": "gst_28_cess_12",
			"label": "GST-28% CESS-12%",
			"fieldtype": "Currency",
			"width": "155"
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
		SELECT table1.*, (table1.gst_5 + table1.gst_12 + table1.gst_18 + table1.gst_28 + table1.gst_28_cess_12) AS total_tax
		FROM
		(SELECT tabItem.gst_hsn_code, `tabGST HSN Code`.description, SUM(`tabSales Invoice Item`.qty) AS total_qty, SUM(`tabSales Invoice Item`.net_amount) AS taxable_value,
		SUM(IF ((`tabSales Invoice Item`.item_tax_template like "GST 5_ -"), (`tabSales Invoice Item`.cgst_amount + `tabSales Invoice Item`.sgst_amount), 0) ) AS gst_5,
		SUM(IF ((`tabSales Invoice Item`.item_tax_template like "GST 12_ -%"), (`tabSales Invoice Item`.cgst_amount + `tabSales Invoice Item`.sgst_amount), 0) ) AS gst_12,
		SUM(IF ((`tabSales Invoice Item`.item_tax_template like "GST 18_ -"), (`tabSales Invoice Item`.cgst_amount + `tabSales Invoice Item`.sgst_amount), 0) ) AS gst_18,
		SUM(IF ((`tabSales Invoice Item`.item_tax_template like "GST 28_ -"), (`tabSales Invoice Item`.cgst_amount + `tabSales Invoice Item`.sgst_amount), 0) ) AS gst_28,
		SUM(IF ((`tabSales Invoice Item`.item_tax_template like "GST 28_ CESS 12%"), (`tabSales Invoice Item`.cgst_amount + `tabSales Invoice Item`.sgst_amount + `tabSales Invoice Item`.cess_amount), 0) ) AS gst_28_cess_12
		FROM tabItem, `tabGST HSN Code`, `tabSales Invoice Item`, `tabSales Invoice`
		WHERE `tabSales Invoice`.docstatus = 1
		AND tabItem.gst_hsn_code = `tabGST HSN Code`.hsn_code
		AND tabItem.item_code = `tabSales Invoice Item`.item_code
		AND `tabSales Invoice Item`.parent = `tabSales Invoice`.name
		AND posting_date BETWEEN '{0}' AND '{1}'
		GROUP BY tabItem.gst_hsn_code) table1
		""".format(filters.from_date, filters.to_date),
		as_dict=True
	)

	return itemised_hsn_query