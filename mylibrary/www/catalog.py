import frappe

no_cache = 1


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/catalog"
		raise frappe.Redirect
	context.title = "Catalog"
	context.no_breadcrumbs = True
