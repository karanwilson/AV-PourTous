# Copyright (c) 2024, Karan and contributors
# For license information, please see license.txt

import frappe, erpnext
from frappe import _, msgprint
from frappe.utils import getdate


def execute(filters=None):
	if not filters:
		return [], []
	# validate_filters(filters)

	columns, data = [], []

	columns = get_columns()
	data = get_data(filters)

	skip_total_row = 0

	if not data:
		msgprint(_('No records found'))
		return columns, data, None, None, None, skip_total_row

	row["total"] = ""

	return columns, data, None, None, None, skip_total_row


def get_columns():
	return [
		{
			"fieldname": "name",
			"label": "Invoice ID",
			"fieldtype": "Data",
			"width": "150"
		},

		{
			"fieldname": "customer_name",
			"label": "Customer",
			"fieldtype": "Data",
			"width": "300"
		},

		{
			"fieldname": "posting_date",
			"label": "Posting Date",
			"fieldtype": "Date",
			"width": "150"
		},
	]


def get_data(filters):
	if filters.current_date:
		curr_date = getdate()

		sales_query = frappe.db.sql(
			"""
				select name, customer_name, posting_date, status, custom_fs_transfer_status from `tabSales Invoice`
			""",
			as_dict=True
		)

		return sales_query