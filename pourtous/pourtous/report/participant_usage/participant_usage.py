# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	#if not (filters.from_date and filters.to_date): # don't execute until filters are set
	#	return [], []

	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)

	if not data:
		msgprint(_('No records found'))
		return columns, data

	return columns, data


def get_columns(filters):
	if filters.show_breakup:
		# All Customer/Family account Payment Entries
		return [
			{
				"fieldname": "customer_name",
				"label": "Family Name",
				"fieldtype": "Data",
				"width": "200"
			},
			{
				"fieldname": "customer",
				"label": "Family Account",
				"fieldtype": "Link",
				"options": "Customer",
				"width": "120"
			},
			{
				"fieldname": "custom_fs_account_number",
				"label": "PT Account",
				"fieldtype": "Data",
				"width": "100"
			},
			{
				"fieldname": "address_title",
				"label": "Community",
				"fieldtype": "Data",
				"width": "150"
			},
			{
				"fieldname": "voucher_name",
				"label": "Voucher ID",
				"fieldtype": "Link",
				"options": "Payment Entry",
				"width": "135"
			},
			{
				"fieldname": "contribution",
				"label": "Contribution",
				"fieldtype": "Currency",
				"width": "130",
			},
			{
				"fieldname": "posting_date",
				"label": "Date",
				"fieldtype": "Date",
				"width": "100",
			}
		]
		""" {
			"fieldname": "extra_contribution",
			"label": "Extra Contribution",
			"fieldtype": "Currency",
			"width": "100",
		}, """


	else:
		# Monthly Total Contributions and Usage
		return [
			{
				"fieldname": "customer_name",
				"label": "Family Name",
				"fieldtype": "Data",
				"width": "200"
			},
			{
				"fieldname": "customer",
				"label": "Family Account",
				"fieldtype": "Link",
				"options": "Customer",
				"width": "120"
			},
			{
				"fieldname": "custom_fs_account_number",
				"label": "PT Account",
				"fieldtype": "Data",
				"width": "100"
			},
			{
				"fieldname": "address_title",
				"label": "Community",
				"fieldtype": "Link",
				"options": "Address",
				"width": "100"
			},
			{
				"fieldname": "total_contribution",
				"label": "Contribution",
				"fieldtype": "Currency",
				"width": "130"
			},
			{
				"fieldname": "balance_available",
				"label": "Balance",
				"fieldtype": "Currency",
				"width": "100"
			},
		]


def get_data(filters):
	if filters.show_breakup:
		# Customer/Family account Payment Entries breakup
		query = frappe.db.sql(
			"""
			SELECT customer_name, c.name AS customer, c.custom_fs_account_number, pe.name AS voucher_name,
			a.address_title, pe.paid_amount AS contribution, pe.posting_date
			FROM `tabPayment Entry` pe
			JOIN tabCustomer c ON pe.party = c.name
			LEFT JOIN `tabDynamic Link` dl ON dl.link_name = c.name
			JOIN tabAddress a ON dl.parent = a.name
			""",
			as_dict=True
		)
		return query

	else:
		# Customer/Family-account Payment Entries, summed per customer/family-account
		query = frappe.db.sql(
			"""
			SELECT customer_name, c.name AS customer, c.custom_fs_account_number, a.address_title,
			SUM(pe.paid_amount) AS total_contribution
			FROM `tabPayment Entry` pe
			JOIN tabCustomer c ON pe.party = c.name
			LEFT JOIN `tabDynamic Link` dl ON dl.link_name = c.name
			JOIN tabAddress a ON dl.parent = a.name

			GROUP BY c.name
			""",
			as_dict=True
		)
		return query

	#return query