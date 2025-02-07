# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint

def execute(filters=None):
	if not (filters.supplier and filters.from_date and filters.to_date): # don't execute until filters are set
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
			"options": "Purchase Receipt",
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
	query = frappe.db.sql(
		"""
		SELECT `tabPurchase Receipt`.name AS voucher_name, `tabPurchase Receipt`.supplier, `tabPurchase Receipt`.posting_date,
		SUM(`tabPurchase Receipt Item`.price_list_rate) AS taxable_purchase_amount
		FROM `tabPurchase Receipt`, `tabPurchase Receipt Item`
		WHERE `tabPurchase Receipt`.docstatus = 1
		AND `tabPurchase Receipt Item`.parent = `tabPurchase Receipt`.name
		AND `tabPurchase Receipt`.supplier = '{0}'
		AND `tabPurchase Receipt`.posting_date BETWEEN '{1}' AND '{2}'
		GROUP BY `tabPurchase Receipt`.name
		""".format(filters.supplier, filters.from_date, filters.to_date),
		as_dict=True
	)

	return query