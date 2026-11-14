import frappe
from frappe.utils import cint, today

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
	for book in books:
		book.due_back = frappe.db.get_value(
			"Book Register",
			{"book": book.name, "docstatus": 1, "returned_on": ("is", "not set")},
			"due_date",
			order_by="due_date asc",
		)

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
				"due_back": book.due_back,
			}
			for book in books[start : start + page_length]
		],
	}


@frappe.whitelist()
def get_circulation_summary() -> dict:
	frappe.has_permission("Book Register", "read", throw=True)
	values = {"today": today()}
	totals = frappe.db.sql(
		"""
		select
			count(*) as on_loan,
			coalesce(sum(due_date < %(today)s), 0) as overdue
		from `tabBook Register`
		where docstatus = 1 and returned_on is null
		""",
		values,
		as_dict=True,
	)[0]
	top_overdue = frappe.db.sql(
		"""
		select member, member_name, count(*) as overdue
		from `tabBook Register`
		where docstatus = 1 and returned_on is null and due_date < %(today)s
		group by member, member_name
		order by overdue desc, member_name
		limit 5
		""",
		values,
		as_dict=True,
	)
	return {**totals, "top_overdue": top_overdue}
