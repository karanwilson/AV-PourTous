# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	#if not (filters.name or filters.item_code): # don't execute until filters are set
	#	return [], []

	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)

	if not data:
		msgprint(_('No records found'))
		return columns, data

	return columns, data


def get_columns(filters):
	if filters.customer and not filters.show_individuals:
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


	elif filters.customer and filters.show_individuals:
		# Individual Participants contribution template
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
				"fieldname": "contact",
				"label": "Individual",
				"fieldtype": "Link",
				"options": "Contact",
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
				"fieldname": "custom_master_list_number",
				"label": "MLN",
				"fieldtype": "Data",
				"width": "80"
			},
			{
				"fieldname": "custom_in_kind_scheme",
				"label": "IKS",
				"fieldtype": "Currency",
				"width": "100"
			},
			{
				"fieldname": "custom_lunch_scheme",
				"label": "LS",
				"fieldtype": "Currency",
				"width": "100"
			},
			{
				"fieldname": "custom_monthly_contribution",
				"label": "Monthly",
				"fieldtype": "Currency",
				"width": "100"
			},
			{
				"fieldname": "custom_ptdc_maintenance",
				"label": "PTDC Mnt",
				"fieldtype": "Currency",
				"width": "100"
			},
			{
				"fieldname": "custom_extra_contribution",
				"label": "Extra",
				"fieldtype": "Currency",
				"width": "100"
			},
			{
				"fieldname": "custom_remarks",
				"label": "Remarks",
				"fieldtype": "Data",
				"width": "80"
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
	pass
