# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowtime, nowdate
from datetime import datetime, timedelta

import requests, json
#import urllib


class ZohoBooksAPI(Document):
	DATE_FORMAT = "%Y-%m-%d"
	TIME_FORMAT = "%H:%M:%S.%f"
	DATETIME_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"

	scope = 'ZohoBooks.invoices.CREATE,ZohoBooks.invoices.READ,ZohoBooks.invoices.UPDATE,ZohoBooks.invoices.DELETE'

	def	validate(self):
		if self.client_id and self.client_secret and self.user_id and self.organization_id:
			self.validate_zoho_api_params(self.scope)

	def validate_zoho_api_params(self, scope):
		r = self.request_access_token(scope)
		if r.json().get('access_token'):
			#update token details on Zoho API page
			self.last_access_token = r.json().get('access_token')
			self.token_scope = r.json().get('scope')
			self.api_domain = r.json().get('api_domain')
			self.token_type = r.json().get('token_type')
			self.last_token_date = nowdate()
			self.last_token_time = nowtime()
			self.token_received_at = datetime.now()
			self.token_validity = r.json().get('expires_in') / 60
			self.token_valid_till = self.token_received_at + timedelta(minutes=(self.token_validity - 5))
			# reducing 5 mins from the provided validity, to keep a safe margin from the token expiry time.

			#self.token_valid_till = datetime.strptime(self.token_received_at, self.DATETIME_FORMAT) + timedelta(minutes=55)


	#@frappe.whitelist(allow_guest=True)
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

			if r.json().get('access_token'):
				return r
			else:
				r.raise_for_status()


	def update_token_doc(self, token_doc, token, token_validity):
		token_doc.token = token
		token_doc.token_received_at = datetime.now()
		token_doc.token_validity = token_validity
		token_doc.token_valid_till = token_doc.token_received_at + timedelta(minutes=(token_validity - 5))
		token_doc.save()

	def create_token_doc(self, master, scope, token, token_validity):
		new_token_doc = frappe.new_doc("Zoho Books API Token")
		new_token_doc.master = master
		new_token_doc.scope = scope
		new_token_doc.token = token
		new_token_doc.token_received_at = datetime.now()
		new_token_doc.token_validity = token_validity
		new_token_doc.token_valid_till = new_token_doc.token_received_at + timedelta(minutes=(token_validity - 5))
		new_token_doc.save()

	def query_stored_tokens(self, master, scope):
		existing_token_id = frappe.get_value("Zoho Books API Token", {"master": master, "scope": scope}, "name")
		if existing_token_id:
			existing_token_doc = frappe.get_doc("Zoho Books API Token", existing_token_id)

			#if datetime.strptime(self.token_valid_till, self.DATETIME_FORMAT) > datetime.now():
			if existing_token_doc.token_valid_till > datetime.now():
				token_to_use = existing_token_doc.token
			else:
				r = self.request_access_token(scope)
				token_to_use = r.json().get('access_token')
				token_validity = r.json().get('expires_in') / 60
				self.update_token_doc(existing_token_doc, token_to_use, token_validity)

		else:
			r = self.request_access_token(scope)
			token_to_use = r.json().get('access_token')
			token_validity = r.json().get('expires_in') / 60
			self.create_token_doc(master, scope, token_to_use, token_validity)

		return token_to_use



	def post_contact(self, data):
		master = "contacts"
		scope='ZohoBooks.contacts.CREATE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/contacts?'

		authorization = 'Zoho-oauthtoken ' + token_to_use

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.post(api_url, data=json.dumps(data))

			if r.json().get('message') == 'The contact has been added.':
				return {
					"custom_zoho_contact_id": r.json().get('contact').get('contact_id'),
				}
			else:
				r.raise_for_status()


	def put_contact(self, contact_id, data):
		master = "contacts"
		scope='ZohoBooks.contacts.UPDATE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/contacts/' + contact_id + '?'

		authorization = 'Zoho-oauthtoken ' + token_to_use

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.put(api_url, data=json.dumps(data))

			if r.json().get('message') == "Contact does not exist.":
				return self.post_contact(data)

			else:
				r.raise_for_status()
				return {
					"message": r.json().get('message')
				}


	def delete_contact(self, contact_id):
		master = "contacts"
		scope='ZohoBooks.contacts.DELETE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/contacts/' + contact_id + '?'

		authorization = 'Zoho-oauthtoken ' + token_to_use

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.delete(api_url)

			r.raise_for_status()
			return r.json().get('message')


	def get_contacts(self):
		master = "contacts"
		scope='ZohoBooks.contacts.READ'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/contacts?'

		authorization = 'Zoho-oauthtoken ' + token_to_use

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.get(api_url)

			r.raise_for_status()
			if r.json().get('message') == 'success':
				return r.json().get('contacts')


	def get_taxes(self):
		master = "settings"
		scope='ZohoBooks.settings.READ'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/settings/taxes?'

		authorization = 'Zoho-oauthtoken ' + token_to_use

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.get(api_url)

			r.raise_for_status()
			if r.json().get('message') == 'success':
				return r.json().get('taxes')


	def post_item(self, data):
		master = "items"
		scope='ZohoBooks.settings.CREATE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/items?'

		authorization = 'Zoho-oauthtoken ' + token_to_use

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
		master = "items"
		scope='ZohoBooks.settings.UPDATE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/items/' + item_id + '?'

		authorization = 'Zoho-oauthtoken ' + token_to_use

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
		master = "items"
		scope='ZohoBooks.settings.DELETE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/items/' + item_id + '?'

		authorization = 'Zoho-oauthtoken ' + token_to_use

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


	""" def post_invoice(self, invoice):
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
				return custom_zoho_contact_id """



def update_item_in_zoho(doc, method):
	if frappe.defaults.get_user_default("company") in ("Pour Tous Distribution Center", "Pour Tous Canteen"):
		return

	api_controller = frappe.get_doc("Zoho Books API")

	if doc.is_stock_item == 1:
		product_type = "goods"
	else:
		product_type = "service"

	if frappe.defaults.get_user_default("company") == "Pour Tous Purchase Service":
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
	else:
		frappe.throw("Please configure the UOM for this Company")

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
	if frappe.defaults.get_user_default("company") in ("Pour Tous Distribution Center", "Pour Tous Canteen"):
		return

	if doc.custom_zoho_item_id:
		api_controller = frappe.get_doc("Zoho Books API")
		res = api_controller.delete_item(doc.custom_zoho_item_id)
		msg = "Zoho Books Response: " + res
		frappe.msgprint(msg)


def update_contact_in_zoho(doc, method):
	if frappe.defaults.get_user_default("company") in ("Pour Tous Distribution Center", "Pour Tous Canteen"):
		return

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
		if res.get("custom_zoho_contact_id"):
			doc.custom_zoho_contact_id = res.get("custom_zoho_contact_id")

	else:
		# put/update existing Contact
		res = api_controller.put_contact(doc.custom_zoho_contact_id, put_data)
		if res.get("custom_zoho_contact_id"):
			# checks if the API controller handled a non-existing contact,
			# in case of wrong/old Zoho Contact IDs stored in the ERP supplier record, by calling post instead
			doc.custom_zoho_contact_id = res.get("custom_zoho_contact_id")
		else:
			# put/update response
			frappe.msgprint("Zoho Books Response: " + res.get("message"))
			#return { "UPDATED" }


def delete_contact_in_zoho(doc, method):
	if frappe.defaults.get_user_default("company") in ("Pour Tous Distribution Center", "Pour Tous Canteen"):
		return

	if doc.custom_zoho_contact_id:
		api_controller = frappe.get_doc("Zoho Books API")
		res = api_controller.delete_contact(doc.custom_zoho_contact_id)
		msg = "Zoho Books Response: " + res
		frappe.msgprint(msg)


def update_supplier_contact_in_zoho(doc, method):
	if frappe.defaults.get_user_default("company") in ("Pour Tous Distribution Center", "Pour Tous Canteen"):
		return

	api_controller = frappe.get_doc("Zoho Books API")

	gst_treatment = {
		"Registered Regular": "business_gst",
		"Unregistered": "business_none",
		"Overseas": "overseas"
	}

	data = {
		"contact_name": doc.supplier_name,
		"contact_type": "vendor",
		"customer_sub_type": "business",
		"gst_no": doc.gstin,
		"gst_treatment": gst_treatment[doc.gst_category]
	}

	if doc.custom_zoho_contact_id == None:
		res = api_controller.post_contact(data)
		if res.get("custom_zoho_contact_id"):
			doc.custom_zoho_contact_id = res.get("custom_zoho_contact_id")
			return doc.custom_zoho_contact_id
			# returning this value for the add_supplier_to_zb function below (for bulk Supplier additions to Zoho)

	else:
		# put/update existing Contact
		res = api_controller.put_contact(doc.custom_zoho_contact_id, data)
		if res.get("custom_zoho_contact_id"):
			# checks if the API controller handled a non-existing contact,
			# in case of wrong/old Zoho Contact IDs stored in the ERP supplier record, by calling post instead
			doc.custom_zoho_contact_id = res.get("custom_zoho_contact_id")
			#return { "ADDED" }

		else: # put/update response
			frappe.msgprint("Zoho Books Response: " + res.get("message"))
			#return { "UPDATED" }



@frappe.whitelist(allow_guest=True)
def fetch_erp_supplier_list():
	#return frappe.get_all('Supplier', filters = {"disabled": 0})
	return frappe.db.sql(
		"""
		SELECT name FROM tabSupplier
		WHERE disabled = 0
		AND custom_zoho_contact_id IS NULL
		""",
		as_dict=True
	)

@frappe.whitelist(allow_guest=True)
def add_supplier_to_zb(supplier):
	doc = frappe.get_doc("Supplier", supplier)
	custom_zoho_contact_id = update_supplier_contact_in_zoho(doc, method=None)
	if custom_zoho_contact_id:
		doc.custom_zoho_contact_id = custom_zoho_contact_id
		doc.save()
		return { "ADDED" }


@frappe.whitelist(allow_guest=True)
def get_zb_contacts_list():
	api_controller = frappe.get_doc("Zoho Books API")
	return api_controller.get_contacts()

@frappe.whitelist(allow_guest=True)
def sync_zb_contact_id_with_erp(contact_id, contact_name, contact_type):
	if contact_type != "vendor":
		return { "NOT VENDOR" }

	if frappe.get_value("Supplier", contact_name, "name"):
		if frappe.get_value("Supplier", contact_name, "custom_zoho_contact_id") != contact_id:
			existing_supplier_doc = frappe.get_doc("Supplier", contact_name)
			existing_supplier_doc.custom_zoho_contact_id = contact_id
			existing_supplier_doc.save()
			return { "UPDATED" }

		return { "ERP" }



""" def fetch_unsynced_sales_invoice_list():
	return frappe.get_list('Sales Invoice',
		filters={
			'custom_zb_sync_status': ['!=', 'Success']
		},
		#as_list=True
	)

def sync_with_zoho_books(invoice):
	pass """
