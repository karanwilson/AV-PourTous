# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint


def execute(filters=None):
	if not (filters.from_date and filters.to_date): # don't execute until filters are set
		return [], []

	columns, data = [], []

	columns = get_columns()
	data = get_data(from_date=filters.from_date, to_date=filters.to_date, is_return=filters.is_return)

	if not data:
		msgprint(_('No records found'))
		return columns, data

	return columns, data


def get_columns():
	return [
		{
			"fieldname": "name",
			"label": "Checkout Note",
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": "150"
		},
		{
			"fieldname": "customer_name",
			"label": "Family Name",
			"fieldtype": "Data",
			"width": "150"
		},
		{
			"fieldname": "customer",
			"label": "Family Acc",
			"fieldtype": "Link",
			"options": "Customer",
			"width": "150"
		},
		{
			"fieldname": "custom_fs_account_number",
			"label": "PT Account",
			"fieldtype": "Data",
			"width": "100"
		},
		{
			"fieldname": "posting_date",
			"label": "Date",
			"fieldtype": "Date",
			"width": "100"
		},
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
			"width": "200"
		},
		{
			"fieldname": "qty",
			"label": "Quanity",
			"fieldtype": "Float",
			"width": "100"
		},
		{
			"fieldname": "rate",
			"label": "Rate",
			"fieldtype": "Currency",
			"width": "100"
		}
	]


def get_data(from_date, to_date, is_return):
	if is_return == 1:
		query = frappe.db.sql(
			"""
			SELECT s.name, s.customer_name, s.customer, s.custom_fs_account_number, s.posting_date, item_code, item_name, qty, rate
			FROM `tabSales Invoice Item` si, `tabSales Invoice` s
			WHERE s.docstatus = 1 AND si.parent = s.name AND s.is_return = 1
			AND s.posting_date BETWEEN '{0}' AND '{1}'
			AND s.custom_zb_consol_creditnote_id IS NULL
			ORDER BY s.custom_fs_account_number
			""".format(from_date, to_date),
			as_dict=True
		)

	else:
		query = frappe.db.sql(
			"""
			SELECT s.name, s.customer_name, s.customer, s.custom_fs_account_number, s.posting_date, item_code, item_name, qty, rate
			FROM `tabSales Invoice Item` si, `tabSales Invoice` s
			WHERE s.docstatus = 1 AND si.parent = s.name AND s.is_return = 0
			AND s.posting_date BETWEEN '{0}' AND '{1}'
			AND s.custom_zb_consol_inv_id IS NULL
			ORDER BY s.custom_fs_account_number
			""".format(from_date, to_date),
			as_dict=True
		)

	return query


@frappe.whitelist()
def get_participant_monthly_distribution(from_date, to_date, is_return):
	if frappe.defaults.get_user_default("company") == "Pour Tous Distribution Center":
		#return get_data(from_date, to_date)

		consol_list_dict_erp = get_data(from_date, to_date, int(is_return))
		#type casting to int as the data received via frappe.call comes as string, 
		# whereas the internal report above pulls the actual field type int

		#frappe.throw(str(len(consol_dict)))
		#frappe.throw(str(consol_dict[0].get("name")))
		#frappe.throw(str(consol_dict))

		cust_consol_inv_dict = {} # initialise a dictionary of lists of consolidated customer invoices

		for i in range(len(consol_list_dict_erp)):
			consol_inv_id = consol_list_dict_erp[i].get("custom_fs_account_number")

			if consol_inv_id in cust_consol_inv_dict:
				cust_consol_inv_dict[consol_inv_id].append(consol_list_dict_erp[i])
			else:
				cust_consol_inv_dict[consol_inv_id] = [consol_list_dict_erp[i]]

		return cust_consol_inv_dict
