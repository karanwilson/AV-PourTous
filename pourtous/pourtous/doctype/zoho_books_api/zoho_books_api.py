# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

import requests

class ZohoBooksAPI(Document):
	pass


def fetch_unsynced_sales_invoice_list():
	return frappe.get_list('Sales Invoice',
		filters={
			'custom_zb_sync_status': ['!=', 'Success']
		},
		#as_list=True
	)


def sync_with_zoho_books(invoice):
	pass


@frappe.whitelist(allow_guest=True)
def generate_grant_token():
	url = 'https://accounts.zoho.com/oauth/v2/auth?'
	headers = {
		'scope': 'ZohoBooks.invoices.CREATE,ZohoBooks.invoices.READ,ZohoBooks.invoices.UPDATE,ZohoBooks.invoices.DELETE',
		'client_id': '1000.AYZFMY8YD7JAGU0E1IGVMMNDTDZICR',
		#'state': 'testing',
		'response_type': 'code',
		'redirect_uri': 'https://accounts.zoho.in/oauth/v2/token?',
		'prompt': 'Consent'
	}

	#response = requests.get(url, data=data)
	response = requests.request("GET", url, headers=headers)


	return response