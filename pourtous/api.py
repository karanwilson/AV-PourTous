import frappe
from frappe import _
from frappe.utils import nowdate, get_first_day #, flt

from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice

from stdnum import ean

# for testing/checking frappe.session.user
#def check_user(doc, method):
#	frappe.throw(str(frappe.session.user))

@frappe.whitelist()
def set_customer_from_fs_account(custom_fs_account_number):
	return frappe.db.get_value("Customer", {"custom_fs_account_number": custom_fs_account_number}, "name")


@frappe.whitelist()
def tax_exception_fetch_orders_to_invoice():
	frappe.db.delete("Order Invoice Map Err") # deletes the old logs (used in the process_orders_to_invoice method below)

	if frappe.defaults.get_user_default("company") == "Pour Tous Distribution Center":
		return frappe.db.sql(
			"""
			SELECT name FROM `tabSales Order`
			WHERE
				docstatus = 1
				AND status not in ("Closed", "On Hold")
				AND per_billed < 99.99
				AND transaction_date BETWEEN "2025-04-03" AND "2025-04-05"
				AND company = '{0}'
			ORDER BY
				customer
			""".format(frappe.defaults.get_user_default("company")),
			#as_dict=1,
		)

	else:
		# "AND grand_total = advance_paid" is needed to only match Order for which payments have been processed by the script
		return frappe.db.sql(
			"""
			SELECT name FROM `tabSales Order`
			WHERE
				docstatus = 1
				AND status not in ("Closed", "On Hold")
				AND per_billed < 99.99
				AND grand_total = advance_paid
				AND transaction_date BETWEEN "2025-04-02" AND "2025-04-05"
				AND company = '{0}'
			ORDER BY
				customer
			""".format(frappe.defaults.get_user_default("company")),
			#as_dict=1,
		)


@frappe.whitelist()
def tax_exception_process_orders_to_invoice(order):

	si = make_sales_invoice(order, ignore_permissions=True)
	si.allocate_advances_automatically = True
	si.update_stock = 1

	if si.get("taxes"):
		for tax in si.taxes:
			tax.included_in_print_rate = 1

	try:
		si = si.insert(ignore_permissions=True)
		si.submit()

	except Exception as err:
		error_log = frappe.new_doc("Order Invoice Map Err")
		error_log.sales_order = order
		error_log.error = str(err)
		error_log.insert()

		if si.docstatus == 1:
			return "DONE"
		else:
			return "ERROR"

	else:
		return "DONE"


@frappe.whitelist()
def fetch_orders_to_invoice():
	frappe.db.delete("Order Invoice Map Err") # deletes the old logs (used in the process_orders_to_invoice method below)

	is_tax_inclusive = frappe.get_value("POS Profile", {'owner': frappe.session.user}, "posa_tax_inclusive")

	if frappe.defaults.get_user_default("company") == "Pour Tous Distribution Center":
		return frappe.db.sql(
			"""
			SELECT name, custom_pos_profile, transaction_date, custom_posting_time FROM `tabSales Order`
			WHERE
				docstatus = 1
				AND status not in ("Closed", "On Hold")
				AND per_billed < 99.99
				AND transaction_date NOT BETWEEN "2025-04-03" AND "2025-04-05"
				AND company = '{0}'
			ORDER BY
				customer
			""".format(frappe.defaults.get_user_default("company")),
			#as_dict=1,
		), is_tax_inclusive

	else:
		# "AND grand_total = advance_paid" is needed to only match Order for which payments have been processed by the script
		return frappe.db.sql(
			"""
			SELECT name, custom_pos_profile, delivery_date, custom_posting_time FROM `tabSales Order`
			WHERE
				docstatus = 1
				AND status not in ("Closed", "On Hold")
				AND per_billed < 99.99
				AND grand_total = advance_paid
				AND company = '{0}'
			ORDER BY
				customer
			""".format(frappe.defaults.get_user_default("company")),
			#as_dict=1,
			# AND transaction_date > "2025-04-05"
		), is_tax_inclusive


@frappe.whitelist()
def process_orders_to_invoice(order, pos_profile, order_date, order_time, is_tax_inclusive):

	si = make_sales_invoice(order, ignore_permissions=True)
	si.pos_profile = pos_profile
	si.set_posting_time = 1
	si.posting_date = order_date
	si.posting_time = order_time
	si.allocate_advances_automatically = True
	si.update_stock = 1

	if si.get("taxes"):
		for tax in si.taxes:
			tax.included_in_print_rate = is_tax_inclusive

	try:
		si = si.insert(ignore_permissions=True)
		si.submit()

	except Exception as err:
		error_log = frappe.new_doc("Order Invoice Map Err")
		error_log.sales_order = order
		error_log.error = str(err)
		error_log.insert()

		if si.docstatus == 1:
			return "DONE"
		else:
			return "ERROR"

	else:
		return "DONE"


""" @frappe.whitelist()
def process_orders_to_invoice(order):

	si = make_sales_invoice(order, ignore_permissions=True)
	si.allocate_advances_automatically = True
	si.update_stock = 1

	if si.get("taxes"):
		for tax in si.taxes:
			tax.included_in_print_rate = 1

	try:
		si = si.insert(ignore_permissions=True)
		si.submit()

	except Exception as err:
		error_log = frappe.new_doc("Order Invoice Map Err")
		error_log.sales_order = order
		error_log.error = str(err)
		error_log.insert()

		if si.docstatus == 1:
			return "DONE"
		else:
			return "ERROR"

	else:
		return "DONE" """


# PTDC
@frappe.whitelist()
def fetch_monthly_contributions():
	return frappe.db.sql(
		"""
		SELECT tabContact.custom_in_kind_scheme, tabContact.custom_lunch_scheme, tabContact.custom_monthly_contribution, tabContact.custom_ptdc_maintenance,
		tabContact.name AS contact, `tabDynamic Link`.link_name AS customer
		FROM tabContact, `tabDynamic Link`, tabCustomer
		WHERE `tabDynamic Link`.parenttype = 'Contact' AND `tabDynamic Link`.parent = tabContact.name
		AND `tabDynamic Link`.link_name = tabCustomer.name AND tabCustomer.disabled = 0
		AND (tabContact.custom_in_kind_scheme != 0 OR tabContact.custom_lunch_scheme != 0 OR tabContact.custom_monthly_contribution != 0
		OR tabContact.custom_ptdc_maintenance != 0)
		""",
		as_dict=True
		#SELECT tabContact.name,
		#WHERE (custom_member_fs_acc_num IS NOT NULL OR custom_personal_fs_acc_num IS NOT NULL)
		#AND (custom_in_kind_scheme != 0 OR custom_lunch_scheme != 0 OR custom_monthly_contribution != 0 OR custom_ptdc_maintenance != 0)
	)

# PTDC
@frappe.whitelist()
def process_pt_monthly_balances(contact, customer, custom_in_kind_scheme, custom_lunch_scheme, custom_monthly_contribution, custom_ptdc_maintenance):
	company = frappe.defaults.get_user_default("company")

	if company == "Pour Tous Distribution Center":
		existing_pe = frappe.db.sql(
			"""
			SELECT name from `tabPayment Entry`
			WHERE docstatus = 1
			AND party = '{0}' AND custom_contact = '{1}'
			AND posting_date >= '{2}'
			AND (custom_in_kind_scheme > 0 OR custom_lunch_scheme > 0 OR custom_monthly_contribution > 0 OR custom_ptdc_maintenance > 0)
			""".format(customer, contact, get_first_day(nowdate()))
		)

		if len(existing_pe) > 0:
			return "EXISTS"

		in_kind_scheme = int(custom_in_kind_scheme)
		lunch_scheme = int(custom_lunch_scheme)
		monthly_contribution = int(custom_monthly_contribution)
		ptdc_maintenance = int(custom_ptdc_maintenance)

		amount = in_kind_scheme + lunch_scheme + monthly_contribution + ptdc_maintenance
		bank_account = get_bank_cash_account("FS", company)

    	# creating advance payment
		advance_payment_entry = frappe.get_doc(
            {
               	"doctype": "Payment Entry",
               	"mode_of_payment": "FS",
               	"paid_to": bank_account["account"],
               	"payment_type": "Receive",
               	"party_type": "Customer",
               	"party": customer,
				"custom_contact": contact,
				"custom_in_kind_scheme": in_kind_scheme,
				"custom_lunch_scheme": lunch_scheme,
				"custom_monthly_contribution": monthly_contribution,
				"custom_ptdc_maintenance": ptdc_maintenance,
               	"paid_amount": amount,
               	"received_amount": amount,
				"reference_no": customer,
				"reference_date": nowdate(),
               	"company": company,
            }
        )

		advance_payment_entry.flags.ignore_permissions = True
		frappe.flags.ignore_account_permission = True
		try:
			advance_payment_entry.insert()
			advance_payment_entry.submit()
		except Exception as err:
			frappe.msgprint(
				msg=str(err),
				title='Error',
			)
			raise err
		else:
			return "OK"

# PTDC
@frappe.whitelist()
def fetch_extra_contributions():
	return frappe.db.sql(
		"""
		SELECT tabContact.name AS contact, tabContact.custom_extra_contribution, `tabDynamic Link`.link_name AS customer
		FROM tabContact, `tabDynamic Link`, tabCustomer
		WHERE `tabDynamic Link`.parenttype = 'Contact' AND `tabDynamic Link`.parent = tabContact.name
		AND `tabDynamic Link`.link_name = tabCustomer.name AND tabCustomer.disabled = 0
		AND tabContact.custom_extra_contribution != 0
		""",
		as_dict=True
		#WHERE (tabContact.custom_member_fs_acc_num IS NOT NULL OR tabContact.custom_personal_fs_acc_num IS NOT NULL)
	)

# PTDC
@frappe.whitelist()
def process_pt_extra_contributions(contact, customer, custom_extra_contribution):
	company = frappe.defaults.get_user_default("company")

	if company == "Pour Tous Distribution Center":
		extra_contribution = int(custom_extra_contribution)
		bank_account = get_bank_cash_account("FS", company)

    	# creating advance payment
		advance_payment_entry = frappe.get_doc(
            {
               	"doctype": "Payment Entry",
               	"mode_of_payment": "FS",
               	"paid_to": bank_account["account"],
               	"payment_type": "Receive",
               	"party_type": "Customer",
               	"party": customer,
				"custom_contact": contact,
				"custom_extra_contribution": extra_contribution,
               	"paid_amount": extra_contribution,
               	"received_amount": extra_contribution,
				"reference_no": customer,
				"reference_date": nowdate(),
               	"company": company,
            }
        )

		advance_payment_entry.flags.ignore_permissions = True
		frappe.flags.ignore_account_permission = True
		try:
			advance_payment_entry.insert()
			advance_payment_entry.submit()
		except Exception as err:
			frappe.msgprint(
				msg=str(err),
				title='Error',
			)
			raise err
		else:
			# after the 'Extra Contribution' payment entry is successful, reset the custom_extra_contribution field
			frappe.db.set_value("Contact", contact, "custom_extra_contribution", 0)
			frappe.db.commit()
			return "OK"


@frappe.whitelist()
def fetch_invoice_list():
	return frappe.db.sql(
    	"""
		SELECT name, customer FROM `tabSales Invoice`
		WHERE
			posting_date between "2025-04-01" and "2025-04-05"
			AND docstatus = 1
			AND custom_fs_account_number IS NULL
	    """,
       as_dict=1,
	)


@frappe.whitelist()
def add_fs_accounts(invoice, customer):
	fs_acc_num = frappe.get_value("Customer", customer, "custom_fs_account_number")
	frappe.set_value("Sales Invoice", invoice, "custom_fs_account_number", fs_acc_num)

	return "ADDED"


@frappe.whitelist()
def update_fs_accounts(fs_account, name, disable):
	existing_fs_customer = frappe.get_value("Customer", {"custom_fs_account_number": fs_account}, "name")
	if existing_fs_customer:
		customer_doc = frappe.get_doc("Customer", existing_fs_customer)
		updated = "" # to reduce the number of db commits
		if customer_doc.customer_type == 'Company':
			return updated

		if customer_doc.disabled != int(disable):
			customer_doc.disabled = int(disable)
			updated = "UPDATED"
		if customer_doc.customer_name != name:
			customer_doc.customer_name = name
			updated = "UPDATED"

		if updated == "UPDATED":
			customer_doc.custom_update_zoho_contact = 0
			customer_doc.save()
			return updated

	else:
		new_customer = frappe.new_doc("Customer")

		new_customer.customer_name = name
		new_customer.custom_fs_account_number = fs_account
		new_customer.disabled = int(disable)

		new_customer.customer_type = 'Individual'
		new_customer.customer_group = 'Individual'
		new_customer.territory = 'India'

		new_customer.insert()
		return "NEW"


# called from B2B Sales Invoice client script
@frappe.whitelist()
def get_warehouse_name(customer):
	customer_type = frappe.get_value("Customer", customer, "customer_type")
	warehouse = "Sales Order Reserve - " + frappe.get_value("Company", frappe.defaults.get_user_default("company"), 'abbr')
	return {
		"customer_type": customer_type,
		"warehouse": warehouse
	}

# called from B2B Sales Invoice client script
@frappe.whitelist()
def get_so_item_batch(sales_order):
	return frappe.get_doc("Sales Order", sales_order)


@frappe.whitelist()
def fetch_old_so_list():
	return frappe.db.sql(
    	"""
		SELECT name FROM `tabSales Order`
		WHERE
			transaction_date between "2025-02-01" and "2025-02-19"
			AND docstatus = 1
			AND ifnull(status, "") != "Closed"
			AND abs(100 - per_billed) > 0.01
		ORDER BY
			transaction_date, name
	    """,
       #as_dict=1,
	)

@frappe.whitelist()
def update_old_so_item_batch(sales_order_name):
	stock_entry_name = frappe.get_value("Stock Entry", {"remarks": sales_order_name, "docstatus": 1}, "name")

	if stock_entry_name:
		stock_entry = frappe.get_doc("Stock Entry", stock_entry_name)
		sales_order = frappe.get_doc("Sales Order", sales_order_name)

		for item in stock_entry.items:
			# the Items child table array index starts from 0, where the idx field start from 1; hence array[0] = array[array.idx-1]
			try:
				if item.item_code == sales_order.items[item.idx-1].item_code and item.qty == sales_order.items[item.idx-1].qty:
					sales_order.items[item.idx-1].custom_batch_no = item.batch_no
			except Exception as err:
				return sales_order_name + "IndexError: list index out of range"

		sales_order.save()

		return "Updated " + sales_order_name
		
	else:
		return "No Stock Entry for " + sales_order_name


# Sales Order before_cancel hook
def cancel_stock_reservation(doc, method):
	if frappe.defaults.get_user_default("company") == 'Pour Tous Purchasing Service':
		if doc.custom_fs_transfer_status == "OK":
			payment_entry_name = frappe.get_value("Payment Entry Reference", {"reference_name": doc.name, "docstatus": 1}, "parent")
			if payment_entry_name:
				message = "Cannot Modify this document, as Payment Entry " + payment_entry_name + " has been received"
				frappe.throw(message)

		stock_entry_id = frappe.get_value("Stock Entry", {"remarks": doc.name}, "name")

		if stock_entry_id:
			stock_entry = frappe.get_doc("Stock Entry", stock_entry_id)
			stock_entry.cancel()
			frappe.db.commit()


# Sales Order before_submit hook
def make_stock_reservation(doc, method):
	# trigger the stock reservation hook, only if it is a modified doc
	if doc.amended_from and frappe.defaults.get_user_default("company") == 'Pour Tous Purchasing Service':
		stock_entry = frappe.new_doc("Stock Entry")

		stock_entry.company = doc.company
		stock_entry.stock_entry_type = "Material Transfer"
		stock_entry.remarks = doc.name

		# get company abbreviation
		abbr = frappe.get_value("Company", frappe.defaults.get_user_default("company"), 'abbr')
		s_warehouse = "Stall - " + abbr
		t_warehouse = "Sales Order Reserve - " + abbr

		for item in doc.items:
			item.warehouse = t_warehouse
			if item.custom_batch_no:
				stock_entry.append(
					"items",
					{
						"item_code": item.item_code,
						"s_warehouse": s_warehouse,
						"t_warehouse" : t_warehouse,
						"qty": item.qty,
						#"basic_rate": item.rate,
						"uom": item.uom,
						"stock_uom": item.stock_uom,
						"conversion_factor": item.conversion_factor or 1.0,
						"batch_no": item.custom_batch_no
					},
				)

			else:
				stock_entry.append(
					"items",
					{
						"item_code": item.item_code,
						"s_warehouse": s_warehouse,
						"t_warehouse" : t_warehouse,
						"qty": item.qty,
						#"basic_rate": item.rate,
						"uom": item.uom,
						"stock_uom": item.stock_uom,
						"conversion_factor": item.conversion_factor or 1.0,
						#"batch_no": item.custom_batch_no
					},
				)

		try:
			stock_entry.insert()
			stock_entry.submit()
		except Exception as err:
			raise err

		for se_item in stock_entry.items:
			# the Items child table array index starts from 0, where the idx field start from 1; hence array[0] = array[array.idx-1]
			if not doc.items[se_item.idx-1].custom_batch_no:
				doc.items[se_item.idx-1].custom_batch_no = se_item.batch_no
			# fetch the item price or batch price
			if doc.items[se_item.idx-1].rate == 0:
				if doc.items[se_item.idx-1].custom_batch_no:
					doc.items[se_item.idx-1].rate = frappe.get_value("Batch", doc.items[se_item.idx-1].custom_batch_no, "posa_batch_price")
					doc.items[se_item.idx-1].amount = doc.items[se_item.idx-1].rate * doc.items[se_item.idx-1].qty
					if doc.items[se_item.idx-1].rate == 0:
						frappe.msgprint(_("Price is not set for Item {0} Batch {1}").format(doc.items[se_item.idx-1].item_code, doc.items[se_item.idx-1].custom_batch_no))
				else:
					doc.items[se_item.idx-1].rate = frappe.get_value("Item Price", {"price_list": "Standard Selling", "item_code": doc.items[se_item.idx-1].item_code}, "price_list_rate")
					doc.items[se_item.idx-1].amount = doc.items[se_item.idx-1].rate * doc.items[se_item.idx-1].qty
					if doc.items[se_item.idx-1].rate == 0:
						frappe.msgprint(_("Price is not set for Item {0}").format(doc.items[se_item.idx-1].item_code))

				doc.calculate_taxes_and_totals()


@frappe.whitelist()
def get_tax_template(company, supplier):
	if frappe.db.get_value("Company", company, "gstin") and not frappe.db.get_value("Supplier", supplier, "gstin"):
		return frappe.get_list(
			'Purchase Taxes and Charges Template',
			{
				"company": company,
				"tax_category": "Reverse Charge In-State"
			},
			"name"
		)
		""" return frappe.get_list(
			'Purchase Taxes and Charges Template',
			{
				"company": company,
				"tax_category": "In-State"
			},
			"name"
		) """


@frappe.whitelist()
def get_sales_tax_template_form_script():
	return frappe.get_list(
		'Sales Taxes and Charges Template',
		{
			"company": frappe.defaults.get_user_default("company"),
			"tax_category": "In-State"
		},
		"name"
	)


@frappe.whitelist()
def get_purchase_tax_template(doc, method):
	tax_template = frappe.get_list(
		'Purchase Taxes and Charges Template',
		{
			"company": frappe.defaults.get_user_default("company"),
			"tax_category": "In-State"
		},
		"name"
	)
	#frappe.throw("before_insert")
	#doc.taxes_and_charges = tax_template[0].get("name")
	tax_doc = frappe.get_doc("Purchase Taxes and Charges Template", tax_template[0].get("name"))

	for tax_detail in tax_doc.taxes:
		found = any(tax.account_head == tax_detail.get("account_head") for tax in doc.taxes)
		if not found:
			doc.append("taxes",
				{
					"category": tax_detail.get("category"),
					"add_deduct_tax": tax_detail.get("add_deduct_tax"),
					"description": tax_detail.get("description"),
					"charge_type": "On Net Total",
					"account_head": tax_detail.get("account_head"),
					#"included_in_print_rate": tax_detail.get("included_in_print_rate"),
				}
			)


@frappe.whitelist()
def get_sales_tax_template(doc, method):
	tax_template = frappe.get_list(
		'Sales Taxes and Charges Template',
		{
			"company": frappe.defaults.get_user_default("company"),
			"tax_category": "In-State"
		},
		"name"
	)
	#frappe.throw("before_insert")
	#doc.taxes_and_charges = tax_template[0].get("name")
	tax_doc = frappe.get_doc("Sales Taxes and Charges Template", tax_template[0].get("name"))

	for tax_detail in tax_doc.taxes:
		found = any(tax.account_head == tax_detail.get("account_head") for tax in doc.taxes)
		if not found:
			doc.append("taxes",
				{
					"description": tax_detail.get("description"),
					"charge_type": "On Net Total",
					"account_head": tax_detail.get("account_head"),
					"included_in_print_rate": tax_detail.get("included_in_print_rate"),
				}
			)


def create_batch_barcode(doc, method):
	pre_barcode = '890' + doc.name
	doc.custom_barcode = pre_barcode + ean.calc_check_digit(pre_barcode)
	doc.save()
	#save the barcode in the Item table's barcode child-table
	item_doc = frappe.get_doc("Item", doc.item)
	item_doc.append("barcodes",
				{
					"barcode": doc.custom_barcode,
					"barcode_type": "EAN"
				}
	)
	item_doc.custom_skip_zoho_trigger = 1
	item_doc.save()


def create_item_barcode(item_code):
	item_doc = frappe.get_doc("Item", item_code)

	if not item_doc.barcodes: # in case there is no barcode, create/add one
		pre_barcode = '890' + item_code.zfill(9) # adding leading zeros to make 9 digits, plus the 3 digit country code
		item_barcode = pre_barcode + ean.calc_check_digit(pre_barcode)

		#save the barcode in the Item table's barcode child-table
		item_doc.append("barcodes",
					{
						"barcode": item_barcode,
						"barcode_type": "EAN"
					}
		)

		item_doc.custom_skip_zoho_trigger = 1
		item_doc.save()


def verify_batch_qty_for_barcode(doc, method):
	if doc.batch_qty == 0: #drop batch barcode from Item batch table, wben batch becomes empty
		frappe.db.delete("Item Barcode", {"barcode": doc.custom_barcode})

		# existing_item_barcode = frappe.db.get_value("Item Barcode", {"barcode": doc.custom_barcode}, "name")
		# if existing_item_barcode:
		# 	item_barcode_doc = frappe.get_doc("Item Barcode", existing_item_barcode)
		# 	item_barcode_doc.delete()
		# 	frappe.db.commit()


def verify_item_prerequisites(doc, method):
	if not doc.taxes:
		frappe.throw("Please enter a Tax Template")
	if not doc.valuation_rate:
		frappe.throw("Please enter a 'Valuation Rate': it can be the same as Buying or Selling Price")


@frappe.whitelist()
def fetch_batch_list():
	return frappe.db.sql(
    	"""
		select `tabStock Ledger Entry`.item_code,
		`tabStock Ledger Entry`.batch_no, `tabStock Ledger Entry`.warehouse,
		SUM(`tabStock Ledger Entry`.actual_qty) as qty, tabBatch.posa_batch_price AS price
		from `tabStock Ledger Entry`, tabBatch
		where `tabStock Ledger Entry`.is_cancelled = 0
		and `tabStock Ledger Entry`.batch_no = tabBatch.name
		AND tabBatch.batch_qty != 0
		AND tabBatch.posa_batch_price = 0
		AND `tabStock Ledger Entry`.batch_no LIKE "PT-BATCH%"
		group by `tabStock Ledger Entry`.batch_no
	    """,
        #as_dict=1,
    )

@frappe.whitelist()
def sync_batch_prices(batch):
	batch_price = frappe.db.get_value("Item Price", {"batch_no": batch}, "price_list_rate")
	if batch_price:
		frappe.db.set_value("Batch", batch, "posa_batch_price", batch_price)
		return {"OK"}


# called from the Purchase-Order Client-Script 'PO Supplier Item fetch'
@frappe.whitelist()
def supplier_items(supplier):
	query = frappe.db.sql(
		"""
		SELECT tabItem.item_code, tabItem.item_name,
		(
			select `tabStock Ledger Entry`.qty_after_transaction from `tabStock Ledger Entry`
			where (`tabStock Ledger Entry`.item_code = tabItem.item_code) and `tabStock Ledger Entry`.is_cancelled=0
			and warehouse like '{0}'
			order by posting_date desc, posting_time desc, creation desc
			limit 1
		) AS store_qty,
		(
			select `tabStock Ledger Entry`.qty_after_transaction from `tabStock Ledger Entry`
			where (`tabStock Ledger Entry`.item_code = tabItem.item_code) and `tabStock Ledger Entry`.is_cancelled=0
			and warehouse like '{1}'
			order by posting_date desc, posting_time desc, creation desc
			limit 1
		) AS stall_qty,
		(
			select SUM(actual_qty) from `tabStock Ledger Entry`
			where item_code = `tabItem Supplier`.parent
			AND voucher_type = "Sales Invoice"
			AND (month(date(`tabStock Ledger Entry`.posting_date))) = IF(month(curdate())-1, month(curdate())-1, 12)
		) AS sold_last_month, 
		(
			select SUM(actual_qty) from `tabStock Ledger Entry`
			where item_code = `tabItem Supplier`.parent
			AND voucher_type = "Sales Invoice"
			AND (month(date(`tabStock Ledger Entry`.posting_date)) = month(curdate()))
		) AS sold_this_month,
		tabItem.last_purchase_rate AS last_buy_price,
		(
			SELECT qty
			FROM `tabPurchase Invoice` pi, `tabPurchase Invoice Item` pii
			WHERE item_code = tabItem.item_code
			AND parent = pi.name
			AND supplier = '{2}'
			AND pi.is_return = 0
			AND pi.docstatus = 1
			ORDER BY posting_date DESC
			LIMIT 1
		) AS last_order_qty

		FROM tabItem, `tabItem Supplier`
		WHERE tabItem.item_code = `tabItem Supplier`.parent
		AND `tabItem Supplier`.supplier = '{2}'

		""".format("Stores%", "Stall%", supplier),
		as_dict=True
	)

	return query


# def supplier_batch_items(supplier):
# 	query = frappe.db.sql(
# 		"""
# 		SELECT tabItem.item_code, tabItem.item_name, tabItem.last_purchase_rate AS buying_price,
# 		`tabPurchase Receipt Item`.qty AS ordered_qty, MAX(`tabPurchase Receipt Item`.creation),
# 		(
# 			select `tabStock Ledger Entry`.qty_after_transaction from `tabStock Ledger Entry`
# 			where (`tabStock Ledger Entry`.item_code = tabItem.item_code) and `tabStock Ledger Entry`.is_cancelled=0
# 			and warehouse like '{0}'
# 			order by posting_date desc, posting_time desc, creation desc
# 			limit 1
# 		) AS store_qty,
# 		(
# 			select `tabStock Ledger Entry`.qty_after_transaction from `tabStock Ledger Entry`
# 			where (`tabStock Ledger Entry`.item_code = tabItem.item_code) and `tabStock Ledger Entry`.is_cancelled=0
# 			and warehouse like '{1}'
# 			order by posting_date desc, posting_time desc, creation desc
# 			limit 1
# 		) AS stall_qty,
# 		(
# 			select SUM(actual_qty) from `tabStock Ledger Entry`
# 			where item_code = `tabItem Supplier`.parent
# 			AND voucher_type = "Sales Invoice"
# 			AND (month(date(`tabStock Ledger Entry`.posting_date))) = IF(month(curdate())-1, month(curdate())-1, 12)
# 		) AS sold_last_month, 
# 		(
# 			select SUM(actual_qty) from `tabStock Ledger Entry`
# 			where item_code = `tabItem Supplier`.parent
# 			AND voucher_type = "Sales Invoice"
# 			AND (month(date(`tabStock Ledger Entry`.posting_date)) = month(curdate()))
# 		) AS sold_this_month
# 		FROM tabItem, `tabPurchase Receipt Item`, `tabItem Supplier`
# 		WHERE tabItem.has_batch_no = 1
# 		AND `tabItem Supplier`.supplier = '{2}'
# 		AND tabItem.item_code = `tabItem Supplier`.parent
# 		AND `tabPurchase Receipt Item`.item_code = tabItem.item_code
# 		GROUP BY tabItem.item_code
# 		""".format("Stores%", "Stall%", supplier),
# 		as_dict=True
# 	)
# 	return query


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def supplier_items_filter(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql(
		"""
		select parent, tabItem.item_name, tabItem.item_group
		from `tabItem Supplier`, tabItem
		where `tabItem Supplier`.parent = tabItem.name and supplier = %s
		""",
		txt
	)


def update_selling_price(doc, method):
	for item in doc.items:
		if item.custom_selling_price == 0:
			item.custom_selling_price = item.price_list_rate

def update_price_lists_item_barcode(doc, method):
	if (doc.doctype == "Purchase Invoice" and not doc.update_stock) or doc.is_return:
		return

	stock_settings = frappe.get_doc("Stock Settings")
	if stock_settings.update_existing_price_list_rate:
		custom_update_buying_price = False
	else:
		custom_update_buying_price = True

	#if frappe.defaults.get_user_default("company") == "Pour Tous Distribution Center":
	#	return update_price_lists_ptdc(doc, method)

	for item in doc.items:
		if item.batch_no:
			if item.custom_selling_price > 0:
				frappe.set_value("Batch", item.batch_no, "posa_batch_price", item.custom_selling_price)
			# else:
			# 	frappe.set_value("Batch", item.batch_no, "posa_batch_price", item.price_list_rate)

			frappe.set_value("Batch", item.batch_no, "custom_buying_price", item.price_list_rate)

		else:
			# Update the Item Barcode for non-batch Items
			create_item_barcode(item.item_code)

		#existing_item_sell_price_entry = frappe.get_value("Item Price", {"price_list": "Standard Selling", "item_code": item.item_code}, "name")
		existing_item_sell_price_entry = frappe.db.get_list(
			"Item Price",
			filters={"price_list": "Standard Selling", "item_code": item.item_code},
			fields = ["name"],
			order_by='creation desc',
		)
		if len(existing_item_sell_price_entry) > 1:
			frappe.db.delete("Item Price", {"name": existing_item_sell_price_entry[1]['name']})

		if existing_item_sell_price_entry:
			if item.custom_selling_price > 0:
				frappe.db.set_value("Item Price", existing_item_sell_price_entry[0]['name'], "price_list_rate", item.custom_selling_price)
			# else:
			# 	frappe.db.set_value("Item Price", existing_item_sell_price_entry, "price_list_rate", item.price_list_rate)

		else:
			if item.custom_selling_price > 0:
				item_price = frappe.get_doc({
					"doctype": "Item Price",
					"item_code": item.item_code,
					"uom": item.uom,
					"price_list": "Standard Selling",
					"price_list_rate": item.custom_selling_price,
					#"batch_no": item.batch_no
				})

			""" else:
				item_price = frappe.get_doc({
					"doctype": "Item Price",
					"item_code": item.item_code,
					"uom": item.uom,
					"price_list": "Standard Selling",
					"price_list_rate": item.price_list_rate,
					#"batch_no": item.batch_no
				}) """

			item_price.insert()

		if custom_update_buying_price:
			existing_item_buy_price_entry = frappe.db.get_list(
				"Item Price",
				filters={"price_list": "Standard Buying", "item_code": item.item_code},
				fields = ["name"],
				order_by='creation desc',
			)
			if len(existing_item_buy_price_entry) > 1:
				frappe.db.delete("Item Price", {"name": existing_item_buy_price_entry[1]['name']})

			if existing_item_buy_price_entry:
				frappe.db.set_value("Item Price", existing_item_buy_price_entry[0]['name'], "price_list_rate", item.price_list_rate)

	frappe.db.commit()


def stock_recon_update_price_lists(doc, method):
	if doc.purpose == "Stock Reconciliation":
		for item in doc.items:
			if item.batch_no:
				if item.custom_selling_price > 0:
					frappe.set_value("Batch", item.batch_no, "posa_batch_price", item.custom_selling_price)
					item.valuation_rate = item.custom_selling_price

			existing_item_sell_price_entry = frappe.get_value("Item Price", {"price_list": "Standard Selling", "item_code": item.item_code}, "name")
			if existing_item_sell_price_entry:
				if item.custom_selling_price > 0:
					frappe.db.set_value("Item Price", existing_item_sell_price_entry, "price_list_rate", item.custom_selling_price)

			else:
				if item.custom_selling_price > 0:
					item_price = frappe.get_doc({
						"doctype": "Item Price",
						"item_code": item.item_code,
						"uom": frappe.db.get_value('Item', item.item_code, 'stock_uom'),
						"price_list": "Standard Selling",
						"price_list_rate": item.custom_selling_price,
						#"batch_no": item.batch_no
					})

					item_price.insert()

	frappe.db.commit()


def update_difference_account(doc, method):
	adjustment_account = frappe.db.get_value("Account", {"account_name": "Stock Adjustment"}, "name")

	for item in doc.items:
		item.expense_account = adjustment_account

def stock_entry_update_price_lists(doc, method):
	if doc.stock_entry_type == "Repack":
		for item in doc.items:
			if item.batch_no:
				if item.custom_selling_price > 0:
					frappe.set_value("Batch", item.batch_no, "posa_batch_price", item.custom_selling_price)
					item.valuation_rate = item.custom_selling_price
				else:
					frappe.set_value("Batch", item.batch_no, "posa_batch_price", item.basic_rate)
					item.valuation_rate = item.basic_rate

				frappe.set_value("Batch", item.batch_no, "custom_buying_price", item.basic_rate)

			existing_item_sell_price_entry = frappe.get_value("Item Price", {"price_list": "Standard Selling", "item_code": item.item_code}, "name")
			if existing_item_sell_price_entry:
				if item.custom_selling_price > 0:
					frappe.db.set_value("Item Price", existing_item_sell_price_entry, "price_list_rate", item.custom_selling_price)
				# else:
				# 	frappe.db.set_value("Item Price", existing_item_sell_price_entry, "price_list_rate", item.basic_rate)

			else:
				if item.custom_selling_price > 0:
					item_price = frappe.get_doc({
						"doctype": "Item Price",
						"item_code": item.item_code,
						"uom": item.uom,
						"price_list": "Standard Selling",
						"price_list_rate": item.custom_selling_price,
						#"batch_no": item.batch_no
					})

				else:
					item_price = frappe.get_doc({
						"doctype": "Item Price",
						"item_code": item.item_code,
						"uom": item.uom,
						"price_list": "Standard Selling",
						"price_list_rate": item.basic_rate,
						#"batch_no": item.batch_no
					})

				item_price.insert()

	frappe.db.commit()


# creates credit vouchers for returns at PTDC (for pre-paid member accounts)
# called from hooks.py when "Sales Invoice" documents are submitted
def payment_entry_for_return(doc, method):
	if doc.status == "Return" and (doc.company == "Pour Tous Distribution Center" or 
								(doc.company == "Pour Tous Purchasing Service" and doc.payments[0].mode_of_payment != 'FS')):
	#if doc.status == "Return" and frappe.get_value("Sales Invoice", doc.return_against, "custom_fs_transfer_status") != "Insufficient Funds":
		# Check below whether all the MOP have amount == 0
		mop_cash_list = [
        	i.mode_of_payment
        	for i in doc.payments
			if i.amount != 0
        	#if "cash" in i.mode_of_payment.lower() and i.type == "Cash"
    	]
		if len(mop_cash_list) == 0:
			cash_account = {
            	"account": frappe.get_value(
                	"Company", doc.company, "default_cash_account"
            	)
        	}
		else:
			return

    	# creating advance payment
		advance_payment_entry = frappe.get_doc(
            {
               	"doctype": "Payment Entry",
               	#"mode_of_payment": "Cash",
               	"paid_to": cash_account["account"],
               	"payment_type": "Receive",
               	"party_type": "Customer",
               	"party": doc.customer,
               	"paid_amount": -(doc.grand_total),
               	"received_amount": -(doc.grand_total),
               	"company": doc.company,
				"custom_remarks": 1,
				"remarks": doc.name
            }
        )

		advance_payment_entry.flags.ignore_permissions = True
		frappe.flags.ignore_account_permission = True
		advance_payment_entry.insert()
		advance_payment_entry.submit()


""" def delete_item_batch(doc, method):
	for item in doc.items:
		if item.batch_no:
			frappe.delete_doc('Batch', item.batch_no) """

""" def delete_item_price(doc, method):
	for item in doc.items:
		if item.batch_no:
			item_price_name = frappe.get_list('Item Price', filters = {"batch_no": item.batch_no})	# returns a list of dicts (key value pairs)
			frappe.delete_doc('Item Price', item_price_name[0].name)	# item_price_name[0].name extracts the value of key 'name' """

# was called from Customer Client-Script 'Sync FS Accounts'
""" @frappe.whitelist()
def sync_fs_accounts():
	#with open('customer_import.txt', 'w') as file:
	#	file.write(str("inside validate_customer_imports"))
	#frappe.throw("inside validate_customer_imports")

	fs_account_records = frappe.get_all("FS Account Details", pluck='name')

	for record in fs_account_records:
		fs_account_doc = frappe.get_doc("FS Account Details", record)
		existing_customer_id = frappe.get_value("Customer", {"custom_fs_account_number": fs_account_doc.account_number}, "name")

		if existing_customer_id:
			if fs_account_doc.account_type == 3:
				frappe.db.set_value("Customer", existing_customer_id, "custom_fs_kind_account_3", 1)
			elif fs_account_doc.account_type == 4:
				frappe.db.set_value("Customer", existing_customer_id, "custom_fs_cash_account_4", 1)

		elif fs_account_doc.account_type == 3:
			new_customer_doc = frappe.get_doc({
				"doctype": "Customer",
				"customer_name": fs_account_doc.account_name,
				"custom_fs_account_number": fs_account_doc.account_number,
				"custom_fs_kind_account_3": 1,
				"disabled": fs_account_doc.disabled,
				"territory": "India",
				"customer_type": "Individual",
				"customer_group": "Individual"
			})
			new_customer_doc.save()

		elif fs_account_doc.account_type == 4:
			new_customer_doc = frappe.get_doc({
				"doctype": "Customer",
				"customer_name": fs_account_doc.account_name,
				"custom_fs_account_number": fs_account_doc.account_number,
				"custom_fs_cash_account_4": 1,
				"disabled": fs_account_doc.disabled,
				"territory": "India",
				"customer_type": "Individual",
				"customer_group": "Individual"
			})
			new_customer_doc.save() """