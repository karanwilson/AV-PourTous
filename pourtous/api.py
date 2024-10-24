import frappe
from frappe import _
from frappe.utils import flt
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account


# called from Customer Client-Script 'Sync FS Accounts'
@frappe.whitelist(allow_guest=True)
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
			new_customer_doc.save()


# called from the Purchase-Order Client-Script 'PO Supplier Item fetch'
@frappe.whitelist(allow_guest=True)
#@frappe.validate_and_sanitize_search_inputs
def supplier_batch_items(supplier):
	query = frappe.db.sql(
		"""
		SELECT tabItem.item_code, tabItem.item_name, tabItem.last_purchase_rate AS buying_price,
		`tabItem Price`.price_list_rate AS selling_price,
		`tabPurchase Receipt Item`.qty AS ordered_qty, MAX(`tabPurchase Receipt Item`.creation),
		SUM(tabBatch.batch_qty) AS batch_qty,
		(
			SELECT SUM(`tabSales Invoice Item`.qty)
			FROM `tabSales Invoice Item`
			WHERE (`tabSales Invoice Item`.item_code = tabItem.item_code) AND (month(date(`tabSales Invoice Item`.creation)) = month(curdate())-1)
		) AS sold_last_month,
		(
			SELECT SUM(`tabSales Invoice Item`.qty)
			FROM `tabSales Invoice Item`
			WHERE (`tabSales Invoice Item`.item_code = tabItem.item_code) AND (month(date(`tabSales Invoice Item`.creation)) = month(curdate()))
		) AS sold_this_month
		FROM tabItem, `tabItem Price`, `tabPurchase Receipt Item`, tabBatch
		WHERE tabBatch.supplier = %s
		AND `tabItem Price`.item_code = tabItem.item_code AND `tabItem Price`.selling = 1
		AND `tabPurchase Receipt Item`.item_code = tabItem.item_code
		AND tabItem.item_code = tabBatch.item AND tabBatch.batch_qty > 0
		GROUP BY tabItem.item_code
		""",
		supplier,
		as_dict=True
	)
	return query

# called from the Purchase-Order Client-Script 'PO Supplier Item fetch'
@frappe.whitelist(allow_guest=True)
def supplier_items(supplier):
	query = frappe.db.sql(
		"""
		SELECT tabItem.item_code, tabItem.item_name, tabItem.last_purchase_rate AS buying_price,
		`tabItem Price`.price_list_rate AS selling_price,
		`tabPurchase Receipt Item`.qty AS ordered_qty, MAX(`tabPurchase Receipt Item`.creation),
		(
			SELECT SUM(`tabSales Invoice Item`.qty)
			FROM `tabSales Invoice Item`
			WHERE (`tabSales Invoice Item`.item_code = tabItem.item_code) AND (month(date(`tabSales Invoice Item`.creation)) = month(curdate())-1)
		) AS sold_last_month,
		(
			SELECT SUM(`tabSales Invoice Item`.qty)
			FROM `tabSales Invoice Item`
			WHERE (`tabSales Invoice Item`.item_code = tabItem.item_code) AND (month(date(`tabSales Invoice Item`.creation)) = month(curdate()))
		) AS sold_this_month
		FROM tabItem, `tabItem Price`, `tabPurchase Receipt Item`, `tabItem Supplier`
		WHERE `tabItem Supplier`.supplier = %s
		AND `tabItem Price`.item_code = tabItem.item_code AND `tabItem Price`.selling = 1
		AND `tabPurchase Receipt Item`.item_code = tabItem.item_code
		AND tabItem.item_code = `tabItem Supplier`.parent
		GROUP BY tabItem.item_code
		""",
		supplier,
		as_dict=True
	)
	return query

@frappe.whitelist(allow_guest=True)
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


# creates credit vouchers for returns at PTDC (for pre-paid member accounts)
# called from hooks.py when "Sales Invoice" documents are submitted
def payment_entry_for_return(doc, method):
	if doc.company == "Pour Tous Distribution Center" and doc.status == "Return":
		mop_cash_list = [
        	i.mode_of_payment
        	for i in doc.payments
        	if "cash" in i.mode_of_payment.lower() and i.type == "Cash"
    	]
		if len(mop_cash_list) > 0:
			cash_account = get_bank_cash_account(mop_cash_list[0], doc.company)
		else:
			cash_account = {
            	"account": frappe.get_value(
                	"Company", doc.company, "default_cash_account"
            	)
        }

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
            }
        )

		advance_payment_entry.flags.ignore_permissions = True
		frappe.flags.ignore_account_permission = True
		advance_payment_entry.insert()
		advance_payment_entry.submit()


# called from hooks.py when a 'Purchase Receipt' document is submitted
# below we access the 'Purchase Receipt Item' document (via items[]), which is a child doctype of the 'Purchase Receipt' document
def apply_tax_template(doc, method):

	if doc.doctype == "Sales Invoice":
		doc.tax_category = "In-State"

	else:
		# need to dynamically evaluate the taxes_and_charges name (as per company account)
		if not doc.taxes_and_charges:
			doc.taxes_and_charges = 'Input GST In-state - PTPS'

		if doc.taxes_and_charges == 'Input GST In-state - PTPS' and not doc.taxes:
			taxes_row1 = frappe.get_doc({
				'doctype': 'Purchase Taxes and Charges',
				'category': 'Total',
				'charge_type': 'On Net Total',
				'account_head': 'Input Tax CGST - PTPS',
				'add_deduct_tax': 'Add',
				'description': 'CGST',
				'parent': doc.name,
				'parenttype': 'Purchase Receipt'
			})
			taxes_row2 = frappe.get_doc({
				'doctype': 'Purchase Taxes and Charges',
				'category': 'Total',
				'charge_type': 'On Net Total',
				'account_head': 'Input Tax SGST - PTPS',
				'add_deduct_tax': 'Add',
				'description': 'SGST',
				'parent': doc.name,
				'parenttype': 'Purchase Receipt'
			})
			doc.taxes.append(taxes_row1)
			doc.taxes.append(taxes_row2)

""" Comment the below code until the pricing rule/method is defined"""
def update_selling_price_list(doc, method):
	for item in doc.items:
		# creating a tax inclusive item-price for POSA
		if item.custom_rate_with_tax:
			rate_tax_incl = item.custom_rate_with_tax
		else:
			# using flt for setting precision
			rate_tax_incl = item.rate + flt((item.igst_amount + item.cgst_amount + item.sgst_amount + item.cess_amount)/item.qty)

		item_price = frappe.get_doc({
			"doctype": "Item Price",
			"item_code": item.item_code,
			"uom": item.uom,
			"price_list": "Standard Selling",
			"price_list_rate": rate_tax_incl,
			"batch_no": item.batch_no
		})
		item_price.insert()

def delete_item_price(doc, method):
	for item in doc.items:
		item_price_name = frappe.get_list('Item Price', filters = {"batch_no": item.batch_no})	# returns a list of dicts (key value pairs)
		frappe.delete_doc('Item Price', item_price_name[0].name)	# item_price_name[0].name extracts the value of key 'name'