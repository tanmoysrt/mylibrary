# Copyright (c) 2026, Tanmoy Sarkar and contributors
# See license.txt

from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase

from mylibrary.library.doctype.book.test_book import make_book


def make_register(book, submit=True):
	register = frappe.get_doc({"doctype": "Book Register", "book": book.name, "member": "Administrator"}).insert()
	if submit:
		register.submit()
	return register


def available(book):
	return frappe.db.get_value("Book", book.name, "available_copies")


class IntegrationTestBookRegister(IntegrationTestCase):
	def setUp(self):
		self.book = make_book(isbn="9781861972712", total_copies=2)
		mail = patch("mylibrary.library.doctype.book_register.book_register.send_issue_email")
		self.send_issue_email = mail.start()
		self.addCleanup(mail.stop)

	def test_submit_issues_one_copy(self):
		make_register(self.book)
		self.assertEqual(available(self.book), 1)
		self.send_issue_email.assert_called_once()

	def test_cannot_issue_unavailable_book(self):
		make_register(self.book)
		make_register(self.book)
		self.assertRaises(frappe.ValidationError, make_register, self.book)

	def test_return_restores_copy_once(self):
		register = make_register(self.book)
		register.mark_returned()
		self.assertEqual(available(self.book), 2)
		self.assertRaises(frappe.ValidationError, register.mark_returned)
		self.assertEqual(available(self.book), 2)

	def test_cancel_restores_copy(self):
		register = make_register(self.book)
		register.cancel()
		self.assertEqual(available(self.book), 2)

	def test_cancel_after_return_does_not_restore_again(self):
		register = make_register(self.book)
		register.mark_returned()
		register.reload()
		register.cancel()
		self.assertEqual(available(self.book), 2)

	def test_due_date_defaults_to_loan_period(self):
		register = make_register(self.book, submit=False)
		self.assertTrue(register.due_date)
