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

			r = s.get(self.token_url)
			r.raise_for_status()

			return r.json()


		""" client_id = ''
		client_secret = ''
		grant_type = 'client_credentials'
		scope = ['', '', '', '']
		soid = ''
		token_url = ''

		#oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
		#authorization_url, state = oauth.authorization_url('', access_type="offline")

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
