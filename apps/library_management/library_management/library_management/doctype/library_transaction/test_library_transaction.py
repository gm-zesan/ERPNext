# Copyright (c) 2026, Zesan and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, today


class IntegrationTestLibraryTransaction(IntegrationTestCase):
	def test_transaction_issue_and_return(self):
		# 1. Create Article
		article = frappe.get_doc({
			"doctype": "Article",
			"title": "Clean Code",
			"author": "Robert C. Martin",
			"status": "Available"
		}).insert()

		# 2. Create Member
		member = frappe.get_doc({
			"doctype": "Library Member",
			"first_name": "Zesan",
			"last_name": "Ahmed",
			"email_address": "zesan_test@example.com"
		}).insert()

		# 3. Try to issue WITHOUT membership (must fail!)
		tx_issue_no_membership = frappe.get_doc({
			"doctype": "Library Transaction",
			"article": article.name,
			"library_member": member.name,
			"type": "Issue",
			"date": today()
		}).insert()

		self.assertRaises(frappe.ValidationError, tx_issue_no_membership.submit)

		# 4. Create active paid membership for member
		membership = frappe.get_doc({
			"doctype": "Library Membership",
			"library_member": member.name,
			"from_date": today(),
			"to_date": add_days(today(), 30),
			"paid": 1
		}).insert()
		membership.submit()

		# 5. Now issue book WITH membership (must succeed!)
		tx_issue = frappe.get_doc({
			"doctype": "Library Transaction",
			"article": article.name,
			"library_member": member.name,
			"type": "Issue",
			"date": today()
		}).insert()
		tx_issue.submit()

		# Check status updated to Issued
		article.reload()
		self.assertEqual(article.status, "Issued")

		# 6. Cannot issue again when already Issued
		tx_issue_duplicate = frappe.get_doc({
			"doctype": "Library Transaction",
			"article": article.name,
			"library_member": member.name,
			"type": "Issue",
			"date": today()
		}).insert()

		self.assertRaises(frappe.ValidationError, tx_issue_duplicate.submit)

		# 7. Return transaction
		tx_return = frappe.get_doc({
			"doctype": "Library Transaction",
			"article": article.name,
			"library_member": member.name,
			"type": "Return",
			"date": today()
		}).insert()

		tx_return.submit()

		# Check status updated back to Available
		article.reload()
		self.assertEqual(article.status, "Available")

		# 8. Cannot return again when already Available
		tx_return_invalid = frappe.get_doc({
			"doctype": "Library Transaction",
			"article": article.name,
			"library_member": member.name,
			"type": "Return",
			"date": today()
		}).insert()

		self.assertRaises(frappe.ValidationError, tx_return_invalid.submit)

		# 9. Cancel return -> Article becomes Issued again
		tx_return.cancel()
		article.reload()
		self.assertEqual(article.status, "Issued")

		# 10. Cancel issue -> Article becomes Available again
		tx_issue.cancel()
		article.reload()
		self.assertEqual(article.status, "Available")

	def test_maximum_articles_limit(self):
		# Set max limit to 1
		frappe.db.set_single_value("Library Settings", "maximum_articles_allowed", 1)

		member = frappe.get_doc({
			"doctype": "Library Member",
			"first_name": "Quota",
			"last_name": "Tester",
			"email_address": "quota@example.com"
		}).insert()

		membership = frappe.get_doc({
			"doctype": "Library Membership",
			"library_member": member.name,
			"from_date": today(),
			"to_date": add_days(today(), 30),
			"paid": 1
		}).insert()
		membership.submit()

		article1 = frappe.get_doc({
			"doctype": "Article",
			"title": "Book One",
			"status": "Available"
		}).insert()

		article2 = frappe.get_doc({
			"doctype": "Article",
			"title": "Book Two",
			"status": "Available"
		}).insert()

		# Issue book 1 (Quota: 1/1, succeeds)
		tx1 = frappe.get_doc({
			"doctype": "Library Transaction",
			"article": article1.name,
			"library_member": member.name,
			"type": "Issue",
			"date": today()
		}).insert()
		tx1.submit()

		# Issue book 2 (Quota: 2/1, must fail!)
		tx2 = frappe.get_doc({
			"doctype": "Library Transaction",
			"article": article2.name,
			"library_member": member.name,
			"type": "Issue",
			"date": today()
		}).insert()
		self.assertRaises(frappe.ValidationError, tx2.submit)

		# Return book 1 (Quota resets to 0/1)
		tx_return = frappe.get_doc({
			"doctype": "Library Transaction",
			"article": article1.name,
			"library_member": member.name,
			"type": "Return",
			"date": today()
		}).insert()
		tx_return.submit()

		# Now book 2 can be issued!
		tx2.reload()
		tx2.submit()
		self.assertEqual(tx2.docstatus, 1)

		# Restore default limit
		frappe.db.set_single_value("Library Settings", "maximum_articles_allowed", 3)
