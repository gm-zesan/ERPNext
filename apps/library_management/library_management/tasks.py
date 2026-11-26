import frappe
from frappe import _
from frappe.utils import date_diff, getdate, nowdate


def daily():
	"""Scheduled daily task to check overdue books and notify librarians/members."""
	return check_overdue_books_and_send_alerts()


def check_overdue_books_and_send_alerts():
	loan_period = frappe.db.get_single_value("Library Settings", "loan_period_days") or 14
	today = getdate(nowdate())

	# 1. Find all articles currently issued
	issued_articles = frappe.db.get_all(
		"Article",
		filters={"status": "Issued"},
		fields=["name", "title"],
	)

	alerts_sent = 0
	for art in issued_articles:
		last_issue = frappe.db.get_value(
			"Library Transaction",
			{"article": art.name, "type": "Issue", "docstatus": 1},
			["name", "library_member", "date"],
			as_dict=True,
			order_by="date desc, creation desc",
		)

		if not last_issue:
			continue

		issue_date = getdate(last_issue.date)
		days_issued = date_diff(today, issue_date)
		overdue_days = days_issued - int(loan_period)

		if overdue_days > 0:
			# Overdue book found!
			member = frappe.get_doc("Library Member", last_issue.library_member)
			subject = f"⚠️ Overdue Book Alert: '{art.title}' ({overdue_days} days overdue)"
			message = f"""
			<p>Hello Librarian,</p>
			<p>The book <strong>{art.title}</strong> (ID: {art.name}) borrowed by <strong>{member.full_name}</strong> (Member ID: {member.name}) is now <strong>{overdue_days} days overdue</strong>.</p>
			<ul>
				<li><strong>Issue Date:</strong> {issue_date}</li>
				<li><strong>Allowed Loan Period:</strong> {loan_period} days</li>
				<li><strong>Transaction ID:</strong> {last_issue.name}</li>
				<li><strong>Member Email:</strong> {member.email_address or 'N/A'}</li>
				<li><strong>Member Phone:</strong> {member.phone or 'N/A'}</li>
			</ul>
			<p>Please contact the member to return the book promptly or renew their loan.</p>
			"""

			# Find system managers / librarians to notify
			recipients = frappe.get_all(
				"Has Role",
				filters={"role": "System Manager", "parenttype": "User"},
				pluck="parent",
			)
			target_users = set([u for u in recipients if u not in ["Guest"]])

			for user in target_users:
				# Avoid duplicate notification on the same day for this transaction
				already_notified = frappe.db.exists(
					"Notification Log",
					{
						"for_user": user,
						"document_type": "Library Transaction",
						"document_name": last_issue.name,
					},
				)
				if not already_notified:
					doc = frappe.get_doc(
						{
							"doctype": "Notification Log",
							"subject": subject,
							"for_user": user,
							"type": "Alert",
							"email_content": message,
							"document_type": "Library Transaction",
							"document_name": last_issue.name,
						}
					)
					doc.insert(ignore_permissions=True)
					alerts_sent += 1

	frappe.db.commit()
	return f"Checked overdue books. Total alerts created: {alerts_sent}"


