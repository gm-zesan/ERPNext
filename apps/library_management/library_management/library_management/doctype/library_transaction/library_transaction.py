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
		article = frappe.get_doc("Article", self.article)
		if article.status == "Issued":
			frappe.throw(f"Article '{article.title}' ({self.article}) is already issued!")

	def validate_return(self):
		article = frappe.get_doc("Article", self.article)
		if article.status == "Available":
			frappe.throw(f"Article '{article.title}' ({self.article}) cannot be returned as it is already Available!")

	def set_article_status(self, status):
		article = frappe.get_doc("Article", self.article)
		article.status = status
		article.save()
