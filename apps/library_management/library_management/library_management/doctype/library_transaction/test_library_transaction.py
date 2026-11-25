# Copyright (c) 2026, Zesan and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase


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

		# 3. Create Transaction (Issue)
		tx_issue = frappe.get_doc({
			"doctype": "Library Transaction",
			"article": article.name,
			"library_member": member.name,
			"type": "Issue",
			"date": frappe.utils.today()
		}).insert()

		tx_issue.submit()

		# Check status updated to Issued
		article.reload()
		self.assertEqual(article.status, "Issued")

		# 4. Cannot issue again when already Issued
		tx_issue_duplicate = frappe.get_doc({
			"doctype": "Library Transaction",
			"article": article.name,
			"library_member": member.name,
			"type": "Issue",
			"date": frappe.utils.today()
		}).insert()

		self.assertRaises(frappe.ValidationError, tx_issue_duplicate.submit)

		# 5. Return transaction
		tx_return = frappe.get_doc({
			"doctype": "Library Transaction",
			"article": article.name,
			"library_member": member.name,
			"type": "Return",
			"date": frappe.utils.today()
		}).insert()

		tx_return.submit()

		# Check status updated back to Available
		article.reload()
		self.assertEqual(article.status, "Available")

		# 6. Cannot return again when already Available
		tx_return_invalid = frappe.get_doc({
			"doctype": "Library Transaction",
			"article": article.name,
			"library_member": member.name,
			"type": "Return",
			"date": frappe.utils.today()
		}).insert()

		self.assertRaises(frappe.ValidationError, tx_return_invalid.submit)

		# 7. Cancel return -> Article becomes Issued again
		tx_return.cancel()
		article.reload()
		self.assertEqual(article.status, "Issued")

		# 8. Cancel issue -> Article becomes Available again
		tx_issue.cancel()
		article.reload()
		self.assertEqual(article.status, "Available")
