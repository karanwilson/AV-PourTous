# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, nowtime, nowdate
from datetime import datetime, timedelta

import requests
#import urllib


class ZohoBooksAPI(Document):
	def	validate(self):
		self.request_access_token()

	@frappe.whitelist(allow_guest=True)
	def request_access_token(self, throw_if_missing=False):
		soid = 'ZohoBooks.' + self.organization_id
		token_url = 'https://accounts.zoho.in/oauth/v2/token?'

		with requests.Session() as s:
			s.params = {
				'client_id': self.client_id,
				'client_secret': self.get_password(fieldname="client_secret", raise_exception=False),
				'grant_type': 'client_credentials',
				'scope': 'ZohoBooks.invoices.CREATE,ZohoBooks.invoices.READ,ZohoBooks.invoices.UPDATE,ZohoBooks.invoices.DELETE',
				'soid': soid
				}

			#with open('zoho_token5.txt', 'w') as file:
			#	file.write(str(s.params))

			r = s.post(token_url)
			r.raise_for_status()

			self.last_access_token = r.json().get('access_token')
			self.token_scope = r.json().get('scope')
			self.api_domain = r.json().get('api_domain')
			self.token_type = r.json().get('token_type')
			self.last_token_date = today()
			self.last_token_time = nowtime()
			self.token_received_at = nowdate()
			self.expires_in = r.json().get('expires_in') / 60

			#self.save()

			return r.json()
			""" start_time = datetime.strptime(, '%H:%M:%S')
			if self.token_received_at < nowtime() + timedelta(minutes=60):
				return "Token Valid"
			else:
				return "Token Expired" """


	#def post_invoice(self, invoice):
	#	if self.last_token_date == today() and self.last_token_time < self.last_token_time + 60

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
	url = ''
	headers = {
		'scope': '',
		'client_id': '',
		'state': 'testing',
		'response_type': 'code',
		'redirect_uri': '',
		#'prompt': 'Consent'
	}

	#response = requests.get(url, data=data)
	response = requests.request("GET", url, headers=headers)


	return response
