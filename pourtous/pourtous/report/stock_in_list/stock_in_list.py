# Copyright (c) 2024, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not (filters.voucher_type and filters.posting_date): # don't execute until filters are set
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
			"fieldname": "voucher_type",
			"label": "Voucher Type",
			"fieldtype": "Data",
			"width": "135"
		},

		{
			"fieldname": "voucher_name",
			"label": "Voucher ID",
			"fieldtype": "Data",
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
			"fieldtype": "Data",
			"width": "100"
		},

		{
			"fieldname": "item_name",
			"label": "Item Name",
			"fieldtype": "Data",
			"width": "300"
		},

		{
			"fieldname": "qty",
			"label": "Quantity",
			"fieldtype": "Float",
			"width": "100"
		},

		{
			"fieldname": "rate",
			"label": "Price",
			"fieldtype": "Currency",
			"width": "100"
		},
	]


def get_data(filters):

	if filters.voucher_type == "Purchase Receipt":
		query = frappe.db.sql(
			"""
				SELECT parenttype AS voucher_type, `tabPurchase Receipt`.name AS voucher_name,
				title AS supplier, item_code, batch_no, item_name, qty, rate
				FROM `tabPurchase Receipt Item`, `tabPurchase Receipt`
				WHERE `tabPurchase Receipt Item`.parent = `tabPurchase Receipt`.name
				AND `tabPurchase Receipt`.docstatus = 1
				AND `tabPurchase Receipt`.posting_date = '{0}'
			""".format(filters.posting_date),
			as_dict=True
		)

	else:
		query = frappe.db.sql(
			"""
				SELECT stock_entry_type AS voucher_type, `tabStock Entry`.name AS voucher_name,
				item_code, batch_no, item_name, qty, basic_rate AS rate
				FROM `tabStock Entry Detail`, `tabStock Entry`
				WHERE `tabStock Entry Detail`.parent = `tabStock Entry`.name
				AND `tabStock Entry`.docstatus = 1
				AND `tabStock Entry`.posting_date = '{0}'
			""".format(filters.posting_date),
			as_dict=True
		)

	return query