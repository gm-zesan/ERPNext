import frappe
from frappe import _
from frappe.utils import add_days, date_diff, getdate, nowdate


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	report_summary = get_report_summary(data)

	return columns, data, None, chart, report_summary


def get_columns():
	return [
		{
			"label": _("Transaction"),
			"fieldname": "transaction",
			"fieldtype": "Link",
			"options": "Library Transaction",
			"width": 140,
		},
		{
			"label": _("Article ID"),
			"fieldname": "article",
			"fieldtype": "Link",
			"options": "Article",
			"width": 130,
		},
		{
			"label": _("Book Title"),
			"fieldname": "article_title",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label": _("Member ID"),
			"fieldname": "member",
			"fieldtype": "Link",
			"options": "Library Member",
			"width": 130,
		},
		{
			"label": _("Member Name"),
			"fieldname": "member_name",
			"fieldtype": "Data",
			"width": 170,
		},
		{
			"label": _("Issue Date"),
			"fieldname": "issue_date",
			"fieldtype": "Date",
			"width": 110,
		},
		{
			"label": _("Due Date"),
			"fieldname": "due_date",
			"fieldtype": "Date",
			"width": 110,
		},
		{
			"label": _("Days Issued"),
			"fieldname": "days_issued",
			"fieldtype": "Int",
			"width": 100,
		},
		{
			"label": _("Overdue Days"),
			"fieldname": "overdue_days",
			"fieldtype": "Int",
			"width": 110,
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 120,
		},
	]


def get_data(filters):
	loan_period = frappe.db.get_single_value("Library Settings", "loan_period_days") or 14
	today = getdate(nowdate())

	# Find currently issued articles
	issued_articles = frappe.db.get_all(
		"Article",
		filters={"status": "Issued"},
		fields=["name", "title"],
	)

	if not issued_articles:
		return []

	data = []
	for art in issued_articles:
		if filters.get("article") and art.name != filters.get("article"):
			continue

		# Latest Issue transaction for this article
		tx_filters = {"article": art.name, "type": "Issue", "docstatus": 1}
		if filters.get("member"):
			tx_filters["library_member"] = filters.get("member")

		last_issue = frappe.db.get_value(
			"Library Transaction",
			tx_filters,
			["name", "library_member", "date"],
			as_dict=True,
			order_by="date desc, creation desc",
		)

		if not last_issue:
			continue

		issue_date = getdate(last_issue.date)
		due_date = add_days(issue_date, int(loan_period))
		days_issued = date_diff(today, issue_date)
		overdue_days = max(0, days_issued - int(loan_period))
		is_overdue = overdue_days > 0

		status = "Overdue" if is_overdue else "On Loan"

		if filters.get("status"):
			if filters.get("status") == "Overdue" and not is_overdue:
				continue
			if filters.get("status") == "On Loan" and is_overdue:
				continue

		member_name = frappe.db.get_value("Library Member", last_issue.library_member, "full_name")

		data.append(
			{
				"transaction": last_issue.name,
				"article": art.name,
				"article_title": art.title,
				"member": last_issue.library_member,
				"member_name": member_name,
				"issue_date": issue_date,
				"due_date": due_date,
				"days_issued": days_issued,
				"overdue_days": overdue_days,
				"status": status,
			}
		)

	return data


def get_chart_data(data):
	if not data:
		return None

	on_loan = sum(1 for d in data if d["status"] == "On Loan")
	overdue = sum(1 for d in data if d["status"] == "Overdue")

	return {
		"data": {
			"labels": [_("On Loan (Within Time)"), _("Overdue")],
			"datasets": [{"values": [on_loan, overdue]}],
		},
		"type": "donut",
		"colors": ["#29b380", "#ec5858"],
	}


def get_report_summary(data):
	if not data:
		return []

	total_issued = len(data)
	overdue = sum(1 for d in data if d["status"] == "Overdue")
	on_loan = total_issued - overdue

	return [
		{
			"value": total_issued,
			"label": _("Total Issued"),
			"datatype": "Int",
		},
		{
			"value": on_loan,
			"label": _("On Loan"),
			"datatype": "Int",
			"indicator": "Green",
		},
		{
			"value": overdue,
			"label": _("Overdue"),
			"datatype": "Int",
			"indicator": "Red",
		},
	]



