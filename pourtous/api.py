import frappe
from frappe import _
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
def supplier_items(supplier):
	return frappe.db.sql(
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
		supplier
	)


# called from hooks.py when "Sales Invoice" documents are submitted
def payment_entry_for_return(doc, method):
	if doc.status == "Return":
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
		advance_payment_entry.save()
		advance_payment_entry.submit()


""" Comment the below code until the pricing rule/method is defined"""
# called from hooks.py when a 'Purchase Receipt' document is submitted
# below we access the 'Purchase Receipt Item' document (via items[0]), which is a child doctype of the 'Purchase Receipt' document
def update_selling_price_list(doc, method):
	for item in doc.items:
		item_price = frappe.get_doc({
			"doctype": "Item Price",
			"item_code": item.item_code,
			"uom": item.uom,
			"price_list": "Standard Selling",
			"price_list_rate": item.rate,
			"batch_no": item.batch_no
		})
		item_price.insert()

def delete_item_price(doc, method):
	for item in doc.items:
		item_price_name = frappe.get_list('Item Price', filters = {"batch_no": item.batch_no})	# returns a list of dicts (key value pairs)
		frappe.delete_doc('Item Price', item_price_name[0].name)	# item_price_name[0].name extracts the value of key 'name'