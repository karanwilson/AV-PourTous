app_name = "pourtous"
app_title = "pourtous"  
app_publisher = "Karan"
app_description = "Pour Tous App for ERPNext"
app_email = "karan.wilson@auroville.org.in"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/pourtous/css/pourtous.css"
# app_include_js = "/assets/pourtous/js/pourtous.js"

app_include_js = [
    "/assets/pourtous/node_modules/vuetify/dist/vuetify.js",
    "pourtous.bundle.js",
]

# include js, css files in header of web template
# web_include_css = "/assets/pourtous/css/pourtous.css"
# web_include_js = "/assets/pourtous/js/pourtous.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "pourtous/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "pourtous.utils.jinja_methods",
# 	"filters": "pourtous.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "pourtous.install.before_install"
# after_install = "pourtous.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "pourtous.uninstall.before_uninstall"
# after_uninstall = "pourtous.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "pourtous.utils.before_app_install"
# after_app_install = "pourtous.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "pourtous.utils.before_app_uninstall"
# after_app_uninstall = "pourtous.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "pourtous.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    #"Sales Invoice": {
    #    "on_submit": "pourtous.api.payment_entry_for_return" # creates 'Payment Entry' for item returns
	#},
    #"Payment Entry": {
        # initiates an FS transfer for Participant Contributions (Monthly and Extra)
        #"before_save": "payments.payment_gateways.doctype.fs_settings.fs_settings.add_transfer_contribution"
	#},
	"Item": {
		"before_insert": "pourtous.api.verify_tax_template", # verifies whether a tax template was added
        #"before_save": "pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.update_item_in_zoho", # update Zoho Books
        #"on_trash": "pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.delete_item_in_zoho" # update Zoho Books
	},
	"Customer": {
        #"before_save": "pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.update_contact_in_zoho",
        #"on_trash": "pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.delete_contact_in_zoho"
	},
	"Supplier": {
        #"before_save": "pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.update_supplier_contact_in_zoho",
        #"on_trash": "pourtous.pourtous.doctype.zoho_books_api.zoho_books_api.delete_contact_in_zoho"
	},
    # comment the hook below until the pricing rule/method is defined
	"Purchase Receipt": {
		"on_submit": "pourtous.api.update_price_lists", # Add the 'Item Price'
	},
    "Batch": {
        "after_insert": "pourtous.api.create_barcode", # Adds a Batch Barcode
    },
    "Sales Order": {
        "before_cancel": "pourtous.api.cancel_stock_reservation", # removes the associated Sales Order Stock Reservation
        "before_submit": "pourtous.api.make_stock_reservation" # adds stock reservation for the Sales Order
    },
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"pourtous.tasks.all"
# 	],
# 	"daily": [
# 		"pourtous.tasks.daily"
# 	],
# 	"hourly": [
# 		"pourtous.tasks.hourly"
# 	],
# 	"weekly": [
# 		"pourtous.tasks.weekly"
# 	],
# 	"monthly": [
# 		"pourtous.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "pourtous.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "pourtous.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "pourtous.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["pourtous.utils.before_request"]
# after_request = ["pourtous.utils.after_request"]

# Job Events
# ----------
# before_job = ["pourtous.utils.before_job"]
# after_job = ["pourtous.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"pourtous.auth.validate"
# ]

fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                (
					"Item-custom_select_add_on_item", # To select the Add-On Item for configuring Item-add-ons bundling
					"Item-custom_item_add_on", # Automatically pulls the item_code from the above selection
                    "Item-custom_uom_int", #'UOM INT' for fetching stock_uom.must_be_whole_number setting from Item doctype
                    "Item-custom_zoho_item_id", # required in case we create Invoices/Purchases on Zoho Books, via API
                    				#-used in code to prevent decimal entries in Integer values
                    "Payment Entry-custom_contribution_type", # for PTDC Contributions FS Transactions
                    "Payment Entry-custom_fs_transfer_status", # for PTDC contribution Entry transactions
                    "Sales Invoice-custom_fs_transfer_status", # for POS-Billing FS Transactions
                    "Sales Invoice-custom_fs_account_number", # to Identify Invoice based on FS Account number
                    "Sales Invoice-custom_transaction_date", # in case transaction date is earlier than the posting date
                    "Sales Invoice-custom_staff_member", # in case of accounts shared by a group
                    "Sales Invoice-custom_zb_sync_status", # for syncing with Zoho Books
                    "Sales Order-custom_fs_account_number", # to Identify Sales Order based on FS Account number
                    "Sales Order-custom_fs_transfer_status", # for FS Transactions
                    "Sales Order Item-custom_batch_no", # for SO Stock reservations
                    "Customer-custom_fs_account_number", # for FS Transactions
                    "Customer-custom_fs_kind_account_3", # for FS Transactions
                    "Customer-custom_fs_cash_account_4", # for FS Transactions
                    "Customer-custom_zoho_contact_id", # required in case we create Invoices/Purchases on Zoho Books, via API
                    "Customer-custom_update_zoho_contact", # to prevent trigger of Zoho Contact update, during the FS account update script.

                    "Supplier-custom_zoho_contact_id", # required in case we create Invoices/Purchases on Zoho Books, via API

                    "Purchase Order-custom_batch_items", # Creates a Tab Break for custom_batch_items_data and custom_add_batch_items
                    "Purchase Order-custom_batch_items_fetch", # Button
                    "Purchase Order-custom_batch_items_data", # To fetch the Items from the Selected Supplier, along with the required data
                    "Purchase Order-custom_add_batch_items", # Button: pushes the Selected Items (and their Qty) to the PO Items

                    "Purchase Order-custom_non_batch_items", # Creates a Tab Break for custom_non_batch_items_data and custom_add_non_batch_items
                    "Purchase Order-custom_non_batch_items_fetch", # Button
                    "Purchase Order-custom_non_batch_items_data", # To fetch the Items from the Selected Supplier, along with the required data
                    "Purchase Order-custom_add_non_batch_items", # Button: pushes the Selected Items (and their Qty) to the PO Items

                    "Purchase Order Item-custom_comments", # for putting custom UOM (like bag, etc.) in Purchase Orders

                    "Purchase Receipt Item-custom_selling_price", # for setting the Selling Price

                    "Stock Reconciliation Item-custom_comments", # to add comments regarding a stock reconciliation

                    "Batch-custom_barcode", # for adding a batch barcode
                    "Batch-custom_buying_price", # for recording batch wise buying price
				)
			]
		]
	}
]
