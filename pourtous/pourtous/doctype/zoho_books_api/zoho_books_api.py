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
		with requests.Session() as s:
			s.params = {
				'client_id': self.client_id,
				'client_secret': self.client_secret,
				'grant_type': self.grant_type,
				'scope': self.scope,
				'soid': self.soid
				}

			r = s.get("https://accounts.zoho.in/oauth/v2/token?")
			r.raise_for_status()

			data = r.json()


		""" client_id = '1000.AYZFMY8YD7JAGU0E1IGVMMNDTDZICR'
		client_secret = 'e0a04002642b69c66be36ef1a307f0d91916d53387'
		grant_type = 'client_credentials'
		scope = ['ZohoBooks.invoices.CREATE', 'ZohoBooks.invoices.READ', 'ZohoBooks.invoices.UPDATE', 'ZohoBooks.invoices.DELETE']
		soid = 'ZohoBooks.60037640038'
		token_url = 'https://accounts.zoho.in/oauth/v2/token?'

		#oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
		#authorization_url, state = oauth.authorization_url('https://accounts.zoho.com/oauth/v2/auth?', access_type="offline")

		client = BackendApplicationClient(client_id=client_id)
		oauth = OAuth2Session(client=client)

		#oauth = OAuth2Session(client_id, scope=scope)
		token = oauth.fetch_token(token_url=token_url, client_id=client_id, client_secret=client_secret,
							grant_type=grant_type, scope=scope, soid=soid) """


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
		'state': 'testing',
		'response_type': 'code',
		'redirect_uri': 'https://accounts.zoho.in/oauth/v2/token?',
		#'prompt': 'Consent'
	}

	#response = requests.get(url, data=data)
	response = requests.request("GET", url, headers=headers)


	return response
