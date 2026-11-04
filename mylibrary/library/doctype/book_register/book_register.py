# Copyright (c) 2026, Tanmoy Sarkar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, getdate, today

LOAN_DAYS = 14


class BookRegister(Document):
	def validate(self):
		if not self.due_date:
			self.due_date = add_days(self.issue_date, LOAN_DAYS)
		if getdate(self.due_date) < getdate(self.issue_date):
			frappe.throw(_("Due Date cannot be before Issue Date"))

	def on_submit(self):
		available = frappe.db.get_value("Book", self.book, "available_copies", for_update=True)
		if available < 1:
			frappe.throw(_("No copies of {0} are available").format(self.book_title or self.book))
		frappe.db.set_value("Book", self.book, "available_copies", available - 1)

	def on_cancel(self):
		if not self.returned_on:
			restore_copy(self.book)

	@frappe.whitelist()
	def mark_returned(self):
		self.check_permission("write")
		if self.docstatus != 1:
			frappe.throw(_("Only submitted entries can be returned"))
		if frappe.db.get_value(self.doctype, self.name, "returned_on", for_update=True):
			frappe.throw(_("{0} is already returned").format(self.name))
		self.db_set("returned_on", today())
		restore_copy(self.book)


def restore_copy(book: str):
	frappe.db.sql(
		"update `tabBook` set available_copies = available_copies + 1 where name = %s",
		book,
	)
