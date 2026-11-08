import frappe
from frappe.utils import cint

SEARCH_FIELDS = {"isbn": "isbn", "author": "author"}
MAX_PAGE_LENGTH = 100


@frappe.whitelist()
def search_books(query: str, search_by: str = "author", page: int = 1, page_length: int = 20) -> dict:
	frappe.has_permission("Book", "read", throw=True)
	query = (query or "").strip()
	field = SEARCH_FIELDS.get(search_by)
	if not query or not field:
		return {"total": 0, "results": []}

	page = max(cint(page), 1)
	page_length = min(max(cint(page_length), 1), MAX_PAGE_LENGTH)
	names = frappe.get_all("Book", filters={field: ["like", f"%{query}%"]}, pluck="name", limit_page_length=0)
	books = [frappe.get_doc("Book", name) for name in names]
	books.sort(key=lambda book: (book.author.lower(), book.title.lower()))

	start = (page - 1) * page_length
	return {
		"total": len(books),
		"results": [
			{
				"name": book.name,
				"title": book.title,
				"author": book.author,
				"isbn": book.isbn,
				"available_copies": book.available_copies,
				"total_copies": book.total_copies,
			}
			for book in books[start : start + page_length]
		],
	}
