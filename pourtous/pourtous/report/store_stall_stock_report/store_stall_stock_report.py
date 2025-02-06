# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not (filters): # don't execute until filters are set
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
			"fieldname": "item_code",
			"label": "Item Code",
			"fieldtype": "Data",
			"width": "100"
		},
		{
			"fieldname": "item_name",
			"label": "Item Name",
			"fieldtype": "Data",
			"width": "500"
		},
		{
			"fieldname": "qty",
			"label": filters.warehouse,
			"fieldtype": "Float",
			"width": "100"
		}
	]


def get_data(filters):
	query = frappe.db.sql(
		"""
		SELECT tabItem.item_code, tabItem.item_name,
		(
			select `tabStock Ledger Entry`.qty_after_transaction from `tabStock Ledger Entry`
			where (`tabStock Ledger Entry`.item_code = tabItem.item_code) and `tabStock Ledger Entry`.is_cancelled=0
			and warehouse like '{0}%'
			order by posting_date desc, posting_time desc, creation desc
			limit 1
		) AS qty
		FROM tabItem
		where
		(
			select `tabStock Ledger Entry`.qty_after_transaction from `tabStock Ledger Entry`
			where (`tabStock Ledger Entry`.item_code = tabItem.item_code) and `tabStock Ledger Entry`.is_cancelled=0
			and warehouse like '{0}%'
			order by posting_date desc, posting_time desc, creation desc
			limit 1
		) > 0
		""".format(filters.warehouse),
		as_dict=True
	)

	return query