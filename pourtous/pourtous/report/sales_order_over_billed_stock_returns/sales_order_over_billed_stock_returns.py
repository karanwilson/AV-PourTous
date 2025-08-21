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
	if filters.view_so:
		return [
			{
				"fieldname": "sales_invoice",
				"label": "Sales Invoice",
				"fieldtype": "Link",
				"options": "Sales Invoice",
				"width": "200"
			},
			{
				"fieldname": "item_code",
				"label": "Item Code",
				"fieldtype": "Data",
				"width": "90"
			},
			{
				"fieldname": "item_name",
				"label": "Item Name",
				"fieldtype": "Data",
				"width": "350"
			},
			{
				"fieldname": "qty",
				"label": "Quantity",
				"fieldtype": "Float",
				"width": "100"
			},
			{
				"fieldname": "sales_order",
				"label": "Sales Order",
				"fieldtype": "Link",
				"options": "Sales Order",
				"width": "200"
			},
		]

	else:
		return [
			{
				"fieldname": "item_code",
				"label": "Item Code",
				"fieldtype": "Data",
				"width": "90"
			},
			{
				"fieldname": "item_name",
				"label": "Item Name",
				"fieldtype": "Data",
				"width": "350"
			},
			{
				"fieldname": "qty",
				"label": "Quantity",
				"fieldtype": "Float",
				"width": "100"
			}
		]


def get_data(filters):
	if filters.item and filters.view_so:
		query = frappe.db.sql(
			"""
			select si.name as sales_invoice, sii.item_code, sii.item_name, sii.qty, sii.sales_order as sales_order
			from `tabSales Invoice` si, `tabSales Invoice Item` sii
			where date(si.creation) = "2025-08-19" and si.owner = "arulkumarsankar@auroville.org.in"
			and sii.sales_order is not null and sii.parent = si.name and sii.item_code = '{0}'
			""".format(filters.item),
			as_dict=True
		)

	elif filters.item and not filters.view_so:
		query = frappe.db.sql(
			"""
			select sii.item_code, sii.item_name, sum(sii.qty) as qty
			from `tabSales Invoice` si, `tabSales Invoice Item` sii
			where date(si.creation) = "2025-08-19" and si.owner = "arulkumarsankar@auroville.org.in"
			and sii.sales_order is not null and sii.parent = si.name
			and sii.item_code = '{0}'
			group by sii.item_code
			""".format(filters.item),
			as_dict=True
		)

	elif not filters.item and filters.view_so:
		query = frappe.db.sql(
			"""
			select si.name as sales_invoice, sii.item_code, sii.item_name, sii.qty, sii.sales_order as sales_order
			from `tabSales Invoice` si, `tabSales Invoice Item` sii
			where date(si.creation) = "2025-08-19" and si.owner = "arulkumarsankar@auroville.org.in"
			and sii.sales_order is not null and sii.parent = si.name;
			""",
			as_dict=True
		)

	else:
		query = frappe.db.sql(
			"""
			select sii.item_code, sii.item_name, sum(sii.qty) as qty
			from `tabSales Invoice` si, `tabSales Invoice Item` sii
			where date(si.creation) = "2025-08-19" and si.owner = "arulkumarsankar@auroville.org.in"
			and sii.sales_order is not null and sii.parent = si.name group by sii.item_code;
			""",
			as_dict=True
		)


	return query
