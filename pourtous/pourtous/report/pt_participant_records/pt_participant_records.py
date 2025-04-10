# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	#if not (filters.from_date and filters.to_date): # don't execute until filters are set
	#	return [], []

	columns, data = [], []

	columns = get_columns()
	data = get_data()

	if not data:
		msgprint(_('No records found'))
		return columns, data

	return columns, data


def get_columns():
	# Individual Participants contribution template
	return [
		{
			"fieldname": "customer",
			"label": "Family AC",
			"fieldtype": "Link",
			"options": "Customer",
			"width": "100"
		},
		{
			"fieldname": "customer_name",
			"label": "Family Name",
			"fieldtype": "Data",
			"width": "150"
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
			"fieldname": "first_name",
			"label": "Individual Name",
			"fieldtype": "Data",
			"width": "150"
		},
		{
			"fieldname": "address",
			"label": "Community",
			"fieldtype": "Link",
			"options": "Address",
			"width": "150"
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
			"width": "200"
		},
	]


def get_data():
	# Individual Participants contribution template
	query = frappe.db.sql(
		"""
		SELECT tabCustomer.name AS customer, customer_name, tabCustomer.custom_fs_account_number,
		tabContact.name AS contact, tabContact.first_name, tabContact.address, tabContact.custom_master_list_number,
		tabContact.custom_in_kind_scheme, tabContact.custom_lunch_scheme, tabContact.custom_monthly_contribution,
		tabContact.custom_ptdc_maintenance, tabContact.custom_extra_contribution, tabContact.custom_remarks

		FROM tabContact
		JOIN `tabDynamic Link` on `tabDynamic Link`.parenttype = "Contact" AND `tabDynamic Link`.parent = tabContact.name
		LEFT JOIN tabCustomer ON `tabDynamic Link`.link_doctype = "Customer" AND `tabDynamic Link`.link_name = tabCustomer.name
		""",
		as_dict=True
	)

	return query