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

	if not data:
		msgprint(_('No records found'))
		return columns, data

	return columns, data


def get_columns():
	pass


def get_data(filters):
	current_date = getdate()