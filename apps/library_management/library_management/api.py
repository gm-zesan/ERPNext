import frappe
from frappe import _
from frappe.utils import add_days, getdate, nowdate


@frappe.whitelist(allow_guest=True)
def get_catalog(search=None, status=None):
	"""Public API: Get list of books in the library catalog.
	Endpoint: /api/method/library_management.api.get_catalog
	"""
	filters = {}
	if status:
		filters["status"] = status

	articles = frappe.get_all(
		"Article",
		filters=filters,
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

	return {
		"status": "success",
		"count": len(articles),
		"books": articles,
	}


@frappe.whitelist()
def get_member_profile(member_id):
	"""Protected API: Get member profile, active membership and borrowed books.
	Endpoint: /api/method/library_management.api.get_member_profile?member_id=LMB-00001
	"""
	if not frappe.db.exists("Library Member", member_id):
		frappe.throw(_("Library Member {0} not found").format(member_id), frappe.DoesNotExistError)

	member = frappe.get_doc("Library Member", member_id)
	today = getdate(nowdate())

	# Active Membership
	active_membership = frappe.db.get_value(
		"Library Membership",
		{
			"library_member": member_id,
			"from_date": ("<=", today),
			"to_date": (">=", today),
			"docstatus": 1,
		},
		["name", "from_date", "to_date", "paid"],
		as_dict=True,
	)

	# Currently borrowed books
	borrowed_books = []
	transactions = frappe.db.get_all(
		"Library Transaction",
		filters={"library_member": member_id, "docstatus": 1},
		fields=["name", "article", "type", "date"],
		order_by="date desc, creation desc",
	)

	loan_period = frappe.db.get_single_value("Library Settings", "loan_period_days") or 14

	# Track net borrowed articles
	article_status = {}
	for tx in reversed(transactions):
		if tx.type == "Issue":
			article_status[tx.article] = tx
		elif tx.type == "Return" and tx.article in article_status:
			del article_status[tx.article]

	for art_id, tx in article_status.items():
		art_title = frappe.db.get_value("Article", art_id, "title")
		due_date = add_days(getdate(tx.date), int(loan_period))
		borrowed_books.append(
			{
				"article_id": art_id,
				"title": art_title,
				"issue_date": tx.date,
				"due_date": due_date,
				"transaction_id": tx.name,
			}
		)

	return {
		"status": "success",
		"member": {
			"name": member.name,
			"full_name": member.full_name,
			"email": member.email_address,
			"phone": member.phone,
		},
		"has_active_membership": bool(active_membership),
		"active_membership": active_membership,
		"borrowed_books_count": len(borrowed_books),
		"borrowed_books": borrowed_books,
	}


@frappe.whitelist()
def issue_book(article_id, member_id):
	"""Protected API: Issue an article to a member.
	Endpoint: POST /api/method/library_management.api.issue_book
	Payload: { "article_id": "ART-00001", "member_id": "LMB-00001" }
	"""
	tx = frappe.get_doc(
		{
			"doctype": "Library Transaction",
			"article": article_id,
			"library_member": member_id,
			"type": "Issue",
			"date": nowdate(),
		}
	)
	tx.insert()
	tx.submit()

	loan_period = frappe.db.get_single_value("Library Settings", "loan_period_days") or 14
	due_date = add_days(getdate(nowdate()), int(loan_period))

	return {
		"status": "success",
		"message": _("Book issued successfully!"),
		"transaction_id": tx.name,
		"article_id": article_id,
		"member_id": member_id,
		"due_date": due_date,
	}


@frappe.whitelist()
def return_book(article_id, member_id):
	"""Protected API: Return an article.
	Endpoint: POST /api/method/library_management.api.return_book
	Payload: { "article_id": "ART-00001", "member_id": "LMB-00001" }
	"""
	tx = frappe.get_doc(
		{
			"doctype": "Library Transaction",
			"article": article_id,
			"library_member": member_id,
			"type": "Return",
			"date": nowdate(),
		}
	)
	tx.insert()
	tx.submit()

	return {
		"status": "success",
		"message": _("Book returned successfully!"),
		"transaction_id": tx.name,
		"article_id": article_id,
		"member_id": member_id,
	}
