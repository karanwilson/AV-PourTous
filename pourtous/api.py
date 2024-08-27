import frappe
from frappe import _
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account


# called from the Purchase-Order Client-Script called 'PO Supplier Item fetch'
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def supplier_items(supplier):
	# using 'distinct' in the sql statement below because sometimes the testing instance has 4 rows for each supplier-item combination in `tabItem Supplier`
	# this could be because the masters were reuploaded more than once (after deleting company/accounting data) during the testing..
	return frappe.db.sql(
		"""
		select distinct parent, tabItem.item_name, tabItem.item_group
		from `tabItem Supplier`, tabItem
		where `tabItem Supplier`.parent = tabItem.name and supplier = %s
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


""" Commenting the below code as I first need to explore Pricing Rules in order to set the correct markups for the Item Prices

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
"""