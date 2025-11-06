// Copyright (c) 2025, Karan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Zoho Books API', {
	refresh: function(frm) {
		frm.set_query("income_account", () => {
			return {
				filters: {
					filter_by: 'Income'
				},
			};
		});

		frm.set_query("expense_account", () => {
			return {
				filters: {
					filter_by: 'Expense'
				},
			};
		});
	}
});
