# Copyright (c) 2025, Karan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowtime, nowdate
from datetime import datetime, timedelta
import random

import requests, json, re, csv
import os
#import urllib


class ZohoBooksAPI(Document):
	DATE_FORMAT = "%Y-%m-%d"
	TIME_FORMAT = "%H:%M:%S.%f"
	DATETIME_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"

	#scope = 'ZohoBooks.invoices.CREATE,ZohoBooks.invoices.READ,ZohoBooks.invoices.UPDATE,ZohoBooks.invoices.DELETE'
	scope = 'ZohoBooks.invoices.ALL'

	def	validate(self):
		if self.client_id and self.client_secret and self.user_id and self.organization_id:
			self.validate_zoho_api_params(self.scope)
			self.update_locations()
			self.update_accounts()
			self.update_walk_in_customer()


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


	#@frappe.whitelist()
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


	def update_locations(self):
		locations = self.get_locations()
		frappe.db.delete("Zoho Location") # delete the old location data
		for data in locations:
			location = frappe.new_doc('Zoho Location')
			location.location_id = data.get('location_id')
			location.initial_stock = '0'
			location.initial_stock_rate = '0'
			location.location_name = data.get('location_name')
			location.gst_number = data.get('tax_reg_no')
			location.save()


	def update_accounts(self):
		income_accounts = self.get_accounts('AccountType.Income')
		expense_accounts = self.get_accounts('AccountType.Expense')
		frappe.db.delete("Zoho Accounts") # delete the old Accounts data
		for data in income_accounts:
			income_account = frappe.get_doc({
					"doctype": 'Zoho Accounts',
					"account_id": data.get('account_id'),
					"account_name": data.get('account_name'),
					"account_type": data.get('account_type'),
					"filter_by": 'Income',
					"parent_account_id": data.get('parent_account_id'),
					"parent_account_name": data.get('parent_account_name')
				})
			income_account.insert()

		for data in expense_accounts:
			expense_account = frappe.get_doc({
					"doctype": 'Zoho Accounts',
					"account_id": data.get('account_id'),
					"account_name": data.get('account_name'),
					"account_type": data.get('account_type'),
					"filter_by": 'Expense',
					"parent_account_id": data.get('parent_account_id'),
					"parent_account_name": data.get('parent_account_name')
				})
			expense_account.insert()


	def update_walk_in_customer(self):
		customers = self.get_contacts(contact_type='customer',company_name='Walk In customers')
		frappe.db.delete("Zoho Walk In customer") # delete the old Contact data

		for data in customers:
			customer = frappe.get_doc({
					"doctype": 'Zoho Walk In customer',
					"contact_id": data.get('contact_id'),
					"contact_name": data.get('contact_name'),
					"company_name": data.get('company_name'),
				})
			customer.insert()


	def get_locations(self):
		master = "locations"
		scope='ZohoBooks.settings.READ'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/locations?'

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
				return r.json().get('locations')
			else:
				r.raise_for_status()


	def get_accounts(self, account_type):
		master = "chartofaccounts"
		scope='ZohoBooks.accountants.READ'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/chartofaccounts?'

		authorization = 'Zoho-oauthtoken ' + token_to_use

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id,
				'filter_by': account_type
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.get(api_url)

			if r.json().get('message') == 'success':
				return r.json().get('chartofaccounts')
			else:
				r.raise_for_status()


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
			#frappe.throw(str(r.json()))

			# if data["contact_type"] == "vendor" and r.json().get('message') == 'A vendor with the name, "{0}", already exists To proceed, either update your preferences to allow duplicate vendor names or enter a unique vendor name.'.format(data["contact_name"]):
			# 	if not frappe.db.get_value("Supplier", {"supplier_name": data["contact_name"]}, 'supplier_name'):
			# 		return self.put_contact(data)

			# elif data["contact_type"] == "customer" and r.json().get('message') == 'The customer '{0}' already exists. Please specify a different name.'.format(data["contact_name"]):
			# 	if not frappe.db.get_value("Customer", {"customer_name": data["contact_name"]}, 'customer_name'):
			# 		return self.put_contact(data)
			#if r.json().get('message') == 'The contact has been added.':
			if r.json().get('code') == 0:
				frappe.msgprint(r.json().get('message'))
				return {
					"custom_zoho_contact_id": r.json().get('contact').get('contact_id'),
				}
			else:
				frappe.msgprint(r.json().get('message'))
				#r.raise_for_status()


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
				frappe.msgprint(r.json().get('message'))
				#r.raise_for_status()
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

			return r.json().get('message')
			# r.raise_for_status()


	def get_contacts(self, contact_type=None, company_name=None):
		master = "contacts"
		scope='ZohoBooks.contacts.READ'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/contacts?'

		authorization = 'Zoho-oauthtoken ' + token_to_use

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id,
				'contact_type': contact_type,
				'company_name': company_name
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.get(api_url)

			if r.json().get('message') == 'success':
				return r.json().get('contacts')
			else:
				r.raise_for_status()


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

			if r.json().get('message') == 'success':
				return r.json().get('contact')
			else:
				r.raise_for_status()


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

			#if r.json().get('message') == 'The tax has been updated.':
			if r.json().get('code') == 0:
				return {
					"custom_zoho_contact_id": r.json().get('tax').get('tax_id'),
				}
			else:
				r.raise_for_status()

			#{'code': 100017, 'message': 'Tax or tax group already exists with this name.'}


	def get_a_tax(self, tax_id):
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

			r = s.get(api_url)


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

			if r.json().get('code') == 0:
				return r.json().get('message')
			else:
				r.raise_for_status()


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

			if r.json().get('message') == 'success':
				return r.json().get('taxes')
			else:
				frappe.msgprint(r.json().get('message'))
			#r.raise_for_status()


	def post_item(self, data):
		master = "items"
		scope='ZohoBooks.settings.CREATE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/items?'

		authorization = 'Zoho-oauthtoken ' + token_to_use

		#frappe.throw(str(data))

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.post(api_url, data=json.dumps(data))

			#if r.json().get('message') == 'The item has been added.':
			""" if r.json().get('code') == 0:
				custom_zoho_item_id = r.json().get('item').get('item_id')
				return custom_zoho_item_id

			else:
				#frappe.msgprint(r.json().get('message'))
				#r.raise_for_status()
				return r.json().get('message') """

			#frappe.throw(str(r.json()))
			return r.json()


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
			#if r.json().get('message') == "This item cannot be edited as it does not exist.":
			#	return self.post_item(data)

			#else:
			return r.json()


	def delete_item(self, item_id):
		master = "items"
		scope='ZohoBooks.settings.DELETE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/items/' + item_id + '?'

		authorization = 'Zoho-oauthtoken ' + token_to_use

		#frappe.throw(_("api_url: {0} , authorization: {1}").format(api_url, authorization))

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.delete(api_url)
			#r.raise_for_status()

			return r.json().get('message')


	def get_an_item(self, item):
		master = "items"
		scope='ZohoBooks.settings.READ'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/items/' + item + '?'

		authorization = 'Zoho-oauthtoken ' + token_to_use

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id,
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.get(api_url)

			if r.json().get('message') == 'success':
				return r.json().get('item')
			else:
				#r.raise_for_status()
				frappe.msgprint(r.json().get('message'))
				return r.json()


	def get_items(self, sku=None, name=None):
		master = "items"
		scope='ZohoBooks.settings.READ'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/items?'

		authorization = 'Zoho-oauthtoken ' + token_to_use

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id,
				"sku": sku,
				'name': name
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.get(api_url)

			if r.json().get('message') == 'success':
				return r.json().get('items')
			else:
				r.raise_for_status()


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
			#frappe.throw(str(r.json()))

			#if r.json().get('message') == 'The bill has been created.':
			if r.json().get('code') == 0:
				#frappe.msgprint(r.json().get('message'))
				return r.json().get('bill')

			else:
				frappe.msgprint(r.json().get('message'))
				return r.json()
				#with open('tax_info_list_exception_err.txt', 'w') as file:
				#	file.write(r.json().get('message'))
				# r.raise_for_status()


	def put_bill(self, bill_id, data):
		master = "bills"
		scope='ZohoBooks.bills.UPDATE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/bills/' + bill_id + '?'

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
			#if r.json().get('message') == "Bill information has been updated.":
			return r.json()


	def query_bill(self, bill_number, reference_number):
		master = "bills"
		scope='ZohoBooks.bills.READ'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/bills?'

		authorization = 'Zoho-oauthtoken ' + token_to_use

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id,
				'bill_number': bill_number,
				'reference_number': reference_number
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.get(api_url)

			if r.json().get("code") == 0:
				return r.json().get('bills')
			else:
				frappe.msgprint(r.json().get('message'))
			# r.raise_for_status()


	def void_bill(self, bill_id):
		master = "bills"
		scope='ZohoBooks.bills.CREATE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/bills/' + bill_id + '/status/void?'

		authorization = 'Zoho-oauthtoken ' + token_to_use

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.post(api_url)

			return r.json().get('message')
			# if r.json().get('message') != "The bill has been marked as void.":
			# r.raise_for_status()


	def void_vendor_credit(self, vendor_credit_id):
		master = "debitnotes"
		scope='ZohoBooks.debitnotes.CREATE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/vendorcredits/' + vendor_credit_id + '/status/void?'

		authorization = 'Zoho-oauthtoken ' + token_to_use

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.post(api_url)

			return r.json().get('message')
			# if r.json().get('message') != "The vendor credit has been voided.":
			# r.raise_for_status()


	def delete_bill(self, bill_id):
		master = "bills"
		scope='ZohoBooks.bills.DELETE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/bills/' + bill_id + '?'

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

			return r.json()
			#return r.json().get('message')
			# r.raise_for_status()


	def post_vendor_credit(self, data):
		master = "vendorcredit"
		scope='ZohoBooks.debitnotes.CREATE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/vendorcredits?'

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
			#if r.json().get('message') == 'The credit note has been created.':
			if r.json().get('code') == 0:
				return r.json().get('vendor_credit')
				#return r.json().get('invoice').get('invoice_id')
			else :
				frappe.msgprint(r.json().get('message'))
				return r.json()
				#r.raise_for_status()


	def query_vendor_credit(self, vendor_credit_id, reference_number):
		master = "vendorcredit"
		scope='ZohoBooks.debitnotes.READ'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/vendorcredits?'

		authorization = 'Zoho-oauthtoken ' + token_to_use

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id,
				'vendor_credit_id': vendor_credit_id,
				'reference_number': reference_number
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.get(api_url)

			if r.json().get("code") == 0:
				return r.json().get('vendorcredits')
			else:
				frappe.msgprint(r.json().get('message'))
			# r.raise_for_status()


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
			#if r.json().get('message') == 'The invoice has been created.':
			if r.json().get('code') == 0:
				return r.json().get('invoice')
				#return r.json().get('invoice').get('invoice_id')
			else :
				frappe.msgprint(r.json().get('message'))
				return r.json()
				#return
				#r.raise_for_status()


	def post_creditnote(self, data):
		master = "creditnotes"
		scope='ZohoBooks.creditnotes.CREATE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/creditnotes?'

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
			#if r.json().get('message') == 'The credit note has been created.':
			if r.json().get('code') == 0:
				return r.json().get('creditnote')
				#return r.json().get('invoice').get('invoice_id')
			else :
				frappe.msgprint(r.json().get('message'))
				#r.raise_for_status()


	def post_creditnote_refund(self, data, creditnote_id):
		master = "creditnotes"
		scope='ZohoBooks.creditnotes.CREATE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/creditnotes/' + creditnote_id + '/refunds?'

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
			#if r.json().get('message') == '"The credit note amount is refunded successfully."':
			if r.json().get('code') == 0:
				return r.json().get('creditnote_refund').get("creditnote_refund_id")
				#return r.json().get('invoice').get('invoice_id')
			else :
				frappe.msgprint(r.json().get('message'))
				#return
				#r.raise_for_status()


	def delete_creditnote(self, custom_zb_creditnote_id):
		master = "creditnotes"
		scope='ZohoBooks.creditnotes.DELETE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/creditnotes/' + custom_zb_creditnote_id + '?'

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

			return r.json()
			#return r.json().get('message')
			# r.raise_for_status()


	def void_creditnote(self, custom_zb_creditnote_id):
		master = "creditnotes"
		scope='ZohoBooks.creditnotes.CREATE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/creditnotes/' + custom_zb_creditnote_id + '/status/void?'

		authorization = 'Zoho-oauthtoken ' + token_to_use

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.post(api_url)

			return r.json().get('message')
			# if r.json().get('message') != "The credit note has been marked as void.":
			# r.raise_for_status()


	def delete_creditnote_refund(self, custom_zb_creditnote_id, custom_zb_creditnote_refund_id):
		master = "creditnotes"
		scope='ZohoBooks.creditnotes.DELETE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/creditnotes/' + custom_zb_creditnote_id + '/refunds/' + custom_zb_creditnote_refund_id + '?'

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

			return r.json()
			#return r.json().get('message')
			# r.raise_for_status()


	def get_a_credit_note(self, creditnote_id):
		master = "creditnotes"
		scope='ZohoBooks.creditnotes.READ'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/creditnotes/' + creditnote_id + '?'

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

			if r.json().get("code") == 0:
				return r.json().get('creditnote')
			else:
				frappe.msgprint(r.json().get('message'))
			# r.raise_for_status()


	def query_credit_note(self, creditnote_number=None):
		master = "creditnotes"
		scope='ZohoBooks.creditnotes.READ'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/creditnotes?'

		authorization = 'Zoho-oauthtoken ' + token_to_use

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id,
				'invoice_number': creditnote_number
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.get(api_url)

			if r.json().get("code") == 0:
				return r.json().get('creditnotes')
			else:
				frappe.msgprint(r.json().get('message'))
				return r.json()
			# r.raise_for_status()


	def query_invoice(self, invoice_number=None):
		master = "invoices"
		scope='ZohoBooks.invoices.READ'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/invoices?'

		authorization = 'Zoho-oauthtoken ' + token_to_use

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id,
				'invoice_number': invoice_number
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.get(api_url)

			if r.json().get("code") == 0:
				return r.json().get('invoices')
			else:
				frappe.msgprint(r.json().get('message'))
			# r.raise_for_status()


	def get_an_invoice(self, invoice_id):
		master = "invoices"
		scope='ZohoBooks.invoices.READ'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/invoices/' + invoice_id + '?'

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

			if r.json().get("code") == 0:
				return r.json().get('invoice')
			else:
				frappe.msgprint(r.json().get('message'))
			# r.raise_for_status()


	def put_invoice(self, invoice_id, data):
		master = "invoices"
		scope='ZohoBooks.invoices.UPDATE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/invoices?' + invoice_id + '?'

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
			#frappe.throw(str(r.json()))
			#if r.json().get('message') == 'The invoice has been created.':
			if r.json().get('code') == 0:
				return r.json().get('invoice').get('invoice_id')
			else :
				frappe.msgprint(r.json().get('message'))


	def void_invoice(self, invoice_id):
		master = "invoices"
		scope='ZohoBooks.invoices.CREATE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/invoices/' + invoice_id + '/status/void?'

		authorization = 'Zoho-oauthtoken ' + token_to_use

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.post(api_url)

			return r.json().get('message')
			# if r.json().get('message') != "Invoice status has been changed to Void.":
			# r.raise_for_status()


	def mark_invoice_as_sent(self, invoice_id):
		master = "invoices"
		scope='ZohoBooks.invoices.CREATE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/invoices/' + invoice_id + '/status/sent?'

		authorization = 'Zoho-oauthtoken ' + token_to_use

		with requests.Session() as s:
			s.params = {
				'organization_id': self.organization_id
			}

			s.headers = {
				'Authorization': authorization,
				'content-type': 'application/json'
				}

			r = s.post(api_url)

			return r.json().get('message')
			# if r.json().get('message') != "Invoice status has been changed to Sent.":
			# r.raise_for_status()


	def delete_invoice(self, invoice_id):
		master = "invoices"
		scope='ZohoBooks.invoices.DELETE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/invoices/' + invoice_id + '?'

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

			return r.json()
			#return r.json().get('message')
			# r.raise_for_status()


	def delete_customerpayments(self, payment_id):
		master = "payments"
		scope='ZohoBooks.customerpayments.DELETE'

		token_to_use = self.query_stored_tokens(master, scope)

		api_url = 'https://www.zohoapis.in/books/v3/customerpayments/' + payment_id + '?'

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

			return r.json()
			#return r.json().get('message')
			# r.raise_for_status()


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
			#if r.json().get('message') == 'The payment from the customer has been recorded':
			if r.json().get('code') == 0:
				return r.json().get('payment').get('payment_id')
			else :
				frappe.msgprint(r.json().get('message'))
				#return
				#r.raise_for_status()


def update_contact_in_zoho(doc, method):
	if doc.customer_type != "Company":
		return

	if frappe.defaults.get_user_default("company") in ("Pour Tous Canteen"):
		return

	#if doc.custom_update_zoho_contact == 0:
	#	return

	api_controller = frappe.get_doc("Zoho Books API")

	if doc.customer_type == "Company":
		customer_sub_type = "business"
	else:
		customer_sub_type = "individual"

	gst_treatment = {
		"Registered Regular": "business_gst",
		"Unregistered": "business_none",
		"Overseas": "overseas"
	}

	data = {
		"contact_name": doc.customer_name,
		"company_name": doc.customer_name,
		"contact_type": "customer",
		"customer_sub_type": customer_sub_type,
		"gst_no": doc.gstin,
		"gst_treatment": gst_treatment[doc.gst_category],
	}

	if doc.customer_primary_address:
		address_doc = frappe.get_doc("Address", doc.customer_primary_address)
		billing_address = {
            #"attention": "Mr.John",
            "address": address_doc.address_line1,
            "street2": address_doc.address_line2,
            #"state_code": "CA",
            "city": address_doc.city,
            "state": address_doc.state,
            "zip": address_doc.pincode,
            "country": address_doc.country,
            "phone": doc.mobile_no
		}

		data["billing_address"] = billing_address

	if doc.custom_zoho_contact_id == None:
		# post new Contact
		res = api_controller.post_contact(data)
		if res.get("custom_zoho_contact_id"):
			doc.custom_zoho_contact_id = res.get("custom_zoho_contact_id")

	else:
		# put/update existing Contact
		res = api_controller.put_contact(doc.custom_zoho_contact_id, data)
		if res.get("custom_zoho_contact_id"):
			# checks if the API controller handled a non-existing contact,
			# in case of wrong/old Zoho Contact IDs stored in the ERP supplier record, by calling post instead
			doc.custom_zoho_contact_id = res.get("custom_zoho_contact_id")
		else:
			# put/update response
			frappe.msgprint("Zoho Books Response: " + res.get("message"))
			#return { "UPDATED" }


def delete_contact_in_zoho(doc, method):
	if doc.doctype == "Customer":
		if doc.customer_type != "Company":
			return

	#if frappe.defaults.get_user_default("company") in ("Pour Tous Distribution Center", "Pour Tous Canteen"):
	if frappe.defaults.get_user_default("company") in ("Pour Tous Canteen"):
		return

	if doc.custom_zoho_contact_id:
		api_controller = frappe.get_doc("Zoho Books API")
		res = api_controller.delete_contact(doc.custom_zoho_contact_id)
		msg = "Zoho Books Response: " + res
		frappe.msgprint(msg)


def update_supplier_contact_in_zoho(doc, method):
	if not doc.gstin:
		doc.is_reverse_charge_applicable = 1
	else:
		doc.is_reverse_charge_applicable = 0
	#if frappe.defaults.get_user_default("company") in ("Pour Tous Distribution Center", "Pour Tous Canteen"):
	if frappe.defaults.get_user_default("company") in ("Pour Tous Canteen"):
		return

	api_controller = frappe.get_doc("Zoho Books API")

	gst_treatment = {
		"Registered Regular": "business_gst",
		"Registered Composition": "business_registered_composition",
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

	if doc.supplier_primary_address:
		address_doc = frappe.get_doc("Address", doc.supplier_primary_address)
		billing_address = {
            #"attention": "Mr.John",
            "address": address_doc.address_line1,
            "street2": address_doc.address_line2,
            #"state_code": "CA",
            "city": address_doc.city,
            "state": address_doc.state,
            "zip": address_doc.pincode,
            "country": address_doc.country,
            "phone": doc.mobile_no
		}

		data["billing_address"] = billing_address

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



@frappe.whitelist()
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

@frappe.whitelist()
def add_supplier_to_zb(supplier):
	doc = frappe.get_doc("Supplier", supplier)
	custom_zoho_contact_id = update_supplier_contact_in_zoho(doc, method=None)
	if custom_zoho_contact_id:
		doc.custom_zoho_contact_id = custom_zoho_contact_id
		doc.save()
		return { "ADDED" }


@frappe.whitelist()
def get_zb_contacts_list():
	api_controller = frappe.get_doc("Zoho Books API")
	return api_controller.get_contacts()

@frappe.whitelist()
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


@frappe.whitelist()
def get_zb_tax_list():
	api_controller = frappe.get_doc("Zoho Books API")
	return api_controller.get_taxes()


@frappe.whitelist()
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
				frappe.db.set_value("Item Tax Template", existing_erp_tax_template[0].get("name"), "custom_zoho_tax_group_id", tax_id)
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
				frappe.db.set_value("Item Tax Template", existing_erp_tax_template[0].get("name"), "custom_zoho_tax_igst_id", tax_id)
				return { "UPDATED" }


	if tax_type == "tax_group" and not re.search("CESS", tax_name):
		# Match for Non-CESS GST Tax Groups
		existing_erp_tax_template = frappe.db.sql(
			"""
			SELECT name FROM `tabItem Tax Template`
			WHERE disabled = 0 AND name not like "%CESS%"
			AND gst_rate = '{0}'
			""".format(abs(float(tax_percentage))),
			as_dict=True
			# AND custom_zoho_tax_group_id != '{2}'
		)
		if existing_erp_tax_template:
			if float(tax_percentage) > 0:
				frappe.db.set_value("Item Tax Template", existing_erp_tax_template[0].get("name"), "custom_zoho_tax_group_id", tax_id)
			else:
				# for RCM groups (tax_percentage < 0)
				frappe.db.set_value("Item Tax Template", existing_erp_tax_template[0].get("name"), "custom_zoho_rcm_group_id", tax_id)
			return { "UPDATED" }


	elif tax_type == "tax" and tax_specific_type == "igst":
		existing_erp_tax_template = frappe.db.sql(
			"""
			SELECT name FROM `tabItem Tax Template`
			WHERE disabled = 0
			AND gst_rate = '{0}'
			""".format(abs(float(tax_percentage))),
			as_dict=True
			# AND custom_zoho_tax_group_id != '{2}'
		)
		if existing_erp_tax_template:
			if float(tax_percentage) > 0:
				frappe.db.set_value("Item Tax Template", existing_erp_tax_template[0].get("name"), "custom_zoho_tax_igst_id", tax_id)
			else:
				frappe.db.set_value("Item Tax Template", existing_erp_tax_template[0].get("name"), "custom_zoho_igst_rcm_id", tax_id)
			return { "UPDATED" }

	else:
		return { "NO-MATCH" }


@frappe.whitelist()
def fetch_erp_tax_list():
	return frappe.get_all('Item Tax Template', filters = {"disabled": 0})


@frappe.whitelist()
def sync_erp_taxes_with_zoho(erp_tax):
	erp_tax_doc = frappe.get_doc("Item Tax Template", erp_tax)

	zb_taxes = get_zb_tax_list()

	zb_default_taxes = {0, 5, 12, 18, 28}
	# ZB default tax rates cannot be added via API

	existing_gst = False
	existing_gst_rcm = False
	existing_igst = False
	existing_igst_rcm = False

	for tax in zb_taxes:
		# matching for Zoho Tax Groups
		if tax.get("tax_type") == "tax_group" and tax.get("tax_percentage") == erp_tax_doc.gst_rate:
			existing_gst = True

		if tax.get("tax_type") == "tax_group" and tax.get("tax_percentage") == -erp_tax_doc.gst_rate:
			existing_gst_rcm = True

		if erp_tax_doc.gst_rate in zb_default_taxes or (tax.get("tax_type") == "tax" and tax.get("tax_specific_type") == "igst" and tax.get("tax_percentage") == erp_tax_doc.gst_rate):
			existing_igst = True

		if tax.get("tax_type") == "tax" and tax.get("tax_specific_type") == "igst" and tax.get("tax_percentage") == -erp_tax_doc.gst_rate:
			existing_igst_rcm = True

	if existing_gst == True and existing_gst_rcm == True and existing_igst == True and existing_igst_rcm == True:
		# The ERP Tax template has all it's corresponding Taxes on ZB
		return

	# The ERP Tax template does not have a corresponding Tax/RCM/group on ZB; create it:

	api_controller = frappe.get_doc("Zoho Books API")

	if erp_tax_doc.gst_rate not in zb_default_taxes:
		# IGST tax for the above default taxes rates are generated in Zoho Books directly

		if existing_igst == False:
			data = {
				"tax_name": "IGST"+str(int(erp_tax_doc.gst_rate)), # first remove the decimal, then convert to str
				"tax_percentage": erp_tax_doc.gst_rate,
				"tax_type": "tax",
				"tax_specific_type": "igst",
				"tax_specification": "inter"
			}
			res = api_controller.post_tax(data)
			#return { "UPDATED" }
			if res:
				erp_tax_doc.custom_zoho_tax_igst_id = res.get("tax_id")
				erp_tax_doc.save()
				#return { "UPDATED" }

	#frappe.throw(str(zb_taxes))

	if existing_igst_rcm == False:
		# IGST RCM Tax
		data_rcm = {
			"tax_name": "IGST-RCM-"+str(int(erp_tax_doc.gst_rate)), # first remove the decimal, then convert to str
			"tax_percentage": -erp_tax_doc.gst_rate,
			"tax_type": "tax",
			"tax_specific_type": "igst",
			"tax_specification": "inter"
		}
		res_rcm = api_controller.post_tax(data_rcm)
		if res_rcm:
			erp_tax_doc.custom_zoho_igst_rcm_id = res_rcm.get("tax_id")
			erp_tax_doc.save()

	taxes = ""
	taxes_rcm = ""

	#frappe.throw(str(zb_taxes[0]))

	# create the tax elements and group (GST 3%, etc.)
	cgst_rate = sgst_rate = float(erp_tax_doc.gst_rate) / 2

	if erp_tax_doc.gst_rate not in zb_default_taxes and existing_gst == False:
		data1 = {
			"tax_name": "SGST"+str(sgst_rate),
			"tax_percentage": sgst_rate,
			"tax_type": "tax",
			"tax_specific_type": "sgst",
			"tax_specification": "intra"
		}
		#frappe.throw(str(data1))

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
		#frappe.throw(str(data2))

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

		res3 = api_controller.post_tax_group(tax_group_data)
		if res3:
			erp_tax_doc.custom_zoho_tax_group_id = res3.get("tax_group_id")
			erp_tax_doc.save()
			#return { "UPDATED" }

	if existing_gst_rcm == False:
		data1_rcm = {
			"tax_name": "SGST-RCM-"+str(sgst_rate),
			"tax_percentage": -sgst_rate,
			"tax_type": "tax",
			"tax_specific_type": "sgst",
			"tax_specification": "intra"
		}

		res1_rcm = api_controller.post_tax(data1_rcm)
		if res1_rcm.get("tax_id"):
			#taxes.append(res1.get("tax_id"))
			taxes_rcm += res1_rcm.get("tax_id")
		elif res1_rcm.get("message") == 'Tax or tax group already exists with this name.':
			for tax in zb_taxes:
				#if tax.get("tax_percentage") == erp_tax_doc.gst_rate:
					#taxes.append(tax.get("tax_id"))
				if (tax.get("tax_percentage") == float(erp_tax_doc.gst_rate) / 2) and (tax.get("tax_name") == "SGST"+str(sgst_rate)):
					taxes_rcm += tax.get("tax_id")

		data2_rcm = {
			"tax_name": "CGST-RCM-"+str(cgst_rate),
			"tax_percentage": -cgst_rate,
			"tax_type": "tax",
			"tax_specific_type": "cgst",
			"tax_specification": "intra"
		}

		res2_rcm = api_controller.post_tax(data2_rcm)
		if res2_rcm.get("tax_id"):
			#taxes.append(res2.get("tax_id"))
			taxes_rcm += ","+res2_rcm.get("tax_id")
		elif res2_rcm.get("message") == 'Tax or tax group already exists with this name.':
			for tax in zb_taxes:
				#if tax.get("tax_percentage") == erp_tax_doc.gst_rate:
					#taxes.append(tax.get("tax_id"))
				if (tax.get("tax_percentage") == float(erp_tax_doc.gst_rate) / 2) and (tax.get("tax_name") == "CGST"+str(cgst_rate)):
					taxes_rcm += ","+tax.get("tax_id")

		tax_group_data_rcm = {
			"tax_group_name": erp_tax_doc.title + " RCM",
			"taxes": taxes_rcm
		}

		res4 = api_controller.post_tax_group(tax_group_data_rcm)
		if res4:
			erp_tax_doc.custom_zoho_rcm_group_id = res4.get("tax_group_id")
			erp_tax_doc.save()
			#return { "UPDATED" }

	if erp_tax_doc.gst_rate in zb_default_taxes and existing_gst == False:
		frappe.throw("Please Add the Defualt Tax Groups Manually in Zoho Books, as they cannot be created via API (Zoho does not list them in a GET Call);" \
		"However, please replicate the ERP Item Tax template names with the tax group names in Zoho Books, for an accurate Item-Tax mapping")


def update_item_in_zoho(doc, method):
	#frappe.throw(str(doc.custom_skip_zoho_trigger))

	if doc.custom_skip_zoho_trigger and doc.custom_zoho_item_id != None:
		doc.custom_skip_zoho_trigger = 0 # reseting the value after it is matched
		return

	api_controller = frappe.get_doc("Zoho Books API")

	if doc.is_stock_item == 1:
		product_type = "goods"
	else:
		product_type = "service"

	if frappe.defaults.get_user_default("company") in (
		"Pour Tous Distribution Center", "Pour Tous Purchasing Service",
		"Auroville Bakery", "AV Bakery Cafe", "AV Bakery Cafe Townhall"
	):
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
			"Pk": "pcs",
			"Loaf": "pcs",
			"Bund": "pcs",
			"pcs": "pcs"
		}
	else:
		frappe.throw("Please configure the UOM Mapping for this Company")

	try:
		zb_intra_tax_id = frappe.get_value("Item Tax Template", doc.taxes[0].item_tax_template, "custom_zoho_tax_group_id")
		zb_inter_tax_id = frappe.get_value("Item Tax Template", doc.taxes[0].item_tax_template, "custom_zoho_tax_igst_id")
		if not doc.supplier_items:
			zb_contact_id = None
		else:
			zb_contact_id = frappe.get_value("Supplier", doc.supplier_items[0].supplier, "custom_zoho_contact_id")
	except Exception as err:
		msg = "Please verify the Tax-template/ZB-tax_id for Item Code " + doc.item_code
		frappe.msgprint(msg)
		return

	else:
		data = {
			"sku": doc.item_code,
			"name": doc.item_name,
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
			#'can_be_purchased': True,
			'item_type': 'sales_and_purchases',
			'vendor_id': zb_contact_id,
			'purchase_account_id': api_controller.expense_account_id,
			'purchase_account_name': api_controller.expense_account,
			'account_id': api_controller.income_account_id,
			'account_name': api_controller.income_account,
			"hsn_or_sac": doc.gst_hsn_code,
			"rate": 0
		}

		put_data = {
			#"sku": doc.item_code,
			"name": doc.item_name,
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
			#'can_be_purchased': True, # getting message from Zoho Books that Item Type cannot be changed for items having transactions.
			'item_type': 'sales_and_purchases',
			'vendor_id': zb_contact_id,
			'purchase_account_id': api_controller.expense_account_id,
			'purchase_account_name': api_controller.expense_account,
			'account_id': api_controller.income_account_id,
			'account_name': api_controller.income_account,
			"hsn_or_sac": doc.gst_hsn_code,
			"rate": 0
		}

	if api_controller.location_id:
		# bakery items at Townhall location, should only have one location: Townhall
		if frappe.defaults.get_user_default("company") == "AV Bakery Cafe Townhall" and doc.brand == 'Bakery':
			data['custom_fields'] = put_data['custom_fields'] = [
					{
						"index": 1,
						"label": "cf_brand",
						"value": doc.brand,
						"data_type": "text"
					}
				]

			data['locations'] = put_data['locations'] = frappe.db.get_list(
				'Zoho Location', filters={'location_id': api_controller.location_id},
				fields=['location_id','initial_stock','initial_stock_rate']
			)

		else:
			data['locations'] = put_data['locations'] = frappe.db.get_list(
				'Zoho Location', fields=['location_id','initial_stock','initial_stock_rate']
			)

	#frappe.throw(str(put_data))

	if doc.custom_zoho_item_id == None:
		# post new Item
		res = api_controller.post_item(data)
		if res:
			if res.get('code') == 0:
				doc.custom_zoho_item_id = res.get('item').get('item_id')
				return doc.custom_zoho_item_id
				# returning this value for the add_item_to_zb function below (for bulk Items additions to Zoho)

			#frappe.throw(str(res))
			elif res.get('message') == ('This SKU given for "{0}" ({1}) already exists.'.format(doc.item_name, doc.item_code)):
				res3 = api_controller.get_items(sku=doc.item_code)
				if res3:
					doc.custom_zoho_item_id = res3[0].get('item_id')
					return res3[0].get('item_id')

			else:
				frappe.msgprint(res.get("message"))

			# else:
			# 	with open('Item_2.json', 'r') as file:
			# 		data = json.load(file)

			# 	json_str = json.dumps(data, indent=4)
			# 	dict = json.loads(json_str)
			# 	for item in dict:
			# 		if item.get('sku') == doc.item_code:
			# 			item_id = item.get('item_id')
			# 			break

			# 	return item_id


	else:
		# put/update existing Item
		#frappe.throw(str(put_data))
		res = api_controller.put_item(doc.custom_zoho_item_id, put_data)
		#frappe.throw(str(res))
		if res:
			if res.get('message') == "This item cannot be edited as it does not exist.":
				res2 = api_controller.post_item(data)
				#frappe.throw(str(res2))
				if res2:
					if res2.get('code') == 0:
						doc.custom_zoho_item_updated = 1
						doc.custom_zoho_item_id = res2.get('item').get('item_id')
						return res2
						#return doc.custom_zoho_item_id
						# returning this value for the add_item_to_zb function below (for bulk Items additions to Zoho)
					else:
						frappe.msgprint(res2.get("message"))

			elif res.get('code') == 0:
				doc.custom_zoho_item_updated = 1
				return res
			else:
				frappe.msgprint(res.get('message'))
		else:
			frappe.msgprint(str(res))
		#msg = "Zoho Books API Response: " + str(res)
		#frappe.msgprint(msg)


def delete_item_in_zoho(doc, method):
	# if frappe.defaults.get_user_default("company") not in ("Pour Tous Purchasing Service", "Pour Tous Distribution Center"):
	# 	frappe.throw("Please verify if Zoho Books API is enabled for this compamy")

	if doc.custom_zoho_item_id:
		api_controller = frappe.get_doc("Zoho Books API")
		res = api_controller.delete_item(doc.custom_zoho_item_id)
		if res:
			msg = "Zoho Books Response: " + res
			frappe.msgprint(msg)

@frappe.whitelist()
#def custom_delete_item_in_zoho(erp_item, custom_zoho_item_id):
def custom_delete_item_in_zoho(custom_zoho_item_id):
	# if frappe.defaults.get_user_default("company") not in ("Pour Tous Purchasing Service", "Pour Tous Distribution Center"):
	# 	frappe.throw("Please verify if Zoho Books API is enabled for this compamy")

	api_controller = frappe.get_doc("Zoho Books API")
	res = api_controller.delete_item(custom_zoho_item_id)
	if res == "The item has been deleted.":
		#frappe.db.set_value("Item", erp_item, "custom_zoho_item_updated", 0)
		return { "DELETED" }
	# elif res == "":
	# 	str_item = custom_zoho_item_id + 'Items which are a part of other transactions cannot be deleted. Instead, mark them as inactive.'
	# 	if os.path.exists('zb_item_to_update.txt'):
	# 		append_write = 'a' # append if already exists
	# 	else:
	# 		append_write = 'w' # make a new file if not
	# 	with open('zb_item_to_update.txt', append_write) as file:
	# 		file.write(str_item)
	else:
		frappe.msgprint(res)


@frappe.whitelist()
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

@frappe.whitelist()
def add_erp_item_in_zb(erp_item):
	doc = frappe.get_doc("Item", erp_item)
	custom_zoho_item_id = update_item_in_zoho(doc, method=None)
	if custom_zoho_item_id:
		doc.custom_zoho_item_id = custom_zoho_item_id
		doc.save()
		return { "ADDED" }


@frappe.whitelist()
def custom_fetch_erp_items_list():
	#return frappe.get_all('Supplier', filters = {"disabled": 0})
	return frappe.db.sql(
		"""
		SELECT name, custom_zoho_item_id FROM tabItem
		WHERE disabled = 0 AND custom_zoho_item_updated = 0
		AND custom_zoho_item_id IS NOT NULL
		""",
		as_dict=True
		# SELECT name, custom_zoho_item_id, gst_hsn_code FROM tabItem
	)

@frappe.whitelist()
def custom_fetch_erp_items_list_from_file():
	with open('Item_2.csv', newline='') as f:
		reader = csv.reader(f)
		#reader = csv.DictReader(f)
		item_ids_list_of_lists = list(reader)

	# with open('Item_2.json', mode='w', encoding='utf-8') as jsonfile:
	# 	json.dump(item_ids_list_of_lists, jsonfile, indent=4)

	# with open('Item_2.json', 'r') as file:
	# 	data = json.load(file)

	# json_str = json.dumps(data, indent=4)
	# dict = json.loads(json_str)

	item_ids_list = []

	for row in item_ids_list_of_lists:
		item_ids_list.extend(row)

	return item_ids_list


@frappe.whitelist()
def update_erp_item_in_zb(erp_item):
	doc = frappe.get_doc("Item", erp_item)
	res = update_item_in_zoho(doc, method=None)

	if res.get('item').get('item_id'):
		doc.custom_zoho_item_id = res.get('item').get('item_id')
		doc.save()
		return { "ADDED" }

	elif res.get("code") == 0:
		doc.save()
		return { "ADDED" }


@frappe.whitelist()
def custom_update_erp_item_in_zb(erp_item, custom_zoho_item_id):
#def custom_update_erp_item_in_zb(erp_item):
#def custom_update_erp_item_in_zb(custom_zoho_item_id):
	#item_code = frappe.get_value("Item", {"custom_zoho_item_id": custom_zoho_item_id}, "item_code")

	#if item_name:
	# doc = frappe.get_doc("Item", erp_item)

	# try:
	# 	zb_intra_tax_id = frappe.get_value("Item Tax Template", doc.taxes[0].item_tax_template, "custom_zoho_tax_group_id")
	# 	zb_inter_tax_id = frappe.get_value("Item Tax Template", doc.taxes[0].item_tax_template, "custom_zoho_tax_igst_id")

	# except Exception as err:
	# 	msg = "Please verify the Tax-template/ZB-tax_id for Item Code " + doc.item_code
	# 	frappe.msgprint(msg)
	# 	return

	# else:
	# 	put_data = {
	# 		"item_tax_preferences": [
	# 			{
	# 				"tax_id": zb_intra_tax_id,
	# 				"tax_specification": "intra",
	# 			},
	# 			{
	# 				"tax_id": zb_inter_tax_id,
	# 				"tax_specification": "inter",
	# 			},
	# 		],
	# 	}

	put_data = {
		'item_type': 'sales_and_purchases',
		'purchase_account_id': api_controller.expense_account_id,
		'purchase_account_name': api_controller.expense_account,
		'account_id': api_controller.income_account_id,
		'account_name': api_controller.income_account,
	}

	api_controller = frappe.get_doc("Zoho Books API")
	res = api_controller.put_item(custom_zoho_item_id, put_data)
	if res.get('code') == 0:
		#doc.custom_zoho_item_updated = 1
		frappe.db.set_value("Item", erp_item, "custom_zoho_item_updated", 1)
		return { "ADDED" }
	else:
		frappe.msgprint(res.get('message'))


@frappe.whitelist()
def get_zb_item_list():
	api_controller = frappe.get_doc("Zoho Books API")
	return api_controller.get_items()

@frappe.whitelist()
def get_an_item(item):
	api_controller = frappe.get_doc("Zoho Books API")
	return api_controller.get_an_item(item)

@frappe.whitelist()
def sync_zb_item_id_with_erp(item_id, item_name):
	if frappe.get_value("Item", item_name, "name"):
		existing_item_doc = frappe.get_doc("Item", item_name)
		existing_item_doc.custom_zoho_item_id = item_id
		existing_item_doc.save()
		return { "UPDATED" }


# @frappe.whitelist()
# def fetch_ptdc_erp_bills_list():
# 	return frappe.db.sql(
# 		# applying a posting_date filter, because for the month of April, accounts team has recorded the credit notes manually in ZB
# 		"""
# 		SELECT name FROM `tabPurchase Receipt` WHERE docstatus = 1
# 		AND is_return = 0 AND custom_zoho_bill_id IS NULL
# 		AND NOT (posting_date = "2025-04-02" AND owner = "Administrator")
# 		AND posting_date < "2025-06-01" AND name != "PR-25-00891"
# 		""",
# 		# applying a posting_date filter, because for the month of April, accounts team has recorded the credit notes manually in ZB
# 		as_dict=True
# 	)

# @frappe.whitelist()
# def fetch_ptdc_erp_debitnotes_list():
# 	return frappe.db.sql(
# 		# applying a posting_date filter, because for the month of April, accounts team has recorded the credit notes manually in ZB
# 		"""
# 		SELECT name FROM `tabPurchase Receipt` WHERE docstatus = 1
# 		AND is_return = 1 AND custom_zb_vendor_credit_id IS NULL
# 		AND posting_date < "2025-06-01"
# 		""",
# 		# applying a posting_date filter, because for the month of April, accounts team has recorded the credit notes manually in ZB
# 		as_dict=True
# 	)

""" @frappe.whitelist()
def add_ptdc_erp_bills_debitnotes_in_zoho(bill):
	bill_doc = frappe.get_doc("Purchase Receipt", bill)
	#bill_doc = frappe.get_doc("Purchase Invoice", bill)

	# Check if Supplier is Inter/Intra state

	contact_id = frappe.get_value("Supplier", bill_doc.supplier, "custom_zoho_contact_id")
	is_reverse_charge_applied = False # default value initialised here (context: GST-unregistered Vendors)

	if frappe.defaults.get_user_default("company") == "Pour Tous Purchasing Service":
		is_inclusive_tax = False
	else:
		is_inclusive_tax = True

	api_controller = frappe.get_doc("Zoho Books API")

	try:
		contact = api_controller.get_a_contact(contact_id)
		# r2.json().get('contact').get("tax_info_list")[0].get('place_of_supply')

		# check if tax info is available, i.e. whether the supplier GSTIN is updated
		if len(contact.get("tax_info_list")) > 0:
			if contact.get("tax_info_list")[0].get('place_of_supply') == 'TN':
				tax_specification = "intra"
			else:
				tax_specification = "inter"

			reference_invoice_type = "registered" # used in case of "Vendor Credits"

		# in case tax info is not available, i.e. in case the GSTIN of supplier is not updated:-
		else:
			tax_specification = "intra"
			is_reverse_charge_applied = True

			reference_invoice_type = "b2c_others" # used in case of "Vendor Credits"
			#with open('tax_info_list_empty.txt', 'w') as file:
			#	file.write(str(contact.get("tax_info_list")))

	except Exception as err:
		#with open('tax_info_list_exception_err.txt', 'w') as file:
		#	file.write(str(contact.get("tax_info_list")))
		frappe.msgprint(str(err))
		return

	line_items = []

	for item in bill_doc.items:
		item_doc = frappe.get_doc("Item", item.item_code)

		try:
			if is_reverse_charge_applied:
				if tax_specification == "intra":
					reverse_charge_tax_id = frappe.get_value("Item Tax Template", item_doc.taxes[0].item_tax_template, "custom_zoho_rcm_group_id")
				else:
					reverse_charge_tax_id = frappe.get_value("Item Tax Template", item_doc.taxes[0].item_tax_template, "custom_zoho_igst_rcm_id")
			else:
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
				"rate": float(item.price_list_rate),
				"quantity": abs(float(item.qty))
			}
			if is_reverse_charge_applied:
				line_item["reverse_charge_tax_id"] = reverse_charge_tax_id
				is_inclusive_tax = False
			else:
				line_item["tax_id"] = tax_id

			line_items.append(line_item)

	#frappe.throw(str(line_items))

	#if bill_doc.bill_date:
	#	date = bill_doc.bill_date.strftime(api_controller.DATE_FORMAT) # converting Date object to String
	#else:
	date = bill_doc.posting_date.strftime(api_controller.DATE_FORMAT) # converting Date object to String

	data = {
		'vendor_id': frappe.get_value("Supplier", bill_doc.supplier, "custom_zoho_contact_id"),
		#'bill_number': bill_doc.bill_no,
		'reference_number': bill_doc.name,
		'date': date,
		"is_inclusive_tax": is_inclusive_tax,
		"is_reverse_charge_applied": is_reverse_charge_applied,
		#'price_precision': 2,
		#'location_id': '2464766000000030367',
		"line_items": line_items
	}

	if bill_doc.is_return and bill_doc.custom_zb_vendor_credit_id == None:
		# ZB is asking for Bill number to return against.. hence skipping this section for now.
		#return
		#if bill_doc.bill_no:
		#	data["vendor_credit_number"] = bill_doc.bill_no # Supplier/Vendor Bill Number
		#else:
		data["vendor_credit_number"] = bill_doc.name[-16:] # ERPNext Bill Number
		
		data["reference_invoice_type"] = reference_invoice_type

		#frappe.throw(str(data))
		res = api_controller.post_vendor_credit(data)
		if res:
			bill_doc.custom_zb_vendor_credit_id = res
			bill_doc.save()
			frappe.db.commit()
			return { "ADDED" }

	elif bill_doc.custom_zoho_bill_id == None:
		#if bill_doc.bill_no:
		#	data["bill_number"] = bill_doc.bill_no # Supplier/Vendor Bill Number
		#else:
		data["bill_number"] = bill_doc.name[-16:] # ERPNext Bill Number

		#frappe.throw(str(data))
		if bill_doc.amended_from:
			#void_bill_id = frappe.get_value("Purchase Invoice", bill_doc.amended_from, "custom_zoho_void_bill_id")
			void_bill_id = frappe.get_value("Purchase Receipt", bill_doc.amended_from, "custom_zoho_void_bill_id")
			if void_bill_id:
				res = api_controller.delete_bill(void_bill_id)
				#frappe.throw(str(res))
				if res.get('code') != 0:
					frappe.msgprint(res.get("message"))

		res = api_controller.post_bill(data)
		if res:
			bill_doc.custom_zoho_bill_id = res
			bill_doc.save()
			frappe.db.commit()
			return { "ADDED" } """


@frappe.whitelist()
def fetch_erp_bills_list():
	frappe.db.delete("Zoho Sync Err Logs") # deletes the old logs

	return frappe.db.sql(
		# applying a posting_date filter, because for the month of April, accounts team has recorded the credit notes manually in ZB
		"""
		SELECT name FROM `tabPurchase Invoice` WHERE docstatus = 1
		AND is_return = 0 AND custom_zoho_bill_id IS NULL
		AND posting_date >= "2025-06-01"
		""",
		# applying a posting_date filter, because for the month of April, accounts team has recorded the credit notes manually in ZB
		as_dict=True
	)

@frappe.whitelist()
def fetch_erp_debitnotes_list():
	frappe.db.delete("Zoho Sync Err Logs") # deletes the old logs

	if frappe.defaults.get_user_default("company") == "Pour Tous Purchasing Service":
		return frappe.db.sql(
			# applying a posting_date filter, because for the month of April, accounts team has recorded the credit notes manually in ZB
			"""
			SELECT name FROM `tabPurchase Invoice` WHERE docstatus = 1
			AND is_return = 1 AND custom_zb_vendor_credit_id IS NULL
			AND posting_date >= "2025-05-01"
			""",
			# applying a posting_date filter, because for the month of April, accounts team has recorded the credit notes manually in ZB
			as_dict=True
		)

	else:
		return frappe.db.sql(
			# applying a posting_date filter, because for the month of April, accounts team has recorded the credit notes manually in ZB
			"""
			SELECT name FROM `tabPurchase Invoice` WHERE docstatus = 1
			AND is_return = 1 AND custom_zb_vendor_credit_id IS NULL
			AND posting_date >= "2025-06-01"
			""",
			# applying a posting_date filter, because for the month of April, accounts team has recorded the credit notes manually in ZB
			as_dict=True
		)

@frappe.whitelist()
def add_erp_bills_debitnotes_in_zoho(bill):
	#bill_doc = frappe.get_doc("Purchase Receipt", bill)
	bill_doc = frappe.get_doc("Purchase Invoice", bill)

	group_supplier = frappe.get_value("Supplier", {
		"custom_group_supplier": 1,
		"supplier_group": frappe.get_value("Supplier", bill_doc.supplier, "supplier_group")
	}, "name")

	if group_supplier:
		supplier = group_supplier
	else:
		supplier = bill_doc.supplier

	# Check if Supplier is Inter/Intra state

	contact_id = frappe.get_value("Supplier", supplier, "custom_zoho_contact_id")
	is_reverse_charge_applied = False # default value initialised here (context: GST-unregistered Vendors)

	# for better design: need to fetch the is_inclusive_tax from the settings in the ERP tax table
	# if frappe.defaults.get_user_default("company") == "Pour Tous Purchasing Service":
	# 	is_inclusive_tax = False
	# else:
	# 	is_inclusive_tax = True

	if bill_doc.taxes:
		is_inclusive_tax = True if bill_doc.taxes[0].included_in_print_rate else False

	api_controller = frappe.get_doc("Zoho Books API")

	try:
		contact = api_controller.get_a_contact(contact_id)
		# r2.json().get('contact').get("tax_info_list")[0].get('place_of_supply')

		# check if tax info is available, i.e. whether the supplier GSTIN is updated
		if len(contact.get("tax_info_list")) > 0:
			if contact.get("tax_info_list")[0].get('place_of_supply') == 'TN':
				tax_specification = "intra"
			else:
				tax_specification = "inter"

			reference_invoice_type = "registered" # used in case of "Vendor Credits"

		# in case tax info is not available, i.e. in case the GSTIN of supplier is not updated:-
		else:
			tax_specification = "intra"
			is_reverse_charge_applied = True

			reference_invoice_type = "b2c_others" # used in case of "Vendor Credits"
			#with open('tax_info_list_empty.txt', 'w') as file:
			#	file.write(str(contact.get("tax_info_list")))

	except Exception as err:
		#with open('tax_info_list_exception_err.txt', 'w') as file:
		#	file.write(str(contact.get("tax_info_list")))
		frappe.msgprint(str(err))
		return

	line_items = []

	for item in bill_doc.items:
		item_doc = frappe.get_doc("Item", item.item_code)

		try:
			if len(item_doc.taxes) > 1: # in case the item tax table has more than one tax to choose from
				item_tax_template = item.item_tax_template # choose the tax that was recorded for the Invoice Item
			else:
				item_tax_template = item_doc.taxes[0].item_tax_template

			if is_reverse_charge_applied:
				if tax_specification == "intra":
					reverse_charge_tax_id = frappe.get_value("Item Tax Template", item_tax_template, "custom_zoho_rcm_group_id")
				else: # for "inter"
					reverse_charge_tax_id = frappe.get_value("Item Tax Template", item_tax_template, "custom_zoho_igst_rcm_id")
			else:
				if tax_specification == "intra":
					tax_id = frappe.get_value("Item Tax Template", item_tax_template, "custom_zoho_tax_group_id")
				else: # for "inter"
					tax_id = frappe.get_value("Item Tax Template", item_tax_template, "custom_zoho_tax_igst_id")
		except Exception as err:
			frappe.msgprint(str(err))
			msg = "Please verify the Tax-template/Supplier/ZB-tax_id for Item Code " + item.item_code
			frappe.msgprint(msg)
			return

		else:
			line_item = {
				"item_id": frappe.get_value("Item", item.item_code, "custom_zoho_item_id"),
				"rate": float(item.rate),
				"quantity": abs(float(item.qty))
			}
			if is_reverse_charge_applied:
				line_item["reverse_charge_tax_id"] = reverse_charge_tax_id
				is_inclusive_tax = False
			else:
				line_item["tax_id"] = tax_id

			line_items.append(line_item)

	if bill_doc.bill_date:
		date = bill_doc.bill_date.strftime(api_controller.DATE_FORMAT) # converting Date object to String
	else:
		date = bill_doc.posting_date.strftime(api_controller.DATE_FORMAT) # converting Date object to String

	data = {
		'vendor_id': contact_id,
		#'bill_number': bill_doc.bill_no,
		'reference_number': bill_doc.name,
		'date': date,
		#"is_inclusive_tax": is_inclusive_tax,
		"is_reverse_charge_applied": is_reverse_charge_applied,
		#'price_precision': 2,
		#'location_id': api_controller.location_id,
		"line_items": line_items
	}

	if api_controller.location_id:
		data['location_id'] = api_controller.location_id
	
	if bill_doc.taxes:
		data['is_inclusive_tax'] = is_inclusive_tax

	if bill_doc.is_return and bill_doc.custom_zb_vendor_credit_id == None:
		if bill_doc.bill_no:
			data["vendor_credit_number"] = bill_doc.bill_no[:16] # Supplier/Vendor Bill Number
		else:
			data["vendor_credit_number"] = bill_doc.name[-16:] # ERPNext Bill Number

		data["reference_invoice_type"] = reference_invoice_type

		#frappe.throw(str(data))

		zb_vendor_credit_id = None

		res = api_controller.post_vendor_credit(data)
		if "vendor_credit_id" in res:
			zb_vendor_credit_id = res.get('vendor_credit_id')

		elif res.get('message') == 'The vendor credit# specified already exists.':
			res2 = api_controller.query_vendor_credit(data["vendor_credit_number"], data['reference_number'])
			if res2:
				#frappe.throw(res2[0].get("bill_id"))
				zb_vendor_credit_id = res2[0].get("vendor_credit_id")

		if zb_vendor_credit_id is not None:
			bill_doc.custom_zb_vendor_credit_id = zb_vendor_credit_id
			bill_doc.save()
			frappe.db.commit()
			return { "ADDED" }


		else :
			data["vendor_credit_number"] = bill_doc.name[-16:] # Supplier/ERP Bill Number invoice[-16:]
			res3 = api_controller.post_vendor_credit(data)

			if "vendor_credit_id" in res3:
				zb_vendor_credit_id = res3.get('vendor_credit_id')
				bill_doc.custom_zb_vendor_credit_id = zb_vendor_credit_id
				bill_doc.save()
				frappe.db.commit()
				return { "ADDED" }

			else:
				error_log = frappe.new_doc("Zoho Sync Err Logs")
				error_log.document_name = data["vendor_credit_number"]
				error_log.error = str(res3.json())
				error_log.insert()

				frappe.msgprint(res3.json().get('message'))


	elif bill_doc.custom_zoho_bill_id == None:
		if bill_doc.bill_no:
			data["bill_number"] = bill_doc.bill_no[:16] # Supplier/Vendor Bill Number
		else:
			data["bill_number"] = bill_doc.name[-16:] # Supplier/ERP Bill Number invoice[-16:]

		#frappe.throw(str(data))
		if bill_doc.amended_from:
			void_bill_id = frappe.get_value("Purchase Invoice", bill_doc.amended_from, "custom_zoho_void_bill_id")
			if void_bill_id:
				res = api_controller.delete_bill(void_bill_id)
				#frappe.throw(str(res))
				if res.get('code') != 0:
					frappe.msgprint(res.get("message"))

		zb_bill_id = None

		res = api_controller.post_bill(data)
		if "bill_id" in res:
			zb_bill_id = res.get('bill_id')

		elif res.get('message') == 'A bill with this number has already been created for this vendor. Please check and try again.':
			res2 = api_controller.query_bill(data["bill_number"], data["reference_number"])
			#frappe.throw(str(res2))
			if res2:
				#frappe.throw(res2[0].get("bill_id"))
				zb_bill_id = res2[0].get("bill_id")

		if zb_bill_id is not None:
			bill_doc.custom_zoho_bill_id = zb_bill_id
			bill_doc.save()
			frappe.db.commit()
			return { "ADDED" }

		else:
			data["bill_number"] = bill_doc.name[-16:] # Supplier/ERP Bill Number invoice[-16:]
			res3 = api_controller.post_bill(data)

			if "bill_id" in res3:
				zb_bill_id = res3.get('bill_id')
				bill_doc.custom_zoho_bill_id = zb_bill_id
				bill_doc.save()
				frappe.db.commit()
				return { "ADDED" }

			else:
				error_log = frappe.new_doc("Zoho Sync Err Logs")
				error_log.document_name = data["bill_number"]
				error_log.error = str(res3)
				error_log.insert()

				frappe.msgprint(str(res3))


@frappe.whitelist()
def fetch_unsynced_erp_return_invoice_list():
	if frappe.defaults.get_user_default("company") == "Auroville Bakery":
		return frappe.db.sql(
			"""
			SELECT name, customer, docstatus, status FROM `tabSales Invoice`
			WHERE docstatus = 1 AND status = "Return"
			AND posting_date >= "2025-11-01"
			AND custom_zb_creditnote_id IS NULL
			""",
			as_dict=True
		)

	elif frappe.defaults.get_user_default("company") in (
		"AV Bakery Cafe", "AV Bakery Cafe Townhall"
	):
		return frappe.db.sql(
			"""
			SELECT name, customer, docstatus, status FROM `tabSales Invoice`
			WHERE docstatus = 1 AND status = "Return"
			AND posting_date >= "2025-10-01"
			AND custom_zb_creditnote_id IS NULL
			""",
			as_dict=True
		)

	else:
		return frappe.db.sql(
			"""
			SELECT name, customer, docstatus, status FROM `tabSales Invoice`
			WHERE docstatus = 1 AND status = "Return"
			AND custom_zb_creditnote_id IS NULL
			""",
			as_dict=True
		)
		# AND status IN ('Paid', 'Credit Note Issued', 'Return')
		# AND custom_fs_account_number IS NOT NULL
		# AND posting_date BETWEEN "2025-04-01" AND "2025-04-30"
		# AND (custom_zb_creditnote_id IS NULL OR custom_zb_creditnote_refund_id IS NULL)


@frappe.whitelist()
def sync_return_inv_with_zoho_books(invoice, customer):
	api_controller = frappe.get_doc("Zoho Books API")
	invoice_doc = frappe.get_doc("Sales Invoice", invoice)

	if invoice_doc.taxes:
		is_inclusive_tax = True if invoice_doc.taxes[0].included_in_print_rate else False

	if frappe.get_value("Customer", customer, "customer_type") == "Company":
		fs_customer_id = frappe.get_value("Customer", customer, "custom_zoho_contact_id")
	else:
		fs_customer_id = api_controller.walk_in_fs_contact_id


	date = invoice_doc.posting_date.strftime(api_controller.DATE_FORMAT) # converting Date object to String

	#customer_group = frappe.get_value("Customer", invoice_doc.customer, "customer_group")

	# Flow for: registering Paid Invoices and their Payments in ZB; registering Credit Notes and their Credit Note Refunds
	if invoice_doc.custom_zb_creditnote_id == None:
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
					"name": item.item_name,
					#"description": item.item_name,
					"rate": float(item.rate),
					"quantity": abs(float(item.qty)), # ERPNext uses negative values in returns
					"tax_id": tax_id
				}
				line_items.append(line_item)

		creditnote_data = {}
		zb_inv_id = None

		if invoice_doc.custom_fs_account_number:
			creditnote_data = {
				'customer_id': fs_customer_id, # "FS Account Customers" in ZB
				'creditnote_number': invoice,
				'date': date,
				#'location_id': api_controller.location_id,
				#"is_inclusive_tax": is_inclusive_tax,
				"custom_fields": [
					{
						"index": 1,
						"label": "cf_fs_account_number",
						"value": invoice_doc.custom_fs_account_number,
						"data_type": "text"
					}
				],
				"line_items": line_items,
				#"invoice_id": zb_inv_id
			}

		#elif customer_group == "Aurocard Payments":
		elif invoice_doc.payments[0].mode_of_payment == "Aurocard":
			creditnote_data = {
				'customer_id': api_controller.walk_in_aurocard_contact_id, # "Aurocard Customers" in ZB
				'creditnote_number': invoice,
				'date': date,
				#'location_id': api_controller.location_id,
				#"is_inclusive_tax": is_inclusive_tax,
				"custom_fields": [
					{
						"index": 2,
						"label": "cf_aurocard_number",
						"value": invoice_doc.customer_name,
						"data_type": "text"
					}
				],
				"line_items": line_items,
				#"invoice_id": zb_inv_id
			}

		#elif customer_group == "UPI Payments":
		elif invoice_doc.payments[0].mode_of_payment in ("UPI", "ICICI UPI"):
			creditnote_data = {
				'customer_id': api_controller.walk_in_upi_contact_id, # "UPI Customers" in ZB
				'creditnote_number': invoice,
				'date': date,
				#'location_id': api_controller.location_id,
				#"is_inclusive_tax": is_inclusive_tax,
				"custom_fields": [
					{
						"index": 3,
						"label": "cf_upi_transaction_id",
						"value": invoice_doc.custom_upi_transaction_id,
						"data_type": "text"
					}
				],
				"line_items": line_items,
				#"invoice_id": zb_inv_id
			}

		#elif customer_group == "Card Payments":
		elif invoice_doc.payments[0].mode_of_payment in ("Cards", "RuPay"):
			creditnote_data = {
				'customer_id': api_controller.walk_in_card_contact_id, # "UPI Customers" in ZB
				'creditnote_number': invoice,
				'date': date,
				#'location_id': api_controller.location_id,
				#"is_inclusive_tax": is_inclusive_tax,
				"custom_fields": [
					{
						"index": 4,
						"label": "cf_card_transaction_id",
						"value": invoice_doc.custom_card_transaction_id,
						"data_type": "text"
					}
				],
				"line_items": line_items,
				#"invoice_id": zb_inv_id
			}

		#elif customer_group == "Cash Payments":
		elif invoice_doc.payments[0].mode_of_payment == "Cash":
			creditnote_data = {
				'customer_id': api_controller.walk_in_cash_contact_id, # "Cash Customers" in ZB
				'creditnote_number': invoice,
				'date': date,
				#'location_id': api_controller.location_id,
				#"is_inclusive_tax": is_inclusive_tax,
				"line_items": line_items,
				#"invoice_id": zb_inv_id
			}

		if api_controller.location_id:
			creditnote_data['location_id'] = api_controller.location_id

		if invoice_doc.taxes:
			creditnote_data['is_inclusive_tax'] = is_inclusive_tax

		# for Returns
		zb_inv_id = frappe.get_value("Sales Invoice", invoice_doc.return_against, "custom_zoho_invoice_id")
		if not zb_inv_id:
			frappe.msgprint("Return Invoice '{0}' does not have a ZB Invoice ID".format(invoice_doc.name))
			creditnote_data["reference_invoice_type"] = "b2c_others"
			creditnote_data["reference_number"] = invoice_doc.return_against
		
		else:
			creditnote_data['invoice_id'] = zb_inv_id

			# making a recursive call to push to ZB, the Invoices with a status of "Credit Note Issued",
			# in case the invoice does not have a ZB Invoice ID
			""" res = sync_fs_inv_with_zoho_books(invoice_doc.return_against)
			if res != "ADDED":
				frappe.msgprint("Return Invoice '{0}' does not have a ZB Invoice ID".format(invoice_doc.name))
				return """

		#frappe.throw(str(creditnote_data))
		res = api_controller.post_creditnote(creditnote_data)
		if res:
			invoice_doc.custom_zb_creditnote_id = res.get('creditnote_id')
			invoice_doc.save()
			frappe.db.commit()

			return "ADDED"


## WIP ## PTDC Consolidated Invoices push to ZB
@frappe.whitelist()
def sync_pt_consol_inv_with_zb(consol_inv_pt_account, line_items_dict, date, is_return):
	erp_line_items = json.loads(line_items_dict)
	#frappe.throw(str(erp_line_items))
	#frappe.throw(str(erp_line_items[0]))

	api_controller = frappe.get_doc("Zoho Books API")
	#invoice_doc = frappe.get_doc("Sales Invoice", invoice)

	customer = frappe.get_value("Customer", {"custom_fs_account_number": consol_inv_pt_account}, "name")
	customer_doc = frappe.get_doc("Customer", customer)

	company = frappe.defaults.get_user_default("company")

	#if customer_doc.customer_group == "Special Case" and customer_doc.customer_type != "Company":
	if customer_doc.customer_group == "Internal":
		return
		# "Internal" participants are PT internal accounts
		# returning for now, as need to understand how to account for these stock movements

	if customer_doc.customer_type == "Company":
		#customer_id = frappe.get_value("Customer", {"custom_fs_account_number": consol_inv_pt_account}, "custom_zoho_contact_id")
		customer_id = customer_doc.custom_zoho_contact_id
	else:
		customer_id = api_controller.walk_in_fs_contact_id  # get the "PT Account Customers" in PTDC ZB
		#customer_id = 2407242000000343009  # get the "PT Account Customers" in PTDC ZB

	#date = invoice_doc.posting_date.strftime(api_controller.DATE_FORMAT) # converting Date object to String
	#date = nowdate()

	taxable = True
	if frappe.db.get_value("Company", company, "gstin"):
		if customer_doc.gstin == frappe.db.get_value("Company", company, "gstin"):
			taxable = False

	if taxable:
		settings_doc = frappe.get_doc("Accounts Settings")
		is_inclusive_tax = True if settings_doc.show_inclusive_tax_in_print else False

	line_items = []

	for item in erp_line_items:
		item_doc = frappe.get_doc("Item", item.get("item_code"))

		if taxable:
			try:
				tax_id = frappe.get_value("Item Tax Template", item_doc.taxes[0].item_tax_template, "custom_zoho_tax_group_id")
			except Exception as err:
				frappe.msgprint(str(err))
				msg = "Please verify the Tax-template/ZB-tax_id for Item Code " + item.get("item_code")
				frappe.msgprint(msg)
				return

			else:
				line_item = {
					"item_id": item_doc.custom_zoho_item_id,
					"name": item.get("item_name"),
					"rate": float(item.get("rate")),
					"quantity": abs(float(item.get("qty"))), # abs used, as section used for returns as well
					"tax_id": tax_id
				}
				line_items.append(line_item)

		else:
			line_item = {
				"item_id": item_doc.custom_zoho_item_id,
				"name": item.get("item_name"),
				"rate": float(item.get("rate")),
				"quantity": abs(float(item.get("qty"))), # abs used, as section used for returns as well
				'gst_treatment_code': 'out_of_scope'
			}
			line_items.append(line_item)

	data = {
		'customer_id': customer_id,
		#'invoice_number': consol_inv_pt_account+"--"+date[2:],
		'date': date,
		#"is_inclusive_tax": is_inclusive_tax,
		#'location_id': api_controller.location_id,
		#'price_precision': 2,
		"custom_fields": [
			{
				"index": 1,
				"label": "cf_pt_account_number",
				"value": consol_inv_pt_account,
				"data_type": "text"
			}
		],
		"line_items": line_items
	}

	if api_controller.location_id:
		data['location_id'] = api_controller.location_id

	if taxable:
		data['is_inclusive_tax'] = is_inclusive_tax

	#frappe.throw(str(data))

	if is_return == '1': # the value comes as a string
		data["creditnote_number"] = consol_inv_pt_account+"-RT-"+date[5:]

		if customer_doc.gst_category == "Registered Regular":
			data["reference_invoice_type"] = "registered" # used when not referring to a return doc
		else:
			data["reference_invoice_type"] = "b2c_others" # used when not referring to a return doc

		res = api_controller.post_creditnote(data)

		if res.get("message") == "Credit note "+data["creditnote_number"]+" already exists":
			res2 = api_controller.query_credit_note(data["creditnote_number"])
			if res2:
				custom_zb_consol_creditnote_id = res2[0].get("creditnote_id")
		elif res.get('creditnote_id'):
			custom_zb_consol_creditnote_id = res.get('creditnote_id')

		if custom_zb_consol_creditnote_id:
			last_invoice = ""
			for line in erp_line_items:
				if line.get("name") != last_invoice:
					frappe.db.set_value("Sales Invoice", line.get("name"), "custom_zb_consol_creditnote_id", custom_zb_consol_creditnote_id)
					frappe.db.commit()
				last_invoice = line.get("name")

			return "ADDED"

	else:
		data["invoice_number"] = consol_inv_pt_account+"--"+date[2:]

		#frappe.throw(str(data))

		res = api_controller.post_invoice(data)
		#frappe.throw(res.get("message"))

		custom_zb_consol_inv_id = None

		if res.get("message") == ("Invoice "+data["invoice_number"]+" already exists"):
			amended_from = frappe.db.get_value("Sales Invoice", erp_line_items[0].get("name"), "amended_from")
			if amended_from and not frappe.db.get_value("Sales Invoice", amended_from, "custom_fs_account_number"):
				# Checking if this Invoice was amended to add the missing FS account number
				data["invoice_number"] = consol_inv_pt_account+"/"+date[5:]+"/"+str(random.randint(100,999))
				# generating a unique "invoice number"
				res3 = api_controller.post_invoice(data)

				if res3.get('invoice_id'):
					custom_zb_consol_inv_id = res3.get('invoice_id')

			else:
				res2 = api_controller.query_invoice(data["invoice_number"])
				if res2:
					custom_zb_consol_inv_id = res2[0].get("invoice_id")

		elif res.get('invoice_id'):
			custom_zb_consol_inv_id = res.get('invoice_id')

		if custom_zb_consol_inv_id:
			last_invoice = ""
			for line in erp_line_items:
				if line.get("name") != last_invoice:
					frappe.db.set_value("Sales Invoice", line.get("name"), "custom_zb_consol_inv_id", custom_zb_consol_inv_id)
					frappe.db.commit()
				last_invoice = line.get("name")

			res3 = api_controller.mark_invoice_as_sent(custom_zb_consol_inv_id)
			if res3 == "Invoice status has been changed to Sent.":
				return "ADDED"


@frappe.whitelist()
def fetch_unsynced_erp_fs_invoice_list():
	if frappe.defaults.get_user_default("company") == "Auroville Bakery":
		return frappe.db.sql(
			"""
			SELECT name, customer, custom_fs_account_number, docstatus, status FROM `tabSales Invoice`
			WHERE docstatus = 1 AND status IN ('Paid', 'Submitted', 'Unpaid', 'Overdue', 'Credit Note Issued')
			AND posting_date >= "2025-11-01"
			AND custom_fs_account_number IS NOT NULL
			AND custom_zoho_invoice_id IS NULL
			""",
			as_dict=True
		)

	elif frappe.defaults.get_user_default("company") in (
		"AV Bakery Cafe", "AV Bakery Cafe Townhall"
	):
		return frappe.db.sql(
			"""
			SELECT name, customer, custom_fs_account_number, docstatus, status FROM `tabSales Invoice`
			WHERE docstatus = 1 AND status IN ('Paid', 'Submitted', 'Unpaid', 'Overdue', 'Credit Note Issued')
			AND posting_date >= "2025-10-01"
			AND custom_fs_account_number IS NOT NULL
			AND custom_zoho_invoice_id IS NULL
			""",
			as_dict=True
		)

	else:
		return frappe.db.sql(
			"""
			SELECT name, customer, custom_fs_account_number, docstatus, status FROM `tabSales Invoice`
			WHERE docstatus = 1 AND status IN ('Paid', 'Submitted', 'Unpaid', 'Overdue', 'Credit Note Issued')
			AND custom_fs_account_number IS NOT NULL
			AND custom_zoho_invoice_id IS NULL
			""",
			as_dict=True
		)
			# AND posting_date BETWEEN "2025-04-01" AND "2025-04-30"
			# AND (custom_zoho_invoice_id IS NULL OR custom_zoho_payment_id IS NULL)
			# AND status IN ('Paid', 'Credit Note Issued', 'Return')


@frappe.whitelist()
def sync_fs_inv_with_zoho_books(invoice, customer):
	api_controller = frappe.get_doc("Zoho Books API")
	invoice_doc = frappe.get_doc("Sales Invoice", invoice)
	if frappe.get_value("Customer", customer, "customer_type") == "Company":
		customer_id = frappe.get_value("Customer", customer, "custom_zoho_contact_id")
	else:
		customer_id = api_controller.walk_in_fs_contact_id		


	date = invoice_doc.posting_date.strftime(api_controller.DATE_FORMAT) # converting Date object to String

	if invoice_doc.custom_zoho_invoice_id == None:
		line_items = []

		for item in invoice_doc.items:
			item_doc = frappe.get_doc("Item", item.item_code)

			if invoice_doc.taxes:
				is_inclusive_tax = True if invoice_doc.taxes[0].included_in_print_rate else False

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
						"name": item.item_name,
						#"description": item.item_name,
						"rate": float(item.rate),
						"quantity": float(item.qty),
						"tax_id": tax_id
					}
					line_items.append(line_item)

			else:
				line_item = {
					"item_id": item_doc.custom_zoho_item_id,
					"name": item.item_name,
					#"description": item.item_name,
					"rate": float(item.rate),
					"quantity": float(item.qty),
					'gst_treatment_code': 'out_of_scope'
				}
				line_items.append(line_item)

		#if not invoice_doc.is_return:
		invoice_data = {
			'customer_id': customer_id,
			'invoice_number': invoice[-16:],
			'date': date,
			#'location_id': api_controller.location_id,
			#"is_inclusive_tax": is_inclusive_tax,
			#'price_precision': 2,
			"custom_fields": [
				{
					"index": 1,
					"label": "cf_fs_account_number",
					"value": invoice_doc.custom_fs_account_number,
					"data_type": "text"
				}
			],
			"line_items": line_items,
		}

		if invoice_doc.taxes:
			invoice_data['is_inclusive_tax'] = is_inclusive_tax

		if api_controller.location_id:
			invoice_data['location_id'] = api_controller.location_id

		# adding delivery charge if any
		if invoice_doc.posa_delivery_charges:
			for row in invoice_doc.taxes: # searching in the "Taxes and Charges" table
				if row.gst_tax_type == None:
					invoice_data["shipping_charge"] = row.tax_amount

		#frappe.throw(str(invoice_data))
		if invoice_doc.amended_from:
			void_invoice_id = frappe.get_value("Sales Invoice", invoice_doc.amended_from, "custom_zoho_void_invoice_id")
			if void_invoice_id:
				res = api_controller.delete_invoice(void_invoice_id)
				#frappe.throw(str(res))
				if res.get('code') != 0:
					frappe.msgprint(res.get("message"))

		res = api_controller.post_invoice(invoice_data)

		zb_invoice_id = None

		if "invoice_id" in res:
			zb_invoice_id = res.get('invoice_id')

		elif res.get("message") == ("Invoice "+invoice_data["invoice_number"]+" already exists"):
			res2 = api_controller.query_invoice(invoice_data["invoice_number"])
			#frappe.throw(str(res2))
			if res2:
				#frappe.throw(res2[0].get("invoice_id"))
				zb_invoice_id = res2[0].get("invoice_id")

		else:
			frappe.throw(str(res))

		#if "invoice_id" in res:
		if zb_invoice_id is not None:
			#zb_invoice_id = res.get('invoice_id')
			invoice_doc.custom_zoho_invoice_id = zb_invoice_id
			invoice_doc.save()
			frappe.db.commit()

			res2 = api_controller.mark_invoice_as_sent(zb_invoice_id)
			if res2 == "Invoice status has been changed to Sent.":
				return "ADDED"


@frappe.whitelist()
def fetch_unsynced_erp_adv_payment_invoice_list():
	if frappe.defaults.get_user_default("company") in "Auroville Bakery":
		return frappe.db.sql(
			"""
			SELECT si.name, si.customer, si.posting_date, si.custom_fs_account_number, si.docstatus, si.status
			FROM `tabSales Invoice` si, `tabSales Invoice Advance` sia
			WHERE si.docstatus = 1
			AND posting_date >= "2025-11-01"
			AND si.status IN ('Paid', 'Submitted', 'Unpaid', 'Overdue', 'Credit Note Issued')
			AND si.grand_total = si.total_advance
			AND si.custom_fs_account_number IS NULL
			AND si.custom_zoho_invoice_id IS NULL
			group by si.name;
			""",
			as_dict=True
		)

	elif frappe.defaults.get_user_default("company") in (
		"AV Bakery Cafe", "AV Bakery Cafe Townhall"
	):
		return frappe.db.sql(
			"""
			SELECT si.name, si.customer, si.posting_date, si.custom_fs_account_number, si.docstatus, si.status
			FROM `tabSales Invoice` si, `tabSales Invoice Advance` sia
			WHERE si.docstatus = 1
			AND posting_date >= "2025-10-01"
			AND si.status IN ('Paid', 'Submitted', 'Unpaid', 'Overdue', 'Credit Note Issued')
			AND si.grand_total = si.total_advance
			AND si.custom_fs_account_number IS NULL
			AND si.custom_zoho_invoice_id IS NULL
			group by si.name;
			""",
			as_dict=True
		)

	else:
		return frappe.db.sql(
			"""
			SELECT si.name, si.customer, si.posting_date, si.custom_fs_account_number, si.docstatus, si.status
			FROM `tabSales Invoice` si, `tabSales Invoice Advance` sia
			WHERE si.docstatus = 1
			AND si.status IN ('Paid', 'Submitted', 'Unpaid', 'Overdue', 'Credit Note Issued')
			AND si.grand_total = si.total_advance
			AND si.custom_fs_account_number IS NULL
			AND si.custom_zoho_invoice_id IS NULL
			group by si.name;
			""",
			as_dict=True
		)

@frappe.whitelist()
def sync_adv_payment_inv_with_zoho_books(invoice, customer):
	api_controller = frappe.get_doc("Zoho Books API")
	invoice_doc = frappe.get_doc("Sales Invoice", invoice)

	fs_account_number = frappe.get_value("Customer", customer, "custom_fs_account_number")
	#customer_group = frappe.get_value("Customer", customer, "customer_group")

	if frappe.get_value("Customer", customer, "customer_type") == "Company":
		customer_id = frappe.get_value("Customer", customer, "custom_zoho_contact_id")
	elif fs_account_number:
		customer_id = api_controller.walk_in_fs_contact_id

	elif invoice_doc.payments[0].mode_of_payment == "Aurocard":
		customer_id = api_controller.walk_in_aurocard_contact_id # AVB "Aurocard Customers" in ZB
	#elif customer_group == "UPI Payments":
	elif invoice_doc.payments[0].mode_of_payment in ("UPI", "ICICI UPI"):
		customer_id = api_controller.walk_in_upi_contact_id # AVB "UPI Customers" in ZB
	#elif customer_group == "Cash Payments":
	elif invoice_doc.payments[0].mode_of_payment == "Cash":
		customer_id = api_controller.walk_in_cash_contact_id # AVB "Cash Customers" in ZB
	#elif customer_group == "Card Payments":
	elif invoice_doc.payments[0].mode_of_payment == "Cards":
		customer_id = api_controller.walk_in_card_contact_id # AVB "Card Customers" in ZB


	date = invoice_doc.posting_date.strftime(api_controller.DATE_FORMAT) # converting Date object to String

	if invoice_doc.custom_zoho_invoice_id == None:
		line_items = []

		for item in invoice_doc.items:
			item_doc = frappe.get_doc("Item", item.item_code)

			if invoice_doc.taxes:
				is_inclusive_tax = True if invoice_doc.taxes[0].included_in_print_rate else False

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
						"name": item.item_name,
						#"description": item.item_name,
						"rate": float(item.rate),
						"quantity": float(item.qty),
						"tax_id": tax_id
					}
					line_items.append(line_item)

			else:
				line_item = {
					"item_id": item_doc.custom_zoho_item_id,
					"name": item.item_name,
					#"description": item.item_name,
					"rate": float(item.rate),
					"quantity": float(item.qty),
					'gst_treatment_code': 'out_of_scope'
				}
				line_items.append(line_item)


		invoice_data = {
			'customer_id': customer_id,
			'invoice_number': invoice[-16:],
			'date': date,
			#'location_id': api_controller.location_id,
			#"is_inclusive_tax": is_inclusive_tax,
			#'price_precision': 2,
			"line_items": line_items,
		}

		if invoice_doc.taxes:
			invoice_data['is_inclusive_tax'] = is_inclusive_tax

		if api_controller.location_id:
			invoice_data['location_id'] = api_controller.location_id

		if fs_account_number:
			invoice_data["custom_fields"] = [
				{
					"index": 1,
					"label": "cf_fs_account_number",
					"value": fs_account_number,
					"data_type": "text"
				}
			]

		#elif customer_group == "Aurocard Payments":
		elif invoice_doc.payments[0].mode_of_payment == "Aurocard":
			invoice_data["custom_fields"] = [
					{
						"index": 2,
						"label": "cf_aurocard_number",
						"value": invoice_doc.customer_name,
						"data_type": "text"
					}
				]

		elif invoice_doc.payments[0].mode_of_payment in ("UPI", "ICICI UPI"):
			invoice_data["custom_fields"] = [
					{
						"index": 3,
						"label": "cf_upi_transaction_id",
						"value": invoice_doc.custom_upi_transaction_id,
						"data_type": "text"
					}
				]

		elif invoice_doc.payments[0].mode_of_payment in ("Cards", "RuPay"):
			invoice_data["custom_fields"] = [
					{
						"index": 4,
						"label": "cf_card_transaction_id",
						"value": invoice_doc.custom_card_transaction_id,
						"data_type": "text"
					}
				]

		# adding delivery charge if any
		if invoice_doc.posa_delivery_charges:
			for row in invoice_doc.taxes: # searching in the "Taxes and Charges" table
				if row.gst_tax_type == None:
					invoice_data["shipping_charge"] = row.tax_amount

		#frappe.throw(str(invoice_data))
		if invoice_doc.amended_from:
			void_invoice_id = frappe.get_value("Sales Invoice", invoice_doc.amended_from, "custom_zoho_void_invoice_id")
			if void_invoice_id:
				res = api_controller.delete_invoice(void_invoice_id)
				#frappe.throw(str(res))
				if res.get('code') != 0:
					frappe.msgprint(res.get("message"))

		res = api_controller.post_invoice(invoice_data)

		if "invoice_id" in res:
			zb_invoice_id = res.get('invoice_id')

		elif res.get("message") == ("Invoice "+invoice_data["invoice_number"]+" already exists"):
			res2 = api_controller.query_invoice(invoice_data["invoice_number"])
			#frappe.throw(str(res2))
			if res2:
				#frappe.throw(res2[0].get("invoice_id"))
				zb_invoice_id = res2[0].get("invoice_id")

		else:
			frappe.throw(res.get("message"))

		#if "invoice_id" in res:
		if zb_invoice_id:
			#zb_invoice_id = res.get('invoice_id')
			invoice_doc.custom_zoho_invoice_id = zb_invoice_id
			invoice_doc.save()
			frappe.db.commit()

			res2 = api_controller.mark_invoice_as_sent(zb_invoice_id)
			if res2 == "Invoice status has been changed to Sent.":
				return "ADDED"


@frappe.whitelist()
def fetch_unsynced_erp_aurocard_invoice_list():
	if frappe.defaults.get_user_default("company") == "Auroville Bakery":
		return frappe.db.sql(
			"""
			SELECT si.name, si.docstatus, si.status
			FROM `tabSales Invoice` si, tabCustomer c WHERE si.docstatus = 1
			AND posting_date >= "2025-11-01"
			AND si.status IN ('Paid', 'Submitted', 'Unpaid', 'Overdue', 'Credit Note Issued')
			AND si.custom_fs_account_number IS NULL AND c.customer_group = "Aurocard Payments" AND si.customer = c.name
			AND custom_zoho_invoice_id IS NULL
			""",
			as_dict=True
			# AND posting_date BETWEEN "2025-04-01" AND "2025-04-30"
		)

	elif frappe.defaults.get_user_default("company") == "AV Bakery Cafe":
		return frappe.db.sql(
			"""
			SELECT si.name, si.docstatus, si.status
			FROM `tabSales Invoice` si, tabCustomer c WHERE si.docstatus = 1
			AND posting_date >= "2025-10-01"
			AND si.status IN ('Paid', 'Submitted', 'Unpaid', 'Overdue', 'Credit Note Issued')
			AND si.custom_fs_account_number IS NULL AND c.customer_group = "Aurocard Payments" AND si.customer = c.name
			AND custom_zoho_invoice_id IS NULL
			""",
			as_dict=True
			# AND posting_date BETWEEN "2025-04-01" AND "2025-04-30"
		)

	elif frappe.defaults.get_user_default("company") == "AV Bakery Cafe Townhall":
		return frappe.db.sql(
			"""
			SELECT si.name, si.docstatus, si.status, si.custom_zoho_invoice_id, si.custom_zoho_payment_id
			FROM `tabSales Invoice` si, `tabSales Invoice Payment` sip
			WHERE si.docstatus = 1
			AND posting_date >= "2025-10-01"
			AND si.status IN ('Paid', 'Submitted', 'Unpaid', 'Overdue', 'Credit Note Issued')
			AND si.custom_fs_account_number IS NULL AND sip.mode_of_payment = "Aurocard" AND sip.parent = si.name
			AND custom_zoho_invoice_id IS NULL
			""",
			as_dict=True
			# AND posting_date BETWEEN "2025-04-01" AND "2025-04-30"
		)

	else:
		return frappe.db.sql(
			"""
			SELECT si.name, si.docstatus, si.status
			FROM `tabSales Invoice` si, tabCustomer c WHERE si.docstatus = 1
			AND si.status IN ('Paid', 'Submitted', 'Unpaid', 'Overdue', 'Credit Note Issued')
			AND si.custom_fs_account_number IS NULL AND c.customer_group = "Aurocard Payments" AND si.customer = c.name
			AND custom_zoho_invoice_id IS NULL
			""",
			as_dict=True
			# AND posting_date BETWEEN "2025-04-01" AND "2025-04-30"
		)

@frappe.whitelist()
def sync_aurocard_inv_with_zoho_books(invoice):
	api_controller = frappe.get_doc("Zoho Books API")
	invoice_doc = frappe.get_doc("Sales Invoice", invoice)
	date = invoice_doc.posting_date.strftime(api_controller.DATE_FORMAT) # converting Date object to String
	customer_id = api_controller.walk_in_aurocard_contact_id

	if invoice_doc.custom_zoho_invoice_id == None:
		line_items = []

		for item in invoice_doc.items:
			item_doc = frappe.get_doc("Item", item.item_code)

			if invoice_doc.taxes:
				is_inclusive_tax = True if invoice_doc.taxes[0].included_in_print_rate else False

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
						"name": item.item_name,
						#"description": item.item_name,
						"rate": float(item.rate),
						"quantity": float(item.qty),
						"tax_id": tax_id
					}
					line_items.append(line_item)

			else:
				line_item = {
					"item_id": item_doc.custom_zoho_item_id,
					"name": item.item_name,
					#"description": item.item_name,
					"rate": float(item.rate),
					"quantity": float(item.qty),
					'gst_treatment_code': 'out_of_scope'
				}
				line_items.append(line_item)	

		invoice_data = {
			'customer_id': customer_id, # "Aurocard Customers" in ZB
			'invoice_number': invoice[-16:],
			'date': date,
			#'location_id': api_controller.location_id,
			#"is_inclusive_tax": is_inclusive_tax,
			#'price_precision': 2,
			"custom_fields": [
				{
					"index": 2,
					"label": "cf_aurocard_number",
					"value": invoice_doc.customer_name,
					"data_type": "text"
				}
			],
			"line_items": line_items
		}

		if invoice_doc.taxes:
			invoice_data['is_inclusive_tax'] = is_inclusive_tax

		if api_controller.location_id:
			invoice_data['location_id'] = api_controller.location_id

		# adding delivery charge if any
		if invoice_doc.posa_delivery_charges:
			for row in invoice_doc.taxes: # searching in the "Taxes and Charges" table
				if row.gst_tax_type == None:
					invoice_data["shipping_charge"] = row.tax_amount

		#frappe.throw(str(invoice_data))
		if invoice_doc.amended_from:
			void_invoice_id = frappe.get_value("Sales Invoice", invoice_doc.amended_from, "custom_zoho_void_invoice_id")
			res = api_controller.delete_invoice(void_invoice_id)
			#frappe.throw(str(res))
			if res.get('code') != 0:
				frappe.msgprint(res.get("message"))

		res = api_controller.post_invoice(invoice_data)

		zb_invoice_id = None

		if "invoice_id" in res:
			zb_invoice_id = res.get('invoice_id')

		elif res.get("message") == ("Invoice "+invoice_data["invoice_number"]+" already exists"):
			res2 = api_controller.query_invoice(invoice_data["invoice_number"])
			if res2:
				zb_invoice_id = res2[0].get("invoice_id")

		else:
			frappe.throw(res.get("message"))

		#if "invoice_id" in res:
		if zb_invoice_id:
			zb_invoice_id = res.get('invoice_id')
			invoice_doc.custom_zoho_invoice_id = zb_invoice_id
			invoice_doc.save()
			frappe.db.commit()

			res2 = api_controller.mark_invoice_as_sent(zb_invoice_id)
			if res2 == "Invoice status has been changed to Sent.":
				return { "ADDED" }


@frappe.whitelist()
def fetch_unsynced_erp_upi_invoice_list():
	if frappe.defaults.get_user_default("company") == "Auroville Bakery":
		return frappe.db.sql(
			"""
			SELECT si.name, si.docstatus, si.status, si.custom_zoho_invoice_id, si.custom_zoho_payment_id
			FROM `tabSales Invoice` si, tabCustomer c WHERE si.docstatus = 1
			AND posting_date >= "2025-11-01"
			AND si.status IN ('Paid', 'Submitted', 'Unpaid', 'Overdue', 'Credit Note Issued')
			AND si.custom_fs_account_number IS NULL AND c.customer_group = "UPI Payments" AND si.customer = c.name
			AND custom_zoho_invoice_id IS NULL
			""",
			as_dict=True
			# AND posting_date BETWEEN "2025-04-01" AND "2025-04-30"
		)

	elif frappe.defaults.get_user_default("company") == "AV Bakery Cafe":
		return frappe.db.sql(
			"""
			SELECT si.name, si.docstatus, si.status, si.custom_zoho_invoice_id, si.custom_zoho_payment_id
			FROM `tabSales Invoice` si, tabCustomer c WHERE si.docstatus = 1
			AND posting_date >= "2025-10-01"
			AND si.status IN ('Paid', 'Submitted', 'Unpaid', 'Overdue', 'Credit Note Issued')
			AND si.custom_fs_account_number IS NULL AND c.customer_group = "UPI Payments" AND si.customer = c.name
			AND custom_zoho_invoice_id IS NULL
			""",
			as_dict=True
			# AND posting_date BETWEEN "2025-04-01" AND "2025-04-30"
		)

	elif frappe.defaults.get_user_default("company") == "AV Bakery Cafe Townhall":
		return frappe.db.sql(
			"""
			SELECT si.name, si.docstatus, si.status, si.custom_zoho_invoice_id, si.custom_zoho_payment_id
			FROM `tabSales Invoice` si, `tabSales Invoice Payment` sip
			WHERE si.docstatus = 1
			AND posting_date >= "2025-10-01"
			AND si.status IN ('Paid', 'Submitted', 'Unpaid', 'Overdue', 'Credit Note Issued')
			AND si.custom_fs_account_number IS NULL AND sip.mode_of_payment = "UPI" AND sip.parent = si.name
			AND custom_zoho_invoice_id IS NULL
			""",
			as_dict=True
			# AND posting_date BETWEEN "2025-04-01" AND "2025-04-30"
		)

	else:
		return frappe.db.sql(
			"""
			SELECT si.name, si.docstatus, si.status, si.custom_zoho_invoice_id, si.custom_zoho_payment_id
			FROM `tabSales Invoice` si, tabCustomer c WHERE si.docstatus = 1
			AND si.status IN ('Paid', 'Submitted', 'Unpaid', 'Overdue', 'Credit Note Issued')
			AND si.custom_fs_account_number IS NULL AND c.customer_group = "UPI Payments" AND si.customer = c.name
			AND custom_zoho_invoice_id IS NULL
			""",
			as_dict=True
			# AND posting_date BETWEEN "2025-04-01" AND "2025-04-30"
		)

@frappe.whitelist()
def sync_upi_inv_with_zoho_books(invoice):
	api_controller = frappe.get_doc("Zoho Books API")
	invoice_doc = frappe.get_doc("Sales Invoice", invoice)
	date = invoice_doc.posting_date.strftime(api_controller.DATE_FORMAT) # converting Date object to String
	customer_id = api_controller.walk_in_upi_contact_id

	# if invoice_doc.company == "Pour Tous Purchasing Service":
	# 	customer_id = 2464766000000395241
	# elif invoice_doc.company == "Auroville Bakery":
	# 	customer_id = 2386181000000192017 # AVB "UPI Customers" in ZB
	# elif invoice_doc.company == "AV Bakery Cafe":
	# 	customer_id = 2567347000000380968 # AVBC "UPI Customers" in ZB
	# else:
	# 	frappe.throw("Please set the ZB Walk-in Customer IDs for this Company")

	if invoice_doc.custom_zoho_invoice_id == None:
		line_items = []

		for item in invoice_doc.items:
			item_doc = frappe.get_doc("Item", item.item_code)

			if invoice_doc.taxes:
				is_inclusive_tax = True if invoice_doc.taxes[0].included_in_print_rate else False

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
						"name": item.item_name,
						#"description": item.item_name,
						"rate": float(item.rate),
						"quantity": float(item.qty),
						"tax_id": tax_id
					}
					line_items.append(line_item)

			else:
				line_item = {
					"item_id": item_doc.custom_zoho_item_id,
					"name": item.item_name,
					#"description": item.item_name,
					"rate": float(item.rate),
					"quantity": float(item.qty),
					'gst_treatment_code': 'out_of_scope'
				}
				line_items.append(line_item)

		invoice_data = {
			'customer_id': customer_id, # "UPI Customers" in ZB
			'invoice_number': invoice[-16:],
			'date': date,
			#"location_id": api_controller.location_id,
			#"is_inclusive_tax": is_inclusive_tax,
			"custom_fields": [
				{
					"index": 3,
					"label": "cf_upi_transaction_id",
					"value": invoice_doc.custom_upi_transaction_id,
					"data_type": "text"
				}
			],
			#'price_precision': 2,
			"line_items": line_items
		}

		if invoice_doc.taxes:
			invoice_data['is_inclusive_tax'] = is_inclusive_tax

		if api_controller.location_id:
			invoice_data['location_id'] = api_controller.location_id

		# adding delivery charge if any
		if invoice_doc.posa_delivery_charges:
			for row in invoice_doc.taxes: # searching in the "Taxes and Charges" table
				if row.gst_tax_type == None:
					invoice_data["shipping_charge"] = row.tax_amount

		#frappe.throw(str(invoice_data))
		if invoice_doc.amended_from:
			void_invoice_id = frappe.get_value("Sales Invoice", invoice_doc.amended_from, "custom_zoho_void_invoice_id")
			res = api_controller.delete_invoice(void_invoice_id)
			#frappe.throw(str(res))
			if res.get('code') != 0:
				frappe.msgprint(res.get("message"))

		res = api_controller.post_invoice(invoice_data)

		zb_invoice_id = None

		if "invoice_id" in res:
			zb_invoice_id = res.get('invoice_id')

		elif res.get("message") == ("Invoice "+invoice_data["invoice_number"]+" already exists"):
			res2 = api_controller.query_invoice(invoice_data["invoice_number"])
			if res2:
				zb_invoice_id = res2[0].get("invoice_id")

		#if "invoice_id" in res:
		if zb_invoice_id:
			zb_invoice_id = res.get('invoice_id')
			invoice_doc.custom_zoho_invoice_id = zb_invoice_id
			invoice_doc.save()
			frappe.db.commit()

			res2 = api_controller.mark_invoice_as_sent(zb_invoice_id)
			if res2 == "Invoice status has been changed to Sent.":
				return { "ADDED" }


@frappe.whitelist()
def fetch_unsynced_erp_card_invoice_list():
	if frappe.defaults.get_user_default("company") == "Auroville Bakery":
		return frappe.db.sql(
			"""
			SELECT si.name, si.docstatus, si.status, si.custom_zoho_invoice_id, si.custom_zoho_payment_id
			FROM `tabSales Invoice` si, tabCustomer c WHERE si.docstatus = 1
			AND posting_date >= "2025-11-01"
			AND si.status IN ('Paid', 'Submitted', 'Unpaid', 'Overdue', 'Credit Note Issued')
			AND si.custom_fs_account_number IS NULL AND c.customer_group = "Card Payments" AND si.customer = c.name
			AND custom_zoho_invoice_id IS NULL
			""",
			as_dict=True
			# AND posting_date BETWEEN "2025-04-01" AND "2025-04-30"
		)

	elif frappe.defaults.get_user_default("company") == "AV Bakery Cafe":
		return frappe.db.sql(
			"""
			SELECT si.name, si.docstatus, si.status, si.custom_zoho_invoice_id, si.custom_zoho_payment_id
			FROM `tabSales Invoice` si, tabCustomer c WHERE si.docstatus = 1
			AND posting_date >= "2025-10-01"
			AND si.status IN ('Paid', 'Submitted', 'Unpaid', 'Overdue', 'Credit Note Issued')
			AND si.custom_fs_account_number IS NULL AND c.customer_group = "Card Payments" AND si.customer = c.name
			AND custom_zoho_invoice_id IS NULL
			""",
			as_dict=True
			# AND posting_date BETWEEN "2025-04-01" AND "2025-04-30"
		)

	elif frappe.defaults.get_user_default("company") == "AV Bakery Cafe Townhall":
		return frappe.db.sql(
			"""
			SELECT si.name, si.docstatus, si.status, si.custom_zoho_invoice_id, si.custom_zoho_payment_id
			FROM `tabSales Invoice` si, `tabSales Invoice Payment` sip
			WHERE si.docstatus = 1
			AND posting_date >= "2025-10-01"
			AND si.status IN ('Paid', 'Submitted', 'Unpaid', 'Overdue', 'Credit Note Issued')
			AND si.custom_fs_account_number IS NULL AND sip.mode_of_payment = "Cards" AND sip.parent = si.name
			AND custom_zoho_invoice_id IS NULL
			""",
			as_dict=True
			# AND posting_date BETWEEN "2025-04-01" AND "2025-04-30"
		)

	else:
		return frappe.db.sql(
			"""
			SELECT si.name, si.docstatus, si.status, si.custom_zoho_invoice_id, si.custom_zoho_payment_id
			FROM `tabSales Invoice` si, tabCustomer c WHERE si.docstatus = 1
			AND si.status IN ('Paid', 'Submitted', 'Unpaid', 'Overdue', 'Credit Note Issued')
			AND si.custom_fs_account_number IS NULL AND c.customer_group = "Card Payments" AND si.customer = c.name
			AND custom_zoho_invoice_id IS NULL
			""",
			as_dict=True
			# AND posting_date BETWEEN "2025-04-01" AND "2025-04-30"
		)


@frappe.whitelist()
def sync_card_inv_with_zoho_books(invoice):
	api_controller = frappe.get_doc("Zoho Books API")
	invoice_doc = frappe.get_doc("Sales Invoice", invoice)
	date = invoice_doc.posting_date.strftime(api_controller.DATE_FORMAT) # converting Date object to String
	customer_id = api_controller.walk_in_card_contact_id

	if invoice_doc.custom_zoho_invoice_id == None:
		line_items = []

		for item in invoice_doc.items:
			item_doc = frappe.get_doc("Item", item.item_code)

			if invoice_doc.taxes:
				is_inclusive_tax = True if invoice_doc.taxes[0].included_in_print_rate else False

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
						"name": item.item_name,
						#"description": item.item_name,
						"rate": float(item.rate),
						"quantity": float(item.qty),
						"tax_id": tax_id
					}
					line_items.append(line_item)

			else:
				line_item = {
					"item_id": item_doc.custom_zoho_item_id,
					"name": item.item_name,
					"rate": float(item.rate),
					"quantity": float(item.qty),
					'gst_treatment_code': 'out_of_scope'
				}
				line_items.append(line_item)

		invoice_data = {
			'customer_id': customer_id, # "Card Customers" in ZB
			'invoice_number': invoice[-16:],
			'date': date,
			#"location_id": api_controller.location_id,
			#"is_inclusive_tax": is_inclusive_tax,
			"custom_fields": [
				{
					"index": 4,
					"label": "cf_card_transaction_id",
					"value": invoice_doc.custom_card_transaction_id,
					"data_type": "text"
				}
			],
			#'price_precision': 2,
			"line_items": line_items
		}

		if invoice_doc.taxes:
			invoice_data['is_inclusive_tax'] = is_inclusive_tax

		if api_controller.location_id:
			invoice_data['location_id'] = api_controller.location_id

		# adding delivery charge if any
		if invoice_doc.posa_delivery_charges:
			for row in invoice_doc.taxes: # searching in the "Taxes and Charges" table
				if row.gst_tax_type == None:
					invoice_data["shipping_charge"] = row.tax_amount

		#frappe.throw(str(invoice_data))
		if invoice_doc.amended_from:
			void_invoice_id = frappe.get_value("Sales Invoice", invoice_doc.amended_from, "custom_zoho_void_invoice_id")
			res = api_controller.delete_invoice(void_invoice_id)
			#frappe.throw(str(res))
			if res.get('code') != 0:
				frappe.msgprint(res.get("message"))

		res = api_controller.post_invoice(invoice_data)

		zb_invoice_id = None

		if "invoice_id" in res:
			zb_invoice_id = res.get('invoice_id')

		elif res.get("message") == ("Invoice "+invoice_data["invoice_number"]+" already exists"):
			res2 = api_controller.query_invoice(invoice_data["invoice_number"])
			if res2:
				zb_invoice_id = res2[0].get("invoice_id")

		#if "invoice_id" in res:
		if zb_invoice_id:
			zb_invoice_id = res.get('invoice_id')
			invoice_doc.custom_zoho_invoice_id = zb_invoice_id
			invoice_doc.save()
			frappe.db.commit()

			res2 = api_controller.mark_invoice_as_sent(zb_invoice_id)
			if res2 == "Invoice status has been changed to Sent.":
				return { "ADDED" }


@frappe.whitelist()
def fetch_unsynced_erp_cash_invoice_list():
	if frappe.defaults.get_user_default("company") == "Auroville Bakery":
		return frappe.db.sql(
			"""
			SELECT si.name, si.docstatus, si.status, si.custom_zoho_invoice_id, si.custom_zoho_payment_id
			FROM `tabSales Invoice` si, tabCustomer c WHERE si.docstatus = 1
			AND posting_date >= "2025-11-01"
			AND si.status IN ('Paid', 'Submitted', 'Unpaid', 'Overdue', 'Credit Note Issued')
			AND si.custom_fs_account_number IS NULL AND c.customer_group = "Cash Payments" AND si.customer = c.name
			AND custom_zoho_invoice_id IS NULL
			""",
			as_dict=True
			# AND posting_date BETWEEN "2025-04-01" AND "2025-04-30"
		)

	elif frappe.defaults.get_user_default("company") == "AV Bakery Cafe":
		return frappe.db.sql(
			"""
			SELECT si.name, si.docstatus, si.status, si.custom_zoho_invoice_id, si.custom_zoho_payment_id
			FROM `tabSales Invoice` si, tabCustomer c WHERE si.docstatus = 1
			AND posting_date >= "2025-10-01"
			AND si.status IN ('Paid', 'Submitted', 'Unpaid', 'Overdue', 'Credit Note Issued')
			AND si.custom_fs_account_number IS NULL AND c.customer_group = "Cash Payments" AND si.customer = c.name
			AND custom_zoho_invoice_id IS NULL
			""",
			as_dict=True
			# AND posting_date BETWEEN "2025-04-01" AND "2025-04-30"
		)

	elif frappe.defaults.get_user_default("company") == "AV Bakery Cafe Townhall":
		return frappe.db.sql(
			"""
			SELECT si.name, si.docstatus, si.status, si.custom_zoho_invoice_id, si.custom_zoho_payment_id
			FROM `tabSales Invoice` si, `tabSales Invoice Payment` sip
			WHERE si.docstatus = 1
			AND posting_date >= "2025-10-01"
			AND si.status IN ('Paid', 'Submitted', 'Unpaid', 'Overdue', 'Credit Note Issued')
			AND si.custom_fs_account_number IS NULL AND sip.mode_of_payment = "Cash" AND sip.parent = si.name
			AND custom_zoho_invoice_id IS NULL
			""",
			as_dict=True
			# AND posting_date BETWEEN "2025-04-01" AND "2025-04-30"
		)

	else:
		return frappe.db.sql(
			"""
			SELECT si.name, si.docstatus, si.status, si.custom_zoho_invoice_id, si.custom_zoho_payment_id
			FROM `tabSales Invoice` si, tabCustomer c WHERE si.docstatus = 1
			AND si.status IN ('Paid', 'Submitted', 'Unpaid', 'Overdue', 'Credit Note Issued')
			AND si.custom_fs_account_number IS NULL AND c.customer_group = "Cash Payments" AND si.customer = c.name
			AND custom_zoho_invoice_id IS NULL
			""",
			as_dict=True
			# AND posting_date BETWEEN "2025-04-01" AND "2025-04-30"
		)


@frappe.whitelist()
def sync_cash_inv_with_zoho_books(invoice):
	api_controller = frappe.get_doc("Zoho Books API")
	invoice_doc = frappe.get_doc("Sales Invoice", invoice)
	date = invoice_doc.posting_date.strftime(api_controller.DATE_FORMAT) # converting Date object to String
	customer_id = api_controller.walk_in_cash_contact_id

	if invoice_doc.custom_zoho_invoice_id == None:
		line_items = []

		for item in invoice_doc.items:
			item_doc = frappe.get_doc("Item", item.item_code)

			if invoice_doc.taxes:
				is_inclusive_tax = True if invoice_doc.taxes[0].included_in_print_rate else False

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
						"name": item.item_name,
						#"description": item.item_name,
						"rate": float(item.rate),
						"quantity": float(item.qty),
						"tax_id": tax_id
					}
					line_items.append(line_item)

			else:
				line_item = {
					"item_id": item_doc.custom_zoho_item_id,
					"name": item.item_name,
					#"description": item.item_name,
					"rate": float(item.rate),
					"quantity": float(item.qty),
					'gst_treatment_code': 'out_of_scope'
				}
				line_items.append(line_item)

		invoice_data = {
			'customer_id': customer_id, # "Card Customers" in ZB
			'invoice_number': invoice[-16:],
			'date': date,
			#"location_id": api_controller.location_id,
			#"is_inclusive_tax": is_inclusive_tax,
			#'price_precision': 2,
			"line_items": line_items
		}

		if invoice_doc.taxes:
			invoice_data['is_inclusive_tax'] = is_inclusive_tax

		if api_controller.location_id:
			invoice_data['location_id'] = api_controller.location_id

		# adding delivery charge if any
		if invoice_doc.posa_delivery_charges:
			for row in invoice_doc.taxes: # searching in the "Taxes and Charges" table
				if row.gst_tax_type == None:
					invoice_data["shipping_charge"] = row.tax_amount

		#frappe.throw(str(invoice_data))
		if invoice_doc.amended_from:
			void_invoice_id = frappe.get_value("Sales Invoice", invoice_doc.amended_from, "custom_zoho_void_invoice_id")
			res = api_controller.delete_invoice(void_invoice_id)
			#frappe.throw(str(res))
			if res.get('code') != 0:
				frappe.msgprint(res.get("message"))

		res = api_controller.post_invoice(invoice_data)

		zb_invoice_id = None

		if "invoice_id" in res:
			zb_invoice_id = res.get('invoice_id')

		elif res.get("message") == ("Invoice "+invoice_data["invoice_number"]+" already exists"):
			res2 = api_controller.query_invoice(invoice_data["invoice_number"])
			if res2:
				zb_invoice_id = res2[0].get("invoice_id")

		#if "invoice_id" in res:
		if zb_invoice_id:
			zb_invoice_id = res.get('invoice_id')
			invoice_doc.custom_zoho_invoice_id = zb_invoice_id
			invoice_doc.save()
			frappe.db.commit()

			res2 = api_controller.mark_invoice_as_sent(zb_invoice_id)
			if res2 == "Invoice status has been changed to Sent.":
				return { "ADDED" }


def void_invoice_in_zoho(doc, method):
	if frappe.defaults.get_user_default("company") in ("Pour Tous Distribution Center", "Pour Tous Canteen"):
	#if frappe.defaults.get_user_default("company") in ("Pour Tous Canteen"):
		return

	if doc.is_return == 0 and doc.custom_zoho_invoice_id:
		api_controller = frappe.get_doc("Zoho Books API")
		res = api_controller.void_invoice(doc.custom_zoho_invoice_id)
		if res == "Invoice status has been changed to Void.":
			msg = "Zoho Books Response: " + res
			frappe.msgprint(msg)
			# setting the invoice ids to null here, to avoid checking for amends in the highly subscribed "Sales Invoice" before_save hook
			doc.custom_zoho_void_invoice_id = doc.custom_zoho_invoice_id
			doc.custom_zoho_invoice_id = None
			# if r.json().get('message') != "Invoice status has been changed to Void.":
		else:
			msg = "Zoho Books Response: " + res
			frappe.throw(msg)

	elif doc.is_return == 1 and doc.custom_zb_creditnote_id:
		api_controller = frappe.get_doc("Zoho Books API")
		res = api_controller.void_creditnote(doc.custom_zb_creditnote_id)
		if res == "The credit note has been marked as void.":
			msg = "Zoho Books Response: " + res
			frappe.msgprint(msg)
			# setting the invoice ids to null here, to avoid checking for amends in the highly subscribed "Sales Invoice" before_save hook
			doc.custom_zoho_void_invoice_id = doc.custom_zb_creditnote_id
			doc.custom_zb_creditnote_id = None
			# if r.json().get('message') != "The credit note has been marked as void.":
		else:
			msg = "Zoho Books Response: " + res
			frappe.throw(msg)

def amend_sales_invoice(doc, method):
	if doc.amended_from and doc.custom_zoho_void_invoice_id:
		doc.custom_zoho_void_invoice_id = None


def void_bill_in_zoho(doc, method):
	if frappe.defaults.get_user_default("company") in ("Pour Tous Canteen"):
		return

	api_controller = frappe.get_doc("Zoho Books API")

	if doc.is_return == 0 and doc.custom_zoho_bill_id:
		res = api_controller.void_bill(doc.custom_zoho_bill_id)
		if res:
			msg = "Zoho Books Response: " + res
			frappe.msgprint(msg)
			doc.custom_zoho_void_bill_id = doc.custom_zoho_bill_id
			doc.custom_zoho_bill_id = None
			# if r.json().get('message') != "The bill has been marked as void.":
	
	elif doc.is_return == 1 and doc.custom_zb_vendor_credit_id:
		res = api_controller.void_vendor_credit(doc.custom_zb_vendor_credit_id)
		if res:
			msg = "Zoho Books Response: " + res
			frappe.msgprint(msg)
			doc.custom_zoho_void_bill_id = doc.custom_zb_vendor_credit_id
			doc.custom_zb_vendor_credit_id = None
			# if r.json().get('message') != "The credit note has been marked as void.":

def amend_return_purchase_invoice(doc, method):
	if doc.amended_from:
		doc.custom_zoho_void_bill_id = None
	if doc.is_return:
		doc.custom_zoho_bill_id = None

	""" if doc.price_list_rate != doc.rate and frappe.session.user not in [
		'Administrator', 'karan@pourtous-av.in', 'iyyappan@pourtous-av.in', 'kumaran@pourtous-av.in', 'accounts-server@pourtous-av.in'
	]:
		return """


@frappe.whitelist()
def fetch_bills_to_delete():
	return frappe.db.sql(
		"""
		select name, custom_zoho_bill_id FROM `tabPurchase Receipt`
		where owner = "karan@pourtous-av.in" and posting_date = "2025-04-06"
		and custom_zoho_bill_id IS NOT NULL and docstatus = 1
		""",
		as_dict=True
	)

@frappe.whitelist()
def delete_bills_in_zoho(bill, custom_zoho_bill_id):
	api_controller = frappe.get_doc("Zoho Books API")
	res = api_controller.delete_bill(custom_zoho_bill_id)

	if res.get("code") == 0:
		frappe.db.set_value("Purchase Receipt", bill, "custom_zoho_bill_id", "")
		return { "DELETED" }


@frappe.whitelist()
def delete_specific_invoice_payments(invoice):
	frappe.db.set_value("Sales Invoice", invoice, "custom_zoho_payment_id", "")
	return { "DELETED" }


@frappe.whitelist()
def fetch_invoices_to_delete():
	return frappe.db.sql(
		"""
		SELECT name FROM `tabSales Invoice` WHERE docstatus = 1 and custom_zoho_invoice_id IS NOT NULL
		""",
		as_dict=True
	)
	# and posting_date <= "2025-04-30"
	"""
	select si.name, si.custom_zoho_invoice_id from `tabSales Invoice` si, tabCustomer c
	where si.customer = c.name and c.customer_type = "Company"
	and si.custom_zoho_invoice_id IS NOT NULL
	and posting_date <= "2025-05-01" and si.docstatus = 1;
	"""


@frappe.whitelist()
def delete_invoice_ids_in_erp(invoice):
	import csv

	with open('Invoice_ids_to_retain.csv', newline='') as f:
		reader = csv.reader(f)
		inv_ids_list_of_lists = list(reader)

	inv_ids_list = []

	for row in inv_ids_list_of_lists:
		inv_ids_list.extend(row)

	exists = any(inv_name == invoice for inv_name in inv_ids_list)

	if not exists:
		frappe.db.set_value("Sales Invoice", invoice, "custom_zoho_invoice_id", "")
		return { "DELETED" }

	#return inv_ids_list_of_lists

	#return frappe.db.sql(
	#	"""
	#	SELECT name, custom_zoho_invoice_id FROM `tabSales Invoice`
	#	WHERE docstatus = 1 AND status = 'paid'
	#	AND custom_zoho_invoice_id IS NOT NULL
	#	AND name IN {0}
	#	""".format(tuple(del_inv_list)),
	#	as_dict=True
	#)


@frappe.whitelist()
def delete_invoices_in_zoho(invoice, custom_zoho_invoice_id):
#def delete_invoice_ids_in_erp(invoice):
	api_controller = frappe.get_doc("Zoho Books API")

	res = api_controller.delete_invoice(custom_zoho_invoice_id)

	#frappe.throw(str(res))

	if res.get("code") == 0:
	#if res.get("code") == 1002 and res.get("message") == 'Invoice does not exist.':
		frappe.db.set_value("Sales Invoice", invoice, "custom_zoho_invoice_id", "")
		return { "DELETED" }
		#msg = "Zoho Books Response: " + res.json().get("message")
		#frappe.msgprint(msg)


@frappe.whitelist()
def fetch_payments_cn_refunds_to_delete():
	return frappe.db.sql(
		"""
		SELECT name, customer, custom_fs_account_number, docstatus, status, custom_zoho_payment_id
		FROM `tabSales Invoice` WHERE docstatus = 1
		and (custom_zoho_payment_id IS NOT NULL)
		""",
		as_dict=True
	)


@frappe.whitelist()
#def delete_customer_payments_cn_refunds_in_zb(invoice, custom_zoho_payment_id, custom_zb_creditnote_id, custom_zb_creditnote_refund_id):
def delete_customer_payments_cn_refunds_in_zb(invoice, custom_zoho_payment_id):
	api_controller = frappe.get_doc("Zoho Books API")

	if custom_zoho_payment_id != None:
		res = api_controller.delete_customerpayments(custom_zoho_payment_id)

		if res.get("code") == 0:
			frappe.db.set_value("Sales Invoice", invoice, "custom_zoho_payment_id", "")
			return { "DELETED" }
			#msg = "Zoho Books Response: " + res.json().get("message")
			#frappe.msgprint(msg)


@frappe.whitelist()
def fetch_erp_invoice_list_to_update():
	return frappe.db.sql(
		"""
		SELECT si.name, sip.mode_of_payment, si.custom_fs_account_number, si.docstatus, si.status, si.posting_date, si.remarks
		FROM `tabSales Invoice` si, `tabSales Invoice Payment` sip
		WHERE si.docstatus = 1 AND si.status = 'paid' AND sip.mode_of_payment LIKE "FS%" AND sip.parent = si.name
		AND (si.custom_zoho_invoice_id IS NOT NULL OR si.custom_zoho_payment_id IS NOT NULL)
		AND si.custom_zb_updated = 0
		AND si.posting_date BETWEEN "2025-04-01" AND "2025-04-25"
		""",
		as_dict=True
	)
