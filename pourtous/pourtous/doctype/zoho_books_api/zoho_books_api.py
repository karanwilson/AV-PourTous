# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, nowtime, nowdate
from datetime import datetime, timedelta

import requests, json
#import urllib


class ZohoBooksAPI(Document):
	def	validate(self):
		if self.client_id and self.client_secret and self.user_id and self.organization_id:
			scope = 'ZohoBooks.invoices.CREATE,ZohoBooks.invoices.READ,ZohoBooks.invoices.UPDATE,ZohoBooks.invoices.DELETE'
			self.validate_zoho_api_params(scope)

	def validate_zoho_api_params(self, scope):
		r = self.request_access_token(scope)
		if r.json().get('access_token'):
			#update token details on Zoho API page
			self.last_access_token = r.json().get('access_token')
			self.token_scope = r.json().get('scope')
			self.api_domain = r.json().get('api_domain')
			self.token_type = r.json().get('token_type')
			self.last_token_date = today()
			self.last_token_time = nowtime()
			self.token_received_at = nowdate()
			self.expires_in = r.json().get('expires_in') / 60


	@frappe.whitelist(allow_guest=True)
	def request_access_token(self, scope):
		soid = 'ZohoBooks.' + self.organization_id
		token_url = 'https://accounts.zoho.in/oauth/v2/token?'

		with requests.Session() as s:
			s.params = {
				'client_id': self.client_id,
				'client_secret': self.get_password(fieldname="client_secret", raise_exception=False),
				'grant_type': 'client_credentials',
				'scope': scope,
				'soid': soid
				}

			r = s.post(token_url)
			r.raise_for_status()

			return r

			""" start_time = datetime.strptime(, '%H:%M:%S')
			if self.token_received_at < nowtime() + timedelta(minutes=60):
				return "Token Valid"
			else:
				return "Token Expired" """


	def post_invoice(self, invoice):
		api_url = 'https://www.zohoapis.in/books/v3/invoices?'

		r = self.request_access_token(scope='ZohoBooks.invoices.CREATE')
		authorization = 'Zoho-oauthtoken ' + r.json().get('access_token')

		data = {
			'customer_id': '2289738000000059003',
			'invoice_number': 'SINV-25-14027-3',
			'is_inclusive_tax': True,
			'date': '2025-03-02',
			'line_items': [
				{
					'item_id': '2289738000000064002',
					'rate': 1514.80,
					'quantity': 2,
					'tax_name': 'GST',
					'tax_percentage': 12
				},
				{
					'item_id': '2289738000000065001',
					'rate': 280,
					'quantity': 10,
					'tax_name': 'GST',
					'tax_percentage': 12
				},
				{
					'item_id': '2289738000000066001',
					'rate': 238,
					'quantity': 10,
					'tax_name': 'GST',
					'tax_percentage': 12
				}
			]
		}

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}			

			r = s.post(api_url, data=json.loads(data))
			r.raise_for_status()

			if r.json().get('message') == 'The invoice has been added.':
				custom_zoho_contact_id = r.json().get('invoice').get('invoice_id')
				return custom_zoho_contact_id


	def post_contact(self, data):
		api_url = 'https://www.zohoapis.in/books/v3/contacts?'

		r = self.request_access_token(scope='ZohoBooks.contacts.CREATE')
		authorization = 'Zoho-oauthtoken ' + r.json().get('access_token')

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.post(api_url, data=json.dumps(data))
			try:
				r.raise_for_status()
			except Exception as err:
				frappe.msgprint("Zoho Books Response: " + r.json().get('message'))
				raise err

			if r.json().get('message') == 'The contact has been added.':
				custom_zoho_contact_id = r.json().get('contact').get('contact_id')
				return custom_zoho_contact_id

			else:
				frappe.msgprint(r.json().get('message'))


	def put_contact(self, contact_id, data):
		api_url = 'https://www.zohoapis.in/books/v3/contacts/' + contact_id + '?'

		r = self.request_access_token(scope='ZohoBooks.contacts.UPDATE')
		authorization = 'Zoho-oauthtoken ' + r.json().get('access_token')

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.put(api_url, data=json.dumps(data))
			try:
				r.raise_for_status()
			except Exception as err:
				frappe.msgprint("Zoho Books Response: " + r.json().get('message'))
				raise err

			return r.json().get('message') 


	def delete_contact(self, contact_id):
		api_url = 'https://www.zohoapis.in/books/v3/contacts/' + contact_id + '?'

		r = self.request_access_token('ZohoBooks.contacts.DELETE')
		authorization = 'Zoho-oauthtoken ' + r.json().get('access_token')

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.delete(api_url)
			try:
				r.raise_for_status()
			except Exception as err:
				frappe.msgprint("Zoho Books Response: " + r.json().get('message'))
				raise err

			return r.json().get('message')


	def post_item(self, data):
		api_url = 'https://www.zohoapis.in/books/v3/items?'

		r = self.request_access_token('ZohoBooks.settings.CREATE')

		authorization = 'Zoho-oauthtoken ' + r.json().get('access_token')

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.post(api_url, data=json.dumps(data))
			try:
				r.raise_for_status()
			except Exception as err:
				frappe.msgprint("Zoho Books Response: " + r.json().get('message'))
				raise err

			if r.json().get('message') == 'The item has been added.':
				custom_zoho_item_id = r.json().get('item').get('item_id')
				return custom_zoho_item_id

			else:
				frappe.msgprint(r.json().get('message'))


	def put_item(self, item_id, data):
		api_url = 'https://www.zohoapis.in/books/v3/items/' + item_id + '?'

		r = self.request_access_token('ZohoBooks.settings.UPDATE')
		authorization = 'Zoho-oauthtoken ' + r.json().get('access_token')

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.put(api_url, data=json.dumps(data))
			try:
				r.raise_for_status()
			except Exception as err:
				frappe.msgprint("Zoho Books Response: " + r.json().get('message'))
				raise err

			return r.json().get('message')


	def delete_item(self, item_id):
		api_url = 'https://www.zohoapis.in/books/v3/items/' + item_id + '?'

		r = self.request_access_token('ZohoBooks.settings.DELETE')
		authorization = 'Zoho-oauthtoken ' + r.json().get('access_token')

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.delete(api_url)
			try:
				r.raise_for_status()
			except Exception as err:
				frappe.msgprint("Zoho Books Response: " + r.json().get('message'))
				raise err

			return r.json().get('message')


def update_item_in_zoho(doc, method):
	api_controller = frappe.get_doc("Zoho Books API")

	if doc.is_stock_item == 1:
		product_type = "goods"
	else:
		product_type = "service"

	uom = {
		"Bag": "pcs",
		"Bott": "pcs",
		"Box": "box",
		"Jar": "pcs",
		"Kg": "kg",
		"Litre": "litre",
		"Nos": "pcs",
		"Packet": "pcs",
		"Set": "pcs",
		"Slab": "pcs",
		"Tin": "pcs",
		"Tube": "pcs"
	}

	data = {
		"name": doc.name,
		"description": doc.item_name,
		"unit": uom[doc.stock_uom],
		"product_type": product_type,
		"hsn_or_sac": doc.gst_hsn_code,
		"rate": 0
	}

	put_data = {
		"description": doc.item_name,
		"unit": uom[doc.stock_uom],
		"product_type": product_type,
		"hsn_or_sac": doc.gst_hsn_code,
		"rate": 0
	}

	if doc.custom_zoho_item_id == None:
		# post new Item
		res = api_controller.post_item(data)
		if res:
			doc.custom_zoho_item_id = res

	else:
		# put/update existing Item
		res = api_controller.put_item(doc.custom_zoho_item_id, put_data)
		msg = "Zoho Books API Response: " + res
		frappe.msgprint(msg)


def delete_item_in_zoho(doc, method):
	if doc.custom_zoho_item_id:
		api_controller = frappe.get_doc("Zoho Books API")
		res = api_controller.delete_item(doc.custom_zoho_item_id)
		msg = "Zoho Books Response: " + res
		frappe.msgprint(msg)


def update_contact_in_zoho(doc, method):
	if doc.custom_update_zoho_contact == 0:
		return

	api_controller = frappe.get_doc("Zoho Books API")

	if doc.customer_type == "Individual":
		customer_sub_type = "individual"
	else:
		customer_sub_type = "business"

	data = {
		"contact_name": doc.name,
		"contact_type": "customer",
		"customer_sub_type": customer_sub_type
	}

	put_data = {
		"contact_type": "customer",
		"customer_sub_type": customer_sub_type
	}

	if doc.custom_zoho_contact_id == None:
		# post new Contact
		res = api_controller.post_contact(data)
		if res:
			doc.custom_zoho_contact_id = res

	else:
		# put/update existing Contact
		res = api_controller.put_contact(doc.custom_zoho_contact_id, put_data)
		msg = "Zoho Books API Response: " + res
		frappe.msgprint(msg)


def delete_contact_in_zoho(doc, method):
	if doc.custom_zoho_contact_id:
		api_controller = frappe.get_doc("Zoho Books API")
		res = api_controller.delete_contact(doc.custom_zoho_contact_id)
		msg = "Zoho Books Response: " + res
		frappe.msgprint(msg)


def update_supplier_contact_in_zoho(doc, method):
	api_controller = frappe.get_doc("Zoho Books API")

	data = {
		"contact_name": doc.supplier_name,
		"contact_type": "vendor",
		"customer_sub_type": "business"
	}

	if doc.custom_zoho_contact_id == None:
		res = api_controller.post_contact(data)
		if res:
			doc.custom_zoho_contact_id = res

	else:
		# put/update existing Contact
		res = api_controller.put_contact(doc.custom_zoho_contact_id, data)
		frappe.msgprint("Zoho Books API Response: " + res)


""" def fetch_unsynced_sales_invoice_list():
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


	return response """
