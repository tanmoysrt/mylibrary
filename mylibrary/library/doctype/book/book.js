// Copyright (c) 2026, Tanmoy Sarkar and contributors
// For license information, please see license.txt

frappe.ui.form.on("Book", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Issue"), () => {
				frappe.new_doc("Book Register", { book: frm.doc.name });
			});
		}
	},
});
