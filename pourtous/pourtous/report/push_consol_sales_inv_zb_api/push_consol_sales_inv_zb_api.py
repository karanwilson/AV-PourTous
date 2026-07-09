# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
# from pourtous.pourtous.doctype.zoho_books_api.zoho_books_api import sync_pt_consol_inv_with_zb

def execute(filters=None):
	if not (filters.from_date and filters.to_date): # don't execute until filters are set
		return [], []

	columns, data = [], []

	columns = get_columns()
	data = get_data(from_date=filters.from_date, to_date=filters.to_date, is_return=filters.is_return, custom_fs_account_number=filters.custom_fs_account_number)

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


def get_data(from_date, to_date, custom_fs_account_number, is_return):
	if is_return == 1:
		query = """
					SELECT s.name, s.customer_name, s.customer, s.custom_fs_account_number, s.posting_date, item_code, item_name, qty, rate
					FROM `tabSales Invoice Item` si, `tabSales Invoice` s
					WHERE s.docstatus = 1 AND si.parent = s.name AND s.is_return = 1
					AND s.posting_date BETWEEN '{0}' AND '{1}'
					AND s.custom_zb_consol_creditnote_id IS NULL
				"""

	else:
		query = """
					SELECT s.name, s.customer_name, s.customer, s.custom_fs_account_number, s.posting_date, item_code, item_name, qty, rate
					FROM `tabSales Invoice Item` si, `tabSales Invoice` s
					WHERE s.docstatus = 1 AND si.parent = s.name AND s.is_return = 0
					AND s.posting_date BETWEEN '{0}' AND '{1}'
					AND s.custom_zb_consol_inv_id IS NULL
				"""

	# FS Account filter is optional.
	if custom_fs_account_number:
		query += " AND s.custom_fs_account_number = '{2}' ORDER BY s.custom_fs_account_number"
	else:
		query += " ORDER BY s.custom_fs_account_number"

	#return query
	return frappe.db.sql(query.format(from_date, to_date, custom_fs_account_number, is_return), as_dict=1)


@frappe.whitelist()
def get_participant_monthly_distribution(from_date, to_date, custom_fs_account_number, is_return):
	if frappe.defaults.get_user_default("company") == "Pour Tous Distribution Center":
		#return get_data(from_date, to_date)

		consol_list_dict_erp = get_data(from_date, to_date, custom_fs_account_number, int(is_return))
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

		# frappe.enqueue(
		# 	bulk_processing, cust_consol_inv_dict=cust_consol_inv_dict, to_date=to_date, is_return=is_return,
		# 	queue="long", timeout=6000, is_async=False, at_front=True
		# )

# def bulk_processing(cust_consol_inv_dict, to_date, is_return):
# 		length = len(cust_consol_inv_dict)
# 		count = 1

# 		for key in cust_consol_inv_dict:
# 			# frappe.throw(key)
# 			# frappe.throw(str(cust_consol_inv_dict[key]))
# 			message = "Adding "+str(count)+" of "+str(length)
# 			frappe.publish_progress((count / length) * 100,	title="Pushing Consolidated Invoices to Zoho Books", description=message)

# 			res = sync_pt_consol_inv_with_zb(key, cust_consol_inv_dict[key], to_date, is_return)
# 			if res == "ADDED":
# 				count += 1

# 		return "Completed"
