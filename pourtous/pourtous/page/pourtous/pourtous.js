frappe.pages['pourtous'].on_page_load = function(wrapper) {
	let page = frappe.ui.make_app_page({
		title: 'Pour Tous',
		parent: wrapper,
		single_column: true
	});
	this.page.$PourTous = new frappe.PourTous.pourtous(this.page);
};