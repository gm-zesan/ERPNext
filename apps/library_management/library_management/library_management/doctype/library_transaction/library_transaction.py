# Copyright (c) 2026, Zesan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LibraryTransaction(Document):
	def before_submit(self):
		if self.type == "Issue":
			self.validate_issue()
			self.set_article_status("Issued")
		elif self.type == "Return":
			self.validate_return()
			self.set_article_status("Available")

	def on_cancel(self):
		if self.type == "Issue":
			self.set_article_status("Available")
		elif self.type == "Return":
			self.set_article_status("Issued")

	def validate_issue(self):
		self.validate_membership()
		self.validate_maximum_limit()
		article = frappe.get_doc("Article", self.article)
		if article.status == "Issued":
			frappe.throw(f"Article '{article.title}' ({self.article}) is already issued!")

	def validate_membership(self):
		has_membership = frappe.db.exists(
			"Library Membership",
			{
				"library_member": self.library_member,
				"docstatus": 1,
				"paid": 1,
				"from_date": ("<=", self.date),
				"to_date": (">=", self.date),
			},
		)
		if not has_membership:
			frappe.throw(
				f"Member '{self.library_member}' does not have an active paid membership on {self.date}!"
			)

	def validate_maximum_limit(self):
		max_articles = frappe.db.get_single_value("Library Settings", "maximum_articles_allowed")
		if not max_articles:
			max_articles = 3

		issued_count = frappe.db.count(
			"Library Transaction",
			{
				"library_member": self.library_member,
				"type": "Issue",
				"docstatus": 1,
			},
		)
		returned_count = frappe.db.count(
			"Library Transaction",
			{
				"library_member": self.library_member,
				"type": "Return",
				"docstatus": 1,
			},
		)
		current_active_issues = issued_count - returned_count
		if current_active_issues >= max_articles:
			frappe.throw(
				f"Member '{self.library_member}' has already reached the maximum limit of {max_articles} issued articles!"
			)

	def validate_return(self):
		article = frappe.get_doc("Article", self.article)
		if article.status == "Available":
			frappe.throw(f"Article '{article.title}' ({self.article}) cannot be returned as it is already Available!")

	def set_article_status(self, status):
		article = frappe.get_doc("Article", self.article)
		article.status = status
		article.save()
