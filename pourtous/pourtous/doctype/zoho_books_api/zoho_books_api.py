# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

import requests
#import urllib
#from requests_oauthlib import OAuth2Session
#from oauthlib.oauth2 import BackendApplicationClient

class ZohoBooksAPI(Document):
	@frappe.whitelist(allow_guest=True)
	def zoho_api_token(self, throw_if_missing=False):
		soid = 'ZohoBooks.' + self.organization_id
		token_url = 'https://accounts.zoho.in/oauth/v2/token?'
		""" with open('zoho_token1.txt', 'w') as file:
			file.write(str(token_url))
		with open('zoho_token2.txt', 'w') as file:
			file.write(str(self.client_id))
		with open('zoho_token3.txt', 'w') as file:
			file.write(str(self.get_password(fieldname="client_secret", raise_exception=False)))
		with open('zoho_token4.txt', 'w') as file:
			file.write(str(soid)) """
		with requests.Session() as s:
			s.params = {
				'client_id': self.client_id,
				'client_secret': self.get_password(fieldname="client_secret", raise_exception=False),
				'grant_type': 'client_credentials',
				'scope': 'ZohoBooks.invoices.CREATE,ZohoBooks.invoices.READ,ZohoBooks.invoices.UPDATE,ZohoBooks.invoices.DELETE',
				'soid': soid
				}

			with open('zoho_token5.txt', 'w') as file:
				file.write(str(s.params))

			r = s.post(token_url)
			r.raise_for_status()
			return r.json()

		""" client_id = self.client_id
		client_secret = self.client_secret
		grant_type = 'client_credentials'
		scope = ['ZohoBooks.invoices.CREATE', 'ZohoBooks.invoices.READ', 'ZohoBooks.invoices.UPDATE', 'ZohoBooks.invoices.DELETE']
		#authorization_url = 'https://accounts.zoho.com/oauth/v2/auth?'
		token_url = 'https://accounts.zoho.com/oauth/v2/token?'

		client = BackendApplicationClient(client_id=client_id)
		oauth = OAuth2Session(client=client)

		token = oauth.fetch_token(token_url=token_url, client_id=client_id, client_secret=client_secret, grant_type=grant_type, scope=scope) """


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
