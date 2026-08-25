# Copyright (c) 2026, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe import _, msgprint
from pourtous.pourtous.doctype.zoho_books_api.zoho_books_api import add_erp_bill_debitnote_in_zoho


def execute(filters=None):
	if not (filters.from_posting_date and filters.to_posting_date and filters.is_return): # don't execute until filters are set
		return [], []

	if filters.is_return == "No" and not (filters.from_bill_date and filters.to_bill_date): # don't execute until filters are set
		return [], []

	columns, data = [], []

	columns = get_columns()
	# data = get_data(from_date=filters.from_posting_date, to_date=filters.to_posting_date, is_return=filters.is_return)
	data = get_data(filters.from_posting_date, filters.to_posting_date, filters.from_bill_date, filters.to_bill_date, filters.is_return)

	if not data:
		msgprint(_('No records found'))
		return columns, data

	return columns, data

def get_columns():
	return [
		{
			"fieldname": "name",
			"label": "Pur.Invoice",
			"fieldtype": "Link",
			"options": "Purchase Invoice",
			"width": "135"
		},
		{
			"fieldname": "is_return",
			"label": "Is Return",
			"fieldtype": "Check",
			"width": "80",
		},
		{
			"fieldname": "posting_date",
			"label": "Date",
			"fieldtype": "Date",
			"width": "100",
		},
		{
			"fieldname": "supplier",
			"label": "Supplier",
			"fieldtype": "Data",
			"width": "150"
		},
		{
			"fieldname": "bill_no",
			"label": "Bill No.",
			"fieldtype": "Data",
			"width": "100"
		},
		{
			"fieldname": "custom_bill_id",
			"label": "Bill ID",
			"fieldtype": "Data",
			"width": "100"
		},
		{
			"fieldname": "bill_date",
			"label": "Bill Date",
			"fieldtype": "Date",
			"width": "100",
		},
		{
			"fieldname": "total_taxes_and_charges",
			"label": "Taxes",
			"fieldtype": "currency",
			"width": "100",
		},
		{
			"fieldname": "grand_total",
			"label": "Grand Total",
			"fieldtype": "currency",
			"width": "100",
		},
		{
			"fieldname": "rounding_adjustment",
			"label": "Rounding",
			"fieldtype": "currency",
			"width": "100",
		},
	]

def get_data(from_posting_date, to_posting_date, from_bill_date, to_bill_date, is_return):
	if is_return == "Yes":
		query = """
					SELECT name, is_return, posting_date, supplier, bill_no, custom_bill_id, bill_date, total_taxes_and_charges, grand_total, rounding_adjustment
					FROM `tabPurchase Invoice`
					WHERE docstatus = 1 AND is_return = 1
					AND posting_date BETWEEN '{0}' AND '{1}'
					AND custom_zb_vendor_credit_id IS NULL
				"""

	else:
		query = """
					SELECT name, is_return, posting_date, supplier, bill_no, custom_bill_id, bill_date, total_taxes_and_charges, grand_total, rounding_adjustment
					FROM `tabPurchase Invoice`
					WHERE docstatus = 1 AND is_return = 0
					AND posting_date BETWEEN '{0}' AND '{1}'
					AND bill_date BETWEEN '{2}' AND '{3}'
					AND custom_zoho_bill_id IS NULL
				"""

	return frappe.db.sql(query.format(from_posting_date, to_posting_date, from_bill_date, to_bill_date), as_dict=1)


@frappe.whitelist()
def get_purchase_invoices(from_posting_date, to_posting_date, from_bill_date, to_bill_date, is_return):
	if frappe.defaults.get_user_default("company") == "Pour Tous Distribution Center":
		#return get_data(from_date, to_date)

		pur_inv_list_dict = get_data(from_posting_date, to_posting_date, from_bill_date, to_bill_date, is_return)
		#type casting to int as the data received via frappe.call comes as string, 
		# whereas the internal report above pulls the actual field type int

		# frappe.throw(str(len(pur_inv_list_dict)))

		frappe.enqueue(
			bulk_processing, bills=pur_inv_list_dict,
			queue="long", timeout=6000, is_async=False, at_front=True
		)

def bulk_processing(bills):
	# frappe.throw(str(bills))

	total_count = len(bills)
	# total_count = 10
	added = 0

	for i in range(total_count):
		res = add_erp_bill_debitnote_in_zoho(bills[i]["name"])
		if res == "ADDED":
			added += 1
		# message = "Adding "+str(added)+" of "+str(total_count)

		frappe.publish_progress(
			int((added/total_count)*100),
			title = "Pushing Bills to Zoho Books",
			description = f"Pushing {added} of {total_count} bills"
		)

	frappe.msgprint(f"Pushed {added} of {total_count}")
	# return "Completed"
