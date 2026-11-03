// Copyright (c) 2026, Tanmoy Sarkar and contributors
// For license information, please see license.txt

frappe.ui.form.on("Book Register", {
	refresh(frm) {
		if (frm.doc.docstatus === 1 && !frm.doc.returned_on) {
			frm.add_custom_button(__("Mark Returned"), () => {
				frm.call("mark_returned").then(() => frm.reload_doc());
			});
		}
	},
});
