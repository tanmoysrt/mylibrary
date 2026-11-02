# Copyright (c) 2026, Tanmoy Sarkar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


def normalize_isbn(value: str) -> str:
	return "".join(character for character in (value or "") if character.isdigit())


def is_valid_isbn13(isbn: str) -> bool:
	if len(isbn) != 13 or not isbn.isdigit():
		return False
	total = sum(int(digit) * (3 if index % 2 else 1) for index, digit in enumerate(isbn[:12]))
	return (10 - total % 10) % 10 == int(isbn[12])


class Book(Document):
	def validate(self):
		self.isbn = normalize_isbn(self.isbn)
		if not is_valid_isbn13(self.isbn):
			frappe.throw(_("{0} is not a valid ISBN-13").format(self.isbn))
		self.update_available_copies()

	def update_available_copies(self):
		if self.is_new():
			self.available_copies = self.total_copies
			return
		previous_total = self.get_db_value("total_copies") or 0
		self.available_copies = (self.get_db_value("available_copies") or 0) + self.total_copies - previous_total
		if self.available_copies < 0:
			frappe.throw(_("Total Copies cannot be less than the copies currently issued"))
