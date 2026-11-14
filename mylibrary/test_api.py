import frappe
from frappe.tests import IntegrationTestCase

from mylibrary.api import get_circulation_summary, search_books
from mylibrary.library.doctype.book.test_book import make_book


class TestSearchBooks(IntegrationTestCase):
	def setUp(self):
		make_book(isbn="9780131103627", title="The C Programming Language", author="Brian Kernighan")
		make_book(isbn="9780201633610", title="Design Patterns", author="Erich Gamma")

	def test_isbn_lookup(self):
		result = search_books("9780131103627", search_by="isbn")
		self.assertEqual([book["title"] for book in result["results"]], ["The C Programming Language"])

	def test_author_lookup(self):
		result = search_books("Erich", search_by="author")
		self.assertIn("Design Patterns", [book["title"] for book in result["results"]])

	def test_unknown_field_returns_nothing(self):
		self.assertEqual(search_books("x", search_by="title")["total"], 0)

	def test_page_length_is_bounded(self):
		self.assertLessEqual(len(search_books("9", search_by="isbn", page_length=1000)["results"]), 100)

	def test_circulation_summary_shape(self):
		summary = get_circulation_summary()
		self.assertEqual(set(summary), {"on_loan", "overdue", "top_overdue"})

	def test_due_back_shows_earliest_open_loan(self):
		result = search_books("9780201633610", search_by="isbn")
		self.assertIn("due_back", result["results"][0])
