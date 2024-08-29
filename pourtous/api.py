import frappe
from frappe import _
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account


# called from the Purchase-Order Client-Script called 'PO Supplier Item fetch'
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def supplier_items(supplier):
	return frappe.db.sql(
		"""
		SELECT tabItem.item_code, tabItem.item_name, tabItem.item_group, tabItem.last_purchase_rate AS buying_price,
		`tabItem Price`.price_list_rate AS selling_price,
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
		FROM tabItem, tabBatch, `tabItem Price`
		WHERE tabBatch.supplier = %s
		AND tabItem.item_code = tabBatch.item AND tabBatch.batch_qty > 0
		AND `tabItem Price`.item_code = tabItem.item_code AND `tabItem Price`.selling = 1
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


""" Commenting the below code until the pricing rule/method is defined"""

# called from hooks.py when a 'Purchase Receipt' document is submitted
# below we access the 'Purchase Receipt Item' document (via items[0]), which is a child doctype of the 'Purchase Receipt' document
def update_selling_price_list(doc, method):
	item_price = frappe.get_doc({
		"doctype": "Item Price",
		"item_code": doc.items[0].item_code,
		"uom": doc.items[0].uom,
		"price_list": "Standard Selling",
		"price_list_rate": doc.items[0].rate,
		"batch_no": doc.items[0].batch_no
	})
	item_price.insert()

def delete_item_price(doc, method):
	item_price_name = frappe.get_list('Item Price', filters = {"batch_no": doc.items[0].batch_no})	# returns a list of dicts (key value pairs)
	frappe.delete_doc('Item Price', item_price_name[0].name)	# item_price_name[0].name extracts the value of key 'name'