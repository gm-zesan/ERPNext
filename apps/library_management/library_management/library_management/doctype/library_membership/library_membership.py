# Copyright (c) 2026, Zesan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class LibraryMembership(Document):
	def validate(self):
		self.validate_dates()

	def before_submit(self):
		self.validate_paid()
		self.validate_overlapping_membership()

	def validate_dates(self):
		"""From Date cannot be after To Date"""
		if getdate(self.from_date) > getdate(self.to_date):
			frappe.throw("From Date cannot be after To Date!")

	def validate_paid(self):
		"""Cannot submit unpaid membership"""
		if not self.paid:
			frappe.throw("Cannot submit Membership without payment confirmation (Please check 'Paid')!")

	def validate_overlapping_membership(self):
		"""Check if an active submitted membership already exists for this member in this date range"""
		overlapping = frappe.db.exists(
			"Library Membership",
			{
				"library_member": self.library_member,
				"docstatus": 1,
				"name": ("!=", self.name),
				"to_date": (">=", self.from_date),
				"from_date": ("<=", self.to_date),
			},
		)
		if overlapping:
			frappe.throw(
				f"There is already an active Membership ({overlapping}) for {self.library_member} during this period!"
			)
