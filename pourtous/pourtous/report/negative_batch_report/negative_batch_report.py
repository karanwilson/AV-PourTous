# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
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
			"label": "Code",
			"fieldtype": "Data",
			"width": "80"
		},
		{
			"fieldname": "item_name",
			"label": "Item Name",
			"fieldtype": "Data",
			"width": "300"
		},
		{
			"fieldname": "supplier",
			"label": "Supplier",
			"fieldtype": "Data",
			"width": "300"	
		},
		{
			"fieldname": "batch",
			"label": "Batch No.",
			"fieldtype": "Data",
			"width": "130"
		},
		{
			"fieldname": "store_qty",
			"label": "Store Qty",
			"fieldtype": "Float",
			"width": "100"
		},
		{
			"fieldname": "stall_qty",
			"label": "Stall Qty",
			"fieldtype": "Float",
			"width": "100"
		},
		{
			"fieldname": "price",
			"label": "Price",
			"fieldtype": "Currency",
			"width": "80"
		},
	]


def get_data(filters):
	query = frappe.db.sql(
		"""
		SELECT `tabStock Ledger Entry`.item_code, tabBatch.item_name, tabBatch.supplier, tabBatch.name AS batch,
		(
			SELECT SUM(actual_qty) FROM `tabStock Ledger Entry`
			WHERE is_cancelled = 0 AND warehouse LIKE '{0}'
			AND batch_no = tabBatch.name
		) AS store_qty,
		(
			SELECT SUM(actual_qty) FROM `tabStock Ledger Entry`
			WHERE is_cancelled = 0 AND warehouse LIKE '{1}'
			AND batch_no = tabBatch.name
		) AS stall_qty,
		tabBatch.posa_batch_price AS price
		FROM `tabStock Ledger Entry`, tabBatch
		WHERE `tabStock Ledger Entry`.is_cancelled = 0
		AND `tabStock Ledger Entry`.batch_no = tabBatch.name
		AND (

		(
			SELECT SUM(actual_qty) FROM `tabStock Ledger Entry`
			WHERE is_cancelled = 0 AND warehouse LIKE '{0}'
			AND batch_no = tabBatch.name
		) < 0
		OR
		(
			SELECT SUM(actual_qty) FROM `tabStock Ledger Entry`
			WHERE is_cancelled = 0 AND warehouse LIKE '{1}'
			AND batch_no = tabBatch.name
		) < 0

		)
		GROUP BY tabBatch.name
		""".format("Stores%", "Stall%", filters.name),
		as_dict=True
	)

	return query