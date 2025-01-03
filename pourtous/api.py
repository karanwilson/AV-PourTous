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
		`tabPurchase Receipt Item`.qty AS ordered_qty, MAX(`tabPurchase Receipt Item`.creation),
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
			SELECT SUM(`tabSales Invoice Item`.qty)
			FROM `tabSales Invoice Item`
			WHERE (`tabSales Invoice Item`.item_code = tabItem.item_code) AND (month(date(`tabSales Invoice Item`.creation)) = month(curdate())-1)
		) AS sold_last_month,
		(
			SELECT SUM(`tabSales Invoice Item`.qty)
			FROM `tabSales Invoice Item`
			WHERE (`tabSales Invoice Item`.item_code = tabItem.item_code) AND (month(date(`tabSales Invoice Item`.creation)) = month(curdate()))
		) AS sold_this_month
		FROM tabItem, `tabPurchase Receipt Item`, `tabItem Supplier`
		WHERE tabItem.has_batch_no = 1
		AND `tabItem Supplier`.supplier = '{2}'
		AND tabItem.item_code = `tabItem Supplier`.parent
		AND `tabPurchase Receipt Item`.item_code = tabItem.item_code
		GROUP BY tabItem.item_code
		""".format("Stores%", "Stall%", supplier),
		as_dict=True
	)
	return query

# called from the Purchase-Order Client-Script 'PO Supplier Item fetch'
@frappe.whitelist(allow_guest=True)
def supplier_non_batch_items(supplier):
	query = frappe.db.sql(
		"""
		SELECT tabItem.item_code, tabItem.item_name, tabItem.last_purchase_rate AS buying_price,
		`tabPurchase Receipt Item`.qty AS ordered_qty, MAX(`tabPurchase Receipt Item`.creation),
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
			SELECT SUM(`tabSales Invoice Item`.qty)
			FROM `tabSales Invoice Item`
			WHERE (`tabSales Invoice Item`.item_code = tabItem.item_code) AND (month(date(`tabSales Invoice Item`.creation)) = month(curdate())-1)
		) AS sold_last_month,
		(
			SELECT SUM(`tabSales Invoice Item`.qty)
			FROM `tabSales Invoice Item`
			WHERE (`tabSales Invoice Item`.item_code = tabItem.item_code) AND (month(date(`tabSales Invoice Item`.creation)) = month(curdate()))
		) AS sold_this_month
		FROM tabItem, `tabPurchase Receipt Item`, `tabItem Supplier`
		WHERE tabItem.has_batch_no = 0
		AND `tabItem Supplier`.supplier = '{2}'
		AND `tabPurchase Receipt Item`.item_code = tabItem.item_code
		AND tabItem.item_code = `tabItem Supplier`.parent
		GROUP BY tabItem.item_code
		""".format("Stores%", "Stall%", supplier),
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
	#if doc.company == "Pour Tous Distribution Center" and doc.status == "Return":
	if doc.status == "Return" and frappe.get_value("Sales Invoice", doc.return_against, "custom_fs_transfer_status") != "Insufficient Funds":
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

		""" if len(mop_cash_list) > 0:
			cash_account = get_bank_cash_account(mop_cash_list[0], doc.company)
		else:
			cash_account = {
            	"account": frappe.get_value(
                	"Company", doc.company, "default_cash_account"
            	)
        	} """

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


def update_selling_price_list(doc, method):
	for item in doc.items:

		if not item.batch_no:
			existing_item_price_entry = frappe.get_value("Item Price", {"price_list": "Standard Selling", "item_code": item.item_code}, "name")
			if existing_item_price_entry:
				frappe.db.set_value("Item Price", existing_item_price_entry, "price_list_rate", item.rate)
				frappe.db.commit()

			else:
				item_price = frappe.get_doc({
					"doctype": "Item Price",
					"item_code": item.item_code,
					"uom": item.uom,
					"price_list": "Standard Selling",
					"price_list_rate": item.rate,
					#"batch_no": item.batch_no
				})
				item_price.insert()

		else:
			frappe.set_value("Batch", item.batch_no, "posa_batch_price", item.rate)
			frappe.db.commit()
			""" item_price = frappe.get_doc({
				"doctype": "Item Price",
				"item_code": item.item_code,
				"uom": item.uom,
				"price_list": "Standard Selling",
				"price_list_rate": item.rate,
				"batch_no": item.batch_no
			})
			item_price.insert() """

""" def delete_item_batch(doc, method):
	for item in doc.items:
		if item.batch_no:
			frappe.delete_doc('Batch', item.batch_no) """

""" def delete_item_price(doc, method):
	for item in doc.items:
		if item.batch_no:
			item_price_name = frappe.get_list('Item Price', filters = {"batch_no": item.batch_no})	# returns a list of dicts (key value pairs)
			frappe.delete_doc('Item Price', item_price_name[0].name)	# item_price_name[0].name extracts the value of key 'name' """