# Copyright (c) 2024, Karan and contributors
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
			"fieldname": "name",
			"label": "Invoice ID",
			"fieldtype": "Data",
			"width": "130"
		},

		{
			"fieldname": "return_against",
			"label": "Return Against",
			"fieldtype": "Data",
			"width": "130"
		},

		{
			"fieldname": "customer_name",
			"label": "Customer Name",
			"fieldtype": "Data",
			"width": "130"
		},

		{
			"fieldname": "posting_date",
			"label": "Posting Date",
			"fieldtype": "Date",
			"width": "130"
		},

		{
			"fieldname": "sales_exempted",
			"label": "Sales - Exempted",
			"fieldtype": "Currency",
			"width": "135"
		},

		{
			"fieldname": "sales_5",
			"label": "Sales - 5%",
			"fieldtype": "Currency",
			"width": "100"
		},

		{
			"fieldname": "sales_12",
			"label": "Sales - 12%",
			"fieldtype": "Currency",
			"width": "100"
		},

		{
			"fieldname": "sales_18",
			"label": "Sales - 18%",
			"fieldtype": "Currency",
			"width": "100"
		},

		{
			"fieldname": "sales_28",
			"label": "Sales - 28%",
			"fieldtype": "Currency",
			"width": "100"
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

		{
			"fieldname": "grand_total",
			"label": "Grand Total",
			"fieldtype": "Currency",
			"width": "100"
		},
	]


def get_data(filters):

	if filters.customer:
		gst_sales_query = frappe.db.sql(
			"""
			SELECT name, return_against, customer_name, posting_date,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item`
			WHERE parent = `tabSales Invoice`.name
			AND (item_tax_template like "Nil-Rated%" OR item_tax_template like "Non-GST%" OR item_tax_template like "Exempted%"))
			AS sales_exempted,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item`
			WHERE parent = `tabSales Invoice`.name AND item_tax_template like "GST 5%")
			AS sales_5,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item`
			WHERE parent = `tabSales Invoice`.name AND item_tax_template like "GST 12%")
			AS sales_12,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item`
			WHERE parent = `tabSales Invoice`.name AND item_tax_template like "GST 18%")
			AS sales_18,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item`
			WHERE parent = `tabSales Invoice`.name AND item_tax_template like "GST 28%")
			AS sales_28,

			(SELECT tax_amount FROM `tabSales Taxes and Charges`
			WHERE parent = `tabSales Invoice`.name AND description = "CGST")
			AS cgst_amount,

			(SELECT tax_amount FROM `tabSales Taxes and Charges`
			WHERE parent = `tabSales Invoice`.name AND description = "SGST")
			AS sgst_amount,

			((SELECT tax_amount FROM `tabSales Taxes and Charges` WHERE parent = `tabSales Invoice`.name AND description = "CGST")
			+(SELECT tax_amount FROM `tabSales Taxes and Charges` WHERE parent = `tabSales Invoice`.name AND description = "SGST"))
			AS total_tax,

			grand_total

			FROM `tabSales Invoice` WHERE docstatus = 1
			AND posting_date = '{0}' AND customer = '{1}'
			""".format(filters.query_date, filters.customer),
			as_dict=True
		)

		return gst_sales_query
	
	else:
		gst_sales_query = frappe.db.sql(
			"""
			SELECT name, return_against, customer_name, posting_date,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item`
			WHERE parent = `tabSales Invoice`.name
			AND (item_tax_template like "Nil-Rated%" OR item_tax_template like "Non-GST%" OR item_tax_template like "Exempted%"))
			AS sales_exempted,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item`
			WHERE parent = `tabSales Invoice`.name AND item_tax_template like "GST 5%")
			AS sales_5,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item`
			WHERE parent = `tabSales Invoice`.name AND item_tax_template like "GST 12%")
			AS sales_12,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item`
			WHERE parent = `tabSales Invoice`.name AND item_tax_template like "GST 18%")
			AS sales_18,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item`
			WHERE parent = `tabSales Invoice`.name AND item_tax_template like "GST 28%")
			AS sales_28,

			(SELECT tax_amount FROM `tabSales Taxes and Charges`
			WHERE parent = `tabSales Invoice`.name AND description = "CGST")
			AS cgst_amount,

			(SELECT tax_amount FROM `tabSales Taxes and Charges`
			WHERE parent = `tabSales Invoice`.name AND description = "SGST")
			AS sgst_amount,

			((SELECT tax_amount FROM `tabSales Taxes and Charges` WHERE parent = `tabSales Invoice`.name AND description = "CGST")
			+(SELECT tax_amount FROM `tabSales Taxes and Charges` WHERE parent = `tabSales Invoice`.name AND description = "SGST"))
			AS total_tax,

			grand_total

			FROM `tabSales Invoice` WHERE docstatus = 1
			AND posting_date = '{0}'
			""".format(filters.query_date),
			as_dict=True
		)

		return gst_sales_query