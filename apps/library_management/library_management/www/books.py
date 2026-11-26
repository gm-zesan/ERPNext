import frappe


def get_context(context):
	search = frappe.form_dict.get("search")

	articles = frappe.get_all(
		"Article",
		fields=["name", "title", "author", "isbn", "status", "description", "image"],
		order_by="title asc",
	)

	if search:
		search_lower = search.strip().lower()
		articles = [
			a
			for a in articles
			if search_lower in (a.title or "").lower()
			or search_lower in (a.author or "").lower()
			or search_lower in (a.isbn or "").lower()
		]

	context.books = articles
	context.search_query = search or ""
	context.title = "City Central Library - Book Catalog"
