frappe.ui.form.on('Sales Invoice', {
	refresh(frm) {
		// your code here
		frm.add_custom_button('Submit Offline FS Bills', () => {
		    frappe.call({
		        
		    })
		})
	}
})