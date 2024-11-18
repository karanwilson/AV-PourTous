// Copyright (c) 2024, Karan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Veg Fruit Prices"] = {
	"filters": [
		{
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "Select",
			"options": ["", "0710/VEGETABLES", "0810 Fresh fruits, pomgranate,kiwi,black,white,red currants,lichi,tamarind,strawberry,chico,black berries, cranberries,durians"],
			"width": "60px"
		},

		{
			"fieldname": "price_list",
			"label": __("Price List"),
			"fieldtype": "Select",
			"options": ["", "Standard Buying", "Standard Selling"],
			"width": "60px"
		},
	]
};