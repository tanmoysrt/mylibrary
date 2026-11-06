import smtplib
from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase

from mylibrary import notifications
from mylibrary.library.doctype.book.test_book import make_book


class TestNotifications(IntegrationTestCase):
	def make_register(self):
		book = make_book(isbn="9780262033848")
		register = frappe.get_doc({"doctype": "Book Register", "book": book.name, "member": "Administrator"})
		with patch("mylibrary.library.doctype.book_register.book_register.send_issue_email"):
			register.insert().submit()
		return register

	@patch("mylibrary.notifications.time.sleep")
	@patch("mylibrary.notifications.smtplib.SMTP")
	def test_marks_failed_after_all_attempts(self, smtp, sleep):
		smtp.side_effect = smtplib.SMTPServerDisconnected("relay closed the connection")
		register = self.make_register()
		notifications.send_issue_email(register)
		self.assertEqual(smtp.call_count, notifications.MAX_ATTEMPTS)
		self.assertEqual(frappe.db.get_value("Book Register", register.name, "email_status"), "Failed")

	@patch("mylibrary.notifications.smtplib.SMTP")
	def test_marks_sent(self, smtp):
		register = self.make_register()
		notifications.send_issue_email(register)
		self.assertEqual(frappe.db.get_value("Book Register", register.name, "email_status"), "Sent")
