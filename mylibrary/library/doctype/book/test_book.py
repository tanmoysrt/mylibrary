# Copyright (c) 2026, Tanmoy Sarkar and contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

from mylibrary.library.doctype.book.book import is_valid_isbn13, normalize_isbn


def make_book(isbn="9780306406157", total_copies=2, **fields):
	frappe.db.delete("Book", {"isbn": isbn})
	return frappe.get_doc(
		{
			"doctype": "Book",
			"title": fields.get("title", "Test Book"),
			"author": fields.get("author", "Test Author"),
			"isbn": isbn,
			"total_copies": total_copies,
		}
	).insert()


class IntegrationTestBook(IntegrationTestCase):
	def test_isbn_checksum(self):
		self.assertTrue(is_valid_isbn13("9780306406157"))
		self.assertFalse(is_valid_isbn13("9780306406158"))
		self.assertEqual(normalize_isbn("978-0-306-40615-7"), "9780306406157")

	def test_new_book_is_fully_available(self):
		book = make_book(total_copies=3)
		self.assertEqual(book.available_copies, 3)

	def test_changing_total_adjusts_available(self):
		book = make_book(total_copies=3)
		frappe.db.set_value("Book", book.name, "available_copies", 1)
		book.reload()
		book.total_copies = 5
		book.save()
		self.assertEqual(book.available_copies, 3)
