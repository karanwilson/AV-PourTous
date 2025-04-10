# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not (filters.from_date and filters.to_date): # don't execute until filters are set
		return [], []

	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)

	if not data:
		msgprint(_('No records found'))
		return columns, data

	return columns, data


def get_columns(filters):
	if filters.pt_account and not filters.show_individuals:
		# Customer/Family account Payment Entries
		return [
			{
				"fieldname": "customer",
				"label": "Family Account",
				"fieldtype": "Link",
				"options": "Customer",
				"width": "100"
			},
			{
				"fieldname": "custom_fs_account_number",
				"label": "PT Account",
				"fieldtype": "Data",
				"width": "100"
			},
			{
				"fieldname": "address",
				"label": "Community",
				"fieldtype": "Link",
				"options": "Address",
				"width": "100"
			},
			{
				"fieldname": "voucher_name",
				"label": "Voucher ID",
				"fieldtype": "Link",
				"options": "Payment Entry",
				"width": "135"
			},
			{
				"fieldname": "posting_date",
				"label": "Date",
				"fieldtype": "Date",
				"width": "100",
			},
			{
				"fieldname": "contribution",
				"label": "Contribution",
				"fieldtype": "Currency",
				"width": "100",
			},
			{
				"fieldname": "extra_contribution",
				"label": "Extra Contribution",
				"fieldtype": "Currency",
				"width": "100",
			},
		]


	else:
		# Monthly Total Contributions and Usage
		return [
			{
				"fieldname": "customer",
				"label": "Family Account",
				"fieldtype": "Link",
				"options": "Customer",
				"width": "100"
			},
			{
				"fieldname": "custom_fs_account_number",
				"label": "PT Account",
				"fieldtype": "Data",
				"width": "100"
			},
			{
				"fieldname": "address",
				"label": "Community",
				"fieldtype": "Link",
				"options": "Address",
				"width": "100"
			},
			{
				"fieldname": "total_contribution",
				"label": "Contribution",
				"fieldtype": "Currency",
				"width": "100"
			},
			{
				"fieldname": "balance_available",
				"label": "Balance",
				"fieldtype": "Currency",
				"width": "100"
			},
		]


def get_data(filters):
	if filters.pt_account and not filters.show_individuals:
		# Customer/Family account Payment Entries
		pass


	else:
		pass
