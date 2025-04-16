# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not (filters.from_date and filters.to_date): # don't execute until filters are set
		msgprint(_("Please enter both 'from' and 'to' dates"))
		return [], []

	columns, data = [], []

	columns = get_columns(filters)
	data = get_data(filters)

	if not data:
		msgprint(_('No records found'))
		return columns, data

	return columns, data


def get_columns(filters):
	if (frappe.defaults.get_user_default("company") == "Pour Tous Distribution Center"):
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
					"fieldname": "customer_group",
					"label": "Category",
					"fieldtype": "Data",
					"width": "100"
				},
				{
					"fieldname": "customer",
					"label": "Family Acc",
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
					"fieldname": "address_title",
					"label": "Community",
					"fieldtype": "Data",
					"width": "100"
				},
				{
					"fieldname": "voucher_name",
					"label": "Voucher ID",
					"fieldtype": "Link",
					"options": "Payment Entry",
					"width": "180"
				},
				{
					"fieldname": "contribution",
					"label": "Contribution",
					"fieldtype": "Currency",
					"width": "120",
				},
				{
					"fieldname": "posting_date",
					"label": "Date",
					"fieldtype": "Date",
					"width": "100",
				}
			]


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
					"fieldname": "customer_group",
					"label": "Category",
					"fieldtype": "Data",
					"width": "100"
				},
				{
					"fieldname": "customer",
					"label": "Family Acc",
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
					"fieldname": "address_title",
					"label": "Community",
					"fieldtype": "Link",
					"options": "Address",
					"width": "110"
				},
				{
					"fieldname": "total_contribution",
					"label": "Contribution",
					"fieldtype": "Currency",
					"width": "110"
				},
				{
					"fieldname": "usage_invoice",
					"label": "Usage-Invoice",
					"fieldtype": "Currency",
					"width": "115"
				},
				{
					"fieldname": "usage_order",
					"label": "Usage-Order",
					"fieldtype": "Currency",
					"width": "110"
				},
				{
					"fieldname": "balance",
					"label": "Balance",
					"fieldtype": "Currency",
					"width": "100"
				},
			]
			""" {
				"fieldname": "returns_credit",
				"label": "Return Credit",
				"fieldtype": "Currency",
				"width": "110"
			}, """

	else:
		if filters.show_breakup:
			# Customer Payment Entry Details
			return [
				{
					"fieldname": "customer_name",
					"label": "Customer Name",
					"fieldtype": "Data",
					"width": "200"
				},
				{
					"fieldname": "customer",
					"label": "Customer",
					"fieldtype": "Link",
					"options": "Customer",
					"width": "120"
				},
				{
					"fieldname": "custom_fs_account_number",
					"label": "FS Account",
					"fieldtype": "Data",
					"width": "100"
				},
				{
					"fieldname": "voucher_name",
					"label": "Voucher ID",
					"fieldtype": "Link",
					"options": "Payment Entry",
					"width": "150"
				},
				{
					"fieldname": "contribution",
					"label": "Payments",
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


		else:
			# Monthly Payments and Usage
			return [
				{
					"fieldname": "customer_name",
					"label": "Customer Name",
					"fieldtype": "Data",
					"width": "200"
				},
				{
					"fieldname": "customer",
					"label": "Customer",
					"fieldtype": "Link",
					"options": "Customer",
					"width": "120"
				},
				{
					"fieldname": "custom_fs_account_number",
					"label": "FS Account",
					"fieldtype": "Data",
					"width": "100"
				},
				{
					"fieldname": "total_contribution",
					"label": "Post Payments",
					"fieldtype": "Currency",
					"width": "130"
				},
				{
					"fieldname": "usage_invoice",
					"label": "Invoice Amounts",
					"fieldtype": "Currency",
					"width": "130"
				},
				{
					"fieldname": "usage_order",
					"label": "Order Amounts",
					"fieldtype": "Currency",
					"width": "130"
				},
				{
					"fieldname": "balance",
					"label": "Balance",
					"fieldtype": "Currency",
					"width": "100"
				},
			]


def get_data(filters):
	if (frappe.defaults.get_user_default("company") == "Pour Tous Distribution Center"):
		if filters.show_breakup and filters.from_date and filters.to_date:
			# Customer/Family account Payment Entries breakup
			query = frappe.db.sql(
				"""
				SELECT customer_name, c.customer_group, c.name AS customer, c.custom_fs_account_number, pe.name AS voucher_name,
				a.address_title, pe.paid_amount AS contribution, pe.posting_date

				FROM `tabPayment Entry` pe
				JOIN tabCustomer c ON pe.party = c.name
				LEFT JOIN `tabDynamic Link` dl ON dl.link_name = c.name
				LEFT JOIN tabAddress a ON dl.parent = a.name

				WHERE pe.docstatus = 1 AND pe.posting_date between '{0}' and '{1}'
				""".format(filters.from_date, filters.to_date),
				as_dict=True
			)

		elif filters.from_date and filters.to_date:
			# Customer/Family-account Payment Entries, summed per customer/family-account
			query = frappe.db.sql(
				"""
				SELECT table1.*,
				(IF((table1.total_contribution IS NULL), 0, table1.total_contribution) - IF((table1.usage_invoice IS NULL), 0, table1.usage_invoice) - IF((table1.usage_order IS NULL), 0, table1.usage_order))
				AS balance

				FROM
				(SELECT c.customer_name, c.customer_group, c.name AS customer, c.custom_fs_account_number, a.address_title,
				(
					SELECT SUM(sub1_pe.paid_amount) FROM `tabPayment Entry` sub1_pe
					WHERE sub1_pe.docstatus = 1
					AND sub1_pe.mode_of_payment = "FS"
					AND sub1_pe.posting_date between '{0}' and '{1}'
					AND sub1_pe.party = c.name
				) AS total_contribution,
				(
					SELECT SUM(si.grand_total) FROM `tabSales Invoice` si
					WHERE docstatus = 1
					AND si.customer = c.name
					AND si.posting_date between '{0}' and '{1}'
				) AS usage_invoice,
				(
					SELECT SUM(so.grand_total) FROM `tabSales Order` so
					WHERE so.docstatus = 1
					AND so.status NOT IN ("Closed", "On Hold")
					AND so.per_billed < 99.99
					AND so.customer = c.name
					AND so.transaction_date between '{0}' and '{1}'
				) AS usage_order
				FROM tabCustomer c
				LEFT JOIN `tabDynamic Link` dl ON dl.link_name = c.name
				LEFT JOIN tabAddress a ON dl.parent = a.name

				GROUP BY c.name) table1
				""".format(filters.from_date, filters.to_date),
				as_dict=True
			)
			""" (
				SELECT SUM(sub2_pe.paid_amount) FROM `tabPayment Entry` sub2_pe
				WHERE sub2_pe.docstatus = 1
				AND sub2_pe.mode_of_payment IS NULL
				AND sub2_pe.posting_date between '{0}' and '{1}'
				AND sub2_pe.party = c.name
			) AS returns_credit, """

	else:
		if filters.show_breakup and filters.from_date and filters.to_date:
			# Customer/Family account Payment Entries breakup
			query = frappe.db.sql(
				"""
				SELECT customer_name, c.name AS customer, c.custom_fs_account_number, pe.name AS voucher_name,
				pe.paid_amount AS contribution, pe.posting_date

				FROM `tabPayment Entry` pe
				JOIN tabCustomer c ON pe.party = c.name

				WHERE pe.docstatus = 1 AND pe.posting_date between '{0}' and '{1}'
				""".format(filters.from_date, filters.to_date),
				as_dict=True
			)

		elif filters.from_date and filters.to_date:
			# Customer/Family-account Payment Entries, summed per customer/family-account
			query = frappe.db.sql(
				"""
				SELECT table1.*,
				(IF((table1.total_contribution IS NULL), 0, table1.total_contribution) - IF((table1.usage_invoice IS NULL), 0, table1.usage_invoice) - IF((table1.usage_order IS NULL), 0, table1.usage_order))
				AS balance

				FROM
				(SELECT c.customer_name, c.customer_group, c.name AS customer, c.custom_fs_account_number,
				(
					SELECT SUM(sub1_pe.paid_amount) FROM `tabPayment Entry` sub1_pe
					WHERE sub1_pe.docstatus = 1
					AND sub1_pe.mode_of_payment = "FS"
					AND sub1_pe.posting_date between '{0}' and '{1}'
					AND sub1_pe.party = c.name
				) AS total_contribution,
				(
					SELECT SUM(si.grand_total) FROM `tabSales Invoice` si
					WHERE docstatus = 1
					AND si.customer = c.name
					AND si.posting_date between '{0}' and '{1}'
				) AS usage_invoice,
				(
					SELECT SUM(so.grand_total) FROM `tabSales Order` so
					WHERE so.docstatus = 1
					AND so.status NOT IN ("Closed", "On Hold")
					AND so.per_billed < 99.99
					AND so.customer = c.name
					AND so.transaction_date between '{0}' and '{1}'
				) AS usage_order
				FROM tabCustomer c

				GROUP BY c.name) table1
				""".format(filters.from_date, filters.to_date),
				as_dict=True
			)

	return query