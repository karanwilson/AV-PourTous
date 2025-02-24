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
			"fieldname": "voucher_name",
			"label": "Voucher ID",
			"fieldtype": "Link",
			"options": "Purchase Invoice",
			"width": "150"
		},

		{
			"fieldname": "supplier",
			"label": "Supplier",
			"fieldtype": "Data",
			"width": "300"
		},

		{
			"fieldname": "posting_date",
			"label": "Posting Date",
			"fieldtype": "Date",
			"width": "150"
		},

		{
			"fieldname": "taxable_purchase_amount",
			"label": "Taxable Purchase Amount",
			"fieldtype": "Currency",
			"width": "200"
		},
	]


def get_data(filters):
	if filters.supplier:
		query = frappe.db.sql(
			"""
			SELECT `tabPurchase Invoice`.name AS voucher_name, `tabPurchase Invoice`.supplier, `tabPurchase Invoice`.posting_date,
			SUM(price_list_rate * qty) AS taxable_purchase_amount
			FROM `tabPurchase Invoice`, `tabPurchase Invoice Item`
			WHERE `tabPurchase Invoice`.docstatus = 1
			AND `tabPurchase Invoice`.status = "Return"
			AND `tabPurchase Invoice Item`.parent = `tabPurchase Invoice`.name
			AND `tabPurchase Invoice`.supplier = '{0}'
			AND `tabPurchase Invoice`.posting_date BETWEEN '{1}' AND '{2}'
			GROUP BY `tabPurchase Invoice`.name
			""".format(filters.supplier, filters.from_date, filters.to_date),
			as_dict=True
		)
		return query
	
	else:
		query = frappe.db.sql(
			"""
			SELECT `tabPurchase Invoice`.name AS voucher_name, `tabPurchase Invoice`.supplier, `tabPurchase Invoice`.posting_date,
			SUM(price_list_rate * qty) AS taxable_purchase_amount
			FROM `tabPurchase Invoice`, `tabPurchase Invoice Item`
			WHERE `tabPurchase Invoice`.docstatus = 1
			AND `tabPurchase Invoice Item`.parent = `tabPurchase Invoice`.name
			AND `tabPurchase Invoice`.posting_date BETWEEN '{0}' AND '{1}'
			GROUP BY `tabPurchase Invoice`.name
			""".format(filters.from_date, filters.to_date),
			as_dict=True
		)
		return query