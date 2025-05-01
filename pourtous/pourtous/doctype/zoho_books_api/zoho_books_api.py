# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowtime, nowdate, flt
from datetime import datetime, timedelta

import requests, json, re
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


	def get_a_contact(self, contact_id):
		master = "contacts"
		scope='ZohoBooks.contacts.READ'

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

			r = s.get(api_url)

			r.raise_for_status()
			if r.json().get('message') == 'success':
				return r.json().get('contact')


	def post_tax(self, data):
		master = "settings"
		scope='ZohoBooks.settings.CREATE'

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

			r = s.post(api_url, data=json.dumps(data))

			if r.json().get('message') == 'The tax has been added.':
				return {
					"tax_id": r.json().get('tax').get('tax_id'),
				}
			elif r.json().get('message') == 'Tax or tax group already exists with this name.':
				return {
					"message": r.json().get('message'),
				}
			else:
				r.raise_for_status()


	def put_tax(self, tax_id, data):
		master = "settings"
		scope='ZohoBooks.settings.UPDATE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/settings/taxes/' + tax_id + '?'

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

			if r.json().get('message') == 'The tax has been updated.':
				return {
					"custom_zoho_contact_id": r.json().get('tax').get('tax_id'),
				}
			else:
				r.raise_for_status()

			#{'code': 100017, 'message': 'Tax or tax group already exists with this name.'}


	def get_a_tax(self, tax_id, data):
		master = "settings"
		scope='ZohoBooks.settings.READ'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/settings/taxes/' + tax_id + '?'

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

			""" if r.json().get('message') == 'The contact has been added.':
				return {
					"custom_zoho_contact_id": r.json().get('contact').get('contact_id'),
				}
			else:
				r.raise_for_status() """


	def delete_tax(self, tax_id):
		master = "settings"
		scope='ZohoBooks.settings.DELETE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/settings/taxes/' + tax_id + '?'

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


	def post_tax_group(self, data):
		master = "settings"
		scope='ZohoBooks.settings.CREATE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/settings/taxgroups?'

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

			if r.json().get('message') == 'success':
				return r.json().get('tax_group')
			else:
				r.raise_for_status()


	def put_tax_group(self, tax_id, data):
		master = "settings"
		scope='ZohoBooks.settings.UPDATE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/settings/taxgroups/' + tax_id + '?'

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

			""" if r.json().get('message') == 'The contact has been added.':
				return {
					"custom_zoho_contact_id": r.json().get('contact').get('contact_id'),
				}
			else:
				r.raise_for_status() """


	def get_a_tax_group(self, tax_id):
		master = "settings"
		scope='ZohoBooks.settings.READ'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/settings/taxgroups/' + tax_id + '?'

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

			if r.json().get('message') == 'success':
				return r.json().get('tax_group')
			else:
				r.raise_for_status()


	def delete_tax_group(self, tax_id):
		master = "settings"
		scope='ZohoBooks.settings.DELETE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/settings/taxgroups/' + tax_id + '?'

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
			# {'code': 0, 'message': 'The tax group has been deleted.'}
			# {'code': 100019,
 			# 'message': 'This tax cannot be deleted because it has been used in transactions.'}


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

			if r.json().get('message') == 'The item has been added.':
				custom_zoho_item_id = r.json().get('item').get('item_id')
				return custom_zoho_item_id

			else:
				#frappe.msgprint(r.json().get('message'))
				#r.raise_for_status()
				return r.json().get('message')


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
			#r.raise_for_status()
			if r.json().get('message') == "This item cannot be edited as it does not exist.":
				return self.post_item(data)

			else:
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
			r.raise_for_status()

			return r.json().get('message')


	def get_items(self):
		master = "items"
		scope='ZohoBooks.settings.READ'

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

			r = s.get(api_url)

			r.raise_for_status()
			if r.json().get('message') == 'success':
				return r.json().get('items')



	def post_bill(self, data):
		master = "bills"
		scope='ZohoBooks.bills.CREATE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/bills?'

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
			r.raise_for_status()
			#frappe.throw(str(r.json()))

			if r.json().get('message') == 'The bill has been created.':
				return r.json().get('bill').get('bill_id')

			else:
				frappe.msgprint(r.json().get('message'))


	def post_invoice(self, data):
		master = "invoices"
		scope='ZohoBooks.invoices.CREATE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/invoices?'

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
			#frappe.throw(str(r.json()))
			if r.json().get('message') == 'The invoice has been created.':
				return r.json().get('invoice').get('invoice_id')
			else :
				frappe.msgprint(r.json().get('message'))
				return
				#r.raise_for_status()


	def post_payment(self, data):
		master = "payments"
		scope='ZohoBooks.customerpayments.CREATE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/customerpayments?'

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
			#frappe.throw(str(r.json()))
			if r.json().get('message') == 'The payment from the customer has been recorded':
				return r.json().get('payment').get('payment_id')
			else :
				frappe.msgprint(r.json().get('message'))
				return
				#r.raise_for_status()


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


@frappe.whitelist(allow_guest=True)
def get_zb_tax_list():
	api_controller = frappe.get_doc("Zoho Books API")
	return api_controller.get_taxes()


@frappe.whitelist(allow_guest=True)
def sync_zb_tax_id_with_erp(tax_id, tax_name, tax_percentage, tax_type, tax_specific_type):
	if tax_type == "tax_group" and re.search("CESS", tax_name):
		# Match for I/GST-CESS Tax Groups

		api_controller = frappe.get_doc("Zoho Books API")
		zb_tax_group = api_controller.get_a_tax_group(tax_id)

		# extracting GST/IGST rate from the I/GST-CESS groups
		gst_rate = igst_rate = 0
		zb_tax_specific_type = ""
		for tax in zb_tax_group.get('taxes'):
			if tax.get("tax_specific_type") != 'cess':
				if tax.get("tax_specific_type") == 'sgst' or tax.get("tax_specific_type") == 'cgst':
					gst_rate += tax.get("tax_percentage")
					zb_tax_specific_type = "gst"
				elif tax.get("tax_specific_type") == 'igst':
					igst_rate = tax.get("tax_percentage")
					zb_tax_specific_type = 'igst'

		if zb_tax_specific_type == "gst":
			existing_erp_tax_template = frappe.db.sql(
				"""
				SELECT name FROM `tabItem Tax Template`
				WHERE disabled = 0 AND name like "%CESS%"
				AND gst_rate = '{0}'
				""".format(gst_rate),
				as_dict=True
				# AND custom_zoho_tax_group_id != '{2}'
			)

			if existing_erp_tax_template:
				frappe.set_value("Item Tax Template", existing_erp_tax_template[0].get("name"), "custom_zoho_tax_group_id", tax_id)
				return { "UPDATED" }
		
		else:
			existing_erp_tax_template = frappe.db.sql(
				"""
				SELECT name FROM `tabItem Tax Template`
				WHERE disabled = 0 AND name like "%CESS%"
				AND gst_rate = '{0}'
				""".format(igst_rate),
				as_dict=True
				# AND custom_zoho_tax_group_id != '{2}'
			)

			if existing_erp_tax_template:
				frappe.set_value("Item Tax Template", existing_erp_tax_template[0].get("name"), "custom_zoho_tax_igst_id", tax_id)
				return { "UPDATED" }


	if tax_type == "tax_group" and not re.search("CESS", tax_name):
		# Match for Non-CESS GST Tax Groups
		existing_erp_tax_template = frappe.db.sql(
			"""
			SELECT name FROM `tabItem Tax Template`
			WHERE disabled = 0 AND name not like "%CESS%"
			AND gst_rate = '{0}'
			""".format(tax_percentage),
			as_dict=True
			# AND custom_zoho_tax_group_id != '{2}'
		)
		if existing_erp_tax_template:
			frappe.set_value("Item Tax Template", existing_erp_tax_template[0].get("name"), "custom_zoho_tax_group_id", tax_id)
			return { "UPDATED" }


	elif tax_type == "tax" and tax_specific_type == "igst":
		existing_erp_tax_template = frappe.db.sql(
			"""
			SELECT name FROM `tabItem Tax Template`
			WHERE disabled = 0
			AND gst_rate = '{0}'
			""".format(tax_percentage),
			as_dict=True
			# AND custom_zoho_tax_group_id != '{2}'
		)
		if existing_erp_tax_template:
			frappe.set_value("Item Tax Template", existing_erp_tax_template[0].get("name"), "custom_zoho_tax_igst_id", tax_id)
			return { "UPDATED" }

	else:
		return { "NO-MATCH" }


@frappe.whitelist(allow_guest=True)
def fetch_erp_tax_list():
	return frappe.get_all('Item Tax Template', filters = {"disabled": 0})


@frappe.whitelist(allow_guest=True)
def sync_erp_taxes_with_zoho(erp_tax):
	erp_tax_doc = frappe.get_doc("Item Tax Template", erp_tax)

	zb_taxes = get_zb_tax_list()

	zb_default_taxes = {0, 5, 12, 18, 28}
	# ZB default tax rates cannot be added via API

	api_controller = frappe.get_doc("Zoho Books API")

	if erp_tax_doc.gst_rate not in zb_default_taxes:
		# IGST tax for the above default taxes rates are generated in Zoho Books directly
		data= {
			"tax_name": "IGST"+str(int(erp_tax_doc.gst_rate)), # first remove the decimal, then convert to str
			"tax_percentage": erp_tax_doc.gst_rate,
			"tax_type": "tax",
			"tax_specific_type": "igst",
			"tax_specification": "inter"
		}
		api_controller.post_tax(data)
		return { "UPDATED" }

	#frappe.throw(str(zb_taxes))

	for tax in zb_taxes:
		# matching for Zoho Tax Groups
		if tax.get("tax_type") == "tax_group" and tax.get("tax_percentage") == erp_tax_doc.gst_rate:
			# The ERP Tax template has a corresponding Tax group on ZB
			return

	# The ERP Tax template does not have a corresponding Tax group on ZB; create it.
	taxes = ""

	#frappe.throw(str(zb_taxes[0]))

	if erp_tax_doc.gst_rate in zb_default_taxes:
		frappe.throw("Please Add the Defualt Tax Groups Manually in Zoho Books, as they cannot be created via API (Zoho does not list them in a GET Call);" \
		"However, please replicate the ERP Item Tax template names with the tax group names in Zoho Books, for an accurate Item-Tax mapping")

	else:
		# create the tax elements and group (GST 3%, etc.)

		cgst_rate = sgst_rate = float(erp_tax_doc.gst_rate) / 2

		data1 = {
			"tax_name": "SGST"+str(sgst_rate),
			"tax_percentage": sgst_rate,
			"tax_type": "tax",
			"tax_specific_type": "sgst",
			"tax_specification": "intra"
		}

		res1 = api_controller.post_tax(data1)
		if res1.get("tax_id"):
			#taxes.append(res1.get("tax_id"))
			taxes += res1.get("tax_id")
		elif res1.get("message") == 'Tax or tax group already exists with this name.':
			for tax in zb_taxes:
				#if tax.get("tax_percentage") == erp_tax_doc.gst_rate:
					#taxes.append(tax.get("tax_id"))
				if (tax.get("tax_percentage") == float(erp_tax_doc.gst_rate) / 2) and (tax.get("tax_name") == "SGST"+str(sgst_rate)):
					taxes += tax.get("tax_id")

		data2 = {
			"tax_name": "CGST"+str(cgst_rate),
			"tax_percentage": cgst_rate,
			"tax_type": "tax",
			"tax_specific_type": "cgst",
			"tax_specification": "intra"
		}

		res2 = api_controller.post_tax(data2)
		if res2.get("tax_id"):
			#taxes.append(res2.get("tax_id"))
			taxes += ","+res2.get("tax_id")
		elif res2.get("message") == 'Tax or tax group already exists with this name.':
			for tax in zb_taxes:
				#if tax.get("tax_percentage") == erp_tax_doc.gst_rate:
					#taxes.append(tax.get("tax_id"))
				if (tax.get("tax_percentage") == float(erp_tax_doc.gst_rate) / 2) and (tax.get("tax_name") == "CGST"+str(cgst_rate)):
					taxes += ","+tax.get("tax_id")

		tax_group_data = {
			"tax_group_name": erp_tax_doc.title,
			"taxes": taxes
		}

		#frappe.throw(str(tax_group_data))
		res4 = api_controller.post_tax_group(tax_group_data)
		if res4:
			erp_tax_doc.custom_zoho_tax_group_id = res4.get("tax_group_id")
			erp_tax_doc.save()
			return { "UPDATED" }



def update_item_in_zoho(doc, method):
	if frappe.defaults.get_user_default("company") in ("Pour Tous Distribution Center", "Pour Tous Canteen"):
		return

	api_controller = frappe.get_doc("Zoho Books API")

	if doc.is_stock_item == 1:
		product_type = "goods"
	else:
		product_type = "service"

	if frappe.defaults.get_user_default("company") == "Pour Tous Purchasing Service":
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
			"Tube": "pcs",
			"Pk": "pcs"
		}
	else:
		frappe.throw("Please configure the UOM Mapping for this Company")

	try:
		zb_intra_tax_id = frappe.get_value("Item Tax Template", doc.taxes[0].item_tax_template, "custom_zoho_tax_group_id")
		zb_inter_tax_id = frappe.get_value("Item Tax Template", doc.taxes[0].item_tax_template, "custom_zoho_tax_igst_id")
		zb_contact_id = frappe.get_value("Supplier", doc.supplier_items[0].supplier, "custom_zoho_contact_id")
	except Exception as err:
		msg = "Please verify the Tax-template/Supplier/ZB-tax_id for Item Code " + doc.item_code
		frappe.msgprint(msg)
		return

	else:
		data = {
			"sku": doc.item_code,
			"name": doc.item_name,
			"description": doc.item_name,
			"unit": uom[doc.stock_uom],
			"product_type": product_type,
			"item_tax_preferences": [
				{
					"tax_id": zb_intra_tax_id,
					"tax_specification": "intra",
				},
				{
					"tax_id": zb_inter_tax_id,
					"tax_specification": "inter",
				},
			],
			'can_be_purchased': True,
			'item_type': 'sales_and_purchases',
			'vendor_id': zb_contact_id,
			'purchase_account_id': '2464766000000341487',
			'purchase_account_name': 'Purchase of Goods & Services',
			'purchase_description': doc.item_name,
			"hsn_or_sac": doc.gst_hsn_code,
			"rate": 0
		}

		put_data = {
			#"sku": doc.item_code,
			"name": doc.item_name,
			"description": doc.item_name,
			"unit": uom[doc.stock_uom],
			"product_type": product_type,
			"item_tax_preferences": [
				{
					"tax_id": zb_intra_tax_id,
					"tax_specification": "intra",
				},
				{
					"tax_id": zb_inter_tax_id,
					"tax_specification": "inter",
				},
			],
			'can_be_purchased': True,
			'item_type': 'sales_and_purchases',
			'vendor_id': zb_contact_id,
			'purchase_account_id': '2464766000000341487',
			'purchase_account_name': 'Purchase of Goods & Services',
			'purchase_description': doc.item_name,
			"hsn_or_sac": doc.gst_hsn_code,
			"rate": 0
		}

	if doc.custom_zoho_item_id == None:
		# post new Item
		res = api_controller.post_item(data)
		if res:
			doc.custom_zoho_item_id = res
			return doc.custom_zoho_item_id
			# returning this value for the add_item_to_zb function below (for bulk Items additions to Zoho)

	else:
		# put/update existing Item
		res = api_controller.put_item(doc.custom_zoho_item_id, put_data)
		msg = "Zoho Books API Response: " + str(res)
		frappe.msgprint(msg)


def delete_item_in_zoho(doc, method):
	if frappe.defaults.get_user_default("company") in ("Pour Tous Distribution Center", "Pour Tous Canteen"):
		return

	if doc.custom_zoho_item_id:
		api_controller = frappe.get_doc("Zoho Books API")
		res = api_controller.delete_item(doc.custom_zoho_item_id)
		msg = "Zoho Books Response: " + res
		frappe.msgprint(msg)


@frappe.whitelist(allow_guest=True)
def fetch_erp_items_list():
	#return frappe.get_all('Supplier', filters = {"disabled": 0})
	return frappe.db.sql(
		"""
		SELECT name FROM tabItem
		WHERE disabled = 0
		AND custom_zoho_item_id IS NULL
		""",
		as_dict=True
	)

@frappe.whitelist(allow_guest=True)
def add_erp_item_in_zb(erp_item):
	doc = frappe.get_doc("Item", erp_item)
	custom_zoho_item_id = update_item_in_zoho(doc, method=None)
	if custom_zoho_item_id:
		doc.custom_zoho_item_id = custom_zoho_item_id
		doc.save()
		return { "ADDED" }


@frappe.whitelist(allow_guest=True)
def custom_fetch_erp_items_list():
	#return frappe.get_all('Supplier', filters = {"disabled": 0})
	return frappe.db.sql(
		"""
		SELECT custom_zoho_item_id, item_name FROM tabItem
		WHERE disabled = 0
		""",
		as_dict=True
	)


@frappe.whitelist(allow_guest=True)
#def custom_add_erp_item_in_zb(erp_item):
def custom_add_erp_item_in_zb(custom_zoho_item_id, item_name):
	#item_code = frappe.get_value("Item", {"custom_zoho_item_id": custom_zoho_item_id}, "item_code")
	
	""" custom_zoho_item_id = update_item_in_zoho(doc, method=None)
	if custom_zoho_item_id:
		doc.custom_zoho_item_id = custom_zoho_item_id
		doc.save()
		return { "ADDED" }

	try:
		zb_contact_id = frappe.get_value("Supplier", doc.supplier_items[0].supplier, "custom_zoho_contact_id")
	except Exception as err:
		msg = "Please verify the Supplier for Item Code " + doc.item_code
		frappe.msgprint(msg)
		return

	data = {
		'can_be_purchased': True,
		'item_type': 'sales_and_purchases',
		'vendor_id': zb_contact_id,
		'purchase_account_id': '2464766000000030873',
		'purchase_account_name': 'Purchases',
		'purchase_description': doc.item_name,
	} """

	if item_name:
		#doc = frappe.get_doc("Item", item)

		data = {
			"name": item_name,
		}

		api_controller = frappe.get_doc("Zoho Books API")
		res = api_controller.put_item(custom_zoho_item_id, data)

		if str(res) == 'Item details have been saved.' or 'The item has been added.':
			#doc.save()
			return { "ADDED" }


@frappe.whitelist(allow_guest=True)
def get_zb_item_list():
	api_controller = frappe.get_doc("Zoho Books API")
	return api_controller.get_items()


@frappe.whitelist(allow_guest=True)
def sync_zb_item_id_with_erp(item_id, item_name):
	if frappe.get_value("Item", item_name, "name"):
		existing_item_doc = frappe.get_doc("Item", item_name)
		existing_item_doc.custom_zoho_item_id = item_id
		existing_item_doc.save()
		return { "UPDATED" }


@frappe.whitelist(allow_guest=True)
def fetch_erp_bills_list():
	return frappe.get_all('Purchase Receipt', filters = {
		"docstatus": 1,
		"custom_zoho_bill_id": ["is", "not set"]
	})


@frappe.whitelist(allow_guest=True)
def add_erp_bills_in_zoho(bill):
	bill_doc = frappe.get_doc("Purchase Receipt", bill)

	# Check if Supplier is Inter/Intra state

	contact_id = frappe.get_value("Supplier", bill_doc.supplier, "custom_zoho_contact_id")
	api_controller = frappe.get_doc("Zoho Books API")

	try:
		contact = api_controller.get_a_contact(contact_id)
		# r2.json().get('contact').get("tax_info_list")[0].get('place_of_supply')
		if contact.get("tax_info_list")[0].get('place_of_supply') == 'TN':
			tax_specification = "intra"
		else:
			tax_specification = "inter"
	except Exception as err:
		frappe.msgprint(str(err))
		return

	line_items = []

	for item in bill_doc.items:
		item_doc = frappe.get_doc("Item", item.item_code)

		try:
			if tax_specification == "intra":
				tax_id = frappe.get_value("Item Tax Template", item_doc.taxes[0].item_tax_template, "custom_zoho_tax_group_id")
			else:
				tax_id = frappe.get_value("Item Tax Template", item_doc.taxes[0].item_tax_template, "custom_zoho_tax_igst_id")
		except Exception as err:
			frappe.msgprint(str(err))
			msg = "Please verify the Tax-template/Supplier/ZB-tax_id for Item Code " + item.item_code
			frappe.msgprint(msg)
			return

		else:
			line_item = {
				"item_id": frappe.get_value("Item", item.item_code, "custom_zoho_item_id"),
				"rate": flt(item.price_list_rate, 2),
				"quantity": flt(item.qty, 2),
				"tax_id": tax_id
			}
			line_items.append(line_item)

	date = bill_doc.posting_date.strftime(api_controller.DATE_FORMAT) # converting Date object to String

	data = {
		'vendor_id': frappe.get_value("Supplier", bill_doc.supplier, "custom_zoho_contact_id"),
		'bill_number': bill_doc.name,
		'date': date,
		"is_inclusive_tax": False,
		'price_precision': 2,
		'location_id': '2464766000000030367',
		"line_items": line_items
	}

	res = api_controller.post_bill(data)
	if res:
		bill_doc.custom_zoho_bill_id = res
		bill_doc.save()
		frappe.db.commit()
		return { "ADDED" }


@frappe.whitelist(allow_guest=True)
def fetch_unsynced_erp_fs_invoice_list():
	return frappe.db.sql(
		"""
		SELECT si.name, sip.mode_of_payment, si.custom_fs_account_number, si.docstatus, si.status, si.posting_date, si.remarks
		FROM `tabSales Invoice` si, `tabSales Invoice Payment` sip
		WHERE si.docstatus = 1 AND si.status = 'paid' AND sip.mode_of_payment LIKE "FS%"
		AND (si.custom_zoho_invoice_id IS NULL OR si.custom_zoho_payment_id IS NULL) and sip.parent
		= si.name and si.posting_date between "2025-04-15" and "2025-04-21"
		""",
		as_dict=True
	)

@frappe.whitelist(allow_guest=True)
def sync_fs_inv_with_zoho_books(invoice):
	api_controller = frappe.get_doc("Zoho Books API")
	invoice_doc = frappe.get_doc("Sales Invoice", invoice)
	date = invoice_doc.posting_date.strftime(api_controller.DATE_FORMAT) # converting Date object to String

	if invoice_doc.custom_zoho_invoice_id == None:
		line_items = []

		for item in invoice_doc.items:
			item_doc = frappe.get_doc("Item", item.item_code)

			try:
				tax_id = frappe.get_value("Item Tax Template", item_doc.taxes[0].item_tax_template, "custom_zoho_tax_group_id")
			except Exception as err:
				frappe.msgprint(str(err))
				msg = "Please verify the Tax-template/ZB-tax_id for Item Code " + item.item_code
				frappe.msgprint(msg)
				return

			else:
				line_item = {
					"item_id": item_doc.custom_zoho_item_id,
					"name": item.item_code,
					"description": item.item_name,
					"rate": flt(item.rate, 2, "Commercial Rounding"),
					"quantity": flt(item.qty, 2, "Commerial rounding"),
					"tax_id": tax_id
				}
				line_items.append(line_item)

		invoice_data = {
			'customer_id': 2464766000000395217,
			'invoice_number': invoice,
			'date': date,
			"is_inclusive_tax": True,
			'price_precision': 2,
			"custom_fields": [
				{
					"index": 1,
					"label": "cf_fs_account_number",
					"value": invoice_doc.custom_fs_account_number,
					"data_type": "text"
				}
			],
			"line_items": line_items
		}

		#frappe.throw(str(invoice_data))
		res = api_controller.post_invoice(invoice_data)
		if res:
			invoice_doc.custom_zoho_invoice_id = res
			invoice_doc.save()
			frappe.db.commit()


	if invoice_doc.custom_zoho_payment_id == None:
		payment_data = {
			"customer_id": 2464766000000395217,
			"payment_mode": 'Bank Transfer',
			"amount": flt(invoice_doc.grand_total, 2, "Commercial Rounding"),
			"date": date,
			"reference_number": invoice_doc.name,
			"cf_transaction_id": invoice_doc.remarks[-95:],
			'account_id': '2464766000000103144',
			'account_name': 'PT PURCHASING SERVICE',
			'payment_status': 'paid',
			"invoices": [
				{
					"invoice_id": invoice_doc.custom_zoho_invoice_id,
					"amount_applied": flt(invoice_doc.grand_total, 2, "Commercial Rounding")
				}
			],
			"custom_fields": [
				{
					"index": 1,
					"label": "cf_transaction_id",
					"value": invoice_doc.remarks[-95:],
					"data_type": "text"
				}
			]
		}
		#frappe.throw(str(payment_data))
		res = api_controller.post_payment(payment_data)
		if res:
			invoice_doc.custom_zoho_payment_id = res
			invoice_doc.save()
			frappe.db.commit()

		return { "ADDED" }



@frappe.whitelist(allow_guest=True)
def fetch_unsynced_erp_aurocard_invoice_list():
	return frappe.db.sql(
		"""
		select si.name, sip.mode_of_payment, si.docstatus, si.status, si.posting_date, si.remarks
		from `tabSales Invoice` si, `tabSales Invoice Payment` sip
		where si.docstatus = 1 and si.status = 'paid' and sip.mode_of_payment like "Aurocard%"
		and (si.custom_zoho_invoice_id IS NULL OR si.custom_zoho_payment_id IS NULL) and sip.parent
		= si.name and si.posting_date between "2025-04-01" and "2025-04-05";
		""",
		as_dict=True
	)

@frappe.whitelist(allow_guest=True)
def sync_aurocard_inv_with_zoho_books(invoice):
	api_controller = frappe.get_doc("Zoho Books API")
	invoice_doc = frappe.get_doc("Sales Invoice", invoice)
	date = invoice_doc.posting_date.strftime(api_controller.DATE_FORMAT) # converting Date object to String

	if invoice_doc.custom_zoho_invoice_id == None:
		line_items = []

		for item in invoice_doc.items:
			item_doc = frappe.get_doc("Item", item.item_code)

			try:
				tax_id = frappe.get_value("Item Tax Template", item_doc.taxes[0].item_tax_template, "custom_zoho_tax_group_id")
			except Exception as err:
				frappe.msgprint(str(err))
				msg = "Please verify the Tax-template/ZB-tax_id for Item Code " + item.item_code
				frappe.msgprint(msg)
				return

			else:
				line_item = {
					"item_id": item_doc.custom_zoho_item_id,
					"name": item.item_code,
					"description": item.item_name,
					"rate": flt(item.rate, 2),
					"quantity": flt(item.qty, 2),
					"tax_id": tax_id
				}
				line_items.append(line_item)

		invoice_data = {
			'customer_id': 2464766000000395229,
			'invoice_number': invoice,
			'date': date,
			"is_inclusive_tax": True,
			#'price_precision': 2,
			"line_items": line_items
		}

		#frappe.throw(str(invoice_data))
		res = api_controller.post_invoice(invoice_data)
		if res:
			invoice_doc.custom_zoho_invoice_id = res
			invoice_doc.save()
			frappe.db.commit()


	if invoice_doc.custom_zoho_payment_id == None:
		payment_data = {
			"customer_id": 2464766000000395229,
			"payment_mode": 'Bank Transfer',
			"amount": flt(invoice_doc.grand_total, 2),
			"date": date,
			"reference_number": invoice_doc.name,
			"cf_transaction_id": invoice_doc.remarks[-95:],
			'account_id': '2464766000000103144',
			'account_name': 'PT PURCHASING SERVICE',
			'payment_status': 'paid',
			"invoices": [
				{
					"invoice_id": invoice_doc.custom_zoho_invoice_id,
					"amount_applied": flt(invoice_doc.grand_total, 2)
				}
			],
			"custom_fields": [
				{
					"index": 1,
					"label": "cf_transaction_id",
					"value": invoice_doc.remarks[-95:],
					"data_type": "text"
				}
			]
		}
		#frappe.throw(str(payment_data))
		res = api_controller.post_payment(payment_data)
		if res:
			invoice_doc.custom_zoho_payment_id = res
			invoice_doc.save()
			frappe.db.commit()

		return { "ADDED" }