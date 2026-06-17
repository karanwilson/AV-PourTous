# Copyright (c) 2024, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not (filters.from_date and filters.to_date): # don't execute until filters are set
		return [], []

	# if (filters.from_date and filters.to_date and filters.customer_type and not filters.customer_group): # don't execute until filters are set
	# 	return [], []

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
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": "150"
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
			"fieldname": "custom_is_donation",
			"label": "Donation",
			"fieldtype": "Check",
			"width": "100"
		},

		{
			"fieldname": "customer_type",
			"label": "Customer Type",
			"fieldtype": "Data",
			"width": "100"
		},

		{
			"fieldname": "mode_of_payment",
			"label": "MOP",
			"fieldtype": "Data",
			"width": "100"
		},

		{
			"fieldname": "grand_total",
			"label": "Grand Total",
			"fieldtype": "Currency",
			"width": "100"
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
			"fieldname": "sales_40",
			"label": "Sales - 40%",
			"fieldtype": "Currency",
			"width": "100"
		},

		{
			"fieldname": "cgst_amount",
			"label": "CGST Amount",
			"fieldtype": "Currency",
			"width": "120"
		},

		{
			"fieldname": "sgst_amount",
			"label": "SGST Amount",
			"fieldtype": "Currency",
			"width": "120"
		},

		{
			"fieldname": "igst_amount",
			"label": "IGST Amount",
			"fieldtype": "Currency",
			"width": "120"
		},

		{
			"fieldname": "total_tax",
			"label": "Total Tax",
			"fieldtype": "Currency",
			"width": "100"
		},

		{
			"fieldname": "sales_3",
			"label": "Sales - 3%",
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
			"fieldname": "return_against",
			"label": "Return Against",
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": "130"
		},

	]


def get_data(filters):

	if filters.mop == "FS":
		gst_sales_query = frappe.db.sql(
			"""
			SELECT table1.name, table1.return_against, table1.customer_name, table1.posting_date,
			table1.custom_is_donation, table1.customer_type, table1.mode_of_payment, table1.sales_exempted,
			table1.sales_3, table1.sales_5, table1.sales_12, table1.sales_18, table1.sales_28, table1.sales_40,
			IF((table1.cgst_amount IS NULL), 0, table1.cgst_amount) AS cgst_amount,
			IF((table1.sgst_amount IS NULL), 0, table1.sgst_amount) AS sgst_amount,
			IF((table1.igst_amount IS NULL), 0, table1.igst_amount) AS igst_amount,
			(
			IF((table1.cgst_amount IS NULL), 0, table1.cgst_amount) + IF((table1.sgst_amount IS NULL), 0, table1.sgst_amount) + IF((table1.igst_amount IS NULL), 0, table1.igst_amount)
			) AS total_tax,
			table1.grand_total

			FROM

			(
			SELECT si.name, si.return_against, si.customer_name, si.posting_date, si.custom_is_donation, c.customer_type, sip.mode_of_payment,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item`
			WHERE parent = si.name
			AND (item_tax_template like "Nil-Rated%" OR item_tax_template like "Non-GST%" OR item_tax_template like "Exempted%"))
			AS sales_exempted,

			(SELECT SUM(sii.net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 3.0)
			AS sales_3,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 5.0)
			AS sales_5,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 12.0)
			AS sales_12,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 18.0)
			AS sales_18,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 28.0)
			AS sales_28,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 40.0)
			AS sales_40,

			(SELECT tax_amount FROM `tabSales Taxes and Charges`
			WHERE parent = si.name AND description = "CGST" limit 1)
			AS cgst_amount,

			(SELECT tax_amount FROM `tabSales Taxes and Charges`
			WHERE parent = si.name AND description = "SGST" limit 1)
			AS sgst_amount,

			(SELECT tax_amount FROM `tabSales Taxes and Charges`
			WHERE parent = si.name AND description = "IGST" limit 1)
			AS igst_amount,

			grand_total

			FROM `tabSales Invoice` AS si
			JOIN tabCustomer AS c
			ON si.customer = c.name
			LEFT JOIN `tabSales Invoice Payment` AS sip
			ON si.name = sip.parent
			WHERE si.docstatus = 1
			AND si.custom_fs_account_number IS NOT NULL
			AND (c.customer_group LIKE 'Individual%' OR sip.mode_of_payment = 'FS')
			AND posting_date between '{0}' and '{1}'
			) table1
			""".format(filters.from_date, filters.to_date),
			as_dict=True
		)

		return gst_sales_query


	elif filters.mop == "Aurocard":
		gst_sales_query = frappe.db.sql(
			"""
			SELECT table1.name, table1.return_against, table1.customer_name, table1.posting_date,
			table1.custom_is_donation, table1.customer_type, table1.mode_of_payment, table1.sales_exempted,
			table1.sales_3, table1.sales_5, table1.sales_12, table1.sales_18, table1.sales_28, table1.sales_40,
			IF((table1.cgst_amount IS NULL), 0, table1.cgst_amount) AS cgst_amount,
			IF((table1.sgst_amount IS NULL), 0, table1.sgst_amount) AS sgst_amount,
			IF((table1.igst_amount IS NULL), 0, table1.igst_amount) AS igst_amount,
			(
			IF((table1.cgst_amount IS NULL), 0, table1.cgst_amount) + IF((table1.sgst_amount IS NULL), 0, table1.sgst_amount) + IF((table1.igst_amount IS NULL), 0, table1.igst_amount)
			) AS total_tax,
			table1.grand_total

			FROM

			(
			SELECT si.name, return_against, si.customer_name, posting_date, si.custom_is_donation, c.customer_type, sip.mode_of_payment,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item`
			WHERE parent = si.name
			AND (item_tax_template like "Nil-Rated%" OR item_tax_template like "Non-GST%" OR item_tax_template like "Exempted%"))
			AS sales_exempted,

			(SELECT SUM(sii.net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 3.0)
			AS sales_3,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 5.0)
			AS sales_5,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 12.0)
			AS sales_12,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 18.0)
			AS sales_18,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 28.0)
			AS sales_28,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 40.0)
			AS sales_40,

			(SELECT tax_amount FROM `tabSales Taxes and Charges`
			WHERE parent = si.name AND description = "CGST" limit 1)
			AS cgst_amount,

			(SELECT tax_amount FROM `tabSales Taxes and Charges`
			WHERE parent = si.name AND description = "SGST" limit 1)
			AS sgst_amount,

			(SELECT tax_amount FROM `tabSales Taxes and Charges`
			WHERE parent = si.name AND description = "IGST" limit 1)
			AS igst_amount,

			grand_total

			FROM `tabSales Invoice` AS si
			JOIN tabCustomer AS c
			ON si.customer = c.name
			LEFT JOIN `tabSales Invoice Payment` AS sip
			ON si.name = sip.parent
			WHERE si.docstatus = 1
			AND (c.customer_group = 'Aurocard Payments' OR sip.mode_of_payment = 'Aurocard')
			AND posting_date between '{0}' and '{1}'
			) table1
			""".format(filters.from_date, filters.to_date),
			as_dict=True
		)

		return gst_sales_query


	elif filters.mop == "UPI":
		gst_sales_query = frappe.db.sql(
			"""
			SELECT table1.name, table1.return_against, table1.customer_name, table1.posting_date,
			table1.custom_is_donation, table1.customer_type, table1.mode_of_payment, table1.sales_exempted,
			table1.sales_3, table1.sales_5, table1.sales_12, table1.sales_18, table1.sales_28, table1.sales_40,
			IF((table1.cgst_amount IS NULL), 0, table1.cgst_amount) AS cgst_amount,
			IF((table1.sgst_amount IS NULL), 0, table1.sgst_amount) AS sgst_amount,
			IF((table1.igst_amount IS NULL), 0, table1.igst_amount) AS igst_amount,
			(
			IF((table1.cgst_amount IS NULL), 0, table1.cgst_amount) + IF((table1.sgst_amount IS NULL), 0, table1.sgst_amount) + IF((table1.igst_amount IS NULL), 0, table1.igst_amount)
			) AS total_tax,
			table1.grand_total

			FROM

			(
			SELECT si.name, return_against, si.customer_name, posting_date, si.custom_is_donation, c.customer_type, sip.mode_of_payment,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item`
			WHERE parent = si.name
			AND (item_tax_template like "Nil-Rated%" OR item_tax_template like "Non-GST%" OR item_tax_template like "Exempted%"))
			AS sales_exempted,

			(SELECT SUM(sii.net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 3.0)
			AS sales_3,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 5.0)
			AS sales_5,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 12.0)
			AS sales_12,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 18.0)
			AS sales_18,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 28.0)
			AS sales_28,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 40.0)
			AS sales_40,

			(SELECT tax_amount FROM `tabSales Taxes and Charges`
			WHERE parent = si.name AND description = "CGST" limit 1)
			AS cgst_amount,

			(SELECT tax_amount FROM `tabSales Taxes and Charges`
			WHERE parent = si.name AND description = "SGST" limit 1)
			AS sgst_amount,

			(SELECT tax_amount FROM `tabSales Taxes and Charges`
			WHERE parent = si.name AND description = "IGST" limit 1)
			AS igst_amount,

			grand_total

			FROM `tabSales Invoice` AS si
			JOIN tabCustomer AS c
			ON si.customer = c.name
			LEFT JOIN `tabSales Invoice Payment` AS sip
			ON si.name = sip.parent
			WHERE si.docstatus = 1
			AND (c.customer_group = 'UPI Payments' OR sip.mode_of_payment IN ('UPI', 'ICICI UPI'))
			AND posting_date between '{0}' and '{1}'
			) table1
			""".format(filters.from_date, filters.to_date),
			as_dict=True
		)

		return gst_sales_query


	elif filters.mop == "Cards":
		gst_sales_query = frappe.db.sql(
			"""
			SELECT table1.name, table1.return_against, table1.customer_name, table1.posting_date,
			table1.custom_is_donation, table1.customer_type, table1.mode_of_payment, table1.sales_exempted,
			table1.sales_3, table1.sales_5, table1.sales_12, table1.sales_18, table1.sales_28, table1.sales_40,
			IF((table1.cgst_amount IS NULL), 0, table1.cgst_amount) AS cgst_amount,
			IF((table1.sgst_amount IS NULL), 0, table1.sgst_amount) AS sgst_amount,
			IF((table1.igst_amount IS NULL), 0, table1.igst_amount) AS igst_amount,
			(
			IF((table1.cgst_amount IS NULL), 0, table1.cgst_amount) + IF((table1.sgst_amount IS NULL), 0, table1.sgst_amount) + IF((table1.igst_amount IS NULL), 0, table1.igst_amount)
			) AS total_tax,
			table1.grand_total

			FROM

			(
			SELECT si.name, return_against, si.customer_name, posting_date, si.custom_is_donation, c.customer_type, sip.mode_of_payment,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item`
			WHERE parent = si.name
			AND (item_tax_template like "Nil-Rated%" OR item_tax_template like "Non-GST%" OR item_tax_template like "Exempted%"))
			AS sales_exempted,

			(SELECT SUM(sii.net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 3.0)
			AS sales_3,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 5.0)
			AS sales_5,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 12.0)
			AS sales_12,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 18.0)
			AS sales_18,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 28.0)
			AS sales_28,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 40.0)
			AS sales_40,

			(SELECT tax_amount FROM `tabSales Taxes and Charges`
			WHERE parent = si.name AND description = "CGST" limit 1)
			AS cgst_amount,

			(SELECT tax_amount FROM `tabSales Taxes and Charges`
			WHERE parent = si.name AND description = "SGST" limit 1)
			AS sgst_amount,

			(SELECT tax_amount FROM `tabSales Taxes and Charges`
			WHERE parent = si.name AND description = "IGST" limit 1)
			AS igst_amount,

			grand_total

			FROM `tabSales Invoice` AS si
			JOIN tabCustomer AS c
			ON si.customer = c.name
			LEFT JOIN `tabSales Invoice Payment` AS sip
			ON si.name = sip.parent
			WHERE si.docstatus = 1
			AND (c.customer_group = 'Card Payments' OR sip.mode_of_payment IN ('Cards', 'RuPay'))
			AND posting_date between '{0}' and '{1}'
			) table1
			""".format(filters.from_date, filters.to_date),
			as_dict=True
		)

		return gst_sales_query


	elif filters.mop == "Cash":
		gst_sales_query = frappe.db.sql(
			"""
			SELECT table1.name, table1.return_against, table1.customer_name, table1.posting_date,
			table1.custom_is_donation, table1.customer_type, table1.mode_of_payment, table1.sales_exempted,
			table1.sales_3, table1.sales_5, table1.sales_12, table1.sales_18, table1.sales_28, table1.sales_40,
			IF((table1.cgst_amount IS NULL), 0, table1.cgst_amount) AS cgst_amount,
			IF((table1.sgst_amount IS NULL), 0, table1.sgst_amount) AS sgst_amount,
			IF((table1.igst_amount IS NULL), 0, table1.igst_amount) AS igst_amount,
			(
			IF((table1.cgst_amount IS NULL), 0, table1.cgst_amount) + IF((table1.sgst_amount IS NULL), 0, table1.sgst_amount) + IF((table1.igst_amount IS NULL), 0, table1.igst_amount)
			) AS total_tax,
			table1.grand_total

			FROM

			(
			SELECT si.name, return_against, si.customer_name, posting_date, si.custom_is_donation, c.customer_type, sip.mode_of_payment,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item`
			WHERE parent = si.name
			AND (item_tax_template like "Nil-Rated%" OR item_tax_template like "Non-GST%" OR item_tax_template like "Exempted%"))
			AS sales_exempted,

			(SELECT SUM(sii.net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 3.0)
			AS sales_3,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 5.0)
			AS sales_5,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 12.0)
			AS sales_12,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 18.0)
			AS sales_18,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 28.0)
			AS sales_28,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 40.0)
			AS sales_40,

			(SELECT tax_amount FROM `tabSales Taxes and Charges`
			WHERE parent = si.name AND description = "CGST" limit 1)
			AS cgst_amount,

			(SELECT tax_amount FROM `tabSales Taxes and Charges`
			WHERE parent = si.name AND description = "SGST" limit 1)
			AS sgst_amount,

			(SELECT tax_amount FROM `tabSales Taxes and Charges`
			WHERE parent = si.name AND description = "IGST" limit 1)
			AS igst_amount,

			grand_total

			FROM `tabSales Invoice` AS si
			JOIN tabCustomer AS c
			ON si.customer = c.name
			LEFT JOIN `tabSales Invoice Payment` AS sip
			ON si.name = sip.parent
			WHERE si.docstatus = 1
			AND (c.customer_group = 'Cash Payments' OR sip.mode_of_payment = 'Cash')
			AND posting_date between '{0}' and '{1}'
			) table1
			""".format(filters.from_date, filters.to_date),
			as_dict=True
		)

		return gst_sales_query


	elif filters.mop == "NEFT":
		gst_sales_query = frappe.db.sql(
			"""
			SELECT table1.name, table1.return_against, table1.customer_name, table1.posting_date,
			table1.custom_is_donation, table1.customer_type, table1.mode_of_payment, table1.sales_exempted,
			table1.sales_3, table1.sales_5, table1.sales_12, table1.sales_18, table1.sales_28, table1.sales_40,
			IF((table1.cgst_amount IS NULL), 0, table1.cgst_amount) AS cgst_amount,
			IF((table1.sgst_amount IS NULL), 0, table1.sgst_amount) AS sgst_amount,
			IF((table1.igst_amount IS NULL), 0, table1.igst_amount) AS igst_amount,
			(
			IF((table1.cgst_amount IS NULL), 0, table1.cgst_amount) + IF((table1.sgst_amount IS NULL), 0, table1.sgst_amount) + IF((table1.igst_amount IS NULL), 0, table1.igst_amount)
			) AS total_tax,
			table1.grand_total

			FROM

			(
			SELECT si.name, return_against, si.customer_name, posting_date, si.custom_is_donation, c.customer_type, sip.mode_of_payment,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item`
			WHERE parent = si.name
			AND (item_tax_template like "Nil-Rated%" OR item_tax_template like "Non-GST%" OR item_tax_template like "Exempted%"))
			AS sales_exempted,

			(SELECT SUM(sii.net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 3.0)
			AS sales_3,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 5.0)
			AS sales_5,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 12.0)
			AS sales_12,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 18.0)
			AS sales_18,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 28.0)
			AS sales_28,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 40.0)
			AS sales_40,

			(SELECT tax_amount FROM `tabSales Taxes and Charges`
			WHERE parent = si.name AND description = "CGST" limit 1)
			AS cgst_amount,

			(SELECT tax_amount FROM `tabSales Taxes and Charges`
			WHERE parent = si.name AND description = "SGST" limit 1)
			AS sgst_amount,

			(SELECT tax_amount FROM `tabSales Taxes and Charges`
			WHERE parent = si.name AND description = "IGST" limit 1)
			AS igst_amount,

			grand_total

			FROM `tabSales Invoice` AS si
			JOIN tabCustomer AS c
			ON si.customer = c.name
			LEFT JOIN `tabSales Invoice Payment` AS sip
			ON si.name = sip.parent
			WHERE si.docstatus = 1
			AND (c.customer_group = 'NEFT Payments' OR sip.mode_of_payment = 'NEFT')
			AND posting_date between '{0}' and '{1}'
			) table1
			""".format(filters.from_date, filters.to_date),
			as_dict=True
		)

		return gst_sales_query


	else:
		gst_sales_query = frappe.db.sql(
			"""
			SELECT table1.name, table1.return_against, table1.customer_name, table1.posting_date,
			table1.custom_is_donation, table1.customer_type, table1.mode_of_payment, table1.sales_exempted,
			table1.sales_3, table1.sales_5, table1.sales_12, table1.sales_18, table1.sales_28, table1.sales_40,
			IF((table1.cgst_amount IS NULL), 0, table1.cgst_amount) AS cgst_amount,
			IF((table1.sgst_amount IS NULL), 0, table1.sgst_amount) AS sgst_amount,
			IF((table1.igst_amount IS NULL), 0, table1.igst_amount) AS igst_amount,
			(
			IF((table1.cgst_amount IS NULL), 0, table1.cgst_amount) + IF((table1.sgst_amount IS NULL), 0, table1.sgst_amount) + IF((table1.igst_amount IS NULL), 0, table1.igst_amount)
			) AS total_tax,
			table1.grand_total

			FROM

			(
			SELECT si.name, si.return_against, si.customer_name, si.posting_date, si.custom_is_donation, c.customer_type, sip.mode_of_payment,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item`
			WHERE parent = si.name
			AND (item_tax_template like "Nil-Rated%" OR item_tax_template like "Non-GST%" OR item_tax_template like "Exempted%"))
			AS sales_exempted,

			(SELECT SUM(sii.net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 3.0)
			AS sales_3,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 5.0)
			AS sales_5,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 12.0)
			AS sales_12,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 18.0)
			AS sales_18,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 28.0)
			AS sales_28,

			(SELECT SUM(net_amount) FROM `tabSales Invoice Item` sii, `tabItem Tax Template` itt
			WHERE parent = si.name AND sii.item_tax_template = itt.name AND itt.gst_rate = 40.0)
			AS sales_40,

			(SELECT tax_amount FROM `tabSales Taxes and Charges`
			WHERE parent = si.name AND description = "CGST" limit 1)
			AS cgst_amount,

			(SELECT tax_amount FROM `tabSales Taxes and Charges`
			WHERE parent = si.name AND description = "SGST" limit 1)
			AS sgst_amount,

			(SELECT tax_amount FROM `tabSales Taxes and Charges`
			WHERE parent = si.name AND description = "IGST" limit 1)
			AS igst_amount,

			grand_total

			FROM `tabSales Invoice` AS si
			JOIN tabCustomer AS c
			ON si.customer = c.name
			LEFT JOIN `tabSales Invoice Payment` AS sip
			ON si.name = sip.parent
			WHERE si.docstatus = 1
			AND si.posting_date between '{0}' and '{1}'
			) table1
			""".format(filters.from_date, filters.to_date),
			as_dict=True
		)

		return gst_sales_query